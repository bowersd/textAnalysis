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
from pyodide.ffi.wrappers import add_event_listener
from pyodide.http import pyfetch
#from pyodide.http import open_url
#from pyscript import fetch
import regex
import pyhfst
import tabulate
import sentence_complexity as sc
import opd_links as opd
import pure_python_tmp_container as pp

###functions copied directly/modified from elsewhere in the repo

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


def find_focus(**kwargs):
    x =  [k for k in {kw:kwargs[kw] for kw in kwargs if kw != "Pcp"} if kwargs[k] == kwargs['Pcp']]
    #if len(x) > 1: print(x) #there better not be ambiguity!!
    if x: return x[0]
    return "".join([kwargs["Pcp"]["Pers"], kwargs["Pcp"]["Num"]])

def interpret_ciw(analysis_in, postags):
    summary = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":[], "Periph":"", "Pcp":{"Pers":"", "Num":""}, "Else": []}
    if regex.search("({0})(.*({0}))?".format(postags), analysis_in): summary["DerivChain"] = [x for x in regex.search("({0})(.*({0}))?".format(postags), analysis_in)[0].split("+") if x] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    if summary["DerivChain"]: 
        summary["Head"] = summary["DerivChain"][-1]
        summary["DerivChain"] = ">".join(summary["DerivChain"])
    for x in analysis_in.split("+"):
        if x == "Dim": summary["Else"].append(x)
        elif x == "Pej": summary["Else"].append(x)
        elif x == "Poss": summary["Else"].append(x)
        elif x == "Pret": summary["Mode"].append(x)
        elif x == "Loc": summary["Periph"] = x
        elif x == "LocDist": summary["Else"].append(x)
        #elif x == "ProxSg": pass #this information is not retained
        elif x.startswith("Obv"): summary["Periph"] = "Obv" #violence done to Hammerly's rep. Collapsing across the number differentiations ...iirc it isn't fully collapsed in VIIs...
        elif x == "ProxPl": summary["Periph"] = "Pl" #proximal is not retained
        elif x == "Pl": summary["Periph"] = "Pl" #proximal is not retained
        #elif x == "Sg": pass #this information is not retained
        elif x == "Voc": summary["Mode"].append(x)
        #elif x == "1Sg": pass #this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "2Pl": pass #this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "2Sg": pass #this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "3Obv": pass #DOUBLE CHECK: this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "3ObvPlus": pass #DOUBLE CHECK: this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "3Pl": pass #DOUBLE CHECK: this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "3PlObvPlus": pass #DOUBLE CHECK: this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "3Sg": pass #this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "Excl": pass #this is person information for pronouns, which we do not have a good place for at the moment
        #elif x == "Incl": pass #this is person information for pronouns, which we do not have a good place for at the moment
        elif x.endswith("Poss") and x[0] in ["1", "2", "3"]: 
            summary["S"]["Pers"] = x[0]
            if x[1:6] == "PlObv": summary["S"]["Num"] = "Obv" #sg/prox is not retained. this specific combination is targeted to retrieve Obv because that will come first in lexicographic sort of ambiguous analyses, and will be selected by disambiguation
            elif x[1:3] == "Pl": summary["S"]["Num"] = "Pl" 
        elif x == "ExclPoss": 
            summary["S"]["Pers"] = "1"
            summary["S"]["Num"] = "Pl"
        elif x == "InclPoss": 
            summary["S"]["Pers"] = "2"
            summary["S"]["Num"] = "1Pl"
        elif x.endswith("Head"): #Participle information
            summary["Pcp"]["Pers"] = x[0]
            if x[1:6] == "PlObv": summary["Pcp"]["Num"] = "Obv"#sg/prox is not retained. this specific combination is targeted to retrieve Obv because that will come first in lexicographic sort of ambiguous analyses, and will be selected by disambiguation
            elif x[1:3] == "Pl": summary["Pcp"]["Num"] = "Pl" 
        elif x.endswith("Obj") and x[0] in ["0", "1", "2", "3", "X"]:
            summary["O"]["Pers"] = x[0]
            if x[1:6] == "PlObv": summary["O"]["Num"] = "Obv" #sg/prox is not retained. this specific combination is targeted to retrieve Obv because that will come first in lexicographic sort of ambiguous analyses, and will be selected by disambiguation
            elif x[1:3] == "Pl": summary["O"]["Num"] = "Pl" 
        elif x == "ExclObj": 
            summary["O"]["Pers"] = "1"
            summary["O"]["Num"] = "Pl"
        elif x == "InclObj": 
            summary["O"]["Pers"] = "2"
            summary["O"]["Num"] = "1Pl"
        elif x.endswith("Subj") and x[0] in ["0", "1", "2", "3", "X"]:
            summary["S"]["Pers"] = x[0]
            if x[1:6] == "PlObv": summary["S"]["Num"] = "Obv" #sg/prox is not retained. this specific combination is targeted to retrieve Obv because that will come first in lexicographic sort of ambiguous analyses, and will be selected by disambiguation
            elif x[1:3] == "Pl": summary["S"]["Num"] = "Pl" 
        elif x == "ExclSubj": 
            summary["S"]["Pers"] = "1"
            summary["S"]["Num"] = "Pl"
        elif x == "InclSubj": 
            summary["S"]["Pers"] = "2"
            summary["S"]["Num"] = "1Pl"
        elif x == "Imp": summary["Order"] = x
        elif x == "Cnj": summary["Order"] = x
        #elif x == "Ind": summary["Order"] = x
        elif x == "Neg": summary["Neg"] = x
        elif x == "Prb": summary["Neg"] = "Neg"
        elif x == "Pcp": summary["Else"].append(x)
        elif x == "Del": summary["Else"].append(x)
        elif x == "Dub": summary["Mode"].append(x)
        elif x == "Prt": summary["Mode"].append(x)
        elif x == "DubPrt": summary["Mode"].extend(['Prt', 'Dub'])
        elif x == "PVTense/gii": summary["Else"].append(x)
        #VII+Augment/magad is dropped
        #Simple imperative "Sim" is dropped
    return summary

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

