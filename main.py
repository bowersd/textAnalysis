import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
from pyweb import pydom
import pyscript
import asyncio
from js import console, Uint8Array
from pyodide.ffi.wrappers import add_event_listener
import regex
import pyhfst
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


async def _upload_file_and_show(e):
    console.log("Attempted file upload: " + e.target.value)
    file_list = e.target.files
    first_item = file_list.item(0)

    print("I'm here!")
    my_bytes: bytes = await get_bytes_from_file(first_item)
    print("I'm still here!")
    print(my_bytes[:10])
    console.log(my_bytes[:10])
    #new_txt = pyscript.document.createElement('txt')
    #new_txt.src = pyscript.window.URL.createObjectURL(first_item)
    #pyscript.document.getElementById("output_upload").appendChild(new_txt)

async def get_bytes_from_file(file):
    array_buf = await file.arrayBuffer()
    return array_buf.to_bytes()

upload_file = pyscript.document.getElementById("file-upload")
add_event_listener(upload_file, "change", _upload_file_and_show) #maybe "click" instead of "change"
