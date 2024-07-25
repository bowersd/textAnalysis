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
        while cnt < sys.argv[3] and difftypes[dt]:
            cnt += 1
            locus = difftypes[dt].pop(random.randrange(0, len(difftypes[dt])))
            h.append(locus)
        for v in versions:
            with open("diff_check_{0}_{1}_{2}.txt".format(dt, v, date.today()), 'w') as file_out:
                for locus in h: 
                    padded = lemmatize.pad(versions[v][locus[0]]["chunked"], versions[v][locus[0]]["m_parse_lo"], versions[v][locus[0]]["m_parse_hi"], versions[v][locus[0]]["tiny_gloss"], versions[v][locus[0]]["english"])
                    for p in padded: file_out.write(p+"\n")
                    file_out.write("\n")


