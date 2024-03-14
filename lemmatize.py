import code
import os
import argparse
import re
import json
import json_encoder
import parse
import readwrite as rw
import postprocess as pst
import preprocess as pre
import engdict as eng
import alg_morphological_summary as algsum

#def analyze_word(fst_file, fst_format, pos_regex, gdict, w):
#    p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, w).decode())
#    best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
#    lem = pst.extract_lemma(p[w][best][0], pos_regex)
#    if lem: return [p[w][best][0], lem]
#    else: return ["?", "?"]
#
#def analyze_sent(fst_file, fst_format, *sent):
#    analysis = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, *sent).decode())
#    analyses = []
#    for w in sent: analyses.append(analysis[w][pst.disambiguate(pst.min_morphs(*analysis[w]), pst.min_morphs, *analysis[w])][0])
#    return analyses

def analyze_text(fst_file, fst_format, *text_in):
    analysis = []
    analyses = parse.parse_native(os.path.expanduser(fst_file), *[x for s in text_in for x in pre.sep_punct(s.lower()).split()]) #get all analyses of every word
    #analyses = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, *[x for s in text_in for x in pre.sep_punct(s.lower()).split()]).decode()) #get all analyses of every word
    #for s in text_in: analysis.append([analyses[w][pst.disambiguate(pst.min_morphs(*analyses[w]), pst.min_morphs, *analyses[w])][0] for w in pre.sep_punct(s.lower()).split()]) #look up each word's analyses and disambiguate ... better: disambiguate while the analyses are being computed ... though the parse() function should not be troubled with disambiguation questions. modular=siloed?
    performance = [0, 0] #hits, misses
    for s in text_in: 
        a = []
        for w in pre.sep_punct(s.lower()).split():
            best = analyses[w][pst.disambiguate(pst.min_morphs(*analyses[w]), pst.min_morphs, *analyses[w])][0]
            a.append(best)
            performance[int(best.endswith("+?"))] += 1 
        analysis.append(a)
    print("hit rate:", str(round(performance[0]/(performance[1]+performance[0]), 3)*100)+"%", "hits:", performance[0], "misses:", performance[1])
    return analysis

def lemmatize(pos_regex, *analysis):
    return [pst.extract_lemma(a, pos_regex) for a in analysis]

def drop_vals(vector, *values):
    return [x for x in vector if x not in values]

def interlinearize(fst_file, fst_format, pos_regex, gdict, text_in, trans_in):
    holder = []
    for i in range(len(text_in)):
        sub = [[],[],[], [], [], [trans_in[i]]]
        for w in pre.sep_punct(text_in[i]).split():
            w=w.lower()
            #p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, w).decode())
            p = parse.parse_native(os.path.expanduser(fst_file), fst_format, w)
            best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
            lem = pst.extract_lemma(p[w][best][0], pos_regex)
            try: gloss = gdict[lem]
            except KeyError: 
                gloss = "NODEF" 
            abbr = re.search('(\w*\s*){0,4}',gloss)[0].lstrip(" 1")
            if lem: 
                sub[0].append(w)
                sub[1].append(p[w][best][0])
                sub[2].append(lem)
                sub[3].append(abbr)
                if (w, gloss) not in sub[4]: sub[4].append((w, gloss))
            else: 
                sub[0].append(w)
                sub[1].append("?")
                sub[2].append("?")
                sub[3].append("?")
        holder.append(sub)
    return holder

def name_lists(names, *lists):
    named_lists = {}
    for i in range(len(names)): named_lists[names[i]] = lists[i]
    return named_lists

def pad(*lists_of_strings):
    #lists must be same length!
    nu_lists = []
    padlen = []
    for i in range(len(lists_of_strings)):
        nu = []
        for j in range(len(lists_of_strings[i])): #pad items in list to max length at their indices
            if not i: padlen.append(max([len(lists_of_strings[k][j]) for k in range(len(lists_of_strings))]))
            nu.append(lists_of_strings[i][j]+" "*(padlen[j]-len(lists_of_strings[i][j])))
        nu_lists.append(nu)
    return nu_lists

