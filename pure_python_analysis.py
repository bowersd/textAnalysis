import pyhfst
import regex

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

def extract_pos(string, pos_regex):
    if "+Cmpd" in string:
        cmpd = []
        for x in regex.split(r"\+Cmpd", string):
            cmpd.append(regex.search(pos_regex, x)[0][1:])
        return "+".join(cmpd)
    srch = regex.search(pos_regex, string) #first pos tag ... maybe want all (and especially then extract last!)
    if srch: return srch[0][1:] #want to drop the leading + sign
    return None

def min_morphs(*msds):
    """the length of the shortest morphosyntactic description"""
    return min([m[0].count("+") for m in msds])

def score_edits(typed, *generated):
    h = {}
    for g in generated:
        alnd = needleman.align(typed, g[0], -1, needleman.make_id_matrix(typed, g[0]))
        h[g[0]] = sum([alnd[0][i] != alnd[1][i] for i in range(len(alnd[0]))])
    return h

def disambiguate2(scored, *msds):
    """get the first of the lowest scored"""
    lowest = min([scored[x] for x in scored])
    return min([i for i in range(len(msds)) if scored[msds[i][0]] == lowest])

def disambiguate(target, f, *msds): 
    """the earliest of the morphosyntactic descriptions|f(m) = target"""
    #prioritizing order allows weighting schemes to be exploited
    for i in range(len(msds)):
        if f(msds[i]) == target: return i
    #first default
    return 0

