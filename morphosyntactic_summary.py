#goal: provide a user friendly description of morphosyntactic analysis

#read in morphosyntax-user friendly pairs to dict (tuple if you want reversible)
    #use left and right delimiters to mark where root/stem/lexical information goes in the morphosyntactic description (msd)
#extract morphosyntax portion of analyzed word -> delimit where lexical material is
#check morphosyntax against reference unit, obtain user friendly translation
#check lexical material against gloss mapping (if available, else, it will just be the lemma)

import re

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
    return gloss_dict[re.search(delimit_left+"\([^"+delimit_right+"]*\)"+delimit_right, analysis)[1]]