def unpad(*lists_of_strings):
    nu_lists = []
    for x in lists_of_strings: nu_lists.append([y.strip() for y in x])
    return nu_lists

def atomic_json_dump(filename, names, lists):
    with open(filename, 'w') as file_out:
        json.dump([{names[j]:lists[j][i] for j in range(len(lists))} for i in range(len(lists[0]))], file_out, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent=1) 

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fst_file", help="file path to primary analyser")
    parser.add_argument("fst_format", help="hfst or xfst")
    parser.add_argument("pos_regex", help="regexes for part of speech")
    parser.add_argument("gloss_file", help="file path to translation dictionary")
    parser.add_argument("text", help="file path to target text")
    parser.add_argument("trans", help="file path to text translation")
    parser.add_argument("-o", "--output", dest="o", nargs="?", help="file name/suffix without filetype extension", default="Lemmatization")
    parser.add_argument("-a", "--analysis", dest="a", nargs="?", help="name of analysis file", default="")
    return parser.parse_args()

def human_readable(fst_file, fst_format, regex_file, gloss_file, text, trans, output):
    gdict = eng.mk_glossing_dict(*rw.readin(gloss_file))
    pos_regex = "".join(rw.readin(regex_file))
    with open(output, 'w') as file_out:
        l = 0
        for inter in  interlinearize(fst_file, fst_format, pos_regex, gdict, text, trans):
            file_out.write(str(l)+'\n')
            l += 1
            wrap = 0
            mainline = []
            subline = [[],[],[],[]]
            for i in range(len(inter[0])):
                m = max(len(inter[0][i]), len(inter[1][i]), len(inter[2][i]), len(inter[3][i]))
                if wrap + m > 200: #wrapping at less than 267 (full screen) to allow lines to be edited
                    wrap = 0
                    mainline.append(subline)
                    subline = [[], [], [], []]
                wrap += m+1 #+1 because we add a space between words
                subline[0].append(inter[0][i]+(" "*(m-len(inter[0][i]))))
                subline[1].append(inter[1][i]+(" "*(m-len(inter[1][i]))))
                subline[2].append(inter[2][i]+(" "*(m-len(inter[2][i]))))
                subline[3].append(inter[3][i]+(" "*(m-len(inter[3][i]))))
                #inter[0][i] = inter[0][i]+(" "*(m-len(inter[0][i])))
                #inter[1][i] = inter[1][i]+(" "*(m-len(inter[1][i])))
                #inter[2][i] = inter[2][i]+(" "*(m-len(inter[2][i])))
                #inter[3][i] = inter[3][i]+(" "*(m-len(inter[3][i])))
            else: mainline.append(subline)
            for sl in mainline:
                file_out.write(" ".join(sl[0])+'\n') 
                file_out.write(" ".join(sl[1])+'\n') 
                file_out.write(" ".join(sl[2])+'\n') 
                file_out.write(" ".join(sl[3])+'\n') 
                file_out.write('\n')
            file_out.write(inter[5][0]+'\n') 
            file_out.write('\n')
            for x in sorted(inter[4]): file_out.write("\t".join(x)+'\n') 
            file_out.write('#######'*3)
            file_out.write('\n')
            file_out.write('\n')

