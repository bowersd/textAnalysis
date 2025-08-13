#import pyodide
#await pyodide.loadPackage("micropip")
import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/e0/02/c10a69ff21d6679a6b6e28c42cd265bec2cdd9be3dcbbee830a10fa4b0e5/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
from pyweb import pydom
import pyscript
import asyncio
from js import console, Uint8Array, File, FileReader, URL, document, window #File et seq were added for download, maybe pyscript.File, URL, document will work?
import io #this was added for download
#from pyodide import create_proxy
from pyodide.ffi.wrappers import add_event_listener
from pyodide.http import pyfetch
#from pyodide.http import open_url
#from pyscript import fetch
import regex
import pyhfst
import tabulate
import sentence_complexity as sc
import opd_links as opd
#print("Coming soon: put in a Nishnaabemwin text, get back a (rough) interlinear analysis of the text")
#print("For now, a demonstration that a functioning analyzer is loaded")

###functions copied directly/modified from elsewhere in the repo
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

def sep_punct(string, drop_punct): #diy tokenization, use nltk?
    if not drop_punct: return "'".join(regex.sub(r"(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", r" \g<1> ", string).split("’")) #separate all punc, then replace single quote ’ with '
    return "'".join(regex.sub(r"(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", " ", string).split("’")) #remove all punc, then replace single quote ’ with '

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

def pad(*lists_of_strings):
    #lists must be same length!
    nu_lists = []
    padlen = []
    for i in range(len(lists_of_strings)):
        nu = []
        for j in range(len(lists_of_strings[i])): #pad items in list to max length at their indices
            if not i: padlen.append(max([len(lists_of_strings[k][j]) for k in range(len(lists_of_strings))]))
            nu.append(lists_of_strings[i][j]+" "*(padlen[j]-len(lists_of_strings[i][j])))
        nu_lists.append(nu)
    return nu_lists

def readin(filename):
    holder = []
    with open(filename, 'r') as f_in:
        for line in f_in:
            holder.append(line.strip())
    return holder

def mk_glossing_dict(*strings):
    gd = {}
    for s in strings:
        chunked = s.split("\t")
        if chunked[0] not in gd: gd[chunked[0]] = chunked[1]
        #else: gd[chunked[0]] = gd[chunked[0]] + " HOMOPHONE DEFINITION>" + chunked[1]
        else: gd[chunked[0]] = gd[chunked[0]] + "/" + chunked[1]
    return gd


def retrieve_glosses(*lemmata, **gloss_dict):
    tinies = []
    for l in lemmata:
        try: gloss = gloss_dict[l]
        except KeyError:
            if "+" in l: 
                gloss = "-".join(retrieve_glosses(*l.split("+"), **gloss_dict, ))
            else: gloss = "?"
        tinies.append(gloss)
    return tinies

def wrap_glosses(*glosses):
    return ["'"+g+"'" for g in glosses]

def wrap_nod_entry_url(*lemmata, **nishIDdict):
    h = []
    #gotta split up the complex lemmata somehow
    for l in lemmata:
        tot = []
        #if '+' in l: tot.append(l)
        cmpd = l.split("+") #this can't do what is intended (split the IDs of conjuncts), and it is crashes when the word is not found in the dictionary
        for c in cmpd:
        #else:
            #cmpd = regex.split("(?<=n)-(?=n)", nishIDdict[l]) #this can't do what is intended (split the IDs of conjuncts), and it is crashes when the word is not found in the dictionary
            #for c in cmpd:
            try: 
                alts = regex.split("(?<=n)/(?=n)", nishIDdict[c])
                for i in range(len(alts)):
                    if i == 0: 
                        tot.append('<a href='+"'https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/{0}' target='_blank' rel='noopener noreferrer'>{1}</a>".format(alts[i], c))
                        #print('initially formatted link')
                        #print('<a href='+"'https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/{0}' target='_blank' rel='noopener noreferrer'>{1}</a>".format(alts[i], c))
                    else: tot.append('<a href='+"'https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/{0}' target='_blank' rel='noopener noreferrer'>(alt {1})</a>".format(alts[i], str(i)))
            except KeyError: tot.append(c)
        h.append(" ".join(tot))
    return h
    #return ['<a href="https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/'+ln[1]+'">'+ln[0]+'</a>' for ln in lemmataAndNishIDs]

def undo_html(string):
    return regex.sub('&\#x27;', "'", regex.sub('&lt;', '<', regex.sub('&gt;', '>', string)))
    #return regex.sub('&quot;', '', regex.sub('&lt;', '<', regex.sub('&gt;', '>', string)))

