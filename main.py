import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
import regex
import pyhfst
from pyweb import pydom
import pyscript

#print("Coming soon: put in a Nishnaabemwin text, get back a (rough) interlinear analysis of the text")
#print("For now, a demonstration that a functioning analyzer is loaded")

def parse_pyhfst(transducer, *strings):
    h = {}
    parser = pyhfst.HfstInputStream(transducer).read()
    for s in strings: 
        if s not in h: 
            h[s] = []
            p = parser.lookup(s)
            if not p: h[s].append((s+"+?", 0.00))
            else: 
                for q in p: h[s].append((regex.sub("@.*?@", "" ,q[0]), q[1])) #filtering out flag diacritics, which the hfst api does not do as of dec 2023
    return h

def parse_words(event):
    input_text = pyscript.document.querySelector("#freeNish")
    freeNish = input_text.value
    output_div = pyscript.document.querySelector("#output")
    output_div.innerText = parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *freeNish.split(" "))

def parse_text(event):
    analysis = []
    textIn = []
    with open(pyscript.document.querySelector("#targetLanguageText").text) as fileIn:
        for line in fileIn: textIn.append(line.strip()) #split on sentence final punctuation to make life easier on users?
    analyses = parse_pyhfst("./morphphonologyclitics_analyze.hfstol", *[x for s in textIn for x in s.lower().split()]) #need tokenization
    for s in textIn:
        a = []
        for w in s.lower().split(): #need tokenization
            a.append(analyses[w])
        analysis.append(a)
    return analysis


#import asyncio
#import js
#from js import document, FileReader
#from pyodide.ffi import create_proxy
# 
#def read_complete(event):
#    # event is ProgressEvent
#    content = document.getElementById("content");
#    content.innerText = event.target.result
#
# 
#async def process_file(x):
#    fileList = document.getElementById('targetLanguageText').files
#    for f in fileList:
#        # reader is a pyodide.JsProxy
#        reader = FileReader.new()
#        # Create a Python proxy for the callback function
#        onload_event = create_proxy(read_complete)
#        #console.log("done")
#        reader.onload = onload_event
#        reader.readAsText(f)
#    return
# 
#def main(x):
#    # Create a Python proxy for the callback function
#    file_event = create_proxy(process_file)
#
#    # Set the listener to the callback
#    e = document.getElementById("targetLanguageText")
#    e.addEventListener("change", file_event, False)
#    print(e)
 
import asyncio
from js import document, window, Uint8Array
from pyodide.ffi.wrappers import add_event_listener

async def upload_file_and_show(e):
    print("I'm here!")
    file_list = e.target.files
    first_item = file_list.item(0)

    my_bytes: bytes = await get_bytes_from_file(first_item)
    print(my_bytes[:10]) # Do something with file contents

async def get_bytes_from_file(file):
    array_buf = await file.arrayBuffer()
    return array_buf.to_bytes()

print("the script has been run")
add_event_listener(document.getElementById("file-upload"), "change", upload_file_and_show)
