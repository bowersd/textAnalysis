import yaml
import re
import sys

import lemmatize as lem
import engdict as eng
import readwrite as rw

def interpret(analysis_in):
    summary = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":"", "Else": []}
    #analysis = [x for x in in analysis_in]
    summary["S"]["Pers"] = analysis_in["prefix"][0]
    analysis_in["prefix"][1] = True
    summary["DerivChain"] = " ".join([x[0] for x in analysis_in["Derivation"]])
    summary["Head"] = analysis_in["Derivation"][-1][0]
    for x in analysis_in["Derivation"]: x[1] = True
    for i in range(len(analysis_in["suffixes"])):
        if analysis_in[suffixes][i][0] == "Neg": 
            summary["Neg"] = analysis_in[suffixes][i][0]
            analysis_in[suffixes][i][1] = True
        elif analysis_in[suffixes][i][0] == "Prt":
            summary["Mode"] = analysis_in[suffixes][i][0]
            analysis_in[suffixes][i][1] = True
        elif analysis_in[suffixes][i][0] == "Dub":
            summary["Mode"] += analysis_in[suffixes][i][0]
            analysis_in[suffixes][i][1] = True
        elif analysis_in[suffixes][i][0] == "Cnj" or analysis_in[suffixes][i][0] == "Imp":
            summary["Order"] = analysis_in[suffixes][i][0]
            analysis_in[suffixes][i][1] = True
        #{prefix information already obtained
        elif summary["S"]["Pers"] == "1" and analysis_in[suffixes][i][0] == "1Pl": #need to join 1+Pl to 1Pl in analysis_dict()
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        elif summary["S"]["Pers"] == "2" and analysis_in[suffixes][i][0] == "1Pl": #need to join 1+Pl to 1Pl in analysis_dict()
            summary["S"]["Num"] = "1Pl"
            analysis_in[suffixes][i][1] = True
        elif summary["S"]["Pers"] == "2" and analysis_in[suffixes][i][0] == "2Pl": #need to join 2+Pl to 2Pl in analysis_dict()
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        elif summary["S"]["Pers"] == "3" and analysis_in[suffixes][i][0] == "2Pl": #need to join 2+Pl to 2Pl in analysis_dict()
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        #end prefix information obtained}
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "1Pl": #need to join 1+Pl to 1Pl in analysis_dict()
            summary["S"]["Pers"] = "1"
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "21Pl": #need to join 2+1+Pl to 21Pl in analysis_dict()
            summary["S"]["Pers"] = "2"
            summary["S"]["Num"] = "1Pl"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "2Pl": #need to join 2+Pl to 2Pl in analysis_dict()
            summary["S"]["Pers"] = "2"
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "3Pl": #need to join 3+Pl to 3Pl in analysis_dict()
            summary["S"]["Pers"] = "3"
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "1":
            summary["S"]["Pers"] = "1"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "2":
            summary["S"]["Pers"] = "2"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "3": #VAI independent/conjunct, VTI conjunct
            summary["S"]["Pers"] = "3"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "0": #VTIs/VTAs still not covered
            summary["S"]["Pers"] = "0"
            analysis_in[suffixes][i][1] = True
        elif (not summary["S"]["Pers"]) and analysis_in[suffixes][i][0] == "0Pl": #VTIs/VTAs still not covered
            summary["S"]["Pers"] = "0"
            summary["S"]["Num"] = "Pl"
            analysis_in[suffixes][i][1] = True
    summary["Else"] = [y[0] for x in analysis_in for y in analysis_in[x] if not y[1]]
    return summary

def analysis_dict(analysis_string):
    adict = {"prefix":[], "derivation": [], "preforms":[], "suffixes":[], "clitics":[]}
    adict["clitic"].append([re.search("\+dash\+Adv", analysis_string)[0], False])
    analysis_string = analysis_string.strip("+dash+Adv") #this only needs to happen after clitics are checked and before derivation/suffixes are inspected, stuck with post-clitics
    adict["prefix"].append([re.search("(^[123X])?", analysis_string)[0], False])
    adict["derivation"] = [[x, False] for x in re.search("POSTAGS(.*POSTAGS)?", analysis_string)[0].split("+")] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
    adict["preforms"] = [[x, False] for x in re.search("(PV|PN|PA[^\+]*\+)*", analysis_string)[0].split("+")]
    adict["suffixes"] = list(reversed([["".join(reversed(x)), False] for x in re.search(".*(?!REVPOSTAGS)", "".join(reversed(analysis_string)))[0].split("+")])) #reading everything backwards then re-reversing it (in order to avoid non-fixed width negative lookbehind
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