def extract_lemma(string, pos_regex):
    """pull lemma out of string"""
    #lemma is always followed by Part Of Speech regex
    #lemma may be preceeded by prefixes, else word initial
    #if regex.search(pos_regex, string): return regex.search("(^|\+)(.*?)"+pos_regex, string).group(2)
    if "+Cmpd" in string:
        cmpd = []
        for x in regex.split(r"\+Cmpd", string):
            cmpd.append(regex.split(pos_regex, x)[0].split("+")[-1])
        return "+".join(cmpd)
    if regex.search(pos_regex, string): return regex.split(pos_regex, string)[0].split("+")[-1] #last item before pos tag, after all other morphemes, is lemma
    return None

def lemmatize(pos_regex, *analysis):
    return [extract_lemma(a, pos_regex) for a in analysis]


def extract_pos(string, pos_regex):
    if "+Cmpd" in string:
        cmpd = []
        for x in regex.split(r"\+Cmpd", string):
            cmpd.append(regex.search(pos_regex, x)[0][1:])
        return "+".join(cmpd)
    srch = regex.search(pos_regex, string) #first pos tag ... maybe want all (and especially then extract last!)
    if srch: return srch[0][1:] #want to drop the leading + sign
    return None

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

def interpret(analysis_in):
    summary = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":[], "Periph":"", "Pcp":{"Pers":"", "Num":""}, "Else": [x for x in analysis_in["preforms"]+analysis_in["clitic"]]}
    inversion = False #if true, S/O will be inverted at end
    summary["S"]["Pers"] = analysis_in["prefix"][0]
    summary["DerivChain"] = ">".join([x for x in analysis_in["derivation"]])
    summary["Head"] = analysis_in["derivation"][-1]
    if summary["Head"] == "VTI": summary["O"]["Pers"] = "0" #cheating a little and not putting this in the theme sign info because we don't actually have a suffix tag for VTI themes
    if summary["Head"] == "VAIO": 
        summary["O"]["Pers"] = "3" #cheating a little and not putting this in the theme sign info because VAIOs don't actually have themes
        if analysis_in["suffixes"][-1] == "3": analysis_in["suffixes"].pop() #in some VAIO forms there is a real third person object morpheme, but it is redundant, so dropping it
    while analysis_in["suffixes"]:
        #gnarly list of elif statements
        #general strategy: fill object information with theme sign, then fill object number information, then unify prefix information with number information in subject field, then fill in subject information with remaining suffixes 
        s = analysis_in["suffixes"].pop(0)
        if s == "Neg": summary["Neg"] = s
        elif s == "Prt": summary["Mode"].append(s)
        elif s == "Dub": summary["Mode"].append(s)
        elif s == "Voc": summary["Mode"].append(s)
        elif s == "Cnj": summary["Order"] = s
        elif s == "Imp": 
            summary["Order"] = s
            if summary["Head"] == "VTA": #VTA imperative object information is not in a theme sign, but directly spelled out in tags that are not always immediately adjacent to order tag, so here's a hack that goes backwards through the tags and updates subject and object information while removing the argument information from the computation
                while any([feature in analysis_in["suffixes"] for feature in ["3", "2", "1", "1Pl", "2Pl", "21Pl", "3Pl"]]): 
                    feature = analysis_in["suffixes"].pop()
                    if feature.startswith("2"):
                        summary["S"]["Pers"] = feature[0]
                        summary["S"]["Num"] = feature[1:]
                    elif feature.startswith("1") or feature.startswith("3"):
                        summary["O"]["Pers"] = feature[0]
                        summary["O"]["Num"] = feature[1:]
                        if summary["S"]["Pers"] == "2" and not summary["S"]["Num"] and feature == "3": summary["O"]["Num"] = "Pl/3"
                #h = []
                #subject = True
                #while "3" in analysis_in["suffixes"] or "2" in analysis_in["suffixes"] or "1" in analysis_in["suffixes"]:
                #    h.append(analysis_in["suffixes"].pop())
                #    if "3" in h or "2" in h or ("1" in h and analysis_in["suffixes"][-1:] != ["2"]):
                #        if subject: 
                #            summary["S"]["Pers"] = h[0][0]
                #            summary["S"]["Num"] = "".join(h[1:])
                #            h = []
                #            subject = False
                #        else:
                #            summary["O"]["Pers"] = h[0]
                #            summary["O"]["Num"] = "".join(h[1:])
        #{extracting theme sign (primarily object person) information 
        #IND        CNJ
        #Thm1       Thm1
        #Thm1Pl2    Thm1Pl2
        #Thm2       Thm2a
        #           Thm2b
        #ThmDir     ThmDir #3|3pl -> 3(pl) v 3', NEG ONLY:  #1|1pl      3|3pl   -> 1(pl)    v 3(pl), 
                                                            #2|21pl|2pl 3|3pl   -> 2(1(pl)) v 3(pl)
        #           ThmNul #                     POS ONLY:  #1|1pl      3|3pl   -> 1(pl)    v 3(pl), 
                                                            #2|21pl|2pl 3|3pl   -> 2(1(pl)) v 3(pl)
        #ThmInv     ThmInv #1|1pl -> 0 v 1(pl), 2|21pl|2pl -> 0 v 2(1(pl)), 3|3pl -> 0/3' v 3(pl) NEG ONLY: 2pl 3 -> 3 v 2pl (Thm2a not present, handled when 2 Pl is filled into prefixless subject information)
        #{local theme signs
        elif (s == "Thm1Pl2" or s == "Thm1" or s == "Thm2"):
            summary["O"]["Pers"] = "1"
            if s == "Thm2" or s == "Thm1Pl2": inversion = True
            if s == "Thm1Pl2": summary["O"]["Num"] = "Pl"
                #summary["S"]["Pers"] = "2" #not needed because in ind there is a prefix and in cnj there is a following +2
        elif (s == "Thm2a" or s == "Thm2b"):
            summary["O"]["Pers"] = "2"
            #summary["S"]["Pers"] = "1" #default, though later 3 may over ride
            #local theme signs end}
        elif (s == "ThmDir" or s == "ThmInv" or s == "ThmNul"):
            summary["O"]["Pers"] = "3"
            if s == "ThmInv": inversion = True
            if summary["Order"] == "Cnj" and s == "ThmInv": summary["O"]["Pers"] = "0" #will need to revise if 3 is encountered later
        #} extracting theme sign information end
        #{getting number information for theme signs/objects, also finding inanimate subjects
        elif summary["O"]["Pers"] == "1" and s == "1Pl":  #this should only happen with thm1 (see below)
            #first person objects are only written in with Thm1, Thm2, Thm1Pl2. 
            #Thm2, Thm1Pl2 are never followed by 1pl (bc Thm1Pl2 is how you indicate first person plurals). 
            #Thm1 .* 1Pl precludes 2pl marking, and so is ambiguous for second person number.  1 obj...1pl = 2Pl/2 vs 1pl.  it never means 21pl bc ban on XvX
            summary["O"]["Num"] = "Pl"
            #summary["S"]["Pers"] = "2" #redundant, but VTA Cnj Thm1 1Pl needs a default value. because 1Pl blocks 2 person marking ... maybe just add that marking in the model?, no because there are later markings that can appear
            summary["S"]["Num"] = "Pl/2"
        elif summary["O"]["Pers"] == "2" and s == "21Pl": summary["O"]["Num"] = "1Pl"
        elif summary["O"]["Pers"] == "2" and s == "2Pl": summary["O"]["Num"] = "Pl"
        elif summary["O"]["Pers"] == "3" and s == "3Obv": 
            summary["O"]["Num"] = "Obv"
        elif summary["O"]["Pers"] == "3" and s == "3ObvPlus": summary["O"]["Num"] = "ObvPlus"
        elif summary["O"]["Pers"] == "3" and s == "3Pl": 
            summary["O"]["Num"] = "Pl"
        elif summary["O"]["Pers"] == "3" and (s == "0" or s == "0Pl"): #VTA indep (inverses), have overt suffs for inanimates, need to over ride the default 3 here
            summary["O"]["Pers"] = "0"
            if analysis_in["suffixes"][0:1] == ["0Pl"]: #there is a gratuitous +0 suffix in VAIO indeps with singular actors, so it is possible to encounter solitary 0 and 0Pl. if VTIs had a gratuitous +0 suffix, we would still need next elif, because there would be +0.*+0Pl strings
                analysis_in["suffixes"].pop(0)
                summary["O"]["Num"] = "Pl"
            elif s ==  "0Pl": summary["O"]["Num"] = "Pl"
        elif summary["O"]["Pers"] == "0" and s == "0Pl": summary["O"]["Num"] = "Pl"#there is no longer a gratuitous +0 suffix in VTI indeps with singular actors, so no deliberately clunky syntax needed to drop the +0 tag
        #}theme sign number end
        #{getting number information for person values specified by prefix == NOT CONJUNCT!
        elif analysis_in["prefix"][0] == "1" and s == "1Pl": summary["S"]["Num"] = "Pl"
        elif analysis_in["prefix"][0] == "2" and s == "1Pl": summary["S"]["Num"] = "1Pl"#this does not mess up VTA local themes, since it is a lower elif (2...Thm1...1Pl = 2Pl/2 v 1pl != 21Pl)
        elif analysis_in["prefix"][0] == "2" and s == "2Pl": summary["S"]["Num"] = "Pl" 
            #if summary["O"]["Pers"] == "1" and summary["S"]["Pers"] == "2" and inversion: summary["S"]["Num"] == "Pl"  ## before inversion (thm1sg/thm1pl .*2pl) = (2pl v 1sg/2pl v 1pl), so no need to specify a special case here 
            #note: there is no further number information in another slot for first persons here ... like theme signs really are object agreement and inversion swoops them into subjecthood (and/or peripheral suffixes are just for 3rd persons)
        elif analysis_in["prefix"][0] == "3" and s == "2Pl": summary["S"]["Num"] = "Pl"
        #end prefix number obtained}
        #{getting person/number information from suffixes
        elif (not summary["S"]["Pers"]) and (s == "1" or s == "1Pl"):
            summary["S"]["Pers"] = "1"
            if s  == "1Pl": summary["S"]["Num"] = "Pl"
        elif ((not summary["S"]["Pers"]) or summary["S"]["Pers"]=='3') and (s == "2" or s == "2Pl" or s == "21Pl"): 
            if not summary["S"]["Pers"]: summary["S"]["Pers"] = "2"
            if s == "2Pl":
                summary["S"]["Num"] = "Pl"
                if summary["O"]["Pers"] == "0" and inversion == True and summary["Neg"] and summary["Order"] and analysis_in["suffixes"][0:1] == "3": #VTA CNJ THMINV NEG 2 PL 3(PL)
                    summary["O"]["Pers"] == "3"
                    analysis_in["suffixes"].pop(0) #I think we want to get rid of the next suffix, not the last one (given the 0:1 above)
            elif summary["S"]["Pers"] == "2" and s == "21Pl": summary["S"]["Num"] = "1Pl"
        elif ((not summary["S"]["Pers"]) or summary["S"]["Pers"] == '3') and (s == "3" or s == "3Pl" or s == "3Obv"):
            summary["S"]["Pers"] = "3"
            if inversion == True and summary["O"]["Pers"] == "0" and summary["Order"] == "Cnj":  summary["O"]["Pers"] = "3Obv/0" #VTA CNJ THMINV 3
            if s == "3Pl": summary["S"]["Num"] = "Pl"
            elif s ==  "3Obv": summary["S"]["Num"] = "Obv"
        elif ((not summary["S"]["Pers"]) or summary["S"]["Pers"] == "0") and (s == "0" or s == "0Obv" or s == "0Pl"): 
            summary["S"]["Pers"] = "0"
            if s == "0Obv": summary["S"]["Num"] = "Obv"
            elif s == "0Pl": summary["S"]["Num"] += "Pl" #NB: += used since 0ObvPl is possible
        elif (not summary["S"]["Pers"]) and s == "X": summary["S"]["Pers"] = "X"
        #}end person/number information from suffixes
        elif summary["Head"].startswith("N") and s == "Obv": summary["Periph"] = "Obv"
        elif summary["Head"].startswith("N") and s in ["Loc", "Pl"]: summary["Periph"] = s
        elif s == "Pcp":
            summary["Pcp"]["Pers"] = analysis_in["suffixes"][0][0] 
            summary["Pcp"]["Num"] = analysis_in["suffixes"][0][1:]
            analysis_in["suffixes"].pop(0) #need to vacuum up the focus information so it does not interfere with how subjects and objects are encoded
        else: summary["Else"].append(s)
    if (not summary["S"]["Pers"]) and summary["O"]["Pers"] == "2": summary["S"]["Pers"] = "1" #default person for Thm2a keep at end
    if (not summary["S"]["Pers"]) and summary["O"]["Pers"] == "1": summary["S"]["Pers"] = "2" #default person for Thm1  keep at end
    if (not summary["S"]["Pers"]) and summary["O"]["Pers"] == "3": #lifting information that accrues to object in VTA cnjs/VAIO cnjs when other persons are not specified to subject #default person for cnj ThmDir  ThmInv keep at end
        summary["S"]["Pers"] = "3"
        summary["S"]["Num"] = summary["O"]["Num"] #had to split these up, because just assigning O to S was resulting in the obviation assignment below making the subject and object have obviation
    if not inversion and summary["S"]["Pers"] == "3" and summary["O"]["Pers"] == "3": 
        summary["O"]["Num"] = "Obv" #default obviation for direct themes. should only be necessary for VTA CNJ, which never overtly signals obviation, but kept general
    #summary["Else"] = [y[0] for x in analysis_in for y in analysis_in[x] if not y[1]]
    if inversion == True: summary["S"], summary["O"] = summary["O"], summary["S"]
    return summary

