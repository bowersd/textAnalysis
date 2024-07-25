import sys
import json
import random
import date

if __name__ == "__main__":
    versions = {}
    with open(sys.argv[1]) as oldjson:
        versions["old"] = json.load(oldjson)
    with open(sys.argv[2]) as newjson:
        versions["new"] = json.load(newjson)
    difftypes = {"change":[], "gain":[], "lose":[]}
    diffloci = [(i, j) for i in range(len(versions["old"])) for j in range(len(versions["old"][i]["m_parse_lo"])) if versions["old"][i]["m_parse_lo"][j] != versions["new"][i]["m_parse_lo"][j]]
    for dl in diffloci:
        if not any([versions["new"][locus[0]]["m_parse_lo"][locus[1]].endswith('+?'), versions["old"][locus[0]]["m_parse_lo"][locus[1]].endswith('+?')]): difftypes["change"].append(dl)
        elif versions["old"][locus[0]]["m_parse_lo"][locus[1]].endswith('+?'): difftypes["gain"].append(dl)
        else: difftypes["lose"].append(dl)
    print("diff count {0}".format(sum([len(difftypes[x]) for x in difftypes])))
    for dt in difftypes: 
        print("{0} count {1}".format(dt, len(difftypes[dt])))
        cnt = 0
        h = []
        while cnt < int(sys.argv[3]) and difftypes[dt]:
            cnt += 1
            locus = difftypes[dt].pop(random.randrange(0, len(difftypes[dt])))
            h.append(locus)
        for v in versions:
            with open("diff_check_{0}_{1}_{2}.txt".format(dt, v, date.today()), 'w') as file_out:
                for locus in h: 
                    padded = lemmatize.pad([str(i) for i in range(len(versions[v][locus[0]]["chunked"]))], versions[v][locus[0]]["chunked"], versions[v][locus[0]]["m_parse_lo"], versions[v][locus[0]]["m_parse_hi"], versions[v][locus[0]]["tiny_gloss"])
                    #for p in padded: #file_out.write(p+"\n")
                    start = 0
                    stop = 0
                    while stop < len(padded[0]):
                        while stop < len(padded[0]) and len(" ".join(padded[0][start:stop])) < 100:
                            stop += 1
                        for p in padded: 
                            fileOut.write(" ".join(p[start:stop])+'\n')
                        start = stop
                        if stop < len(padded[0])-1: fileOut.write('\n')
                    file_out.write(versions[v][locus[0]]["english"]+'\n')
                    file_out.write("\n")
        with open("diff_check_{0}_{1}_{2}_report.txt".format(dt, v, date.today()), 'w') as report:
            report.write("For the purposes of this report 'correct' means hi/lo level grammatical analysis and terse gloss fit English translation")
            for locus in h:
                report.write("Sentence ID: {0}".format(versions["old"][locus[0]]["sentenceID"])+'\n')
                report.write("Credit/blame: {0}".format(versions["new"][locus[0]]["analysis_src"][locus[1]][1])+'\n')
                report.write("Target word: {0} (index: {1})".format(versions["old"][locus[0]]["chunked"][locus[1]], str(locus[1]))+'\n')
                if dt == "gain" or dt == "change": report.write("Is {0} (new analysis) correct? (y/n)".format(versions["new"][locus[0]]["m_parse_lo"][locus[1]])+'\n')
                if dt == "change" or dt == "lose": 
                    if dt == "lose": report.write("Is {0} (old analysis) correct? (y/n)".format(versions["old"][locus[0]]["m_parse_lo"][locus[1]])+'\n')
                    if dt == "change": report.write("IF N: Is {0} (old analysis) correct? (y/n)".format(versions["old"][locus[0]]["m_parse_lo"][locus[1]])+'\n')
                report.write('Comments?'+'\n')
                report.write('\n')
