import yaml
import re
import sys

import lemmatize as lem
import engdict as eng
import readwrite as rw

def interpret(analysis_in):
    summary = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":"", "Periph":"", "Else": [x for x in analysis_in["preforms"]+analysis_in["clitic"]]}
    inversion = False #if true, S/O will be inverted at end
    summary["S"]["Pers"] = analysis_in["prefix"][0]
    summary["DerivChain"] = " ".join([x for x in analysis_in["derivation"]])
    summary["Head"] = analysis_in["derivation"][-1]
    if summary["Head"] == "VTI": summary["O"]["Pers"] = "0" #cheating a little and not putting this in the theme sign info because we don't actually have a suffix tag for VTI themes
    while analysis_in["suffixes"]:
        #gnarly list of elif statements
        #general strategy: fill object information with theme sign, then fill object number information, then unify prefix information with number information in subject field, then fill in subject information with remaining suffixes 
        s = analysis_in["suffixes"].pop(0)
        if s == "Neg": summary["Neg"] = s
        elif s == "Prt": summary["Mode"] = s
        elif s == "Dub": summary["Mode"] += s
        elif s == "Voc": summary["Mode"] += s
        elif s == "Cnj" or s == "Imp": summary["Order"] = s
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
        elif summary["O"]["Pers"] == "1" and s == "1" and analysis_in["suffixes"][0:1] == ["Pl"]:  #this should only happen with thm1 (see below)
            #first person objects are only written in with Thm1, Thm2, Thm1Pl2. 
            #Thm2, Thm1Pl2 are never followed by 1pl (bc Thm1Pl2 is how you indicate first person plurals). 
            #Thm1 .* 1Pl precludes 2pl marking, and so is ambiguous for second person number.  1 obj...1pl = 2Pl/2 vs 1pl.  it never means 21pl bc ban on XvX
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] == "Pl"
            #summary["S"]["Pers"] = "2" #redundant, but VTA Cnj Thm1 1Pl needs a default value. because 1Pl blocks 2 person marking ... maybe just add that marking in the model?, no because there are later markings that can appear
            summary["S"]["Num"] = "Pl/2"
        elif summary["O"]["Pers"] == "2" and s == "2" and analysis_in["suffixes"][0:2] == ["1", "Pl"]:
            analysis_in["suffixes"].pop(0)
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] = "1Pl"
        elif summary["O"]["Pers"] == "2" and s == "2" and analysis_in["suffixes"][0:1] == ["Pl"]:
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] = "Pl"
        elif summary["O"]["Pers"] == "3" and s == "3" and analysis_in["suffixes"][0:1] == ["4"]:
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] == "'"
        elif summary["O"]["Pers"] == "3" and s == "3" and analysis_in["suffixes"][0:1] == ["Pl"]:
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] == "Pl"
        elif summary["O"]["Pers"] == "3" and s == "0": #VTA indep (inverses), have overt suffs for inanimates, need to over ride the default 3 here
            summary["O"]["Pers"] = "0"
        elif summary["O"]["Pers"] == "0" and s == "0" and analysis_in["suffixes"][0:1] == ["Pl"]: #there is no longer a gratuitous +0 suffix in VTI indeps with singular actors, so no deliberately clunky syntax needed to drop the +0 tag
                analysis_in["suffixes"].pop(0)
                summary["O"]["Num"] == "Pl"
        #}theme sign number end
        #{getting number information for person values specified by prefix == NOT CONJUNCT!
        elif analysis_in["prefix"][0] == "1" and s == "1" and analysis_in["suffixes"][0:1] == ["Pl"]: 
            summary["S"]["Num"] = "Pl"
            analysis_in["suffixes"].pop(0)
        elif analysis_in["prefix"][0] == "2" and s == "1" and analysis_in["suffixes"][0:2] == ["Pl"]: #this does not mess up VTA local themes, since it is a lower elif (2...Thm1...1Pl = 2Pl/2 v 1pl != 21Pl)
            analysis_in["suffixes"].pop(0)
            summary["S"]["Num"] = "1Pl"
        elif analysis_in["prefix"][0] == "2" and s == "2" and analysis_in["suffixes"][0:1] == ["Pl"]:
            analysis_in["suffixes"].pop(0)
            #if summary["O"]["Pers"] == "1" and summary["S"]["Pers"] == "2" and inversion: summary["S"]["Num"] == "Pl"  ## before inversion (thm1sg/thm1pl .*2pl) = (2pl v 1sg/2pl v 1pl), so no need to specify a special case here 
            #note: there is no further number information in another slot for first persons here ... like theme signs really are object agreement and inversion swoops them into subjecthood (and/or peripheral suffixes are just for 3rd persons)
            summary["S"]["Num"] = "Pl" 
        elif analysis_in["prefix"][0] == "3" and s == "2" and analysis_in["suffixes"][0:1] == ["Pl"]:
            summary["S"]["Num"] = "Pl"
            analysis_in["suffixes"].pop(0)
        #end prefix number obtained}
        #{getting person/number information from suffixes
        elif (not summary["S"]["Pers"]) and s == "1":
            summary["S"]["Pers"] = "1"
            if analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
        elif ((not summary["S"]["Pers"]) or summary["S"]["Pers"]=='3') and s == "2": 
            if not summary["S"]["Pers"]: summary["S"]["Pers"] = "2"
            if summary["S"]["Pers"] == "2" and analysis_in["suffixes"][0:2] == ["1", "Pl"]:
                summary["S"]["Num"] = "1Pl"
                analysis_in["suffixes"].pop(0)
                analysis_in["suffixes"].pop(0)
            elif analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
                if summary["O"]["Pers"] == "0" and inversion == True and summary["Neg"] and summary["Order"] and analysis_in["suffixes"][0:1] == "3": #VTA CNJ THMINV NEG 2 PL 3(PL)
                    summary["O"]["Pers"] == "3"
                    analysis_in["suffixes"].pop()
        elif ((not summary["S"]["Pers"]) or summary["S"]["Pers"] == '3') and s == "3":
            summary["S"]["Pers"] = "3"
            if inversion = True and summary["O"]["Pers"] == "0" and summary["Order"] == "Cnj":  summary["O"]["Pers"] = "3'/0" #VTA CNJ THMINV 3
            if analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
            elif analysis_in["suffixes"][0:1] == ["4"]:
                summary["S"]["Num"] = "'"
                analysis_in["suffixes"].pop(0)
        elif (not summary["S"]["Pers"]) and s == "0": 
            summary["S"]["Pers"] = "0"
            if analysis_in["suffixes"][0:1] == ["4"]:
                summary["S"]["Num"] = "'"
                analysis_in["suffixes"].pop(0)
            elif analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] += "Pl" #NB: += used since 0'Pl is possible
                analysis_in["suffixes"].pop(0)
        elif (not summary["S"]["Pers"]) and s == "X": summary["S"]["Pers"] = "X"
        #}end person/number information from suffixes
        elif summary["Head"].startswith("N") and s == "4": summary["Periph"] = "Obv"
        elif summary["Head"].startswith("N") and s in ["Loc", "Pl"]: summary["Periph"] = s
        else: summary["Else"].append(s)
    if (not summary["S"]["Pers"]) and summary["O"]["Pers"] == "2": summary["S"]["Pers"] = "1" #default person for Thm2a keep at end
    if (not summary["S"]["Pers"]) and summary["O"]["Pers"] == "1": summary["S"]["Pers"] = "2" #default person for Thm1  keep at end
    if not inversion and summary["S"]["Pers"] == "3" and summary["O"]["Pers"] == "3": summary["O"]["Num"] = "'" #default obviation for direct themes. should only be necessary for VTA CNJ, which never overtly signals obviation, but kept general
    #summary["Else"] = [y[0] for x in analysis_in for y in analysis_in[x] if not y[1]]
    if inversion == True: summary["S"], summary["O"] = summary["O"], summary["S"]
    return summary