def analysis_dict(analysis_string):
    postags = r"\+VAI(O)?|\+VII|\+VTI|\+VTA|\+NA(D)?|\+NI(D)?|\+Conj|\+Interj|\+Num|\+Pron(\+NA|\+NI)|\+Ipc|\+Qnt|\+Adv|\+Else"
    adict = {"prefix":[], "derivation": [], "preforms":[], "suffixes":[], "clitic":[]}
    adict["clitic"] = [regex.search(r"((?<=\+)dash\+Adv$)?", analysis_string)[0]]
    analysis_string = regex.sub(r"\+dash\+Adv", "", analysis_string) #this only needs to happen after clitics are checked and before derivation/suffixes are inspected, stuck with post-clitics
    adict["prefix"] = [regex.search("(^[123X])?", analysis_string)[0]]
    if regex.search("({0})(.*({0}))?".format(postags), analysis_string): adict["derivation"] = [x for x in regex.search("({0})(.*({0}))?".format(postags), analysis_string)[0].split("+") if x] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    x =  regex.search(r"((((PV|PN|PA)[^+]*)|Redup)\+)+", analysis_string)
    if x: adict["preforms"] = regex.search(r"(((PV|PN|PA)[^\+]*\+)|Redup\+)*", analysis_string)[0].split("+")
    if regex.search(".*?(?={})".format("|".join([x[2:]+x[:2] for x in postags.split("|")])), "+".join(reversed(analysis_string.split("+")))): adict["suffixes"] = [x for x in reversed(regex.search(".*?(?={})".format("|".join([x[2:]+x[:2] for x in postags.split("|")])), "+".join(reversed(analysis_string.split("+"))))[0].split("+"))]
    if not adict["derivation"]: return None
    return adict