gdict = mk_glossing_dict(*pp.readin("./copilot_otw2eng.txt"))
iddict = mk_glossing_dict(*pp.readin("./otw2nishID.txt"))
pos_regex = "".join(pp.readin("./pos_regex.txt"))
ciw_pos_regex_opd = "".join(pp.readin("./ciw_pos_regex_opd.txt"))
ciw_pos_regex_model = "".join(pp.readin("./ciw_pos_regex_model.txt"))
opd_manual_links = {}
for row in pp.readin("opd_manual_links.csv"):
    tabbed = row.split(',')
    opd_manual_links[(tabbed[0], tabbed[1])] = tabbed[2]

form_values = {
        "rhodes":{"order":"1", "url":"", "file":"./morphophonologyclitics_analyze.hfstol"},
        "rhodes_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_relaxed.hfstol", "file":None},
        "corbiere":{"order":"", "url":"", "file": "./morphophonologyclitics_analyze_mcor_spelling.hfstol"},
        "corbiere_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_mcor_relaxed.hfstol", "file":None},
        "no_deletion":{"order":"", "url":"",  "file": "./morphophonologyclitics_analyze_unsyncopated.hfstol"},
        "no_deletion_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/unsyncopated_analyzer_relaxed.hfstol",  "file":None},
        "western":{"order":"", "url":"",  "file": "./morphophonology_analyze_border_lakes.hfstol"},
        }

