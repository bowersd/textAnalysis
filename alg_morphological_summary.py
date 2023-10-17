import yaml
import re
import sys

import lemmatize as lem
import engdict as eng
import readwrite as rw

def interpret(analysis_in):
    summary = {"S":None, "O":None, "DerivChain":None, "Head":None, "Order":None, "Neg":None, "Mode":None, "Else": []}
    summary["Else"] = analysis_in
    return summary

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




