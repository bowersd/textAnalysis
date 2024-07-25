import sys
import json
import random

if __name__ == "__main__":
    with open(sys.argv[1]) as oldjson:
        old = json.load(oldjson)
    with open(sys.arg[2]) as newjson:
        new = json.load(newjson)
    difftypes = {"change":[], "gain":[], "lose":[]}
    diffloci = [(i, j) for i in range(len(old)) for j in range(len(old[i]["m_parse_lo"])) if old[i]["m_parse_lo"][j] != new[i]["m_parse_lo"][j]]
    for dl in diffloci:
        if not any([new[locus[0]]["m_parse_lo"][locus[1]].endswith('+?'), old[locus[0]]["m_parse_lo"][locus[1]].endswith('+?')]): difftypes["change"].append(dl)
        elif old[locus[0]]["m_parse_lo"][locus[1]].endswith('+?'): difftypes["gain"].append(dl)
        else new[locus[0]]["m_parse_lo"][locus[1]].endswith('+?'): difftypes["lose"].append(dl)
    print("diff count {0}".format(sum([len(difftypes[x]) for x in difftypes])))
    for dt in difftypes: 
        print("{0} count {1}".format(dt, len(difftypes[dt])))
        cnt = 0
        h = []
        while cnt < sys.argv[3] and difftypes[dt]:
            cnt += 1
            locus = difftypes[dt].pop(random.randrange(0, len(difftypes[dt])))
            h.append(locus)

