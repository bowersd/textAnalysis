import regex

def lemma_insert(lemma, tag_skeleton):
    return regex.sub(r'<>', lemma, tag_skeleton)

def tag_assemble(**broad_analysis):
    algonquianized = {"person_prefix": [],
                      "preverbs": [], 
                      "reduplication": [], 
                      "stem": [],
                      "POS": [],
                      "order": [],
                      "theme_sign": [],
                      "negation": [],
                      "prefix_number": [],
                      "mode": [],
                      "peripheral:" [],
                      "diminutive": [],
                      "pejorative": [],
                      "contemptive": [],
                     }
    algonquanized["order"] = broad_analysis["Order"]
    algonquanized["negation"] = broad_analysis["Neg"]
    algonquanized["mode"] = broad_analysis["Mode"]
    if algonquianized["order"]:
        pass #special behavior for imperatives and conjuncts
    elif broad_analysis["S"]["Pers"] != '0': #inanimate subjects (VTA, VII) are special
        inversion = False
        algonquianized["person_prefix"] = broad_analysis["S"]["Pers"]
        algonquianized["prefix_number"] = broad_analysis["S"]["Num"] #standard outputs from interpret() are just Pl instead of 3Pl, need to restore full tag
        hierarchy = {"1":2, "2":1, "3":3, "0": 4, "":5} #VAIOs?
        if hierarchy[broad_analysis["S"]["Pers"]] < hierarchy[broad_analysis["O"]["Pers"]]:
            inversion = True
            algonquianized["person_prefix"] = broad_analysis["O"]["Pers"]
            algonquianized["prefix_number"] = broad_analysis["O"]["Num"]
    return algonquianized