###functions and constants for doing things within the web page
#constants

#analyzers = ["./morphophonologyclitics_analyze.hfstol"]
gdict = mk_glossing_dict(*readin("./copilot_otw2eng.txt"))
iddict = mk_glossing_dict(*readin("./otw2nishID.txt"))
pos_regex = "".join(readin("./pos_regex.txt"))
ciw_pos_regex = "".join(readin("./ciw_pos_regex.txt"))
opd_manual_links = {}
for row in readin("opd_manual_links.csv"):
    tabbed = row.split(',')
    opd_manual_links[(tabbed[0], tabbed[1])] = tabbed[2]

def cascade_customization(event):
    form_values["rhodes"]["order"] = pyscript.document.querySelector("#rhodes").value
    form_values["rhodes_relaxed"]["order"] = pyscript.document.querySelector("#rhodes_relaxed").value
    form_values["corbiere"]["order"] = pyscript.document.querySelector("#corbiere").value
    form_values["corbiere_relaxed"]["order"] = pyscript.document.querySelector("#corbiere_relaxed").value
    form_values["no_deletion"]["order"] = pyscript.document.querySelector("#no_deletion").value
    form_values["no_deletion_relaxed"]["order"] = pyscript.document.querySelector("#no_deletion_relaxed").value
    print(f"Form values are: {form_values}")
    analyzers = []
    print("reset state of analyzers")
    print(analyzers)
    for x in sorted(form_values, key = lambda y: form_values[y]["order"]):
        #if form_values[x]["order"] and form_values[x]["url"]:
        #    form_values[x]["file"] = await pyfetch(form_values[x]["url"])
        #    print(form_values[x]["file"])
        print(form_values[x]["file"])
        analyzers.append(form_values[x]["file"])
    print("updated state of analyzers")
    print(analyzers)
    return analyzers

