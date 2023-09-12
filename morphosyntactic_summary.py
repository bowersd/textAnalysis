#goal: provide a user friendly description of morphosyntactic analysis

#read in morphosyntax-user friendly pairs to dict (tuple if you want reversible)
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


