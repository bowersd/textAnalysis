#import hfst
import regex
import pyhfst

print("Coming soon: put in a Nishnaabemwin text, get back a (rough) interlinear analysis of the text")
print("mkizin")
print("mkizin+NI ... this was hard coded")

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

print(parse_pyhfst("./morphophonologyclitics_analyze.hfstol", "mkizin"))