if __name__ == "__main__":
    args = parseargs()
    #human_readable(args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, rw.burn_metadata(2, *rw.readin(args.text)), rw.readin(args.trans), args.o) #this throws a sigsev error now
    #for generating lemmata from rand files
    pos_regex = "".join(rw.readin(args.pos_regex))
    if args.a: 
        analysis = pst.parser_out_string_dict("\n".join(rw.readin(args.a)))
        #for a in sorted(analysis): print(a, analysis[a])
    full = {
            "sentenceID":[],
            "speakerID":[],
            "speaker_text_num":[],
            "speaker_text_sent_num":[],
            "sentence":[],
            "chunked":[],
            "edited":[],
            "lemmata":[],
            "m_parse_hi":[],
            "m_parse_lo":[],
            #"fiero_orth":[], #new machine with UR as top, then run UR back down to SRs minus corb spelling
            #"unsyncopated":[], #new machine with UR as top, then run UR back down to SRs minus syncope
            "tiny_gloss":[],
            "english":[],
            }
    names = [ #ordering for easy reading
            "sentenceID",
            "speakerID",
            "speaker_text_num",
            "speaker_text_sent_num",
            "chunked",
            "edited",
            "m_parse_lo",
            "m_parse_hi",
            "lemmata",
            "tiny_gloss",
            "english",
            "sentence",
            #"fiero_orth", #new machine with UR as top, then run UR back down to SRs minus corb spelling
            #"unsyncopated", #new machine with UR as top, then run UR back down to SRs minus syncope
            ]
    with open(args.text) as f:
        for line in f:
            split = line.strip().split('\t')
            full["speakerID"].append(split[0])
            full["speaker_text_num"].append(split[1])
            full["speaker_text_sent_num"].append(split[2])
            full["sentence"].append(split[3])
            full["chunked"].append(pre.sep_punct(split[3]).split())
            full["edited"].append(pre.sep_punct(split[3]).split())
            full["english"].append(split[4])
            full["sentenceID"].append(split[5])
            if args.a:
                full["m_parse_lo"].append([])
                for w in pre.sep_punct(split[3].lower()).split(): 
                    full["m_parse_lo"][-1].append(analysis[w][pst.disambiguate(pst.min_morphs(*analysis[w]), pst.min_morphs, *analysis[w])][0])
    if not args.a: full["m_parse_lo"] = analyze_text(args.fst_file, args.fst_format, *full["sentence"])
    gdict = eng.mk_glossing_dict(*rw.readin(args.gloss_file))
    for i in range(len(full["m_parse_lo"])): 
        lem = [x if x else "?" for x in lemmatize(pos_regex, *full["m_parse_lo"][i])] #filter on "if x" to leave out un analyzed forms
        summ = [algsum.formatted(algsum.interpret(algsum.analysis_dict(x))) if algsum.analysis_dict(x) else "?" for x in full["m_parse_lo"][i] ] # filter on "if algsum.analysis_dict(x)" to leave out unanalyzed forms
        tinies = []
        for l in lem:
            try: gloss = gdict[l]
            except KeyError: 
                gloss = "NODEF" 
            tinies.append(re.search('(\w*\s*){0,4}',gloss)[0].lstrip(" 1"))
        padded = pad(full["chunked"][i], lem, summ, tinies, full["m_parse_lo"][i])
        full["chunked"][i] = " ".join(padded[0])
        full["edited"][i] = " ".join(padded[0])
        full["lemmata"].append(" ".join(padded[1]))
        full["m_parse_hi"].append(" ".join(padded[2]))
        full["tiny_gloss"].append(" ".join(padded[3]))
        full["m_parse_lo"][i] = " ".join(padded[4])
    #    full["chunked"][i] = padded[0]
    #    full["edited"][i] = padded[0]
    #    full["lemmata"].append(padded[1])
    #    full["m_parse_hi"].append(padded[2])
    #    full["tiny_gloss"].append(padded[3])
    #    full["m_parse_lo"][i] = padded[4]
    #by_sent = [{x:full[x][i] for x in names} for i in range(len(full["sentenceID"]))]
    #code.interact(local=locals())
    with open(args.o, 'w') as fo:
        json.dump([{x:full[x][i] for x in names} for i in range(len(full["sentenceID"]))], fo, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent=1)
    ##atomic_json_dump(args.o, names, [[d[5] for d in data_in], [d[3] for d in data_in], lemmata, summaries])
    ##needed args: (args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, args.text, args.trans, args.o) args.trans is required but will be ignored for Rand sentences
