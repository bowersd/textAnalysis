import os
import argparse
import parse
import readwrite as rw
import postprocess as pst
import preprocess as pre
import engdict as eng

def update(holder, key, *vals):
    """
    update a dictionary of glossary information with key, vals
    first val is freq
    last val is intended as list of token plus info
    """
    if key not in holder:
        holder[key] = [x for x in vals]
    else:
        holder[key][0] += vals[0]
        holder[key][-1] += [w for w in vals[-1] if w not in holder[key][-1]]

def glossify(fst_file, spellrelax_file, fst_format, pos_regex, gdict, text_in):
    holder = {"zzzz-UnparsedWords":[0, "", "", []]}
    #bad form below, data should already be correctly formatted see readwrite.burn_metadata()
    #tin = rw.readin(text_in)
    #tin.pop(0) #burning corpus info
    #tin.pop(0) #burning text info
    p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, *[x for s in text_in for x in pre.sep_punct(s.lower()).split()]).decode()) #get all analyses of every word
    cnt = 0
    for s in text_in:
        cnt += 1
        for w in pre.sep_punct(s.lower()).split():
            best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
            lem = pst.extract_lemma(p[w][best][0], pos_regex)
            #if not lem: #kludge until I can figure out how to manage capitalization differences on the FST side the way the giellatekno people do
            #    w = w.lower()
            #    p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, w).decode())
            #    best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
            #    lem = pst.extract_lemma(p[w][best][0], pos_regex)
            if lem and lem not in holder:
                try: gloss = gdict[lem]
                except KeyError: gloss = "definition currently unavailable"
                if w != lem or pst.extract_regex(p[w][best][0], pos_regex) not in ["+Adv", "+Ipc", "+Pron+NA", "+Pron+NI", "+Qnt", "+Interj"]: update(holder, lem, *[1, pst.extract_regex(p[w][best][0], pos_regex), gloss, [(w, p[w][best][0])]])
                else: update(holder, lem, *[1, pst.extract_regex(p[w][best][0], pos_regex), gloss, []])
                #holder[lem] = [1, pst.extract_regex(p[w][best][0], pos_regex), gloss, [w]]
            elif lem in holder: update(holder, lem, *[1, [(w, p[w][best][0])]])
            elif spellrelax_file:
                r = pst.parser_out_string_dict(parse.parse(os.path.expanduser(spellrelax_file), fst_format, w).decode())
                best = pst.disambiguate(pst.min_morphs(*r[w]), pst.min_morphs, *r[w])
                lem = pst.extract_lemma(r[w][best][0], pos_regex)
                if lem and lem not in holder:
                    try: gloss = gdict[lem]
                    except KeyError: gloss = "definition currently unavailable"
                    if w != lem or pst.extract_regex(r[w][best][0], pos_regex) not in ["+Adv", "+Ipc", "+Pron+NA", "+Pron+NI", "+Qnt", "+Interj"]: update(holder, lem, *[1, pst.extract_regex(r[w][best][0], pos_regex), gloss, [(w, r[w][best][0]+"SPELLING RELAXED")]])
                    else: update(holder, lem, *[1, pst.extract_regex(r[w][best][0], pos_regex), gloss, []]) 
                    #holder[lem] = [1, pst.extract_regex(p[w][best][0], pos_regex), gloss, [w]]
                elif lem in holder: update(holder, lem, *[1, [(w, r[w][best][0]+"SPELLING RELAXED")]]) 
                else:  
                    update(holder, "zzzz-UnparsedWords", *[1, [(w,)]]) #no lemma
            else:  
                update(holder, "zzzz-UnparsedWords", *[1, [(w,)]]) #no lemma
    return holder

def flag_cap(*words):
    return any([w.lower() != w for w in words])

def flag2string(flag):
    if flag: return "*"
    return ""

def adjust_cap(*vals):
    """collapse tokens that differ in capitalization"""
    h = []
    for v in vals:
        if len(v) == 1: w = (v[0].lower(),)
        else: w = (v[0].lower(), v[1])
        if w not in h: h.append(w)
    return h
    
