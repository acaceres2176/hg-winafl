### Installation:

Open vs_buildtools.exe and install "Visual C++ build tools" and run ```python3 helper.py help```

### Usage:

##### Build winafl:
```
python3 helper.py build
```
##### Generate corpus:
```
python3 helper.py generate
```
*Note* https://en.wikipedia.org/wiki/List_of_file_signatures can be used to find the right file signatures to search for

##### Run winafl:
```
python3 helper.py run
```

##### Get usage information:
```
python3 helper.py help
```

### Special thanks:

* Nightmare Fuzzing Project samples finder(https://github.com/joxeankoret/nightmare/blob/master/runtime/find_samples.py)
    * @author: Joxean Koret, @joxeankoret
    * @author: Hardik Shah, @hardik05
* winafl with mopt mutators and afl fast power schedulers(https://github.com/hardik05/winafl-powermopt)
    * @author: Hardik Shah, @hardik05
    * Michal Zalewski <lcamtuf@google.com>
    * Ivan Fratric <ifratric@google.com>
* https://symeonp.github.io/2017/09/17/fuzzing-winafl.html
    * @author: simospar@gmail.com