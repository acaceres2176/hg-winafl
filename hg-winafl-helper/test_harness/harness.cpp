#include <stdio.h>
#include <tchar.h>
#include <windows.h>
#import <msxml6.dll>

using namespace MSXML2;
extern "C" __declspec(dllexport) _bstr_t fuzzme(wchar_t* filename);
extern "C" __declspec(dllexport)  int main(int argc, char** argv);


inline void TESTHR( HRESULT _hr )   
   { if FAILED(_hr) throw(_hr); }  

wchar_t* charToWChar(const char* text)
{
    size_t size = strlen(text) + 1;
    wchar_t* wa = new wchar_t[size];
    mbstowcs(wa, text, size);
    return wa;
}

void dump_com_error(_com_error &e)
{
    _bstr_t bstrSource(e.Source());
    _bstr_t bstrDescription(e.Description());

    printf("Error\n");
    printf("\a\tCode = %08lx\n", e.Error());
    printf("\a\tCode meaning = %s", e.ErrorMessage());
    printf("\a\tSource = %s\n", (LPCSTR)bstrSource);
    printf("\a\tDescription = %s\n", (LPCSTR)bstrDescription);
}

_bstr_t XMLDOMDocumentFragmentSample( _bstr_t bstrFile)  
{  
    _bstr_t bstrResult = L"";
    try  
    {  
        MSXML2::IXMLDOMDocumentPtr docPtr;  
        _bstr_t bstrLoadOutput = L"";

        TESTHR(docPtr.CreateInstance("Msxml2.DOMDocument.6.0"));
        // load a document
        _variant_t varXml(_T(charToWChar(bstrFile))); 
        _variant_t varOut((bool)TRUE);
        bstrLoadOutput = docPtr->load(varXml);         

        // create a new node and add to the doc  
        _variant_t varTyp((short) MSXML2::NODE_ELEMENT);  
        _bstr_t varName(_T("BOOK"));  
        MSXML2::IXMLDOMNodePtr nodePtr= docPtr->createNode(varTyp, varName, "");  

        // create a doc fragment and associate the new node with it  
        MSXML2::IXMLDOMDocumentFragmentPtr fragPtr = docPtr->createDocumentFragment();  
        fragPtr->appendChild(nodePtr);  
        // add some elements to the new node  
        varName = _T("TITLE");  
        MSXML2::IXMLDOMNodePtr nodePtr1= docPtr->createNode(varTyp, varName, "");  
        nodePtr1->text = _T("asdf-asdf-asdf");  
        nodePtr->appendChild(nodePtr1);
        fragPtr->xml; 
        // add the fragment to the original doc  
        docPtr->documentElement->appendChild(fragPtr);  
        docPtr->xml;
    }   
    catch (_com_error &e)  
    {  
        dump_com_error(e);  
    }  
    CleanUp:
        return bstrResult;
}

_bstr_t fuzzme(wchar_t* filename)
{
    _bstr_t bstrOutput = XMLDOMDocumentFragmentSample(filename);
    return bstrOutput;

}

int main(int argc, char** argv)
{
    if (argc < 2) {
        printf("Usage: %s <xml file>\n", argv[0]);
        return 0;
    }
    HRESULT hr = CoInitialize(NULL);
    if (SUCCEEDED(hr))
    {
        try
        {
            _bstr_t bstrOutput = fuzzme(charToWChar(argv[1]));
        }
        catch (_com_error &e)
        {
            dump_com_error(e);
        }
        CoUninitialize();
    }

    return 0;

}