def stringify(**entries):
    holder = []
    #left = 0 
    #sec = 0
    #for e in entries:
    #    if len(e) > left: left = len(e)
    #    for w in adjust_cap(*entries[e][-1]): 
    #        if len(w[0]) > sec: sec = len(w[0])
    for e in sorted(entries):
        #consider formatting for nicer columns
        holder.append('\t'.join([flag2string(flag_cap(*[v[0] for v in entries[e][-1]]))+e,str(entries[e][0])]+[x.strip('+') for x in entries[e][1:-1]]))
        #holder.append(f"{flag2string(flag_cap(*[v[0] for v in entries[e][-1]]))+e:{left}}  {str(entries[e][0])}  {'  '.join([x.strip('+') for x in entries[e][1:-1]])}")
        #holder.append("    ".join([flag2string(flag_cap(*[v[0] for v in entries[e][-1]]))+e, str(entries[e][0])] + entries[e][1:-1]))
        for w in adjust_cap(*sorted(entries[e][-1])): holder.append('\t'+'\t'.join(w))
        #for w in adjust_cap(*entries[e][-1]): holder.append(f"{' '*((left//2))}{w[0]:{sec}}  {'  '.join(w[1:])}")
            #holder.append("    "+"    ".join(w))
    return holder

abbreviations = {
        "VAI": "Intransitive Verb with an Animate subject",
        "VAIO": "'Intransitive' Verb with an Animate subject and an Object",
        "VII": "Intransitive Verb with an Inanimate subject",
        "VTA": "Transitive Verb with an Animate object",
        "VTI": "Transitive Verb with an Inanimate subject",
        "Cnj": "Conjunct order (used in questions, relative clauses, if-then statements)",
        "Itr": "Iterative (marks repeated actions)",
        "Imp": "Imperative order (used in commands)",
        "Pcp": "Participle (relative clauses: they who X)",
        "1": "First person  (I/me/my/we/us/our)",
        "2": "Second person  (you/your/youse/youse's)",
        "3": "Third person  (he/she/him/her/his/hers/they/them/theirs)",
        "4": "Obviation  ('fourth person', a way of distinguishing third persons from each other)",
        "X": "Unspecified person (when prefixed: someone's X, when suffixed, I was X'ed (by someone), in Nishnaabemwin 'by someone' cannot be added)",
        "0": "Inanimate",
        "Neg": "Negative (not)",
        "Pl": "Plural (more than one)",
        "Prt": "Preterit (in verbs: X has been completed, in nouns: X is broken/deceased/no longer)",
        "Dub": "Dubitative (speaker doubts/needs to infer that X)",
        "Voc": "Vocative (calling to X)",
        "Loc": "Locative (on/in/at X)",
        "Redup": "Reduplication (indicates intensity, repetitiveness, plurality of subject, etc)",
        "ThmDir": "Direct theme [Y Xs him/her] ('-aa', marks third person object for VTAs (prefix is subject), often called a 'direct non-local theme')",
        "Thm2": "Second person theme [you X me] ('-i' (often deleted), marks second person subject and first person object for VTAs (prefix is subject), often called a 'direct local theme')",
        "Thm1Pl": "First person plural theme [we X you] ('-igoo', marks first person plural subject and second person object for VTAs (prefix is object), often called an 'indirect local theme')",
        "Thm1Sg": "First person singular theme [I X you] ('-in', marks first person singular subject and second person object for VTAs (prefix is object), often called an 'indirect local theme')",
        "ThmInv": "Inverse theme [he/she/it Xs Y] ('-igo/ig', marks third person/inanimate subject for VTAs (prefix is object), often called an 'indirect local theme')",
        "ThmPas": "Passive theme [Y is Xed] ('-igoo/aa/ind', marks passive voice (prefix is patient) for VAIs derived from VTAs, often called an 'unspecified actor theme')",
        "Thm1": "Conjunct order first person theme [Y Xs me] ('-i', marks first person object for conjunct order VTAs)",
        "Thm2a": "Conjunct order second person theme A [I X you] ('-inin', marks second person object, non-third person subject for conjunct order VTAs)",
        "Thm2b": "Conjunct order second person theme B [He/she Xs you] ('-ik', marks second person object, third person subject for conjunct order VTAs)",
        "ThmNul": "Conjunct order third person theme [I/you X him/her] ('--', marks third person object, non-third person subject for conjunct order VTAs)",
        "Rflx": "Reflexive (A does X to A's self)",
        "Rcpl": "Reciprocal (A and B do X to each other)",
        "NA": "Animate Noun",
        "NI": "Inanimate Noun",
        "NAD": "Dependent Animate Noun (obligatorily posessed)",
        "NID": "Dependent Inanimate Noun (obligatorily posessed)",
        "Con": "Contemptive (dislike/disdain/teasing for X)",
        "Dim": "Diminutive (cuteness/smallness/affection for X)",
        "Pej": "Pejorative (stronger dislike for X)",
        "ThmPos": "Posessive theme (marks some possessed nouns)",
        "Imm": "Immediate ('do it now!')",
        "Del": "Delayed ('do it in a while!')",
        "Conj": "Conjunctions (and, or, but)",
        "Interj": "Interjections (ah!)",
        "Num": "Numerals (1,2,3...)",
        "Pron": "Pronouns (I/you/that...)",
        "Ipc": "Independent particle (the 'other' category)",
        "Qnt": "Quantifiers (some/all/most...)",
        "Adv": "Adverbials",
        "PV/CCNJ": "Changed conjunct form",
        #"PV/...": "A preverb"
        }

