import sys
import regex

def lemma_insert(lemma, tag_skeleton):
    return regex.sub(r'<>', lemma, tag_skeleton)

def recreate_number_tags(person, number, prefix):
    if person == "1" and number == "Pl": return "1Pl"
    elif person == "2" and number == "Pl": return "2Pl"
    elif person == "2" and number == "1Pl": return "1Pl"
    elif person == "3" and number == "Pl" and prefix: return "2Pl"
    elif person == "3" and number == "Pl" and not prefix: return "3Pl"
    elif person == "3" and number == "Obv" and not prefix: return "3Obv"
    else: return ""

def tag_assemble(**broad_analysis):
    algonquianized = {"person_prefix": "",
                      "person_suffix": "", #unclear in my mind whether this can cover cnj (VTA!) and indep VAI 3s
                      "preverbs": "", 
                      "reduplication": "", 
                      "stem": "",
                      "POS": "",
                      "order": "",
                      "theme_sign": "",
                      "negation": "",
                      "prefix_number": "", #this is the number component of the argument represented by person_prefix. The number component is, however, a suffix (it is realized in a different place than the person_prefix).
                      "mode": "",
                      "peripheral": "",
                      "diminutive": "",
                      "pejorative": "",
                      "contemptive": "",
                     }
    algonquianized["POS"] = broad_analysis["Head"]
    algonquianized["order"] = broad_analysis["Order"]
    algonquianized["negation"] = broad_analysis["Neg"]
    algonquianized["mode"] = broad_analysis["Mode"]
    if algonquianized["order"]:
        pass #special behavior for imperatives and conjuncts
    elif broad_analysis["S"]["Pers"] != '0': #inanimate subjects (VTA, VII) are special (not indexed by prefix)
        inversion = False
        if algonquianized["POS"].startswith("VAI") and broad_analysis["S"]["Pers"] == "3": #including VAIOs
            algonquianized["peripheral"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], False)
            algonquianized["person_suffix"] = broad_analysis["S"]["Pers"]
            if algonquianized["mode"] == ["prt", "dub"] and broad_analysis["S"]["Num"] == "Pl": #And we need to catch other pret dubs going to changed conjunct
                algonquianized["peripheral"] = "2Pl" #BUT THE 2Pl NEEDS TO BE BEFORE THE MODE SUFFIXES ... WE CAN'T JUST ALWAYS PUT PERIPHERAL AFTER MODE
        else:
            algonquianized["person_prefix"] = broad_analysis["S"]["Pers"]
            algonquianized["prefix_number"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True) #standard outputs from interpret() are just Pl instead of 3Pl, need to restore full tag
            hierarchy = {"1":2, "2":1, "3":3, "0": 4, "":5} #VAIOs?
            #does the broad analysis system handle inanimate subjects of VTAs right?
            if hierarchy[broad_analysis["S"]["Pers"]] > hierarchy[broad_analysis["O"]["Pers"]]:
                inversion = True
                algonquianized["person_prefix"] = broad_analysis["O"]["Pers"]
                algonquianized["prefix_number"] = recreate_number_tags(broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"], True)
    return algonquianized

def check_for_person_ties(**broad_analysis):
    if broad_analysis["S"]["Pers"] in ["1", "2"] or broad_analysis["O"]["Pers"] in ["1", "2"]:
        assert (not any([x == broad_analysis["O"]["Pers"] for x in [broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"][0]]])) and (not any([x == broad_analysis["S"]["Pers"] for x in [broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"][0]]]))
    if broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"]["Pers"] == "3":
        assert (broad_analysis["S"]["Num"] == "Obv" or broad_analysis["O"]["Num"] == "Obv") and not (broad_analysis["S"]["Num"] == "Obv" and broad_analysis["O"]["Num"] == "Obv")

def determine_inversion(**broad_analysis):
    hierarchy = {"1":2, "2":1, "3":3, "0": 4,} 
    if hierarchy[broad_analysis["S"]["Pers"]] > hierarchy[broad_analysis["O"]["Pers"]]: return True
    if broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"]["Pers"] == "3" and broad_analysis["S"]["Num"] == "Obv": return True
    return False

