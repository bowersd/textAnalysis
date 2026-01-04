def parse_pyhfst(transducer, *strings):
    h = {}
    parser = pyhfst.HfstInputStream(transducer).read()
    for s in strings: 
        if s not in h: 
            h[s] = []
            p = parser.lookup(s)
            if not p: h[s].append((s+"+?", 0.00))
            else: 
                for q in p: h[s].append((regex.sub(r"@.*?@", "" ,q[0]), q[1])) #filtering out flag diacritics, which the hfst api does not do as of dec 2023
    return h

def formatted(interpreted):
    out = []
    out.append(interpreted["Head"])
    if interpreted["DerivChain"] != interpreted["Head"]: out.append("("+interpreted["DerivChain"]+")")
    if interpreted["Periph"]: out.append(interpreted["Periph"])
    if interpreted["Head"].startswith("N") and interpreted["S"]["Pers"]: out.append("Pos:"+"".join([interpreted["S"]["Pers"], interpreted["S"]["Num"]]))
    if interpreted["S"]["Pers"] and not interpreted["Head"].startswith("N"): out.append("S:"+"".join([interpreted["S"]["Pers"], interpreted["S"]["Num"]]))
    if interpreted["O"]["Pers"]: out.append("O:"+"".join([interpreted["O"]["Pers"], interpreted["O"]["Num"]]))
    if interpreted["Order"]: out.append(interpreted["Order"])
    if interpreted["Neg"]: out.append(interpreted["Neg"])
    if interpreted["Mode"]: out.append(" ".join(interpreted["Mode"]))
    if interpreted["Pcp"]["Pers"]: out.append(" ".join(["Pcp", "(Focus:{})".format(find_focus(**{x:interpreted[x] for x in ["S", "O", "Pcp"] if interpreted[x]["Pers"]}))]))
    if any(interpreted["Else"]): out.append(" ".join([x for x in interpreted["Else"] if x]))
    return " ".join(out)

def find_focus(**kwargs):
    x =  [k for k in {kw:kwargs[kw] for kw in kwargs if kw != "Pcp"} if kwargs[k] == kwargs['Pcp']]
    #if len(x) > 1: print(x) #there better not be ambiguity!!
    if x: return x[0]
    return "".join([kwargs["Pcp"]["Pers"], kwargs["Pcp"]["Num"]])
