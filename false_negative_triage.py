import needleman
import csv
import re

def isolate_divergences(aligned1, aligned2):
    h = []
    for i in range(len(aligned1)):
        if aligned1[i] != aligned2[i]: h.append((aligned1[i], aligned2[i], aligned1[i-3:i], aligned1[i+1:i+4], aligned2[i-3:i], aligned2[i+1:i+4], i, len(aligned1))) #diff in, diff out, 3 letters context left in, 3 letters context right in, 3 letters left out, 3 letters context right out, diff loc, len(str)
    return h

def counts(*error_expected):
    err_dict = {}
    for er_ex in error_expected:
        aligned1, aligned2 = needleman.align(er_ex[0], er_ex[1], -1, needleman.make_id_matrix(er_ex[0], er_ex[1]))
        diffs = isolate_divergences(aligned1, aligned2)
        for d in diffs:
            if d not in err_dict: err_dict[d] = 1
            else: err_dict[d] += 1

def count_report(**counts):
    cng_cnts = {}
    for c in counts:
        cng = c[0:2]
        facs = {}
        lpos= "lft_pos_"+str(c[-2])
        rpos= "rht_pos_"+str(c[-1]-c[-2])
        lcin= "lft_ctx_in"+c[2]
        rcin= "rht_ctx_in"+c[3]
        lcout="lft_ctx_out"+c[4]
        rcout="rht_ctx_out"+c[5]
        if cng not in cng_cnts: cng_cnts[cng] = {
                "total":1, 
                "lft_pos_"+str(c[-2]):1, 
                "rht_pos_"+str(c[-1]-c[-2]):1, 
                "lft_ctx_in"+c[2]:1, 
                "rht_ctx_in"+c[3]:1, 
                "lft_ctx_out"+c[4]:1, 
                "rht_ctx_out"+c[5]:1, 
                }
        if lpos not in cng_cnts[cng]: cng_cnts[cng][lpos]=1
