import yaml
import re
import sys

import lemmatize as lem
import engdict as eng
import readwrite as rw

def interpret(analysis_in):
    summary = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":"", "Else": [x for x in analysis_in["preforms"]+analysis_in["clitic"]}
    inversion = False #if true, S/O will be inverted at end
    #analysis = [x for x in in analysis_in]
    summary["S"]["Pers"] = analysis_in["prefix"][0]
    summary["DerivChain"] = " ".join([x for x in analysis_in["Derivation"]])
    summary["Head"] = analysis_in["Derivation"][-1]
    #probably better to just pop the suffixes and append them to "else" if they don't get satisfied
    #for i in range(len(analysis_in["suffixes"][0])):
    while analysis_in["suffixes"]:
        s = analysis_in["suffixes"].pop(0)
        if s == "Neg": summary["Neg"] = s
        elif s == "Prt": summary["Mode"] = s
        elif s == "Dub": summary["Mode"] += s
        elif s == "Cnj" or s == "Imp": summary["Order"] = s
        #{extracting theme sign information CURRENTLY AGNOSTIC TO CNJ VS IND
        #{local theme signs
        elif s == "Thm2": summary["O"]["Pers"] = "1"
        elif (s == "Thm1Pl" or s == "Thm1Sg"):
            summary["O"]["Pers"] = "1"
            if s == "Thm1Pl": summary["O"]["Num"] = "Pl"
            inversion = True
            #local theme signs end}
        elif (s == "ThmDir" or s == "ThmInv"):
            summary["O"]["Pers"] = "3"
            if s == "ThmInv": inversion = True
        #} extracting theme sign information end
        #{getting number information for theme signs/objects
        elif summary["O"]["Pers"] == "3" and s == "3" and analysis_in["suffixes"][0:1] == ["4"]:
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] == "'"
        elif summary["O"]["Pers"] == "3" and s == "3" and analysis_in["suffixes"][0:1] == ["Pl"]:
            analysis_in["suffixes"].pop(0)
            summary["O"]["Num"] == "Pl"
        elif summary["O"]["Pers"] == "3" and s == "0": 
            summary["O"]["Pers"] = "0"
            if analysis_in["suffixes"][0:1] == ["Pl"]:
                analysis_in["suffixes"].pop(0)
                summary["O"]["Num"] == "Pl"
        #}theme sign number end
        #{getting number information for person values specified by prefix == NOT CONJUNCT!
        elif analysis_in["prefix"][0] == "1" and s == "1" and analysis_in["suffixes"][0:1] == ["Pl"]: 
            summary["S"]["Num"] = "Pl"
            analysis_in["suffixes"].pop(0)
        elif analysis_in["prefix"][0] == "2": 
            if s = "1" and analysis_in["suffixes"][0:2] == ["Pl"]:
                analysis_in["suffixes"].pop(0)
                if summary["O"]["Pers"] == "1" and summary["S"]["Pers"] == "2" and not inversion: #this is thm2 .*1pl = (2v1pl/2plv1pl) 
                    summary["S"]["Num"] = "Pl/2"
                    summary["O"]["Num"] = "Pl"
                else: summary["S"]["Num"] = "1Pl"
            elif s = "2" and analysis_in["suffixes"][0:1] == ["Pl"]:
                analysis_in["suffixes"].pop(0)
                #if summary["O"]["Pers"] == "1" and summary["S"]["Pers"] == "2" and inversion: summary["S"]["Num"] == "Pl"  ## before inversion (thm1sg/thm1pl .*2pl) = (2pl v 1sg/2pl v 1pl), so no need to specify a special case here 
                #note: there is no further number information in another slot for first persons here ... like theme signs really are object agreement and inversion swoops them into subjecthood (and/or peripheral suffixes are just for 3rd persons)
                summary["S"]["Num"] = "Pl" 
        elif analysis_in["prefix"][0] == "3" and and s = "2" and analysis_in["suffixes"][0:1] == ["Pl"]:
            summary["S"]["Num"] = "Pl"
            analysis_in["suffixes"].pop(0)
        #end prefix number obtained}
        elif (not summary["S"]["Pers"]) and s == "1":
            summary["S"]["Pers"] = "1"
            if analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
        elif (not summary["S"]["Pers"]) and s == "2": 
            summary["S"]["Pers"] = "2"
            if analysis_in["suffixes"][0:2] == ["1", "Pl"]:
                summary["S"]["Num"] = "1Pl"
                analysis_in["suffixes"].pop(0)
                analysis_in["suffixes"].pop(0)
            elif analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
        elif (not summary["S"]["Pers"]) and s == "3":
            summary["S"]["Pers"] = "3"
            if analysis_in["suffixes"][0:1] == ["Pl"]:
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
            if analysis_in["suffixes"][0:1] == ["3", "4"]:
                summary["S"]["Num"] = "'"
                analysis_in["suffixes"].pop(0)
        elif (not summary["S"]["Pers"]) and s == "0": #VTIs/VTAs still not covered
            summary["S"]["Pers"] = "0"
            if analysis_in["suffixes"][0:1] == ["Pl"]: #VTIs/VTAs still not covered
                summary["S"]["Num"] = "Pl"
                analysis_in["suffixes"].pop(0)
        else: summary["Else"].append(s)
    #summary["Else"] = [y[0] for x in analysis_in for y in analysis_in[x] if not y[1]]
    if inversion = True: summary["S"], summary["O"] = summary["O"], summary["S"]
    return summary

