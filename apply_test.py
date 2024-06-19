import json
import sys

import parse
import lemmatize
import postprocess as pst

with open(sys.argv[1]) as fin:
    tests = json.load(fin)

analyses = lemmatize.analyze_text(sys.argv[2], 'hfst', True, *[x["written"] for x in tests])
edit_dict = parse.parse_native(sys.argv[3], *analyses)
edits = [edit_dict[a][0][0] for a in analyses]

cnts = [0, 0]
general = 0
for i in range(len(tests)):
    fail = [False, False]
    if tests[i]["analysis"] != analysis[i]: fail[0] = True
    if tests[i]["generated"] != edits[i]: fail[1] = True
    if not any(fail): print(tests[i]['written'], "passed")
    if any(fail): general += 1
    if fail[0]: print("analysis failure, on {2}, expected {0}, got {1}".format(tests[i]["analysis"], analysis[i], tests[i]["written"]))
    if fail[1]: 
        print("suggestion failure, on {0}".format(tests[i]["written"]))
        print("expected {0}".format(tests[i]["generated"]))
        print("observed {0}".format(edits[i]))
    for i in range(len(fail)):
        cnts[i] += fail[i]
print("{0} words tested, {1} successes, {2}% success rate".format(str(len(tests)), str(general), str(round((general/len(tests))*100, 1))))
if cnts[0]: print("{0} analysis failures ({1}% failure rate)".format(str(cnts[0]), str(round(((cnts[0]/len(tests))*100, 1))))
if cnts[1]: print("{0} suggestion failures ({1}% failure rate)".format(str(cnts[1]), str(round(((cnts[1]/len(tests))*100, 1))))