#form_values["rhodes"]=Element("rhodes").element.value

#Element("rhodes").element.oninput = rhodes_handler
#Element("rhodes_relaxed").element.oninput = rhodes_relaxed_handler
#Element("corbiere").element.oninput = corbiere_handler
#Element("corbiere_relaxed").element.oninput = corbiere_relaxed_handler
#Element("no_deletion").element.oninput = no_deletion_handler
#Element("no_deletion_relaxed").element.oninput = no_deletion_relaxed_handler
#Element("analyzer_cascade_customization").element.onsubmit = submit_handler

def submit_handler(event=None):
    if event:
        event.preventDefault()
        print(f"Form values are: {form_values}")
        
def rhodes_handler(event=None):
    if event:
        form_values["rhodes"]["file"] = event.target.value

def rhodes_relaxed_handler(event=None):
    if event:
        form_values["rhodes_relaxed"]["file"] = event.target.value

#add_event_listener(document.getElementById("rhodes_relaxed_upload"), "change", rhodes_relaxed_handler)
#print(form_values)

def corbiere_handler(event=None):
    if event:
        form_values["corbiere"]["file"] = event.target.value

def corbiere_relaxed_handler(event=None):
    if event:
        form_values["corbiere_relaxed"]["file"] = event.target.value

def no_deletion_handler(event=None):
    if event:
        form_values["no_deletion"]["file"] = event.target.value

def no_deletion_relaxed_handler(event=None):
    if event:
        form_values["no_deletion_relaxed"]["file"] = event.target.value

form_values = {
        "rhodes":{"order":"1", "url":"", "file":"./morphophonologyclitics_analyze.hfstol"},
        "rhodes_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_relaxed.hfstol", "file":None},
        "corbiere":{"order":"", "url":"", "file": "./morphophonologyclitics_analyze_mcor_spelling.hfstol"},
        "corbiere_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_mcor_relaxed.hfstol", "file":None},
        "no_deletion":{"order":"", "url":"",  "file": "./morphophonologyclitics_analyze_unsyncopated.hfstol"},
        "no_deletion_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/unsyncopated_analyzer_relaxed.hfstol",  "file":None},
        "western":{"order":"", "url":"",  "file": "./morphophonology_analyze_border_lakes.hfstol"},
        }