def analysis_dict(analysis_string):
    adict = {"prefix":[], "derivation": [], "preforms":[], "suffixes":[], "clitic":[]}
    adict["clitic"] = [re.search("((?<=\+)dash\+Adv$)?", analysis_string)[0]]
    analysis_string = analysis_string.strip("+dash+Adv") #this only needs to happen after clitics are checked and before derivation/suffixes are inspected, stuck with post-clitics
    adict["prefix"] = [re.search("(^[123X])?", analysis_string)[0]]
    adict["derivation"] = re.search("POSTAGS(.*POSTAGS)?", analysis_string)[0].split("+") #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    adict["preforms"] = re.search("(PV|PN|PA[^\+]*\+)*", analysis_string)[0].split("+")
    adict["suffixes"] = [x for x in reversed(re.search(".*(?!POSTAGS)", "+".join(reversed(analysis_string.split("+"))))[0].split("+"))]
    #adict["suffixes"] = list(reversed([["".join(reversed(x)), False] for x in re.search(".*(?!REVPOSTAGS)", "".join(reversed(analysis_string)))[0].split("+")])) #reading everything backwards then re-reversing it (in order to avoid non-fixed width negative lookbehind
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
    mega_tags = []
    gdict = eng.mk_glossing_dict(*rw.readin(sys.argv[4]))
    pos_regex = "".join(rw.readin(sys.argv[3]))
    for x in sys.argv[7:]:
        with open(x) as file_in:
            mega_tags.append(yaml.load(file_in))
    map_dict = {}
    for d in mega_tags:
        for x in d:
            for y in d[x]:
                for z in d[x][y]:
                    map_dict[z] = d[x][y][z]
    tag_set = identify_targets("<>", *[x for x in map_dict])
    x = lem.interlinearize(sys.argv[1], sys.argv[2], pos_regex, gdict, rw.burn_metadata(2, *rw.readin(sys.argv[5])), rw.readin(sys.argv[6]))
    for inter in x:
        for i in range(len(inter[0])):
            print(inter[0][i])
            if inter[1][i]=="?":
                print(inter[1][i])
                print(inter[2][i])
                print(inter[3][i])
                print()
            else:
                straight_tags = re.findall("[^\+]*\+", inter[1][i].split(inter[2][i])[0])+re.findall("[^\+]*\+", inter[1][i].split(inter[2][i])[1])
                wheat, chaff = winnow(straight_tags,  *tag_set)
                print(format_summary(wheat, chaff, inter[2][i], **map_dict))
                print(inter[2][i])
                print(inter[3][i])
                print()




