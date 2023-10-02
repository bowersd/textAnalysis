import needleman
import csv
import re
import sys

def isolate_divergences(aligned1, aligned2):
    h = []
    for i in range(len(aligned1)):
        if aligned1[i] != aligned2[i]: h.append((aligned1[i], aligned2[i], aligned1[i-3:i], aligned1[i+1:i+4], aligned2[i-3:i], aligned2[i+1:i+4], i, len(aligned1))) #diff in, diff out, 3 letters context left in, 3 letters context right in, 3 letters left out, 3 letters context right out, diff loc, len(str)
    return h

def compile_reports(*error_expected):
    atomized = []
    summarized = {}
    for er_ex in error_expected:
        aligned1, aligned2 = needleman.align(er_ex[0], er_ex[1], -1, needleman.make_id_matrix(er_ex[0], er_ex[1]))
        diffs = isolate_divergences(aligned1, aligned2)
        for d in diffs:
            atomized.append([er_ex[0], er_ex[1], aligned1, aligned2]+list(d))
            cng = d[0:2]
            factors = [
                    "total",
                    "lft_pos_"+str(d[-2]),
                    "rht_pos_"+str(d[-1]-d[-2]),
                    "lft_ctx_in"+d[2],
                    "rht_ctx_in"+d[3],
                    "lft_ctx_out"+d[4],
                    "rht_ctx_out"+d[5],
                    ]
            if cng not in summarized: summarized[cng] = { } 
            for f in factors:
                if f not in summarized[cng]: summarized[cng][f] = 1
                else: summarized[cng][f] += 1
    for s in summarized:
            print(s)
            for c in sorted(summarized[s]):
                print("\t"+c+":"+"."*summarized[s][c])

if __name__ == "__main__":
    h = []
    with open(sys.argv[1]) as file_in:
        for line in file_in:
            h.append(line.strip().split(','))
    compile_reports(*h)

