import code
import os
import argparse
import re
from datetime import date
import json
import json_encoder
import parse
import random #for spot checks
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
            abbr = re.search(r'(\w*\s*){0,4}',gloss)[0].lstrip(" 1")
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
    parser.add_argument("-e", "--error-fst" , dest="e", nargs="+", help="name of analyzer composed with an error model", default="")
    parser.add_argument("-g", "--generation-fst" , dest="g", nargs="?", help="name of generation transducer (tags -> forms)", default="")
    parser.add_argument("-p", "--pad" , dest="pad", action="store_true", help="make lists contain a single padded string instead of a collection of strings")
    parser.add_argument("-k", "--key" , dest="key", nargs="?", help="file path to unique keys for lemmata", default="")
    parser.add_argument("--spot-check", dest="spot_check", nargs=3, action = 'append', help="number of spot checks to perform, which data to perform it on, and at what level of abstraction (N/all, analyzed/unanalyzed/specific analysis source, type/token)", default=[])
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

def mk_hand_mod_dicts(filename):
    corrections = {} #corrections are original: [edited, analyzed]
    adjustments = {} #changes for white space (specified in notes files aka corrections)
    for correction in rw.readin(filename):
        cor = correction.split()
        if any(["XX" in x for x in correction.split()]): adjustments[" ".join("XX".split(cor[2]))] = " ".join("XX".split(cor[3])) #this drops analysis of the splitting/joining ... all split/joined words should probably already get good analyses, or have them specified elsewhere in the corrections file
        else: corrections[cor[2]] = cor[3:5]
    return (corrections, adjustments)

def initialize(filename, *field_names):
    ###
    #initialization with metadata (including translation), tokenized values 
    ###
    h = {name:[] for name in field_names}
    with open(filename) as f:
        for line in f:
            data = line.strip().split('\t')
            h["speakerID"].append(data[0])
            h["speaker_text_num"].append(data[1])
            h["speaker_text_sent_num"].append(data[2])
            h["sentence"].append(data[3])
            lowered = data[3].lower()
            for adj in adjdict: #words that need to be split in two or joined together
                if adj in lowered: lowered = re.sub(adj, adjdict[adj], lowered)
            tokenized = pre.sep_punct(lowered, args.d).split()
            h["chunked"].append([t for t in tokenized])
            h["edited"].append([t for t in tokenized]) #this gets rewritten below...
            h["english"].append(data[4])
            h["sentenceID"].append(data[5])
    return h

