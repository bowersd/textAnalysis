import json
import sys

import parse
import lemmatize
import postprocess as pst

with open(sys.argv[1]) as fin:
    tests = json.load(fin)

analysis_dict = parse.parse_native(sys.argv[2],  *[x["written"] for x in tests])
analyses = [analysis_dict[x["written"]][pst.disambiguate(pst.min_morphs(*pst.minimal_filter(*analysis_dict[x["written"]])), pst.min_morphs, *pst.minimal_filter(*analysis_dict[x["written"]]))][0] for x in tests]
edit_dict = parse.parse_native(sys.argv[3], *analyses)
edits = [edit_dict[a][0][0] for a in analyses]

cnts = [0, 0]
general = 0
for i in range(len(tests)):
    fail = [False, False]
    if tests[i]["analysis"] != analyses[i]: fail[0] = True
    if tests[i]["generated"] != edits[i]: fail[1] = True
    #if not any(fail): print(tests[i]['written'], "passed")
    if any(fail): general += 1
    if fail[0]: print("analysis failure, on {2}, expected {0}, got {1}\n".format(tests[i]["analysis"], analyses[i], tests[i]["written"]))
    if fail[1]: 
        print("suggestion failure, on {0}".format(tests[i]["written"]))
        print("expected {0}".format(tests[i]["generated"]))
        print("observed {0}\n".format(edits[i]))
    for i in range(len(fail)):
        cnts[i] += fail[i]
print("{0} words tested, {1} failures, {2}% success rate".format(str(len(tests)), str(general), str(round((1-(general/len(tests)))*100, 1))))
if cnts[0]: print("{0} analysis failures ({1}% failure rate)".format(str(cnts[0]), str(round((cnts[0]/len(tests))*100, 1))))
if cnts[1]: print("{0} suggestion failures ({1}% failure rate)".format(str(cnts[1]), str(round((cnts[1]/len(tests))*100, 1))))
