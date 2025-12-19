import regex

def lemma_insert(lemma, tag_skeleton):
    return regex.sub(r'<>', lemma, tag_skeleton)

def recreate_number_tags(person, number, prefix):
    if person == "1" and number == "Pl": return "1Pl"
    elif person == "2" and number == "Pl": return "2Pl"
    elif person == "2" and number == "1Pl": return "1Pl"
    elif person == "3" and number == "Pl" and prefix: return "2Pl"
    elif person == "3" and number == "Pl" and not prefix: return "3Pl"

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
    algonquanized["POS"] = broad_analysis["Head"]
    algonquanized["order"] = broad_analysis["Order"]
    algonquanized["negation"] = broad_analysis["Neg"]
    algonquanized["mode"] = broad_analysis["Mode"]
    if algonquianized["order"]:
        pass #special behavior for imperatives and conjuncts
    elif broad_analysis["S"]["Pers"] != '0': #inanimate subjects (VTA, VII) are special (not indexed by prefix)
        inversion = False
        if algonquianized["POS"].startswith("VAI") and broad_analysis["S"]["Pers"] == "3": #including VAIOs
            pass #need to make suffixes, also 3+2Pl if independent pret dub
        algonquianized["person_prefix"] = broad_analysis["S"]["Pers"]
        algonquianized["prefix_number"] = broad_analysis["S"]["Num"] #standard outputs from interpret() are just Pl instead of 3Pl, need to restore full tag
        hierarchy = {"1":2, "2":1, "3":3, "0": 4, "":5} #VAIOs?
        if hierarchy[broad_analysis["S"]["Pers"]] < hierarchy[broad_analysis["O"]["Pers"]]:
            inversion = True
            algonquianized["person_prefix"] = broad_analysis["O"]["Pers"]
            algonquianized["prefix_number"] = broad_analysis["O"]["Num"]
    return algonquianized