def analysis_dict(analysis_string):
    postags = "\+VAI|\+VII|\+VTI|\+VTA|\+VAIO|\+NA|\+NI|\+NAD|\+NID|\+Conj|\+Interj|\+Num|\+Pron(\+NA|\+NI)|\+Ipc|\+Qnt|\+Adv"
    adict = {"prefix":[], "derivation": [], "preforms":[], "suffixes":[], "clitic":[]}
    adict["clitic"] = [re.search("((?<=\+)dash\+Adv$)?", analysis_string)[0]]
    analysis_string = re.sub("\+dash\+Adv", "", analysis_string) #this only needs to happen after clitics are checked and before derivation/suffixes are inspected, stuck with post-clitics
    adict["prefix"] = [re.search("(^[123X])?", analysis_string)[0]]
    adict["derivation"] = re.search("{0}(.*{0})?".format(postags), analysis_string)[0].split("+") #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    adict["preforms"] = re.search("(((PV|PN|PA)[^\+]*\+)|Redup\+)*", analysis_string)[0].split("+")
    adict["suffixes"] = [x for x in reversed(re.search(".*?(?={})".format("|".join([x[2:]+x[:2] for x in postags.split("|")])), "+".join(reversed(analysis_string.split("+"))))[0].split("+"))]
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
        for pre in re.findall("[^\+]*\+", lr[0]):
            if pre not in h: h.append(pre)
        for suff in re.findall("\+[^\+]*", lr[1]):
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


if __name__ == "__main__":
    with open(sys.argv[1]) as file_in:
        mega_tags = yaml.load(file_in)
    for x in mega_tags["Mapping"]["VTA - IND"]: 
        print(x)
        print(interpret(analysis_dict(x)))