def parse_words_expanded(event):
    form_values["rhodes"]["order"] = pyscript.document.querySelector("#rhodes").value
    #form_values["rhodes_relaxed"]["order"] = pyscript.document.querySelector("#rhodes_relaxed").value
    form_values["corbiere"]["order"] = pyscript.document.querySelector("#corbiere").value
    #form_values["corbiere_relaxed"]["order"] = pyscript.document.querySelector("#corbiere_relaxed").value
    form_values["no_deletion"]["order"] = pyscript.document.querySelector("#no_deletion").value
    #form_values["no_deletion_relaxed"]["order"] = pyscript.document.querySelector("#no_deletion_relaxed").value
    form_values["western"]["order"] = pyscript.document.querySelector("#western").value
    analyzers = []
    for x in sorted(form_values, key = lambda y: form_values[y]["order"]):
        #if form_values[x]["order"] and form_values[x]["url"]:
        #    form_values[x]["file"] = await pyfetch(form_values[x]["url"])
        #    print(form_values[x]["file"])
        if form_values[x]["order"] and form_values[x]["file"]: analyzers.append(form_values[x]["file"])
    input_text = pyscript.document.querySelector("#larger_text_input")
    freeNish = input_text.value
    to_analyze = sep_punct(freeNish.lower(), True).split()
    parses = {}
    model_credit = {} #as of aug 2025, only using this data to allow correct formatting of western (OPD-based) lemmata urls vs eastern (NOD-based) lemmata. It could be nice to flag misspelled words either to indicate less certainty or to encourage spelling improvement
    #analyzers = await cascade_customization()
    for i in range(len(analyzers)):
        print(analyzers[i])
        analyzed = parse_pyhfst(analyzers[i], *to_analyze)
        to_analyze = []
        for w in analyzed:
            if analyzed[w][0][0].endswith('+?') and i+1 < len(analyzers): to_analyze.append(w)
            elif analyzed[w][0][0].endswith('+?') and i+1 == len(analyzers): 
                parses[w] = analyzed[w]
                model_credit[w] = "unanalyzed" 
            elif (not analyzed[w][0][0].endswith('+?')) and i+1 == len(analyzers): 
                parses[w] = analyzed[w]
                model_credit[w] = analyzers[i]
            else: 
                parses[w] = analyzed[w]
                model_credit[w] = analyzers[i]
    #analyzed = parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *sep_punct(freeNish.lower(), True).split())
    ##m_parse_lo = [analyzed[w][disambiguate(min_morphs(*analyzed[w]), min_morphs, *analyzed[w])][0] for w in sep_punct(freeNish.lower(), True).split()]
    #re_analysis = []
    #for w in sep_punct(freeNish.lower(), True).split():
    #    if analyzed[w][0][0].endswith('+?'): re_analysis.append(w)
    #re_analyzed = parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *re_analysis)
    h = {"original":[],
         "m_parse_lo":[],
         "m_parse_hi":[],
         "lemmata":[],
         "lemma_links":[],
         "tinies":[]}
    for line in freeNish.lower().split('\n'):
        local = []
        for w in sep_punct(line, True).split(): local.append(parses[w][disambiguate(min_morphs(*parses[w]), min_morphs, *parses[w])][0])
            #if analyzed[w][0][0].endswith('+?'): local.append(re_analyzed[w][disambiguate(min_morphs(*re_analyzed[w]), min_morphs, *re_analyzed[w])][0])
            #else: local.append(analyzed[w][disambiguate(min_morphs(*analyzed[w]), min_morphs, *analyzed[w])][0])
        h["original"].append(sep_punct(line, True).split())
        h["m_parse_lo"].append(local)
        h["m_parse_hi"].append(["'"+formatted(interpret(analysis_dict(x)))+"'" if analysis_dict(x) else "'?'" for x in local])
        lemms = []
        lem_links = []
        for i in range(len(local)):
            if model_credit[sep_punct(line, True).split()[i]] == "./morphophonology_analyze_border_lakes.hfstol": 
                lem = extract_lemma(local[i], ciw_pos_regex)
                pos = extract_pos(local[i], ciw_pos_regex)
                lemms.append(lem)
                if (lem, pos) in opd_manual_links: lem_links.append(opd.wrap_opd_url(opd_manual_links[(lem, pos)], lem)) 
                else: lem_links.append(opd.wrap_opd_url(opd.mk_opd_url(lem, pos), lem)) 
            else: 
                lem = extract_lemma(local[i], pos_regex)
                lemms.append(lem)
                lem_links.append(wrap_nod_entry_url(lem, **iddict)[0])
        h["lemmata"].append(lemms) #converted to links in interlinearize, kept plain in freq count ... should always have links available, methinks
        h["lemma_links"].append(lem_links) #converted to links in interlinearize, kept plain in freq count ... should always have links available, methinks
        #h["lemmata"].append([x if x else "?" for x in lemmatize(pos_regex, *local)]) 
        h["tinies"].append(wrap_glosses(*retrieve_glosses(*h["lemmata"][-1], **gdict)))
        #tinies = []
        #for l in h["lemmata"][-1]:
        #    try: gloss = gdict[l]
        #    except KeyError:
        #        gloss = "?"
        #    tinies.append("'"+gloss+"'")
        #h["tinies"].append(tinies)
    analysis_mode = pyscript.document.querySelector("#analysis_mode")
    output_div = pyscript.document.querySelector("#output")
    if analysis_mode.value == "interlinearize":
        for i in range(len(h["m_parse_lo"])):
            #lines_out += tabulate.tabulate([
            #    ["Original Material:"] + h["original"][i],
            #    ["Narrow Analysis:"] + h["m_parse_lo"][i], 
            #    ["Broad Analysis:"] + h["m_parse_hi"][i], 
            #    ["NOD Entry:"] + h["lemmata"][i],
            #    ["Terse Translation:"] + h["tinies"][i]], tablefmt='html')
            new_batch = tabulate.tabulate([
                ["Original Material:"] + h["original"][i],
                ["Narrow Analysis:"] + h["m_parse_lo"][i], 
                ["Broad Analysis:"] + h["m_parse_hi"][i], 
                ["NOD/OPD Entry:"] + h["lemma_links"][i], 
                ["Terse Translation:"] + h["tinies"][i]], tablefmt='html')
            revised = ""
            for nb in new_batch.split('\n'):
                if "NOD/OPD Entry" in nb: revised += undo_html(nb)+'\n'
                else: revised += nb+'\n'
        output_div.innerHTML = revised
    elif analysis_mode.value == "frequency":
        cnts_lem = {}
        for i in range(len(h["lemmata"])):
            for j in range(len(h["lemmata"][i])):
                if h["lemmata"][i][j] not in cnts_lem: cnts_lem[h["lemmata"][i][j]] = {h["original"][i][j]:1, "__dict_link__":h["lemma_links"][i][j]}
                elif h["original"][i][j] not in cnts_lem[h["lemmata"][i][j]]: cnts_lem[h["lemmata"][i][j]][h["original"][i][j]] = 1
                else: cnts_lem[h["lemmata"][i][j]][h["original"][i][j]] += 1
        #cnts = {w:0 for w in sep_punct(freeNish.lower(), True).split()}
        #for w in sep_punct(freeNish.lower(), True).split(): cnts[w] += 1
        #for lem in lemmata: cnts_lem[lem] += 1
        #cnts = []
        header = [["Count", "NOD Entry", "Count", "Actual"]]
        nu_cnts = []
        for lem in cnts_lem:
            for tok in cnts_lem[lem]:
                nu_cnts.append([sum([cnts_lem[lem][x] for x in cnts_lem[lem]]), lem, str(cnts_lem[lem][tok]), tok])
                #else: nu_cnts.append(("", "", tok, str(cnts_lem[lem][tok])))
                #cnts.append((str(cnts_lem[lem][tok]), tok, "("+lem+")"))
        #freqs_out = "Raw frequencies, aka token frequencies (with dictionary header)\n"+"\n".join(["\t".join(x) for x in sorted(cnts)])+"\n"+"Combined frequencies, aka type or lemmatized frequencies, organized by dictionary header\n"+"\n".join(sorted(["{0}\t{1}".format(sum([cnts_lem[key][x] for x in cnts_lem[key]]), key) for key in cnts_lem]))
        #freqs_out = "Raw (token) frequencies\n"+"\n".join(["{0}\t{1}".format(cnts[key], key) for key in cnts])+"\n"+"Combined (type/lemmatized) frequencies\n"+"\n".join(["{0}\t{1}".format(cnts_lem[key], key) for key in cnts_lem])
        nu_cnts = sorted(sorted(nu_cnts, key = lambda x: x[1]), key = lambda x: x[0], reverse = True) #might need to sort 4 times!!
        prev = ""
        unanalyzed_block = []
        for i in range(len(nu_cnts)):
            x = nu_cnts.pop(0)
            if x[1] == "?": unanalyzed_block.append(x)
            else: nu_cnts.append(x)
        nu_cnts.extend(unanalyzed_block)
        for i in range(len(nu_cnts)):
            nu_cnts[i][0] = str(nu_cnts[i][0])
            new = nu_cnts[i][1]
            if new != prev: prev = new
            elif new == prev: 
                nu_cnts[i][0] = ""
                nu_cnts[i][1] = ""
        freqs_out = tabulate.tabulate(header + nu_cnts, tablefmt='html')
        print(freqs_out)
        output_div.innerHTML = freqs_out
    elif analysis_mode.value == "verb_sort":
        comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
        c_order = ["VTA", "VAIO", "VTI", "VAI", "VII", "(No verbs found)"] #need to specify order in order to sort by count of verb in the relevant category
        categorized = {x:[] for x in c_order}
        for i in range(len(comp_counts)):
            if comp_counts[i][0][0]: categorized["VTA"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][1]: categorized["VAIO"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][2]: categorized["VTI"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][3]: categorized["VAI"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][4]: categorized["VII"].append((comp_counts[i], h["original"][i]))
            if not any(comp_counts[i][0]): categorized["(No verbs found)"].append((comp_counts[i], h["original"][i]))
        sectioned = []
        for i in range(len(c_order)-1): #need to skip the last category, because there is no corresponding bin in the verb counts for when there is nothing
            sectioned.append([">>These sentences have verbs of the following category: {}".format(c_order[i])])
            for x in sorted(sorted(categorized[c_order[i]], key = lambda y: y[0][-1][0]), key = lambda z: z[0][0][i]): sectioned.append([" ".join(x[1])]) #sorting by morphological complexity, then count of relevant verb category
        sectioned.append([">>These sentences had no verbs found in them"])
        for x in sorted(categorized["(No verbs found)"], key = lambda y: y[0][-1][0]):
            sectioned.append([" ".join(x[1])])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")
    elif analysis_mode.value == "complexity":
        comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
        overall_score = sc.alg_morph_score_rate(*comp_counts)
        sectioned = [["Overall Score (Features per Sentence):",  str(overall_score[2])]]
        for ssp in sorted([x for x in zip(comp_counts, h["original"])], key = lambda y: y[0][-1][0]): sectioned.append([" ".join(ssp[1]), ssp[0][-1][0]])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")
    elif analysis_mode.value == "verb_collate":
        faced = sc.interface(pos_regex, *h["m_parse_lo"])
        verbcats = ["VAI", "VTA", "VII", "VAIO", "VTI"]
        verbdict = {x:[] for x in verbcats}
        for i in range(len(faced)):
            for j in range(len(faced[i])):
                if faced[i][j]["pos"] in verbdict: 
                    if (h["original"][i][j], h["m_parse_hi"][i][j]) not in verbdict[faced[i][j]["pos"]]: verbdict[faced[i][j]["pos"]].append((h["original"][i][j], h["m_parse_hi"][i][j]))
        sectioned = []
        for c in verbcats:
            sectioned.append(["Found these verbs of category {}:".format(c)])
            for v in sorted(verbdict[c], key = lambda x: x[1]): 
                sectioned.append([v[0]])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")
    elif analysis_mode.value == "glossary":
        pass
    elif analysis_mode.value in ["triage", "reversed_triage"]:
        recall_errors = []
        for i in range(len(h["original"])):
            for j in range(len(h["original"][i])):
                print(h["original"][i])
                if h["m_parse_lo"][i][j].endswith("+?"):
                    error = [(h["original"][i][j], i, " ".join(h["original"][i][:j]), h["original"][i][j], " ".join(h["original"][i][j+1:]))]
                    error.append(["", "", " ".join(h["m_parse_lo"][i][:j]), "",                " ".join(h["m_parse_lo"][i][j+1:])])
                    error.append(["", "", " ".join(h["m_parse_hi"][i][:j]), "",                " ".join(h["m_parse_hi"][i][j+1:])])
                    error.append(["", "", " ".join(h["lemmata"][i][:j]), "",                   " ".join(h["lemmata"][i][j+1:])])
                    error.append(["", "", " ".join(h["tinies"][i][:j]), "",                    " ".join(h["tinies"][i][j+1:])])
                    recall_errors.append(error)
        ordered_recall_errors = []
        if analysis_mode.value == "triage":
            for x in sorted(recall_errors): ordered_recall_errors.extend(x) #[x[0], x[1], x[2], x[3], x[4] for x in sorted(recall_errors)]
        elif analysis_mode.value == "reversed_triage":
            for x in sorted(recall_errors, key=lambda z: [y for y in reversed(z[0][0])]): ordered_recall_errors.extend(x) #[x[0], x[1], x[2], x[3], x[4] for x in sorted(recall_errors)]
        #forwards = ""
        #for r in sorted(recall_errors):
        #    forwards += tabulate.tabulate([[r[0][0], r[0][2]]+r[1], ["", ""]+r[2], ["", ""]+r[3], ["", ""]+r[4], ["", ""]+r[5]], headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        #forwards = tabulate.tabulate([[[r[0][0], r[0][2]]+r[1], ["", ""]+r[2], ["", ""]+r[3], ["", ""]+r[4], ["", ""]+r[5]] for r in sorted(recall_errors)], headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        forwards = tabulate.tabulate(ordered_recall_errors, headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        output_div.innerHTML = forwards
            