if __name__ == "__main__":
    args = parseargs()
    cdict = {} #corrections are original: [edited, analyzed]
    adjdict = {} #changes for white space (specified in notes files aka corrections)
    if args.c: cdict, adjdict = mk_hand_mod_dicts(args.c)
    if args.r: human_readable(args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, args.d, rw.burn_metadata(2, *rw.readin(args.text)), rw.readin(args.trans), args.o) 
    else:
        #for generating lemmata from rand files
        pos_regex = "".join(rw.readin(args.pos_regex))
        #if args.a: 
        #    analysis = pst.parser_out_string_dict("\n".join(rw.readin(args.a)))
        #    #for a in sorted(analysis): print(a, analysis[a])
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
                "nishID",
                "english",
                "sentence",
                "analysis_src",
                #"fiero_orth", #new machine with UR as top, then run UR back down to SRs minus corb spelling
                #"unsyncopated", #new machine with UR as top, then run UR back down to SRs minus syncope
                ]
        full = initialize(args.text, *names)
        glossdict = eng.mk_glossing_dict(*rw.readin(args.gloss_file))
        iddict = {}
        if args.key: iddict = eng.mk_glossing_dict(*rw.readin(args.key))
        sentlist = [" ".join(x) for x in full["chunked"]]
        full["m_parse_lo"] = analyze_text(args.fst_file, args.fst_format, args.d, *sentlist)
        #for i in range(len(full["m_parse_lo"])):
        #    if len(full["m_parse_lo"][i]) != len(full["chunked"][i]): 
        #        print("length mismatch")
        #        print(full["chunked"][i])
        #        print(full["m_parse_lo"][i])
        full["analysis_src"] = [[["analyzed", args.fst_file] if not y.endswith("+?") else ["unanalyzed"] for y in x] for x in full["m_parse_lo"]]
        #alt_analyses = [analyze_text(x, args.fst_format, args.d, *sentlist) for x in args.e]
        ###
        #revisions to initial analysis
        ###
        #if not args.a: full["m_parse_lo"] = analyze_text(args.fst_file, args.fst_format, cdict, args.d, *full["sentence"])
        innovation_adjust = []
        error_adjust = []
        manual_cnt = 0
        manual_fix = 0
        manual_red = 0
        for i in range(len(full["m_parse_lo"])): 
            full["lemmata"].append([x if x else "?" for x in lemmatize(pos_regex, *full["m_parse_lo"][i])]) #filter on "if x" to leave out un analyzed forms
            full["m_parse_hi"].append(["'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(x)))+"'" if algsum.analysis_dict(x) else "'?'" for x in full["m_parse_lo"][i] ]) # filter on "if algsum.analysis_dict(x)" to leave out unanalyzed forms
            #edited = [x if x not in cdict else cdict[x][0] for x in full["chunked"][i]]
            #edited = []
            for j in range(len(full["chunked"][i])):
                if full["chunked"][i][j] in cdict: #manual over ride 1
                    manual_cnt += 1
                    if full["m_parse_lo"][i][j].endswith("+?"): manual_fix += 1
                    if full["m_parse_lo"][i][j] == cdict[full["chunked"][i][j]][1]: manual_red += 1
                    full["edited"][i][j] = cdict[full["chunked"][i][j]][0] #this may need to be relative to specific locations, especially because there is at least one case where a bare word (which could in principle be correctly spelled) should be replaced by an obviative. The hand notes do this, but as written, all cases of the bare word anywhere in the text would be replaced with the obviative (the case is biipiigwenh->biipiigwenyan in underground people) !!
                    full["m_parse_lo"][i][j] = cdict[full["chunked"][i][j]][1] #this may need to be relative to specific locations, especially because there is at least one case where a bare word (which could in principle be correctly spelled) should be replaced by an obviative. The hand notes do this, but as written, all cases of the bare word anywhere in the text would be replaced with the obviative (the case is biipiigwenh->biipiigwenyan in underground people) !!
                    full["analysis_src"][i][j] = ["analyzed", "hand"] #this may need to be relative to specific locations, especially because there is at least one case where a bare word (which could in principle be correctly spelled) should be replaced by an obviative. The hand notes do this, but as written, all cases of the bare word anywhere in the text would be replaced with the obviative (the case is biipiigwenh->biipiigwenyan in underground people) !!
                    full["m_parse_hi"][i][j]="'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(cdict[full["chunked"][i][j]][1])))+"'"
                    full["lemmata"][i][j]= lemmatize(pos_regex, cdict[full["chunked"][i][j]][1])[0]
                if full["m_parse_lo"][i][j].endswith('+?'): error_adjust.append((full["chunked"][i][j], i, j))
                if full["chunked"][i][j].startswith("e-"):
                    #edited.append(full["chunked"][i][j])
                    innovation_adjust.append(("e-", full["chunked"][i][j], i, j))
                elif re.match("[ng]?da-", full["chunked"][i][j]):
                    #edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?da-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                elif re.match("[ng]?di-", full["chunked"][i][j]):
                    #edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?di-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                elif re.match("[ng]?doo-", full["chunked"][i][j]):
                    #edited.append(full["chunked"][i][j])
                    innovation_adjust.append((re.match("[ng]?doo-", full["chunked"][i][j])[0], full["chunked"][i][j], i, j))
                #else: edited.append(full["chunked"][i][j])
            #full["edited"][i] = edited
            full["tiny_gloss"].append(wrap_glosses(*retrieve_glosses(*full["lemmata"][i], **glossdict)))
            full["nishID"].append(wrap_glosses(*retrieve_glosses(*full["lemmata"][i], **iddict)))
        print("hand corrected these many incorrect analyses: ", manual_cnt-manual_fix-manual_red)
        print("redundantly corrected these many correct analyses: ", manual_red)
        print("hand fixed these many misses: ", manual_fix)
        ###
        #re-analyzing failed items with error model
        ###
        if args.e:
            e_dict = {}
            residue = [x[0] for x in error_adjust]
            for e_model in args.e:
                sub_e_dict = parse.parse_native(e_model, *residue)
                residue = []
                for x in sub_e_dict:
                    if not sub_e_dict[x][0][0].endswith('+?'): e_dict[x] = [e_model, sub_e_dict[x]]
                    else: residue.append(x)
            #for x in residue: e_dict[x] = ["unanalyzed", [(x+'+?', 0.00)]] #formatted like a successful analysis, but none of this information is actually retrieved below, so it makes sense to just use a default specification during the initial parse, and overwrite with the successes
            if args.g: generation_dict = parse.parse_native(args.g, *[e_dict[x][1][pst.disambiguate(pst.min_morphs(*pst.minimal_filter(*e_dict[x][1])), pst.min_morphs, *pst.minimal_filter(*e_dict[x][1]))][0] for x in e_dict])
        fixed_errors = []
        for x in error_adjust:
            updates = {
                    "m_parse_lo": "",
                    "m_parse_hi":"",
                    "edited": "",
                    "lemmata": "",
                    "analysis_src": "",
                    "tiny_gloss":"",
                    "nishID":""
                    }
            #if x[0] in cdict: #corrections are {original: [edited, analyzed]}
            #    best = cdict[x[0]][1]
            #    updates["m_parse_lo"]= best
            #    updates["m_parse_hi"]="'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(best)))+"'"
            #    updates["edited"]= cdict[x[0]][0]
            #    updates["lemmata"]= lemmatize(pos_regex, best)[0]
            #    updates["analysis_src"]= ["analyzed", "hand"]
            #    #if x[0] in e_dict and cdict[x[0]][1] != e_dict[x[0]][1][0][0]: print("{0} error analysis {1} manually overwritten by {2}".format(x[0], e_dict[x[0]][1][pst.disambiguate(pst.min_morphs(*pst.minimal_filter(*e_dict[x[0]][1])), pst.min_morphs, *pst.minimal_filter(*e_dict[x[0]][1]))][0], best)) #AS OF 7/15/2024 MANUAL OVERRIDE OF ANALYSIS ONLY HAPPENS FOR ERROR MODEL, NOT BASE MODEL (EDITED FORM SHOULD ALSO JUST GET RE-WRITTEN BY DEFAULT TOO)
            if args.e and args.g:
                #if not e_dict[x[0]][1][0][0].endswith('+?'): 
                if x[0] in e_dict: 
                    best =  e_dict[x[0]][1][pst.disambiguate(pst.min_morphs(*pst.minimal_filter(*e_dict[x[0]][1])), pst.min_morphs, *pst.minimal_filter(*e_dict[x[0]][1]))][0]
                    updates["m_parse_lo"]= best
                    updates["m_parse_hi"]="'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(best)))+"'"
                    updates["edited"]= generation_dict[best][0][0]
                    updates["lemmata"]= lemmatize(pos_regex, best)[0]
                    updates["analysis_src"]= ["analyzed", e_dict[x[0]][0]]
            #try: gloss = glossdict[updates["lemmata"]]
            #except KeyError:
            #    gloss = "?"
            updates["tiny_gloss"] = wrap_glosses(*retrieve_glosses(updates["lemmata"], **glossdict))[0]
            updates["nishID"] = wrap_glosses(*retrieve_glosses(updates["lemmata"], **iddict))[0]
            if updates["m_parse_lo"]: fixed_errors.append((x, updates))
        fix_cnt = {model:0 for model in args.e}
        for x in fixed_errors:
            #print(x[1])
            for y in x[1]:
                full[y][x[0][1]][x[0][2]] = x[1][y]
                if y == "analysis_src": fix_cnt[x[1][y][1]] += 1
                    #print(y, x[1][y])
        for model in args.e: print("{} fixed these many misses: ".format(model), fix_cnt[model])
        ###
        #checking if forms written with innovative affixes can be analyzed as if they were conservative
        ###
        innovation_adjustments = parse.parse_native(os.path.expanduser(args.fst_file), *[conserve_innovation(x[0], x[1]) for x in innovation_adjust])
        #letting the error model loose on these data is too permissive, getting a lot of hallucinated person prefixes
        #for model in args.e: #THIS DOES NOT TRACK WHICH VERSION OF THE ANALYZER DID THE SPECIFIC FIX. I DON'T THINK THERE SHOULD NEVER BE A DIFFERENCE BETWEEN WHICH MODEL SUCCESSFULLY ANALYZED A FORM FIRST AND WHICH ONE CAN HANDLE THE INNOVATION, BUT THIS IS A POTENTIAL SOURCE OF BUGS.
        #    #TO FIX, YOU MAY NEED TO USE innovation_adjust, WHICH TRACKS INDICES
        #    #YOU WILL CERTAINLY NEED TO STORE THE MODEL IN THE VALUE IN innovation_adjustments, AND THEN DANCE AROUND THE MORE COMPLEX VALUES WHEN YOU UNPACK innovation_adjustments
        #    try_again = []
        #    for in_adj in innovation_adjustments:
        #        if innovation_adjustments[in_adj][0][0].endswith('+?'): try_again.append(in_adj)
        #    nu_adj = parse.parse_native(os.path.expanduser(model), *try_again)
        #    for t in try_again:
        #        if not nu_adj[t][0][0].endswith('+?'): innovation_adjustments[t] = nu_adj[t]
        innov_cnt = 0
        innov_fix_cnt = 0
        for x in innovation_adjust:
            ccnj = conserve_innovation(x[0], x[1])
            if not innovation_adjustments[ccnj][0][0].endswith('+?'):
                innov_cnt += 1
                if full["m_parse_lo"][x[2]][x[3]].endswith('+?'): innov_fix_cnt += 1
                full["m_parse_lo"][x[2]][x[3]] = innovation_adjustments[ccnj][pst.disambiguate(pst.min_morphs(*pst.minimal_filter(*innovation_adjustments[ccnj])), pst.min_morphs, *pst.minimal_filter(*innovation_adjustments[ccnj]))][0]
                full["m_parse_hi"][x[2]][x[3]] = "'"+algsum.formatted(algsum.interpret(algsum.analysis_dict(full["m_parse_lo"][x[2]][x[3]])))+"'"
                full["edited"][x[2]][x[3]] = ccnj
                full["analysis_src"][x[2]][x[3]] = ["analyzed", args.fst_file]
                full["lemmata"][x[2]][x[3]]= lemmatize(pos_regex, full["m_parse_lo"][x[2]][x[3]])[0]
                full["tiny_gloss"][x[2]][x[3]] = wrap_glosses(*retrieve_glosses(full["lemmata"][x[2]][x[3]], **glossdict))[0]
                full["nishID"][x[2]][x[3]] = wrap_glosses(*retrieve_glosses(full["lemmata"][x[2]][x[3]], **iddict))[0]
        print("conservatized these many potentially innovative forms: ", str(innov_cnt))
        print("fixed these many potentially innovative misses by conservativization: ", str(innov_fix_cnt))
        if args.g:
            all_low = []
            for x in full["m_parse_lo"]:
                for y in x: all_low.append(y)
            generation_dict = parse.parse_native(args.g, *all_low) 
            for i in range(len(full["m_parse_lo"])):
                for j in range(len(full["m_parse_lo"][i])):
                    if full["chunked"][i][j] in cdict: full["edited"][i][j] = cdict[full["chunked"][i][j]][0]
                    elif not generation_dict[full["m_parse_lo"][i][j]][0][0].endswith("+?"): full["edited"][i][j] = generation_dict[full["m_parse_lo"][i][j]][pst.disambiguate2(pst.score_edits(full["chunked"][i][j], *pst.minimal_filter(*generation_dict[full["m_parse_lo"][i][j]])), *pst.minimal_filter(*generation_dict[full["m_parse_lo"][i][j]]))][0]
                    else: full["edited"][i][j] = full["chunked"][i][j]
        ###
        #spot checks
        ###
        if args.spot_check:
            for s in args.spot_check:
                loci = [] #[(i, j) for j in range(len(full["m_parse_lo"][i])) for i in range(len(full["m_parse_lo"]))]
                for i in range(len(full["m_parse_lo"])):
                    for j in range(len(full["m_parse_lo"][i])): loci.append((i, j))
                used_lemmata = {}
                if s[1] == "unanalyzed": assert s[2] == "token"
                if s[0] == "all": 
                    target_forms = []
                    for locus in loci:
                        if s[1] in full["analysis_src"][locus[0]][locus[1]]: 
                            target_form = (full["chunked"][locus[0]][locus[1]], "".join(reversed(full["chunked"][locus[0]][locus[1]])), locus)
                            target_forms.append(target_form)
                            if s[2] == "type" and full["lemmata"][locus[0]][locus[1]] not in used_lemmata: used_lemmata[full["lemmata"][locus[0]][locus[1]]] = [target_form]
                            elif s[2] == "type" and full["lemmata"][locus[0]][locus[1]] in used_lemmata: used_lemmata[full["lemmata"][locus[0]][locus[1]]].append(target_form)
                    with open('spot_checks_{0}_{1}_{2}_{3}_reversed.csv'.format(s[0], s[1], s[2], date.today()), 'w') as fileOut: 
                        if s[2] == "type":
                            for ul in sorted(used_lemmata):
                                for tf in sorted(used_lemmata[ul], key=lambda x: x[1]):
                                    fileOut.write("\t".join( 
                                                            [ul, 
                                                            tf[0], 
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i < tf[2][1]]), 
                                                             full["chunked"][tf[2][0]][tf[2][1]],                                                                           
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i > tf[2][1]]), 
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i < tf[2][1] ]), 
                                                             full["m_parse_lo"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i > tf[2][1] ]), 
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i > tf[2][1] ]), 
                                                             full["tiny_gloss"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i < tf[2][1] ]), 
                                                            full["english"][tf[2][0]],
                                                            str(tf[2][0]),
                                                            str(tf[2][1])])+"\n")
                        else:
                            for tf in sorted(target_forms, key=lambda x: x[1]):
                                fileOut.write("\t".join( 
                                                        [tf[0], 
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i < tf[2][1]]), 
                                                             full["chunked"][tf[2][0]][tf[2][1]],                                                                           
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i > tf[2][1]]), 
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i < tf[2][1] ]), 
                                                             full["m_parse_lo"][tf[2][0]][tf[2][1]],
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i]  for i in range(len(full["m_parse_lo"][tf[2][0]])) if i > tf[2][1]]), 
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i]  for i in range(len(full["tiny_gloss"][tf[2][0]])) if i > tf[2][1]]), 
                                                             full["tiny_gloss"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i]  for i in range(len(full["tiny_gloss"][tf[2][0]])) if i < tf[2][1]]), 
                                                        full["english"][tf[2][0]],
                                                        str(tf[2][0]),
                                                        str(tf[2][1])])+"\n")
                    with open('spot_checks_{0}_{1}_{2}_{3}.csv'.format(s[0], s[1], s[2], date.today()), 'w') as fileOut:
                        if s[2] == "type":
                            for ul in sorted(used_lemmata):
                                for tf in sorted(used_lemmata[ul]):
                                    fileOut.write("\t".join( 
                                                            [ul, 
                                                            tf[0], 
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i < tf[2][1]]), 
                                                             full["chunked"][tf[2][0]][tf[2][1]],                                                                           
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i > tf[2][1]]), 
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i < tf[2][1] ]), 
                                                             full["m_parse_lo"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i > tf[2][1] ]), 
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i > tf[2][1] ]), 
                                                             full["tiny_gloss"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i < tf[2][1] ]), 
                                                            full["english"][tf[2][0]],
                                                            str(tf[2][0]),
                                                            str(tf[2][1])])+"\n")
                        else:
                            for tf in sorted(target_forms):
                                fileOut.write("\t".join( 
                                                        [tf[0], 
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i < tf[2][1]]), 
                                                             full["chunked"][tf[2][0]][tf[2][1]],                                                                           
                                                            " ".join([full["chunked"][tf[2][0]][i]  for i in range(len(full["chunked"][tf[2][0]])) if i > tf[2][1]]), 
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i < tf[2][1] ]), 
                                                             full["m_parse_lo"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["m_parse_lo"][tf[2][0]][i] for i in range(len(full["m_parse_lo"][tf[2][0]])) if i > tf[2][1] ]), 
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i > tf[2][1] ]), 
                                                             full["tiny_gloss"][tf[2][0]][tf[2][1]],                                                                              
                                                            " ".join([full["tiny_gloss"][tf[2][0]][i] for i in range(len(full["tiny_gloss"][tf[2][0]])) if i < tf[2][1] ]), 
                                                        full["english"][tf[2][0]],
                                                        str(tf[2][0]),
                                                        str(tf[2][1])])+"\n")
                else:
                    cnt = 0
                    with open('spot_checks_{0}_{1}_{2}_{3}.txt'.format(s[0], re.search(r"(([^/]*(?=\.hfstol))|((un)?analyzed))", s[1])[0], s[2], date.today()), 'w') as fileOut:
                        while cnt < int(s[0]) and loci:
                            cnt += 1
                            locus = loci.pop(random.randrange(0, len(loci)))
                            while ((not s[1] in full["analysis_src"][locus[0]][locus[1]]) or full["lemmata"][locus[0]][locus[1]] in used_lemmata) and loci: locus = loci.pop(random.randrange(0, len(loci)))
                            if s[2] == "type": used_lemmata[full["lemmata"][locus[0]][locus[1]]] = 0
                            padded = pad([str(ind) for ind in range(len(full["chunked"][locus[0]]))], full["chunked"][locus[0]], full["edited"][locus[0]], full["m_parse_lo"][locus[0]], full["m_parse_hi"][locus[0]], full["lemmata"][locus[0]], full["tiny_gloss"][locus[0]])
                            fileOut.write("Sentence number:"+' '+str(locus[0])+'\n')
                            fileOut.write("Is target word a loan/not in Nishnaabemwin? (y/n): "+'\n')
                            if s[1] == "unanalyzed":
                                fileOut.write("IF TARGET IS LOAN = N: Span of English sentence translation that most likely corresponds to unanalyzed word (if no good span found, mark with a hyphen (-)): "+'\n')
                                fileOut.write("IF TARGET IS LOAN = N: Most likely dictionary lemmas for unanalyzed word (if none, mark with a hyphen (-); give no more than 3 lemmas; do no more than 10 searches!): "+'\n')
                            if s[1] != "unanalyzed":
                                fileOut.write("IF TARGET IS LOAN = N: Terse translation of target word grossly mismatches English sentence translation? (y/n): "+'\n')
                                fileOut.write("IF TERSE TRANSLATION MISMATCH = N: Grammatical analysis of target word is inconsistent with English sentence translation? (y/n): "+'\n')
                            fileOut.write("Comments?: "+'\n')
                            fileOut.write("Target word, and column:\t"+full["chunked"][locus[0]][locus[1]]+'\t'+str(locus[1])+'\n')
                            #for p in padded: fileOut.write(" ".join(p)+'\n')
                            start = 0
                            stop = 0
                            while stop < len(padded[0]):
                                while stop < len(padded[0]) and len(" ".join(padded[0][start:stop])) < 100:
                                    stop += 1
                                for p in padded: 
                                    fileOut.write(" ".join(p[start:stop])+'\n')
                                start = stop
                                if stop < len(padded[0])-1: fileOut.write('\n')
                            fileOut.write(full['english'][locus[0]]+'\n')
                            fileOut.write('\n')
        ###
        #write-out
        ###
        #converting lists to padded/aligned strings
        if args.pad:
            for i in range(len(full["m_parse_lo"])):
                padded = pad(full["chunked"][i], full["edited"][i], full["lemmata"][i], full["m_parse_hi"][i], full["tiny_gloss"][i], full["m_parse_lo"][i])
                full["chunked"][i] = " ".join(padded[0])
                full["edited"][i] = " ".join(padded[1])
                full["lemmata"][i] = " ".join(padded[2])
                full["m_parse_hi"][i] = " ".join(padded[3])
                full["tiny_gloss"][i] = " ".join(padded[4])
                full["m_parse_lo"][i] = " ".join(padded[5])
        with open(args.o, 'w') as fo:
            json.dump([{x:full[x][i] for x in names} for i in range(len(full["sentenceID"]))], fo, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent=1)
        ##atomic_json_dump(args.o, names, [[d[5] for d in data_in], [d[3] for d in data_in], lemmata, summaries])
        ##needed args: (args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, args.text, args.trans, args.o) args.trans is required but will be ignored for Rand sentences
