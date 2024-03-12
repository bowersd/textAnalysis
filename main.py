import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
#import hfst
import regex
import pyhfst
from pyscript import document
from pyweb import pydom

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

def parse_text(event):
    analysis = []
    textIn = []
    with open("C:\\fakepath\\"+document.querySelector("#targetLanguageText").value) as fileIn:
        for line in fileIn: textIn.append(line.strip()) #split on sentence final punctuation to make life easier on users?
    analyses = parse_pyhfst("./morphphonologyclitics_analyze.hfstol", *[x for s in textIn for x in s.lower().split()]) #need tokenization
    for s in textIn:
        a = []
        for w in s.lower().split(): #need tokenization
            a.append(analyses[w])
        analysis.append(a)
    return analysis


#print(parse_pyhfst("./morphophonologyclitics_analyze.hfstol", "mkizin"))
