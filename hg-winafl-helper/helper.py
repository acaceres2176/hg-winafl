#!/usr/bin/python3

import subprocess
import base64
import os
import sys
import time
import socket
import urllib3
import string
import requests
import hashlib
from urllib.parse import unquote
from bs4 import BeautifulSoup

# max size of file e.g 512 * 512 = 256kb
MAX_SIZE = 512 * 512

def log(msg):
  print("[%s] %s" % (time.asctime(), msg))

class CSamplesFinder:
  def __init__(self):
    pass

  def find(self, ext, magic, folder, isBinary, count, query):
    ext = str(ext)
    magic = str(magic)
    folder = str(folder)
    isBinary = int(isBinary)
    count = str(count)
    query = str(query)
    curCount = 0

    socket.setdefaulttimeout(30)
    url = "https://www.google.com/search?q=filetype:%s+%s+-facebook.com&num=%s" % (ext, query,count)
    headers = {"User Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    r = requests.get(url, headers=headers, timeout=5)
    buf = r.text
    soup = BeautifulSoup(buf, features="html.parser")
    for a in soup.findAll("a", href=True):
      href = a["href"]
      if href.find("webcache.googleusercontent.com") > -1:
        continue
      if href.find("url?q=") > -1:
        pos = href.find("&")
        if pos > -1:
          href = unquote(href[7:pos])
          log("Downloading %s..." % href)
          curCount = curCount + 1
          try:
            file_data = str(requests.get(href, headers=headers, timeout=5).text)
            if len(file_data) > MAX_SIZE:
              #log("Discarding file as it's bigger than maximum size (%d kbs)" % (MAX_SIZE/1024))
              continue
            # compare first 4 bytes of the file's header rather than a string
            if isBinary == 1:
              FileHeader = file_data[:4].encode("utf-8").hex()
              if magic != FileHeader:
                #log("Discarding file as it doesn't start with %s (starts with %s)" % (repr(magic), repr(file_data[:5])))
                continue
            else:
              if not file_data.startswith(magic):
                #log("Discarding file as it doesn't start with %s (starts with %s)" % (repr(magic), repr(file_data[:5])))
                continue
            file_hash = (hashlib.sha1(file_data.encode('utf-8'))).hexdigest()
            f = open(os.path.join(folder, file_hash) + "." + ext, "wb")
            f.write(file_data.encode('utf-8'))
            f.close()
            log("File %s saved" % file_hash)
          except KeyboardInterrupt:
            log("Aborted")
            return
          except:
            #log("Error: %s" % str(sys.exc_info()[1]))
            return
    print("Total Files Processed:",curCount)

def generate_corpus(ext, magic, directory,isBinary,count):
  finder = CSamplesFinder()
  terms = ["a", "b", "c", "d", "e", "f", "g"]
  for string in terms:
    finder.find(ext, magic, directory, isBinary, count, string)

def usage():
  print("Usage:", sys.argv[0], "build | generate | help | run")

def test_samples(extention, directory):
  testcases = []
  for root, dirs, files in os.walk(directory, topdown=False):
      for name in files:
          if name.endswith(extention):
              testcase =  os.path.abspath(os.path.join(root, name))
              testcases.append(testcase)
  for testcase in testcases:
      print("[*] Running DynamoRIO for testcase: ", testcase)

def build():
  vswhere_cmd = "vswhere.exe -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath"
  visual_studio = subprocess.check_output(vswhere_cmd,shell=False)
  vcvarsalldir = visual_studio.decode('utf-8').rstrip() + "\VC\Auxiliary\Build"
  startingdir = os.getcwd()
  
  # build 32 bit winafl
  os.chdir(vcvarsalldir)
  if not os.path.exists(startingdir + "\winafl\\bin32"):
    os.makedirs(startingdir + "\winafl\\bin32")
  cmd_32 = "cmake -G\"Visual Studio 15 2017\" .. -DDynamoRIO_DIR=" + startingdir + "\winafl\dynamrio\cmake && cmake --build "+ startingdir + "\winafl\\bin32" + " --config Release"
  print("vcvarsall.bat x86 && cd " + startingdir + "\winafl\\bin32 && " + cmd_32)
  os.system("vcvarsall.bat x86 && cd /d " + startingdir + "\winafl\\bin32 && " + cmd_32)

  # build 64 bit winafl
  os.chdir(vcvarsalldir)
  if not os.path.exists(startingdir + "\winafl\\bin64"):
    os.makedirs(startingdir + "\winafl\\bin64")
  cmd_64 = "cmake -G\"Visual Studio 15 2017 Win64\" .. -DDynamoRIO_DIR=" + startingdir + "\winafl\dynamrio\cmake && cmake --build "+ startingdir + "\winafl\\bin64" + " --config Release"
  print("vcvarsall.bat x64 && cd " + startingdir + "\winafl\\bin64 && " + cmd_64)
  os.system("vcvarsall.bat x64 && cd /d" + startingdir + "\winafl\\bin64 && " + cmd_64)
  

def run_afl():
  print("Running afl...")

if __name__ == "__main__":
  fuzzing_file_ext = "xml"
  search_binary = 0
  corpus_dir = "corpus"
  fuzzing_file_signature = "<?xml"
  result_size = 100
  
  if len(sys.argv) != 2:
    usage()
  elif sys.argv[1] == "help":
    usage()
  elif sys.argv[1] == "build":
    build()
  elif sys.argv[1] == "generate":
    generate_corpus(fuzzing_file_ext, fuzzing_file_signature, corpus_dir, search_binary, result_size)
  elif sys.argv[1] == "run":
    test_samples(fuzzing_file_ext, corpus_dir)
    run_afl()