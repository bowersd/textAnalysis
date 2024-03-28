import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/e0/02/c10a69ff21d6679a6b6e28c42cd265bec2cdd9be3dcbbee830a10fa4b0e5/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
from pyweb import pydom
import pyscript
import asyncio
from js import console, Uint8Array, File, URL, document #File et seq were added for download, maybe pyscript.File, URL, document will work?
import io #this was added for download
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

def sep_punct(string, drop_punct): #diy tokenization, use nltk?
    if not drop_punct: return "'".join(regex.sub("(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", " \g<1> ", string).split("’")) #separate all punc, then replace single quote ’ with '
    return "'".join(regex.sub("(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", "", string).split("’")) #remove all punc, then replace single quote ’ with '

def min_morphs(*msds):
    """the length of the shortest morphosyntactic description"""
    return min([m[0].count("+") for m in msds])

def disambiguate(target, f, *msds): 
    """the earliest of the morphosyntactic descriptions|f(m) = target"""
    #prioritizing order allows weighting schemes to be exploited
    for i in range(len(msds)):
        if f(msds[i]) == target: return i
    #first default
    return 0

def parse_text(drop_punct, *sentences):
    analysis = []
    analyses = parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *[x for s in sentences for x in sep_punct(s.lower(), drop_punct).split()])
    for s in sentences:
        a = []
        for w in sep_punct(s.lower(), drop_punct).split():
            best = analyses[w][disambiguate(min_morphs(*analyses[w]), min_morphs, *analyses[w])][0]
            console.log(best)
            a.append(best)
        analysis.append(a)
    return analysis


async def _upload_file_and_analyze(e):
    console.log("Attempted file upload: " + e.target.value)
    file_list = e.target.files
    first_item = file_list.item(0)

    my_bytes: bytes = await get_bytes_from_file(first_item)
    console.log(my_bytes[:10])
    textIn = my_bytes.decode().split('\n')
    console.log(textIn[0])
    analyzed = parse_text(False, *textIn)
    console.log(analyzed[0])
    console.log("I did it!")

    #new_txt = pyscript.document.createElement('txt')
    #new_txt.src = pyscript.window.URL.createObjectURL(first_item)
    #pyscript.document.getElementById("output_upload").appendChild(new_txt)

async def get_bytes_from_file(file):
    array_buf = await file.arrayBuffer()
    return array_buf.to_bytes()

upload_file = pyscript.document.getElementById("file-upload")
add_event_listener(upload_file, "change", _upload_file_and_analyze) #maybe "click" instead of "change"

data = "this is some text"
def downloadFile(*args):
    encoded_data = data.encode('utf-8')
    my_stream = io.BytesIO(encoded_data)

    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())

    file = File.new([js_array], "unused_file_name.txt", {type: "text/plain"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", "my_other_file_name.txt")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

add_event_listener(document.getElementById("download"), "click", downloadFile)
