import os
import argparse
import parse
import readwrite as rw
import postprocess as pst
import preprocess as pre
import engdict as eng

def interlinearize(fst_file, fst_format, pos_regex, gdict, text_in, trans_in):
    holder = []
    for i in range(len(text_in)):
        sub = [[],[],[], [trans_in[i]]]
        for w in pre.sep_punct(text_in[i]).split():
            w=w.lower()
            p = pst.parser_out_string_dict(parse.parse(os.path.expanduser(fst_file), fst_format, w).decode(), "xerox")
            best = pst.disambiguate(pst.min_morphs(*p[w]), pst.min_morphs, *p[w])
            lem = pst.extract_lemma(p[w][best][0], pos_regex)
            try: gloss = gdict[lem]
            except KeyError: gloss = "NODEF"
            if lem: 
                sub[0].append(w)
                sub[1].append(p[w][best][0])
                if (w, gloss) not in sub[2]: sub[2].append((w, gloss))
            else: 
                sub[0].append(w)
                sub[1].append("?")
        holder.append(sub)
    return holder


def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fst_file", help="file path to primary analyser")
    parser.add_argument("fst_format", help="hfst or xfst")
    parser.add_argument("pos_regex", help="regexes for part of speech")
    parser.add_argument("gloss_file", help="file path to translation dictionary")
    parser.add_argument("text", help="file path to target text")
    parser.add_argument("trans", help="file path to text translation")
    parser.add_argument("-o", "--output", dest="o", nargs="?", help="file name/suffix without filetype extension", default="Interlinear")
    return parser.parse_args()

def main(fst_file, fst_format, regex_file, gloss_file, text, trans, output):
    gdict = eng.mk_glossing_dict(*rw.readin(gloss_file))
    pos_regex = "".join(rw.readin(regex_file))
    with open(output, 'w') as file_out:
        l = 0
        for inter in  interlinearize(fst_file, fst_format, pos_regex, gdict, text, trans):
            file_out.write(str(l)+'\n')
            l += 1
            for i in range(len(inter[0])):
                m = max(len(inter[0][i]), len(inter[1][i]))
                inter[0][i] = inter[0][i]+(" "*(m-len(inter[0][i])))
                inter[1][i] = inter[1][i]+(" "*(m-len(inter[1][i])))
            file_out.write(" ".join(inter[0])+'\n') 
            file_out.write(" ".join(inter[1])+'\n') 
            file_out.write(inter[3][0]+'\n') 
            file_out.write('\n')
            for x in sorted(inter[2]): file_out.write("\t".join(x)+'\n') 
            file_out.write('#######'*3)
            file_out.write('\n')
            file_out.write('\n')

if __name__ == "__main__":
    args = parseargs()
    main(args.fst_file, args.fst_format, args.pos_regex, args.gloss_file, rw.burn_metadata(2, *rw.readin(args.text)), rw.readin(args.trans), args.o)
