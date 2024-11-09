import json
import sys
import sentence_complexity as sc
import readwrite as rw

if __name__ ==  "__main__":
    h = {"sentence":[], "m_parse_lo":[]}
    with open(sys.argv[1]) as lemmatized:
        jsonic = json.load(lemmatized)
        for x in jsonic:
            h["sentence"].append(x["sentence"])
            h["m_parse_lo"].append(x["m_parse_lo"])
    pos_regex = "".join(rw.readin(sys.argv[2]))
    comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
    overall_score = sc.alg_morph_score_rate(*comp_counts)
    itemized_scores = []
    for x in comp_counts: itemized_scores.append(sc.alg_morph_score_rate(x))
    s_score_pairs = sorted([x for x in zip(itemized_scores, h["sentence"])], key = lambda x: x[0])
    sectioned = [["Overall Scores (Verb Category/Order/Features per Sentence): {0}/{1}/{2}".format(overall_score[0], overall_score[1], overall_score[2])]]
    prev_vcat = []
    prev_vord = []
    for ssp in s_score_pairs:
        new_vcat = ssp[0][0]
        new_vord = ssp[0][1]
        if new_vcat != prev_vcat or new_vord != prev_vord:
            sectioned.append([">>Verb Category/Order Score: {0}/{1}".format(new_vcat, new_vord)])
            sectioned.append(ssp[1])
            prev_vcat = new_vcat
            prev_vord = new_vord
        else:
            sectioned.append(ssp[1])
    for s in sectioned: print(s) #output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")
