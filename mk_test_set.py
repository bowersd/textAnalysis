import json
import json_encoder
import sys
import re

import readwrite as rw

initial_file = rw.readin(sys.argv[1])

i = 0
data = { "written" : "", "analysis" : "", "generated" : "", }
h = []
while i < len(initial_file):
    if initial_file[i].startswith("Sentence number:"):
        need_user = False
        target = ""
        sentence_id = re.search("[0-9]+", initial_file[i])[0]
    if (initial_file[i].startswith("Terse translation") and re.search(r"y/n\):.*[yYf]", initial_file[i])): need_user = True
    if (initial_file[i].startswith("Grammatical analysis") and re.search(r"y/n\):.*[yYf]", initial_file[i])): need_user = True
    if initial_file[i].startswith("Target word"): 
        target = initial_file[i].split()[-1]
    if target and target in initial_file[i].split() and all([re.match('^[0-9]+$', x) for x in initial_file[i].split()]) and not need_user:
        field = [j for j in range(len(initial_file[i].split())) if initial_file[i].split()[j] == target][0]
        data["written"] = initial_file[i+1].split()[field]
        data["generated"] = initial_file[i+2].split()[field]
        data["analysis"] = initial_file[i+3].split()[field]
    if target and target in initial_file[i].split() and all([re.match('^[0-9]+$', x) for x in initial_file[i].split()]) and need_user:
        field = [j for j in range(len(initial_file[i].split())) if initial_file[i].split()[j] == target][0]
        print("written: ", initial_file[i+1].split()[field])
        print("generated: ", initial_file[i+2].split()[field])
        print("analysis: ", initial_file[i+3].split()[field])
        print("sentence id: ", sentence_id)
        data["written"] = initial_file[i+1].split()[field]
        data["generated"] = input("what should the generated string be? ")
        data["analysis"] = input("what should the analysis be? ")
    if all(data[x] for x in data): 
        h.append(data)
        data = { "written" : "", "analysis" : "", "generated" : "", }
    i += 1


#write to json
with open(sys.argv[2], 'w') as fo:
    json.dump(h, fo, cls = json_encoder.MyEncoder, separators = (", ", ":\t"), indent = 1)

#write code to assess match between analyzer and json

