import needleman
import csv
import re
import sys

def isolate_divergences(aligned1, aligned2):
    h = []
    for i in range(len(aligned1)):
        if aligned1[i] != aligned2[i]: h.append((aligned1, aligned2, aligned1[i], aligned2[i], aligned1[i]+":"+aligned2[i], aligned1[i-3:i], aligned1[i+1:i+4], aligned2[i-3:i], aligned2[i+1:i+4], i, i+1-len(aligned1))) #diff in, diff out, 3 letters context left in, 3 letters context right in, 3 letters left out, 3 letters context right out, diff loc left, diff loc rightlen(str)
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
    #compile_reports(*h)
    summ = {}
    with open(sys.argv[2], 'w') as file_out:
        file_out.write("redir_in,redir_out,diff_in,diff_out,diff_complete,trilit_left_in,trilit_right_in,trilit_left_out,trilit_right_out,diff_loc_left,diff_loc_right\n")
        for x in h:
            ald = needleman.align(x[1], x[6], -1, needleman.make_id_matrix(x[1], x[6]))
            isolated = isolate_divergences(ald[0], ald[1])
            for iso in isolated: 
                file_out.write(','.join([str(y) for y in iso])+'\n')
                if iso[4] not in summ: summ[iso[4]] = {iso[7]+"^"+iso[8]:1}
                elif iso[7]+"^"+iso[8] not in summ[iso[4]]: summ[iso[4]][iso[7]+"^"+iso[8]] = 1
                else: summ[iso[4]][iso[7]+"^"+iso[8]] += 1
    ordered = []
    for x in summ: 
        for y in summ[x]:
            ordered.append((x, y, summ[x][y]))
    for x in sorted(ordered, key = lambda y: y[2]): print(x)

