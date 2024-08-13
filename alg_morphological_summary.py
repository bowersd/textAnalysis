import yaml
import re
import sys

import lemmatize as lem
import engdict as eng
import readwrite as rw

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
    adict["clitic"] = [re.search(r"((?<=\+)dash\+Adv$)?", analysis_string)[0]]
    analysis_string = re.sub(r"\+dash\+Adv", "", analysis_string) #this only needs to happen after clitics are checked and before derivation/suffixes are inspected, stuck with post-clitics
    adict["prefix"] = [re.search("(^[123X])?", analysis_string)[0]]
    if re.search("({0})(.*({0}))?".format(postags), analysis_string): adict["derivation"] = [x for x in re.search("({0})(.*({0}))?".format(postags), analysis_string)[0].split("+") if x] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    x =  re.search(r"((((PV|PN|PA)[^+]*)|Redup)\+)+", analysis_string)
    if x: adict["preforms"] = re.search(r"((((PV|PN|PA)[^+]*)|Redup)\+)+", analysis_string)[0].split("+")
    if re.search(".*?(?={})".format("|".join([x[2:]+x[:2] for x in postags.split("|")])), "+".join(reversed(analysis_string.split("+")))): adict["suffixes"] = [x for x in reversed(re.search(".*?(?={})".format("|".join([x[2:]+x[:2] for x in postags.split("|")])), "+".join(reversed(analysis_string.split("+"))))[0].split("+"))]
    if not adict["derivation"]: return None
    return adict


def winnow(analysis_in, *wheat):
    #translation suite does not cover preverbs, clitics, reduplication, participles, derivational morphology (and others)
    #to allow the translation suite to function, we separate what it can handle from what it can't
    h = []
    chaff = []
    for a in analysis_in:
        if a in wheat: h.append(a)
        else: chaff.append(a)
    return (h, chaff)

#need to be smart about lemmata
def identify_targets(sep, *tag_strings):
    h = []
    for s in tag_strings:
        lr = s.split(sep) #sep can be <> for compiling list of relevant tags, or lemma for prepping an analysis for summary: NO! you need all tags for prepping a string, not just all unique tags
        for pre in re.findall(r"[^\+]*\+", lr[0]):
            if pre not in h: h.append(pre)
        for suff in re.findall(r"\+[^\+]*", lr[1]):
            if suff not in h: h.append(suff)
    return h

def insert_lexmarkers(tagmark, lexmark, *tag_stream):
    h = []
    root_seen = False
    for i in range(len(tag_stream)):
        if tag_stream[i].startswith(tagmark) and not root_seen:
            root_seen = True
            h.append(lexmark)
        h.append(tag_stream[i])
    return h

def format_summary(wheat, chaff, lemma, **mapping):
    attempted = "".join(insert_lexmarkers("+", "<>", *wheat))
    try:
        print(lemma, mapping["".join(insert_lexmarkers("+", "<>", *wheat))], "("+", ".join(chaff)+")")
    except KeyError:
        print(lemma, "".join(insert_lexmarkers("+", "<>", *wheat)), "("+", ".join(chaff)+") BROKE SUMMARY TOOL")


#if __name__ == "__main__":
#    major_cnt = 0
#    major_cnt_fail = 0
#    minor_results = []
#    for x in sys.argv[1:]:
#        with open(x) as file_in:
#            minor_tags = yaml.load(file_in, Loader = yaml.FullLoader)
#            minor_cnt = 0
#            minor_cnt_fail = 0
#            for x in minor_tags:
#                for y in minor_tags[x]:
#                    for z in minor_tags[x][y]:
#                        minor_cnt += 1
#                        if formatted(interpret(analysis_dict(z))) != minor_tags[x][y][z]:
#                            minor_cnt_fail += 1
#                            print("in ", z)
#                            print("intended ", minor_tags[x][y][z])
#                            print("produced ", formatted(interpret(analysis_dict(z))))
#            minor_results.append("{0} results ... successes: {1}, failures: {2}, failure pct: {3}".format(str(y), str(minor_cnt-minor_cnt_fail), str(minor_cnt_fail), str(round(100*minor_cnt_fail/minor_cnt, 3))))
#        major_cnt += minor_cnt
#        major_cnt_fail += minor_cnt_fail
#    for x in minor_results: print(x)
#    print("Overall results ... successes: {0}, failures: {1}, failure pct: {2}".format(str(major_cnt-major_cnt_fail), str(major_cnt_fail), str(round(100*major_cnt_fail/major_cnt, 3))))