def interlinearize(parsed_data):
    revised = ""
    for i in range(len(parsed_data["m_parse_lo"])):
        table = [
                ["Original Material:"] + parsed_data["original"][i],
                ["Narrow Analysis:"] + parsed_data["m_parse_lo"][i], 
                ["Broad Analysis:"] + parsed_data["m_parse_hi"][i], 
                ["NOD/OPD Entry:"] + parsed_data["lemma_links"][i], 
                ["Terse Translation:"] + parsed_data["tinies"][i]
                ] 
        lines_out = tabulate.tabulate(table, tablefmt='html')
        for lo in lines_out.split('\n'): #a loop isn't really necessary here
            if "NOD/OPD Entry" in lo: revised += undo_html(lo)+'\n'
            #elif "Terse Translation" in lo and parsed_data["english"]: 
            #    revised += lo+'\n'
            #    transline = '<tr><td>Free Translation</td><td colspan="{0}">'+"'{1}'<td></tr>\n"
            #    revised += transline.format(str(len(parsed_data["m_parse_lo"])), parsed_data["english"][i])
            else: revised += lo+'\n'
    return revised

def interlinearize_blocks(parsed_data): #use kwargs
    ordered = []
    print("passed in data")
    print(parsed_data)
    for i in range(len(parsed_data["m_parse_lo"])):
        ordered.extend([
            ["Original Material:"] + parsed_data["original"][i],
            ["Narrow Analysis:"] + parsed_data["m_parse_lo"][i], 
            ["Broad Analysis:"] + parsed_data["m_parse_hi"][i], 
            ["NOD/OPD Entry:"] + parsed_data["lemma_links"][i], 
            ["Terse Translation:"] + parsed_data["tinies"][i]])
    return ordered

def interlinearize_format(*blocks):
    revised = ""
    for b in blocks:
        lines_out = tabulate.tabulate(b, tablefmt='html')
        for lo in lines_out.split('\n'): #a loop isn't really necessary here
            if "NOD/OPD Entry" in lo: revised += undo_html(lo)+'\n'
            else: revised += lo+'\n'
    return revised


def lexical_perspective(parsed_data):
    lemmata = {}
    for i in range(len(parsed_data["lemmata"])): 
        for j in range(len(parsed_data["lemmata"][i])):
            if parsed_data["lemmata"][i][j] not in lemmata: 
                lemmata[parsed_data["lemmata"][i][j]] = {
                    "tokens":{
                        parsed_data["original"][i][j]: {
                            "cnt":1, 
                            "m_parse_hi":parsed_data["m_parse_hi"][i][j], 
                            "m_parse_lo":parsed_data["m_parse_lo"][i][j],
                            "addr":[(i,j)],
                            "exe":{tuple(parsed_data["original"][i]):[j]}
                            }},
                    "link":parsed_data["lemma_links"][i][j],
                    "pos":parsed_data["m_parse_hi"][i][j].split()[0],
                    "tiny":parsed_data["tinies"][i][j]
                    }
            elif parsed_data["original"][i][j] not in lemmata[parsed_data["lemmata"][i][j]]["tokens"]: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]] = {
                            "cnt":1, 
                            "m_parse_hi":parsed_data["m_parse_hi"][i][j], 
                            "m_parse_lo":parsed_data["m_parse_lo"][i][j],
                            "addr":[(i, j)],
                            "exe":{tuple(parsed_data["original"][i]):[j]}
                            }
            else: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["cnt"] += 1
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["addr"].append((i, j))
                if tuple(parsed_data["original"][i]) in lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"]: lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"][parsed_data["original"][i]].append(j)
                else: lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"][parsed_data["original"][i]] = [j]
    return lemmata