def mk_abbrev_key(**glossary):
    h = []
    for lemma in glossary:
        if lemma != 'zzzz-UnparsedWords':
            for token in glossary[lemma][-1]:
                #split on lemma, remerge, split on +
                for tag in "".join(token[1].split(lemma)).split("+"):
                    if tag not in h:
                        h.append(tag)
    return sorted(h)

def stringify_abbrev_key(*encountered, **mapping):
    h = []
    for x in encountered:
        if x in mapping: h.append('\t'.join([x, mapping[x]]))
        else: h.append('\t'.join([x, 'no current elaboration']))
    return ["Abbreviation Key:"]+sorted(h)


def main(fst_file, spellrelax_file, fst_format, regex_file, gloss_file, output, unique, *texts_in):
    gdict = eng.mk_glossing_dict(*rw.readin(gloss_file)) 
    pos_regex = "".join(rw.readin(regex_file))
    if unique:
        for t in texts_in: 
            addr = t.split("/")
            g = glossify(fst_file, spellrelax_file, fst_format, pos_regex, gdict, rw.burn_metadata(2, *rw.readin(t)))
            rw.writeout("/".join(addr[:-1])+'/'+(output+".").join(addr[-1].split(".")), *stringify(**g)+stringify_abbrev_key(*mk_abbrev_key(**g), **abbreviations))
    else: 
        gholder = {}
        for t in texts_in:
            sub = glossify(fst_file, spellrelax_file, fst_format, pos_regex, gdict, rw.burn_metadata(2, *rw.readin(t)))
            for x in sub:
                update(gholder, x, *sub[x])
        #path = "/".join(t.split("/")[:-1])+"/"
        #rw.writeout("".join([path,output,".txt"]), *stringify(**gholder))
        rw.writeout(output, *stringify(**gholder)+stringify_abbrev_key(*mk_abbrev_key(**gholder), **abbreviations))

def parseargs():
    parser = argparse.ArgumentParser()

    parser.add_argument("fst_file", help="file path to primary analyser")
    parser.add_argument("fst_format", help="hfst or xfst")
    parser.add_argument("pos_regex", help="regexes for part of speech")
    parser.add_argument("gloss_file", help="file path to translation dictionary")
    parser.add_argument("-s", "--spellrelax", dest = "spellrelax_file", nargs = "?", help="file path to  analyser with spelling conventions relaxed", default="")
    parser.add_argument("-u", "--unique", dest="u", action="store_true", help="whether to make unique glossaries for each input file")
    parser.add_argument("-o", "--output", dest="o", nargs="?", help="file name/suffix without filetype extension", default="Glossary")
    parser.add_argument("input_files", help="raw text file paths", nargs="+")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseargs()
    main(args.fst_file, args.spellrelax_file, args.fst_format, args.pos_regex, args.gloss_file, args.o, args.u, *args.input_files)
