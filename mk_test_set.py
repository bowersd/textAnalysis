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
    if (initial_file[i].startswith("Terse translation") and re.search("y/n):.*[yYf]", initial_file[i])) or (initial_file[i+1].startswith("Grammatical analysis") and re.search("y/n):.*[yYf]", initial_file[i+1])): need_user = True
    if initial_file[i].startswith("Target word"): 
        target = initial_file[i].split()[-1]
    if target and target in initial_file[i] and all([re.match('[0-9]+', x) for x in initial_file[i].split()]) and not need_user:
        field = [j for j in range(len(initial_file[i].split())) if initial_file[i].split()[j] == target][0]
        data["written"] = initial_file[i+1].split()[field]
        data["generated"] = initial_file[i+2].split()[field]
        data["analysis"] = initial_file[i+3].split()[field]
    if target and target in initial_file[i] and all([re.match('[0-9]+', x) for x in initial_file[i].split()]) and need_user:
        print( initial_file[i+1].split()[field])
        print( initial_file[i+2].split()[field])
        print( initial_file[i+3].split()[field])
        #print the original sentence id (so you need to store that), prompt the user for the values to written, generated, analysis

#write to json

#write code to assess match between analyzer and json

    if all(data[x] for x in data): 
        h.append(data)
        data = { "written" : "", "analysis" : "", "generated" : "", }
    i += 1

