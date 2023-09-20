import sys
import re
import argparse
import engdict as eng
import readwrite as rw
import glossarygen

def contextualize(target, source, length, *words):
    h = []
    for i in range(len(words)):
        if target == words[i].strip(",.][?!:") and i >= length: h.append([words[i-length:i], words[i], words[i+1:i+length+1], source])
        elif target == words[i].strip(",.][?!:") and i < length: h.append([words[0:i], words[i], words[i+1:i+length+1], source])
    return h

def align_contexts(*contexts):
    h = []
    lef = 0
    cen = 0
    rig = 0
    for c in contexts:
        if len(" ".join(c[0])) > lef: lef = len(" ".join(c[0]))
        if len(" ".join(c[1])) > cen: cen = len(" ".join(c[1]))
        if len(" ".join(c[2])) > rig: rig = len(" ".join(c[2]))
    for c in contexts: h.append(f"{' '.join(c[0]):>{lef}}    {c[1]:{cen}}    {' '.join(c[2]):>{rig}}    {c[3]}")
    return h

def full_context(texts, titles, length, lemmata):
    #assuming lemmata as in glossarygen.glossify() with lemma:[freq, pos, gloss, [(token, analysis)]]
    #assuming texts as [[text1]...]
    h = []
    for lemma in sorted(lemmata):
        contexts = []
        for token in lemmata[lemma][-1]:
            for i in range(len(texts)):
                for sent in texts[i]:
                    if token[0] in sent: contexts.extend(contextualize(token[0], titles[i], length, *sent.split(" ")))
        h.append(" ".join([lemma, lemmata[lemma][1], lemmata[lemma][2]]))
        h.extend(align_contexts(*contexts))
        h.append("")
    return h


if __name__ == "__main__":
    #todo: move this to a wrapper that makes both the glossary and its contextualization with one function call (with a "make context" flag raised), use argparse instead of sys.argv[]
    args = glossarygen.parseargs()
    text = []
    titles = []
    for t in args.input_files: 
        titles.append(t.split('/')[-1])
        text.append(rw.burn_metadata(2, *rw.readin(t)))
    merged = []
    for t in text: merged.extend(t)
    glossary = glossarygen.glossify(args.fst_file, args.spellrelax_file, args.fst_format, "".join(rw.readin(args.pos_regex)), eng.mk_glossing_dict(*rw.readin(args.gloss_file)), merged) #fst, spellrelaxfst, fstformat, regexfile, glossfile, mega text
    #for g in glossary: print(g, glossary[g])
    rw.writeout("glossary_with_contexts.txt", *full_context(text, titles, 5, glossary)) #todo: don't hardcode output title, make it be derivative of whatever the glossary is named, else a sensible default