def vta_prefix_revision(in_progress, **broad_analysis):
    #don't call this unless there is inversion!
    in_progress["person_prefix"] = broad_analysis["O"]["Pers"]
    in_progress["prefix_number"] = recreate_number_tags(broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"], True)
    #a bit of superfluous work here, with a 3 prefix getting updated to 3 when 3Obv vs 3
    #up to this point, this script permits a 0 "inanimate" prefix, which I doubt actually exists in the mind of the ideal speaker-hearer :D

def vta_theme_selection(in_progress, inversion, **broad_analysis):
    #you already have person prefix and prefix number set to subject information in broad_analysis
    #you need to make revisions according to the theme sign
    #does the broad analysis system handle inanimate subjects of VTAs correctly?
    if inversion and broad_analysis["S"]["Pers"] not in ["1", "2"]: in_progress["theme_sign"] = "ThmInv" #3, 0 vs 1, 2, 3 #can't check for 3, because of inanimate subjects
    elif not inversion and broad_analysis["O"]["Pers"] == "3" : in_progress["theme_sign"] = "ThmDir" #1, 2, 3 vs 3
    elif not inversion and broad_analysis["O"]["Pers"] == "1": in_progress["theme_sign"] = "Thm1" #2 vs 1
    elif inversion and broad_analysis["S"]["Pers"] == "1" and broad_analysis["S"]["Num"] == "Pl": in_progress["theme_sign"] = "Thm1Pl2" #1pl vs 2
    else: in_progress["theme_sign"] = "Thm2" #1sg vs 2 #if inversion and broad_analysis["S"]["Pers"] == "1"

def vta_peripheral_setting(in_progress, inversion, **broad_analysis):
    align = {0:"O", 1:"S"}
    in_progress["peripheral"] = recreate_number_tags(broad_analysis[align[int(inversion)]]["Pers"], broad_analysis[align[int(inversion)]]["Num"], False) #this is going to put inanimate plural subject information in the periphery, make sure that's the correct move

def vta_adjustments(in_progress, **broad_analysis)
    #I remember inanimate subjects requiring extra special care, special morphotactics
    assert (not broad_analysis["S"]["Pers"] in ["1", "2", "0"] and broad_analysis["O"]["Num"] == "Obv") and (not broad_analysis["O"]["Pers"] in ["1", "2"] and broad_analysis["S"]["Num"] == "Obv") #preventing obviation outside of 3v3
    #what about inanimate obviatives (they are only legal in VIIs, should we ban them here?)?
    #what about VTAs getting inanimate objects?
    check_for_person_ties(**broad_analysis)
    inversion = determine_inversion(**broad_analysis) #boolean
    if inversion: vta_prefix_revision(in_progress, **broad_analysis)
    vta_theme_selection(in_progress, inversion, **broad_analysis)
    if in_progress["theme_sign"] in ["ThmDir", "ThmInv"]: vta_peripheral_setting(in_progress, inversion, **broad_analysis)

def vti_assembly(**broad_analysis):
    pass

def n_assembly(**broad_analysis):
    pass

def vai_assembly(**broad_analysis):
    pass

def vii_assembly(**broad_analysis):
    pass

def tag_linearize(lemma, **algonquianized):
    return "+".join([algonquianized["person_prefix"], lemma, algonquianized["POS"], algonquianized["order"], algonquianized["theme_sign"], algonquianized["negation"], algonquianized["prefix_number"], algonquianized["mode"], algonquianized["peripheral"]])

if __name__ == "__main__":
    specs = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":[], "Periph":"", "Pcp":{"Pers":"", "Num":""}, "Else": []}
    for x in sys.argv[2:]:
        key, val = x.split(":")
        if val[0] in ["1", "2", "3", "0"]:
            specs[key]["Pers"] = val[0]
            specs[key]["Num"] = val[1:]
        else: specs[key] = val
    print(tag_linearize(sys.argv[1], **tag_assemble(**specs)))