def glossary_format(lemmata_data):
    header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["NOD/OPD Entry", "Part of Speech",  "Terse Translation", "Count", "Show/Hide Examples"])+"</td>\n</tr>\n"
    body = ""
    footer = "</tbody>\n</table>\n"
    for lem in sorted(lemmata_data): #make a neatly sorted list
        if lem != "'?'":
            lem_cnt = 0 #sum([lemmata_data[lem]["tokens"][x]["cnt"] for x in lemmata_data[lem]["tokens"]]) #was going to use an accumulator and += in the for loop, but then I wouldn't have this value available for the unanalyzed forms #-> changed my mind, the unanalyzed forms should be handled differently anyway
            exes = {}
            for tok in lemmata_data[lem]["tokens"]:
                lem_cnt += lemmata_data[lem]["tokens"][tok]["cnt"]
                for e in lemmata_data[lem]["tokens"][tok]["exe"]: 
                    if tuple(e) not in exes:
                        marked = []
                        for i in range(len(e)):
                            if i in lemmata_data[lem]["tokens"][tok]["exe"][e]: marked.append("<mark>"+e[i]+"</mark>")
                            else: marked.append(e[i])
                        exes[tuple(e)] = marked
                    else:
                        for x in lemmata_data[lem]["tokens"][tok]["exe"][e]: exes[tuple(e)][x] = "<mark>"+e[x]+"</mark>" #no risk of double marking because the same index can't correspond to two tokens of a word
            body += '<tr class="parent">\n'+"<td>"+"</td>\n<td>".join([lemmata_data[lem]["link"], lemmata_data[lem]["pos"].strip("'"), lemmata_data[lem]["tiny"], str(lem_cnt)])+'</td>\n<td onclick="toggleRow(this)">'+"(click for examples)"+"</td>\n</tr>\n"
            body += '<tr class="child" style="display: none;">\n'+'<td></td>\n<td colspan="4">'+"<br>\n".join([" ".join(exes[e]) for e in exes])+'</td>\n</tr>\n'
            #body.append([lemmata_data[lem]["link"], lemmata_data[lem]["pos"].strip("'"), lemmata_data[lem]["tiny"], str(lem_cnt), [exes[e] for e in exes]])
    return header+body+footer

def crib_format(lemmata_data):
    header = [["Word", "NOD/OPD Entry",  "Broad Analysis", "Terse Translation", "Count", "Addresses"]]
    nu_crib = []
    for lem in lemmata_data: 
        if lem != "'?'":
            for tok in lemmata_data[lem]["tokens"]: 
                addresses = " ".join([".".join([str(c[0]+1), str(c[1]+1)]) for c in lemmata_data[lem]["tokens"][tok]["addr"]])
                nu_crib.append([
                    tok, 
                    lemmata_data[lem]["link"], 
                    lemmata_data[lem]["tokens"][tok]["m_parse_hi"], 
                    lemmata_data[lem]["tiny"], 
                    lemmata_data[lem]["tokens"][tok]["cnt"], 
                    addresses])
                #print(tok)
                #print(lem)
                #print(addresses)
                #filler = []
                #filler.append(tok)
                #filler.append(lemmata_data[lem]["link"])
                #filler.append(lemmata_data[lem]["tiny"])
                #filler.append(lemmata_data[lem]["tokens"][tok]["m_parse_hi"])
                #filler.append(lemmata_data[lem]["tokens"][tok]["cnt"])
                #filler.append(addresses)
                #nu_crib.append(filler)
    table = tabulate.tabulate(header + sorted(nu_crib), tablefmt='html') #with lemma links instead of lemmas, URLs could be a tie-breaker in sorting instead of lemmas. Such a tie should not happen
    revised_table = ""
    for line in table.split('\n'): revised_table += undo_html(line)+'\n'
    return revised_table

def frequency_format(lemmata_data):
    header = [["Entry Count", "NOD/OPD Entry", "Word Count", "Actual Word"]]
    nu_cnts = []
    for lem in lemmata_data: #make a neatly sorted list
        for tok in lemmata_data[lem]["tokens"]:
            nu_cnts.append([sum([lemmata_data[lem]["tokens"][x]["cnt"] for x in lemmata_data[lem]["tokens"]]), lem, str(lemmata_data[lem]["tokens"][tok]["cnt"]), tok])
    nu_cnts = sorted(sorted(sorted(sorted(nu_cnts, key = lambda x: x[3]), key = lambda x: x[2], reverse = True), key = lambda x: x[1]), key = lambda x: x[0], reverse = True) #alphabetize tokens, then sort tokens by reverse frequency, then alphabetize lemmata, then sort lemmata by reverse frequency
    prev = ""
    unanalyzed_block = []
    for i in range(len(nu_cnts)): #move unanalyzed words to end
        x = nu_cnts.pop(0)
        if x[1] == "'?'": unanalyzed_block.append(x)
        else: nu_cnts.append(x)
    nu_cnts.extend(unanalyzed_block)
    for i in range(len(nu_cnts)): #zap out redundant header information on lines beneath the header, make strings where appropriate, add in lemma links
        nu_cnts[i][0] = str(nu_cnts[i][0])
        nu_cnts[i][2] = str(nu_cnts[i][2])
        new = nu_cnts[i][1]
        if new != prev: 
            prev = new
            nu_cnts[i][1] = lemmata_data[nu_cnts[i][1]]["link"]
        elif new == prev: 
            nu_cnts[i][0] = ""
            nu_cnts[i][1] = ""
    table = tabulate.tabulate(header + nu_cnts, tablefmt='html')
    revised_table = ""
    for line in table.split('\n'): revised_table += undo_html(line)+'\n'
    return revised_table

