import os
import argparse
import parse
import re
import readwrite as rw
import postprocess as pst
import preprocess as pre
import engdict as eng
from grammar_codes import abbreviations

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

def glossify(fst_file, spellrelax_file,  pos_regex, gdict, drop_punct, corrections, text_in): #fst_format used to be the third argument
    holder = {"zzzz-UnparsedWords":[0, "", "", []]}
    #bad form below, data should already be correctly formatted see readwrite.burn_metadata()
    #tin = rw.readin(text_in)
    #tin.pop(0) #burning corpus info
    #tin.pop(0) #burning text info
    p = parse.parse_native(os.path.expanduser(fst_file), *[x for s in text_in for x in pre.sep_punct(s.lower(), drop_punct).split()]) #get all analyses of every word
    #p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, *[x for s in text_in for x in pre.sep_punct(s.lower(), drop_punct).split()]).decode()) #get all analyses of every word
    cnt = 0
    for s in text_in:
        cnt += 1
        for w in pre.sep_punct(s.lower(), drop_punct).split():
            best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
            lem = pst.extract_lemma(p[w][best][0], pos_regex)
            if w in corrections:
                best = 0
                lem = pst.extract_lemma(corrections[w][1], pos_regex) #word, edited word, analysis, comment
                p[w] = [(corrections[w][1], 0.0)]
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
                r = parse.parse_native(os.path.expanduser(spellrelax_file), w)
                #r = pst.parser_out_string_dict(parse.parse(os.path.expanduser(spellrelax_file), fst_format, w).decode())
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


def main(fst_file, spellrelax_file, regex_file, gloss_file, drop_punct, corrections, output, unique, *texts_in):
    gdict = eng.mk_glossing_dict(*rw.readin(gloss_file)) 
    pos_regex = "".join(rw.readin(regex_file))
    cdict = {}#x[1]:re.split(" +", x) for x in rw.readin(corrections)}
    if corrections: 
        for c in rw.readin(corrections):
            s  = re.split(" +", c)
            cdict[s[2]] = s[3:]
    if unique:
        for t in texts_in: 
            addr = t.split("/")
            g = glossify(fst_file, spellrelax_file,  pos_regex, gdict, drop_punct, cdict, rw.burn_metadata(2, *rw.readin(t)))
            rw.writeout("/".join(addr[:-1])+'/'+(output+".").join(addr[-1].split(".")), *stringify(**g)+stringify_abbrev_key(*mk_abbrev_key(**g), **abbreviations))
    else: 
        gholder = {}
        for t in texts_in:
            sub = glossify(fst_file, spellrelax_file,  pos_regex, gdict, drop_punct, cdict, rw.burn_metadata(2, *rw.readin(t)))
            for x in sub:
                update(gholder, x, *sub[x])
        #path = "/".join(t.split("/")[:-1])+"/"
        #rw.writeout("".join([path,output,".txt"]), *stringify(**gholder))
        rw.writeout(output, *stringify(**gholder)+stringify_abbrev_key(*mk_abbrev_key(**gholder), **abbreviations))

def parseargs():
    parser = argparse.ArgumentParser()

    parser.add_argument("fst_file", help="file path to primary analyser")
    #parser.add_argument("fst_format", help="hfst or xfst")
    parser.add_argument("pos_regex", help="regexes for part of speech")
    parser.add_argument("gloss_file", help="file path to translation dictionary")
    parser.add_argument("-c", "--corrections_file", dest = "c", nargs = "?", default = "", help="file with hand corrections")
    parser.add_argument("-s", "--spellrelax", dest = "spellrelax_file", nargs = "?", help="file path to  analyser with spelling conventions relaxed", default="")
    parser.add_argument("-u", "--unique", dest="u", action="store_true", help="whether to make unique glossaries for each input file")
    parser.add_argument("-d", "--drop-punct", dest="d", action="store_true", help="whether to drop punctuation instead of separating it")
    parser.add_argument("-o", "--output", dest="o", nargs="?", help="file name/suffix without filetype extension", default="Glossary")
    parser.add_argument("input_files", help="raw text file paths", nargs="+")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseargs()
    main(args.fst_file, args.spellrelax_file,  args.pos_regex, args.gloss_file, args.d, args.c, args.o, args.u, *args.input_files)
