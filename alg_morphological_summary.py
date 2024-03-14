import pyyaml
import re

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
        lr = s.split(sep) #sep can be <> for compiling list of relevant tags, or lemma for prepping an analysis for summary
        for pre in re.findall("[^\+]*\+", lr[0]):
            if pre not in h: h.append(pre)
        for suff in re.findall("\+[^\+]*", lr[1]):
            if suff not in h: h.append(suff)
    return h