def take_windows(sentence_data, size, *addresses):
    windows = []
    for a in addresses:
        w = {}
        left_edge = 0
        if a[1]-size > 0: left_edge = a[1]-size
        for sd in sentence_data: w[sd] = [sentence_data[sd][a[0]][left_edge:a[1]+size+1]]
        windows.append(w)
    return windows

#this is only called in commented out lines
def retrieve_addrs(lexical_perspective, *keys):
    unanalyzed_token_addresses = []
    for key in keys:
        for t in sorted(lexical_perspective[key]["tokens"]):
            unanalyzed_token_addresses.extend(lexical_perspective["'?'"]["tokens"][t]["addr"])
    return unanalyzed_token_addresses

def unanalyzed_format(size, addresses, *windows):
    header = [ [""]+["-{}".format(str(i)) for i in reversed(range(1, size+1))]+["Target"]+["+{}".format(str(i)) for i in range(1, size+1)]]
    rows = []
    for i in range(len(addresses)):
        #gosh it would be nice to print the whole sentence out, with the free translation under it
        rows.append(["Sentence: {0}, Word: {1}".format(str(addresses[i][0]+1), str(addresses[i][1]+1))]+["" for i in range((size*2)+1)])
        block = interlinearize_blocks(windows[i])
        if addresses[i][1] < size: #need to pad left
            for j in range(len(block)):
                block[j] = [block[j][0]]+["" for k in range(size-addresses[i][1])]+block[j][1:]
        span_len = len(block[0][1:])
        for j in range(len(block)):
            row = block[j] + ["" for k in range((size*2+1)-span_len)]
            rows.append(row)
    for r in header + rows: print(len(r))
    table = tabulate.tabulate(header + rows, tablefmt='html')
    revised_table = "\nBelow are {} unanalyzed words in context.\n".format(str(len(addresses)))
    for line in table.split('\n'): revised_table += undo_html(line)+'\n'
    return revised_table

def vital_statistics_format(vital_statistics):
    #if dont_make_rep_count: return "<p>Overall word count: {0}; Analyzed word count: {1} (incl. repetitions/variants); Unanalyzed word count: {3} </p>".format(*[str(x) for x in vital_statistics])
    return "<p>Overall word count: {0}; Analyzed word count: {1} ({2} w/out repetitions/variants); Unanalyzed word count: {3} </p>".format(*[str(x) for x in vital_statistics])
    #return """
    #<p>Summary counts:<br></p>
    #<p style="margin-left: 40px">
    #    Overall word count: {0}<br>
    #    Analyzed word count: {1}<br>
    #    Analyzed unique word count: {2} (excludes repetitions/variants of 'the same word')<br>
    #    Unanalyzed word count: {3}<br>
    #</p>
    #""".format(*[str(x) for x in vital_statistics])

