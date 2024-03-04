import micropip
await micropip.install(
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    './pyhfst-1.2.0-py2.py3-none-any.whl'
)
#import hfst
import os
import regex
import pyhfst

print("Coming soon: put in a Nishnaabemwin text, get back a (rough) interlinear analysis of the text")
print("mkizin")
print("mkizin+NI ... this was hard coded")
print("taast")

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

print(os.getcwd())
print(os.listdir('/'))
print(os.listdir('./'))
print(parse_pyhfst("./morphophonologyclitics_analyze.hfstol", "mkizin"))
