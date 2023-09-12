#goal: provide a user friendly description of morphosyntactic analysis

#read in morphosyntax-user friendly pairs to dict (tuple if you want reversible)
    #use left and right delimiters to mark where root/stem/lexical information goes in the morphosyntactic description (msd)
#extract morphosyntax portion of analyzed word -> delimit where lexical material is
#check morphosyntax against reference unit, obtain user friendly translation
#check lexical material against gloss mapping (if available, else, it will just be the lemma)

import re
import sys

def delimit_lex(analysis, delimit_left, delimit_right, regex):
    #regex should match lexical material, possibly by referring to POS tags that are near lexical material
   lex = delimit_left+re.search(regex, analysis)[0]+delimit_right #does not allow for discontinuous lexical material (aka very low level analysis of Arabic?)
   return lex.join(re.split(regex, analysis))

def delimit_lex_discontinuous(analysis, delimit_left, delimit_right, regex):
    lex = lambda x: delimit_left+x.group(0)+delimit_right
    return re.sub(regex, lex, analysis)

def translate_msd(analysis, delimit_left, delimit_right, **msd_trans):
    return msd_trans[re.sub(delimit_left+"[^"+delimit_right+"]*"+delimit_right, delimit_left+delimit_right, analysis)]

def gloss_lex(analysis, delimit_left, delimit_right, **gloss_dict):
    return gloss_dict["-".join(re.findall("(?<="+delimit_left+")"+"[^"+delimit_right+"]*(?="+delimit_right+")", analysis))] #assumes discontinuous lexical material is eventually written together with hyphens
    #return gloss_dict[re.search(delimit_left+"\([^"+delimit_right+"]*\)"+delimit_right, analysis)[1]] #won't handle discontinuous lexical material ... perhaps findall()

def read_in_trans(sep, filename):
    h = {}
    with open(filename) as file_in:
        for line in file_in:
            entry = line.strip().split(sep)
            h[entry[0]] = entry[1]
    return h

def write_out_data(data, filename):
    with open(filename, 'w') as file_out:
        pass

if __name__ == "___main___":
    msd_trans = read_in_trans(sys.argv[1], sys.argv[2])
    lex_trans = read_in_trans(sys.argv[1], sys.argv[3])
    data = read_in_data(sys.argv[4])
    delimit_left = sys.argv[5]
    delimit_right = sys.argv[6]
    lex_id_regex = sys.argv[7] #may need to read this in from a file
    #imagining one word per line, but may be one sentence per line
    glosses = []
    msds = []
    for d in data:
        e = delimit_lex_discontinuous(d, delimit_left, delimit_right, lex_id_regex)
        friendly_msd = translate_msd(e, delimit_left, delimit_right, **msd_trans)
        gloss = gloss_lex(e, delimit_left, delimit_right, **lex_trans)