##this is the main function. it puts everything together
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
        if form_values[x]["order"] and form_values[x]["file"]: analyzers.append(form_values[x]["file"])
    #separator = pyscript.document.querySelector("#english_separator").value
    #english = []
    input_text = pyscript.document.querySelector("#larger_text_input")
    freeNish = input_text.value
    #if separator:
    #    print("sep is ", separator)
    #    freeNish = ""
    #    for it in input_text.value.split('\n'):
    #        chopped = it.split(separator)
    #        freeNish += chopped[0]+'\n'
    #        if len(chopped) > 1: english.append(chopped[1])
    #        else: english.append("")
    to_analyze = sep_punct(freeNish.lower(), True).split()
    parses = {}
    model_credit = {} #as of aug 2025, only using this data to allow correct formatting of western (OPD-based) lemmata urls vs eastern (NOD-based) lemmata. It could be nice to flag misspelled words either to indicate less certainty or to encourage spelling improvement
    for i in range(len(analyzers)):
        analyzed = pp.parse_pyhfst(analyzers[i], *to_analyze)
        to_analyze = []
        for w in analyzed:
            if analyzed[w][0][0].endswith('+?') and i+1 < len(analyzers): to_analyze.append(w)
            elif analyzed[w][0][0].endswith('+?') and i+1 == len(analyzers): 
                parses[w] = analyzed[w]
                model_credit[w] = "unanalyzed" 
            #elif (not analyzed[w][0][0].endswith('+?')) and i+1 == len(analyzers): 
            #    parses[w] = analyzed[w]
            #    model_credit[w] = analyzers[i]
            else: 
                parses[w] = analyzed[w]
                model_credit[w] = analyzers[i]
    #analyzed = pp.parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *sep_punct(freeNish.lower(), True).split())
    ##m_parse_lo = [analyzed[w][disambiguate(min_morphs(*analyzed[w]), min_morphs, *analyzed[w])][0] for w in sep_punct(freeNish.lower(), True).split()]
    #re_analysis = []
    #for w in sep_punct(freeNish.lower(), True).split():
    #    if analyzed[w][0][0].endswith('+?'): re_analysis.append(w)
    #re_analyzed = pp.parse_pyhfst("./morphophonologyclitics_analyze.hfstol", *re_analysis)
    h = {"original":[],
         "m_parse_lo":[],
         "m_parse_hi":[],
         "lemmata":[],
         "lemma_links":[],
         "tinies":[],
         #"english":english
         }
    for line in freeNish.lower().split('\n'):
        local = []
        for w in sep_punct(line, True).split(): local.append(parses[w][disambiguate(min_morphs(*parses[w]), min_morphs, *parses[w])][0])
            #if analyzed[w][0][0].endswith('+?'): local.append(re_analyzed[w][disambiguate(min_morphs(*re_analyzed[w]), min_morphs, *re_analyzed[w])][0])
            #else: local.append(analyzed[w][disambiguate(min_morphs(*analyzed[w]), min_morphs, *analyzed[w])][0])
        h["original"].append(sep_punct(line, True).split())
        h["m_parse_lo"].append(local)
        #h["m_parse_hi"].append(["'"+pp.formatted(interpret(analysis_dict(x)))+"'" if analysis_dict(x) else "'?'" for x in local])
        his = []
        lemms = []
        lem_links = []
        for i in range(len(local)):
            if model_credit[sep_punct(line, True).split()[i]] == "./morphophonology_analyze_border_lakes.hfstol": 
                lem = extract_lemma(local[i], ciw_pos_regex_opd)
                pos = pp.extract_pos(local[i], ciw_pos_regex_opd)
                lemms.append(lem)
                #populate hi
                if regex.search("({0})(.*({0}))?".format(ciw_pos_regex_model), local[i]): his.append("'"+pp.formatted(interpret_ciw(local[i], ciw_pos_regex_model))+"'")
                if not regex.search("({0})(.*({0}))?".format(ciw_pos_regex_model), local[i]): his.append("'?'")
                #populate lem
                if (lem, pos) in opd_manual_links: lem_links.append(opd.wrap_opd_url(opd_manual_links[(lem, pos)], lem)) 
                else: lem_links.append(opd.wrap_opd_url(opd.mk_opd_url(lem, pos), lem)) 
            else: 
                #populate lem
                lem = extract_lemma(local[i], pos_regex)
                if not lem: lem = "'?'"
                lemms.append(lem)
                lem_links.append(wrap_nod_entry_url(lem, **iddict)[0])
                #populate hi
                if analysis_dict(local[i]): his.append("'"+pp.formatted(interpret(analysis_dict(local[i])))+"'")
                if not analysis_dict(local[i]): his.append("'?'")
        h["m_parse_hi"].append(his) 
        h["lemmata"].append(lemms) 
        h["lemma_links"].append(lem_links) 
        #h["lemmata"].append([x if x else "?" for x in lemmatize(pos_regex, *local)]) 
        h["tinies"].append(wrap_glosses(*retrieve_glosses(*h["lemmata"][-1], **gdict)))
        #tinies = []
        #for l in h["lemmata"][-1]:
        #    try: gloss = gdict[l]
        #    except KeyError:
        #        gloss = "?"
        #    tinies.append("'"+gloss+"'")
        #h["tinies"].append(tinies)
    #this is yet another routine to collate information. it is inefficient to run through the data this many times. everything here could be collected at other points. trying to integrate it into the various other points was resulting in little bits of spaghetti code duplicated all over the place
    vital_stats = [
            0, # "Overall raw word count"], -> to_analyze gets reset as you work through the cascade, so the count needs to be here
            0,#, "Analyzed raw word count"],
            0,#, "Analyzed processed word count (not counting repetititions/variants of 'the same word')"],
            0,#, "Unanalyzed raw word count"],
            ]
    general_lemmata = []
    for w in sep_punct(freeNish.lower(), True).split():
        vital_stats[0] += 1
        if w in parses and not parses[w][0][0].endswith('+?'): 
            vital_stats[1] += 1
        else: 
            vital_stats[3] += 1
    for i in range(len(h["lemmata"])):
        for j in range(len(h["lemmata"][i])):
            if h["lemmata"][i][j] not in general_lemmata:
                general_lemmata.append(h["lemmata"][i][j])
        vital_stats[2] = len(general_lemmata)
    analysis_mode = pyscript.document.querySelector("#analysis_mode")
    output_div = pyscript.document.querySelector("#output")
    if analysis_mode.value == "interlinearize":
        #revised = ""
        #for i in range(len(h["m_parse_lo"])):
        #    #lines_out += tabulate.tabulate([
        #    #    ["Original Material:"] + h["original"][i],
        #    #    ["Narrow Analysis:"] + h["m_parse_lo"][i], 
        #    #    ["Broad Analysis:"] + h["m_parse_hi"][i], 
        #    #    ["NOD Entry:"] + h["lemmata"][i],
        #    #    ["Terse Translation:"] + h["tinies"][i]], tablefmt='html')
        #    new_batch = tabulate.tabulate([
        #        ["Original Material:"] + h["original"][i],
        #        ["Narrow Analysis:"] + h["m_parse_lo"][i], 
        #        ["Broad Analysis:"] + h["m_parse_hi"][i], 
        #        ["NOD/OPD Entry:"] + h["lemma_links"][i], 
        #        ["Terse Translation:"] + h["tinies"][i]], tablefmt='html')
        #    for nb in new_batch.split('\n'):
        #        if "NOD/OPD Entry" in nb: revised += undo_html(nb)+'\n'
        #        else: revised += nb+'\n'
        #output_div.innerHTML = revised
        output_div.innerHTML = interlinearize(h)+vital_statistics_format(vital_stats)
    elif analysis_mode.value == "glossary": 
        lp = lexical_perspective(h)
        unanalyzed_context_table = ""
        if "'?'" in lp:
            unanalyzed_cnt = 0
            #context_size = 2
            #unanalyzed_addresses = retrieve_addrs(lp, "'?'")
            #unanalyzed_context_table = unanalyzed_format(context_size, unanalyzed_addresses, *take_windows(h, context_size, *unanalyzed_addresses))
            context_size = 2
            unanalyzed_token_addresses = []
            for t in sorted(lp["'?'"]["tokens"]):
                unanalyzed_token_addresses.extend(lp["'?'"]["tokens"][t]["addr"])
                unanalyzed_cnt += lp["'?'"]["tokens"][t]["cnt"]
            context_windows = take_windows(h, context_size, *unanalyzed_token_addresses)
            unanalyzed_context_table = unanalyzed_format(context_size, unanalyzed_token_addresses, *context_windows)
        output_div.innerHTML = glossary_format(lp)+unanalyzed_context_table+vital_statistics_format(vital_stats)
    elif analysis_mode.value == "crib": 
        lp = lexical_perspective(h)
        unanalyzed_context_table = ""
        if "'?'" in lp:
            #context_size = 2
            #unanalyzed_addresses = retrieve_addrs(lp, "'?'")
            #unanalyzed_context_table = unanalyzed_format(context_size, unanalyzed_addresses, *take_windows(h, context_size, *unanalyzed_addresses))
            context_size = 2
            unanalyzed_token_addresses = []
            for t in sorted(lp["'?'"]["tokens"]):
                unanalyzed_token_addresses.extend(lp["'?'"]["tokens"][t]["addr"])
            context_windows = take_windows(h, context_size, *unanalyzed_token_addresses)
            unanalyzed_context_table = unanalyzed_format(context_size, unanalyzed_token_addresses, *context_windows)
        output_div.innerHTML = crib_format(lp)+unanalyzed_context_table+vital_statistics_format(vital_stats)
    elif analysis_mode.value == "frequency": 
        lp = lexical_perspective(h)
        output_div.innerHTML = frequency_format(lp)+vital_statistics_format(vital_statistics)
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
        sectioned = [["Sentences", "Target Verb Count", "Complexity Score"]]
        for i in range(len(c_order)-1): #need to skip the last category, because there is no corresponding bin in the verb counts for when there is nothing
            sectioned.append([">>These sentences have verbs of the following category: {}".format(c_order[i]), "", ""])
            for x in sorted(sorted(categorized[c_order[i]], key = lambda y: y[0][-1][0]), key = lambda z: z[0][0][i]): sectioned.append([" ".join(x[1]), str(x[0][0][i]), str(x[0][-1][0])]) #sorting by morphological complexity, then count of relevant verb category
        sectioned.append([">>These sentences had no verbs found in them"])
        for x in sorted(categorized["(No verbs found)"], key = lambda y: y[0][-1][0]):
            sectioned.append([" ".join(x[1])])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
    elif analysis_mode.value == "complexity":
        comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
        overall_score = sc.alg_morph_score_rate(*comp_counts)
        sectioned = [["Overall Score (Features per Sentence):",  str(overall_score[2])]]
        for ssp in sorted([x for x in zip(comp_counts, h["original"])], key = lambda y: y[0][-1][0]): sectioned.append([" ".join(ssp[1]), ssp[0][-1][0]])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
    elif analysis_mode.value == "verb_collate":
        faced = sc.interface(pos_regex, *h["m_parse_lo"])
        verbcats = ["VAI", "VTA", "VII", "VAIO", "VTI"]
        verbdict = {x:[] for x in verbcats}
        for i in range(len(faced)):
            for j in range(len(faced[i])):
                if faced[i][j]["pos"] in verbdict: 
                    if (h["original"][i][j], h["m_parse_hi"][i][j]) not in verbdict[faced[i][j]["pos"]]: verbdict[faced[i][j]["pos"]].append((h["original"][i][j], h["m_parse_hi"][i][j]))
        sectioned = [["Verbs", "Broad Analysis"]]
        for c in verbcats:
            sectioned.append(["Found these verbs of category {}:".format(c), ""])
            for v in sorted(verbdict[c], key = lambda x: x[1]): sectioned.append([v[0], v[1]])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
    elif analysis_mode.value in ["triage", "reversed_triage"]:
        recall_errors = []
        for i in range(len(h["original"])):
            for j in range(len(h["original"][i])):
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
        output_div.innerHTML = forwards+vital_statistics_format(vital_stats)
            
