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

def analyze_text(fst_file, fst_format, drop_punct, *text_in):
    analysis = []
    analyses = parse.parse_native(os.path.expanduser(fst_file), *[x for s in text_in for x in pre.sep_punct(s.lower(), drop_punct).split()]) #get all analyses of every word
    #analyses = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, *[x for s in text_in for x in pre.sep_punct(s.lower()), drop_punct.split()]).decode()) #get all analyses of every word
    #for s in text_in: analysis.append([analyses[w][pst.disambiguate(pst.min_morphs(*analyses[w]), pst.min_morphs, *analyses[w])][0] for w in pre.sep_punct(s.lower(), drop_punct).split()]) #look up each word's analyses and disambiguate ... better: disambiguate while the analyses are being computed ... though the parse() function should not be troubled with disambiguation questions. modular=siloed?
    performance = [0, 0.01] #hits, misses
    for s in text_in: 
        a = []
        for w in pre.sep_punct(s.lower(), drop_punct).split():
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

def interlinearize(fst_file, fst_format, pos_regex, gdict, drop_punct, text_in, trans_in):
    holder = []
    p = parse.parse_native(os.path.expanduser(fst_file), *[x for s in text_in for x in pre.sep_punct(s.lower(), drop_punct).split()])
    for i in range(len(text_in)):
        sub = [[],[],[], [], [], [trans_in[i]]]
        for w in pre.sep_punct(text_in[i], drop_punct).split():
            w=w.lower()
            #p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, w).decode())
            #p = parse.parse_native(os.path.expanduser(fst_file), fst_format, w)
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

def remerge_punct(*lists_of_strings):
    pass

def unpad(*lists_of_strings):
    nu_lists = []
    for x in lists_of_strings: nu_lists.append([y.strip() for y in x])
    return nu_lists

def atomic_json_dump(filename, names, lists):
    with open(filename, 'w') as file_out:
        json.dump([{names[j]:lists[j][i] for j in range(len(lists))} for i in range(len(lists[0]))], file_out, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent=1) 

def e_ccnj_ambiguous(analyzer, string):
    if string.startswith("e-"): #attempt analysis without the hyphen, if successful, return true
        print(string)
        ccnj = conserve_innovation(string)
        if not parse.parse_native(os.path.expanduser(analyzer), ccnj)[ccnj][0][0].endswith('+?'): return True
    return False


def conserve_innovation(target, string):
    return target[:len(target)-1]+string[len(target):] #be sure to include hyphen in target

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fst_file", help="file path to primary analyser")
    parser.add_argument("fst_format", help="hfst or xfst")
    parser.add_argument("pos_regex", help="regexes for part of speech")
    parser.add_argument("gloss_file", help="file path to translation dictionary")
    parser.add_argument("text", help="file path to target text")
    parser.add_argument("trans", help="file path to text translation")
    parser.add_argument("-o", "--output", dest="o", nargs="?", help="file name/suffix without filetype extension", default="Lemmatization")
    #parser.add_argument("-a", "--analysis", dest="a", nargs="?", help="name of analysis file", default="") #I don't remember what this is for! (DAB 2/2024)
    parser.add_argument("-c", "--corrections", dest="c", nargs="?", help="name of corrections file", default="") #feed in hand-curated notes 
    parser.add_argument("-r", "--human-readable", dest="r", action="store_true", help="whether to write output as a txt file with user-friendly line wrapping")
    parser.add_argument("-d", "--drop-punct" , dest="d", action="store_true", help="whether to separate punctuation (false) or drop punctuation (true) when parsing")
    parser.add_argument("-e", "--error-fst" , dest="e", nargs="?", help="name of analyzer composed with an error model", default="")
    parser.add_argument("-g", "--generation-fst" , dest="g", nargs="?", help="name of generation transducer (tags -> forms)", default="")
    return parser.parse_args()

