import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
#import hfst
import regex
import pyhfst
from pyscript import document

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
    input_text = document.querySelector("#freeNish")
    freeNish = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *freeNish.split(" "))

#print(parse_pyhfst("./morphophonologyclitics_analyze.hfstol", "mkizin"))