def human_readable(fst_file, fst_format, regex_file, gloss_file, drop_punct, text, trans, output):
    gdict = eng.mk_glossing_dict(*rw.readin(gloss_file))
    pos_regex = "".join(rw.readin(regex_file))
    with open(output, 'w') as file_out:
        l = 0
        for inter in  interlinearize(fst_file, fst_format, pos_regex, gdict, drop_punct, text, trans):
            file_out.write(str(l)+'\n')
            l += 1
            wrap = 0
            mainline = []
            subline = [[],[],[],[]]
            for i in range(len(inter[0])):
                m = max(len(inter[0][i]), len(inter[1][i]), len(inter[2][i]), len(inter[3][i]))
                if wrap + m > 100: #wrapping at less than 267 (full screen) to allow lines to be edited
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

def retrieve_glosses(*lemmata, **gloss_dict):
    tinies = []
    for l in lemmata:
        try: gloss = gloss_dict[l]
        except KeyError:
            if "+" in l: 
                gloss = "-".join(retrieve_glosses(*l.split("+"), **gloss_dict, ))
            else: gloss = "?"
        tinies.append(gloss)
    return tinies

def wrap_glosses(*glosses):
    return ["'"+g+"'" for g in glosses]

if __name__ == "__main__":
    args = parseargs()
    cdict = {} #corrections are original: [edited, analyzed]
    adjustments = {} #changes for white space (specified in notes files aka corrections)
    if args.c: 
        for correction in rw.readin(args.c):
            cor = correction.split()
            if any(["XX" in x for x in correction.split()]): adjustments[" ".join("XX".split(cor[2]))] = " ".join("XX".split(cor[3])) #this drops analysis of the splitting/joining ... all split/joined words should probably already get good analyses, or have them specified elsewhere in the corrections file
            else: cdict[cor[2]] = cor[3:5]
    if args.r: human_readable(args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, args.d, rw.burn_metadata(2, *rw.readin(args.text)), rw.readin(args.trans), args.o) 
    else:
        #for generating lemmata from rand files
        pos_regex = "".join(rw.readin(args.pos_regex))
        #if args.a: 
        #    analysis = pst.parser_out_string_dict("\n".join(rw.readin(args.a)))
        #    #for a in sorted(analysis): print(a, analysis[a])
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
            performance = [0, 0.01] #hits, misses
            ###
            #initialization with metadata (including translation), tokenized values 
            ###
            for line in f:
                data = line.strip().split('\t')
                full["speakerID"].append(data[0])
                full["speaker_text_num"].append(data[1])
                full["speaker_text_sent_num"].append(data[2])
                full["sentence"].append(data[3])
                revised = data[3].lower()
                for adj in adjustments: #words that need to be split in two or joined together
                    if adj in revised: revised = re.sub(adj, adjustments[adj], revised)
                tokenized = pre.sep_punct(revised, args.d).split()
                full["chunked"].append(tokenized)
                full["edited"].append(tokenized) #this gets rewritten below...
                full["english"].append(data[4])
                full["sentenceID"].append(data[5])
                #if args.a:
                #    full["m_parse_lo"].append([])
                #    for w in pre.sep_punct(data[3].lower(), args.d).split(): 
                #        full["m_parse_lo"][-1].append(analysis[w][pst.disambiguate(pst.min_morphs(*analysis[w]), pst.min_morphs, *analysis[w])][0])
                #        performance[int(analysis[w][pst.disambiguate(pst.min_morphs(*analysis[w]), pst.min_morphs, *analysis[w])][0].endswith("+?"))] += 1 
            print("hit rate:", str(round(performance[0]/(performance[1]+performance[0]), 3)*100)+"%", "hits:", performance[0], "misses:", performance[1])
        ###
        #analysis and digestion of analysis
        ###
        full["m_parse_lo"] = analyze_text(args.fst_file, args.fst_format, args.d, *full["sentence"])
        #if not args.a: full["m_parse_lo"] = analyze_text(args.fst_file, args.fst_format, cdict, args.d, *full["sentence"])
        gdict = eng.mk_glossing_dict(*rw.readin(args.gloss_file))
        innovation_adjust = []
        error_adjust = []
        for i in range(len(full["m_parse_lo"])): 
            full["lemmata"].append([x if x else "?" for x in lemmatize(pos_regex, *full["m_parse_lo"][i])]) #filter on "if x" to leave out un analyzed forms
            full["m_parse_hi"].append(["'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(x)))+"'" if algsum.analysis_dict(x) else "'?'" for x in full["m_parse_lo"][i] ]) # filter on "if algsum.analysis_dict(x)" to leave out unanalyzed forms
            #edited = [x if x not in cdict else cdict[x][0] for x in full["chunked"][i]]
            edited = []
            for j in range(len(full["chunked"][i])):
                if full["m_parse_lo"][i][j].endswith('+?'): error_adjust.append((full["chunked"][i][j], i, j))
                if full["chunked"][i][j] in cdict: 
                    edited.append(cdict[full["chunked"][i][j]][0]) #this may need to be relative to specific locations, especially because there is at least one case where a bare word (which could in principle be correctly spelled) should be replaced by an obviative. The hand notes do this, but as written, all cases of the bare word anywhere in the text would be replaced with the obviative (the case is biipiigwenh->biipiigwenyan in underground people) !!
                elif full["chunked"][i][j].startswith("e-"):
                    edited.append(full["chunked"][i][j])
                    innovation_adjust.append(("e-", full["chunked"][i][j], i, j))
                elif re.match("[ng]?da-", full["chunked"][i][j]):
                    edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?da-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                elif re.match("[ng]?di-", full["chunked"][i][j]):
                    edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?di-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                elif re.match("[ng]?doo-", full["chunked"][i][j]):
                    edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?doo-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                else: edited.append(full["chunked"][i][j])
            full["edited"][i] = edited
            full["tiny_gloss"].append(wrap_glosses(*retrieve_glosses(*full["lemmata"][i], **gdict)))
            #tinies = []
            #for l in full["lemmata"][i]:
            #    try: gloss = gdict[l]
            #    except KeyError: 
            #        gloss = "?" 
            #    tinies.append("'"+gloss+"'")
            #    #tinies.append("'"+re.search('(\w*\s*){0,4}',gloss)[0].lstrip(" 1")+"'")
            #full["tiny_gloss"].append(tinies)
        ###
        #re-analyzing failed items with error model
        ###
        if args.e and args.g:
            e_dict = parse.parse_native(args.e, *[x[0] for x in error_adjust])
            generation_dict = parse.parse_native(args.g, *[e_dict[x][pst.disambiguate(pst.min_morphs(*e_dict[x]), pst.min_morphs, *e_dict[x])][0] for x in e_dict if not x[0].endswith('+?')])
        fixed_errors = []
        for x in error_adjust:
            updates = {
                    "m_parse_lo": "",
                    "m_parse_hi":"",
                    "edited": "",
                    "lemmata": "",
                    "source": "",
                    "tiny_gloss":""
                    }
            if x[0] in cdict: #corrections are {original: [edited, analyzed]}
                best = cdict[x[0]][1]
                updates["m_parse_lo"]= best
                updates["m_parse_hi"]="'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(best)))+"'"
                updates["edited"]= cdict[x[0]][0]
                updates["lemmata"]= lemmatize(pos_regex, best)[0]
                updates["source"]= "hand"
            elif args.e and args.g:
                if not e_dict[x[0]][0][0].endswith('+?'):
                    best =  e_dict[x[0]][pst.disambiguate(pst.min_morphs(*e_dict[x[0]]), pst.min_morphs, *e_dict[x[0]])][0]
                    updates["m_parse_lo"]= best
                    updates["m_parse_hi"]="'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(best)))+"'"
                    updates["edited"]= generation_dict[best][0][0]
                    updates["lemmata"]= lemmatize(pos_regex, best)[0]
                    updates["source"]= "error_model"
            #try: gloss = gdict[updates["lemmata"]]
            #except KeyError:
            #    gloss = "?"
            updates["tiny_gloss"] = wrap_glosses(*retrieve_glosses(updates["lemmata"], **gdict))[0]
            if updates["m_parse_lo"]: fixed_errors.append((x, updates))
        fix_cnt = {"hand":0, "error_model":0}
        with open("error_model_quick_check.txt", 'w') as error_check_file:
            for x in fixed_errors:
                #print(x[1])
                for y in x[1]:
                    if y != "source":
                        full[y][x[0][1]][x[0][2]] = x[1][y]
                    else: 
                        #print(y, x[1][y])
                        fix_cnt[x[1][y]] += 1
                padded = pad([str(ind) for ind in range(len(full["chunked"][x[0][1]]))], full["chunked"][x[0][1]], full["edited"][x[0][1]], full["m_parse_lo"][x[0][1]], full["m_parse_hi"][x[0][1]], full["lemmata"][x[0][1]], full["tiny_gloss"][x[0][1]])
                error_check_file.write("Sentence number:"+' '+str(x[0][1])+'\n')
                error_check_file.write("Terse translation of fixed word grossly mismatches English sentence translation? (y/n): "+'\n')
                error_check_file.write("Terse translation of any other word grossly mismatches English sentence translation (give column number(s)): "+'\n')
                error_check_file.write("Comments?: "+'\n')
                error_check_file.write("Fixed word, and column:\t"+x[0][0]+'\t'+str(x[0][2])+'\n')
                for p in padded: error_check_file.write(" ".join(p)+'\n')
                error_check_file.write(full['english'][x[0][1]]+'\n')
                error_check_file.write('\n')
        print("hand fixed these many misses: ", fix_cnt["hand"])
        print("mach fixed these many misses: ", fix_cnt["error_model"])
        ###
        #checking if forms written with innovative affixes can be analyzed as if they were conservative
        ###
        innovation_adjustments = parse.parse_native(os.path.expanduser(args.fst_file), *[conserve_innovation(x[0], x[1]) for x in innovation_adjust])
        for x in innovation_adjust:
            ccnj = conserve_innovation(x[0], x[1])
            if not innovation_adjustments[ccnj][0][0].endswith('+?'):
                full["m_parse_lo"][x[2]][x[3]] = innovation_adjustments[ccnj][pst.disambiguate(pst.min_morphs(*innovation_adjustments[ccnj]), pst.min_morphs, *innovation_adjustments[ccnj])][0]
                full["m_parse_hi"][x[2]][x[3]] = "'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(full["m_parse_lo"][x[2]][x[3]])))+"'"
                full["edited"][x[2]][x[3]] = ccnj
        ###
        #converting lists to padded/aligned strings
        ###
        for i in range(len(full["m_parse_lo"])):
            padded = pad(full["chunked"][i], full["edited"][i], full["lemmata"][i], full["m_parse_hi"][i], full["tiny_gloss"][i], full["m_parse_lo"][i])
            full["chunked"][i] = " ".join(padded[0])
            full["edited"][i] = " ".join(padded[1])
            full["lemmata"][i] = " ".join(padded[2])
            full["m_parse_hi"][i] = " ".join(padded[3])
            full["tiny_gloss"][i] = " ".join(padded[4])
            full["m_parse_lo"][i] = " ".join(padded[5])
        #    full["chunked"][i] = padded[0]
        #    full["edited"][i] = padded[0]
        #    full["lemmata"].append(padded[1])
        #    full["m_parse_hi"].append(padded[2])
        #    full["tiny_gloss"].append(padded[3])
        #    full["m_parse_lo"][i] = padded[4]
        #by_sent = [{x:full[x][i] for x in names} for i in range(len(full["sentenceID"]))]
        #code.interact(local=locals())
        ###
        #write-out
        ###
        with open(args.o, 'w') as fo:
            json.dump([{x:full[x][i] for x in names} for i in range(len(full["sentenceID"]))], fo, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent=1)
        ##atomic_json_dump(args.o, names, [[d[5] for d in data_in], [d[3] for d in data_in], lemmata, summaries])
        ##needed args: (args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, args.text, args.trans, args.o) args.trans is required but will be ignored for Rand sentences
