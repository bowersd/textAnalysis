#import sys
#import parse
#todo: iteratives, participles, preverbs, imperatives, warnings/hints, shift to conjunct for prtdub, required initial change, vocative singulars, [123]+Ext|Nul+

def recreate_number_tags(person, number, prefix):
    if person == "2" and number == "1Pl" and prefix: return "1Pl"
    elif person == "3" and number == "Pl" and prefix: return "2Pl"
    elif number: return "".join([person, number])
    else: return ""

def check_for_person_ties(**broad_analysis):
    if broad_analysis["S"]["Pers"] in ["1", "2"] or broad_analysis["O"]["Pers"] in ["1", "2"]:
        assert (not any([x == broad_analysis["O"]["Pers"] for x in [broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]])) and (not any([x == broad_analysis["S"]["Pers"] for x in [broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]]]))
    if broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"]["Pers"] == "3":
        assert (broad_analysis["S"]["Num"] == "Obv" or broad_analysis["O"]["Num"] == "Obv") and not (broad_analysis["S"]["Num"] == "Obv" and broad_analysis["O"]["Num"] == "Obv")

def determine_inversion(**broad_analysis):
    hierarchy = {"1":2, "2":1, "3":3, "0": 4,} 
    if hierarchy[broad_analysis["S"]["Pers"]] > hierarchy[broad_analysis["O"]["Pers"]]: return True
    if broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"]["Pers"] == "3" and broad_analysis["S"]["Num"] == "Obv": return True
    return False

def prefix_update(alignment, **broad_analysis):
    return broad_analysis[alignment]["Pers"]
    #a bit of superfluous work here, with a 3 prefix getting updated to 3 when 3Obv vs 3
    #up to this point, this script permits a 0 "inanimate" prefix, which I doubt actually exists in the mind of the ideal speaker-hearer :D

def vta_central_update(alignment, **broad_analysis):
    if alignment == "O" and broad_analysis["S"]["Pers"] == "2" and broad_analysis["O"] == {"Pers":"1", "Num":"Pl"}: #worthwhile to flag to user that 2 v 1Pl is always ambiguous for subject number (also for cnj)
        return recreate_number_tags("1", "Pl", False) #value of boolean is irrelevant here, but strictly speaking, we are not indexing the prefix's number
    return recreate_number_tags(broad_analysis[alignment]["Pers"], broad_analysis[alignment]["Num"], True) 
    #a bit of superfluous work here, with a 3 prefix getting updated to 3 when 3Obv vs 3
    #up to this point, this script permits a 0 "inanimate" prefix, which I doubt actually exists in the mind of the ideal speaker-hearer :D

def vta_theme_update(inversion, **broad_analysis):
    #you already have person prefix and prefix number set to subject information in broad_analysis
    #you need to make revisions according to the theme sign
    #does the broad analysis system handle inanimate subjects of VTAs correctly?
    if inversion and broad_analysis["S"]["Pers"] not in ["1", "2"]: return  "ThmInv" #3, 0 vs 1, 2, 3 #can't check for 3, because of inanimate subjects
    elif not inversion and broad_analysis["O"]["Pers"] == "3" : return  "ThmDir" #1, 2, 3 vs 3
    elif not inversion and broad_analysis["O"]["Pers"] == "1": return  "Thm1" #2 vs 1
    elif inversion and broad_analysis["S"]["Pers"] == "1" and broad_analysis["S"]["Num"] == "Pl": return  "Thm1Pl2" #1pl vs 2
    else: return  "Thm2" #1sg vs 2 #if inversion and broad_analysis["S"]["Pers"] == "1"

def vta_peripheral_update(alignment, **broad_analysis):
    return recreate_number_tags(broad_analysis[alignment]["Pers"], broad_analysis[alignment]["Num"], False) #this is going to put inanimate plural subject information in the periphery, make sure that's the correct move

def vta_cnj_theme_update(**broad_analysis):
    if broad_analysis["S"]["Pers"] == "0": return "ThmInv" #ironclad first
    elif broad_analysis["O"]["Pers"] == "1": return "Thm1"
    elif broad_analysis["S"] == {"Pers":"1", "Num":"Pl"} and broad_analysis["O"]["Pers"] == "2": return "Thm1Pl2"
    elif not broad_analysis["Neg"] and broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"] == {"Pers":"2", "Num": ""}: return "Thm2b"
    elif broad_analysis["Neg"] and broad_analysis["S"] == {"Pers":"3", "Num":""} and broad_analysis["O"] == {"Pers":2, "Num":"Pl"}: return "ThmInv" #must preced next conditional, otherwise you would expect Thm2a to appear
    elif broad_analysis["O"]["Pers"] == "2" : return "Thm2a"
    #{start crucial ordering/specific before general
    #these lines must precede the one that follows them
    elif broad_analysis["Neg"] and broad_analysis["O"]["Pers"] == "3": return "ThmDir"
    elif not broad_analysis["Neg"] and broad_analysis["O"]["Pers"] == "3": return "ThmNul"
    #}end crucial ordering/specific before general
    #this line must follow the ones that precede it
    elif broad_analysis["O"] == {"Pers":"3", "Num":"Obv"} and broad_analysis["S"]["Pers"] == "3": return "ThmDir"
    else: return "ThmInv" #if broad_analysis["S"] == {"Pers": "3", "Num":"Obv"}: return "ThmInv"

def vta_cnj_continuation(theme_sign, **broad_analysis):
    #Thm2b,                   Subj,                         (Mode)
    #Thm1,   (Neg), (ObjNum)  Subj (but no 2|2Pl if 1Pl),   (Mode)
    #ThmInv, (Neg), (Obj)     (Subj) (but no 2 if 1Pl),     (Mode)
    #Thm2a,  (Neg), (Obj)     (Subj)                        (Mode)
    #ThmDir, (Neg), Subj      (Obj)                         (Mode)
    #ThmNul, (Neg), Subj       Obj                          (Mode)
    h = []
    if theme_sign == "Thm2b": h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])) #this makes 2, 2Pl, recreate_number_tags() only makes 2Pl
    if theme_sign == "Thm1" and broad_analysis["O"]["Num"] == "Pl": h.append(recreate_number_tags("1", "Pl", False))
    if theme_sign == "Thm1" and not broad_analysis["O"]["Num"] and broad_analysis["S"]["Pers"] == "2": h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])) #worthwhile to flag to user the systematic ambiguity for subject number in 2 v 1Pl
    if theme_sign == "Thm1" and broad_analysis["S"]["Pers"] == "3": h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]))
    if theme_sign == "ThmInv" and broad_analysis["O"]["Pers"] in ["2", "1"] and broad_analysis["S"]["Pers"] != "3": h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])) #inverse theme without 3rd marking -> 0 subj and 2/1 O
    if theme_sign == "ThmInv" and broad_analysis["O"]["Pers"] == ["2"] and broad_analysis["S"]["Pers"] == "3": #this is just a few negated forms where you get both 2 marking and 3 
        h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]]))
        h.append(broad_analysis["S"]["Pers"])
    if theme_sign == "ThmInv" and broad_analysis["O"]["Pers"] == ["3"]: h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])) #a case of ambiguity, where you can have either S=0 or S=3Obv, worthwhile to flag to user, also worth it to flag that 0Plis dropped in cnj (as in VII, VTI)
    if theme_sign == "Thm1Pl2": h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]]))
    if theme_sign == "Thm2a" and broad_analysis["O"]["Num"] and broad_analysis["S"]["Pers"] == "3": 
        h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]]))
        h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]))
    if theme_sign == "Thm2a" and not broad_analysis["O"]["Num"] and broad_analysis["S"]["Pers"] == "3": h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]))
    if theme_sign == "Thm2a" and broad_analysis["S"]["Pers"] == "1": h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]]))
    if theme_sign == "ThmDir" and broad_analysis["S"]["Pers"] in ["1", "2"]: 
        h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]))
        h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])) #always 3
    if theme_sign == "ThmDir" and broad_analysis["S"]["Pers"] == "3": h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]))
    if theme_sign == "ThmNul": #I cheated in the dubitatives, which have an "aa" aka ThmDir, worthwhile to flag to user
        h.append("".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])) #always 2|1 
        h.append("".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])) #always 3
    return "+".join(h)
    

def vta_adjustments(**broad_analysis):
    assert (not (broad_analysis["S"]["Pers"] in ["1", "2", "0"] and broad_analysis["O"]["Num"] == "Obv")) and (not (broad_analysis["O"]["Pers"] in ["1", "2"] and broad_analysis["S"]["Num"] == "Obv")) #preventing obviation outside of 3v3
    #what about inanimate obviatives (they are only legal in VIIs, should we ban them here?)?
    #what about VTAs getting inanimate objects?
    h = {"Person_prefix":"", "Central":"", "Theme_sign":"", "Periph":""}
    check_for_person_ties(**broad_analysis)
    if broad_analysis["S"]["Pers"] == "X": #revise broad analysis and h for passive/unspecified subject
        broad_analysis["POS"] = "VAI"
        broad_analysis["Lemma"] += "+VTA+ThmPas"
        broad_analysis["S"] = broad_analysis["O"]
        h = vai_adjustments(**broad_analysis)
    elif broad_analysis["Order"] == "Cnj":
        h["Theme_sign"] = vta_cnj_theme_update(**broad_analysis)
        h["Central"] = vta_cnj_continuation(h["Theme_sign"], **broad_analysis) #independent central is in an analogous spot to the cnj argument elaborations
    elif broad_analysis["Order"] == "Imp":
        h["Central"] = "".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])
        h["Periph"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
        #Delayed imperative tag is treated as part of the Neg category, and so is handled in the front end conversion
    else:
        inversion = determine_inversion(**broad_analysis) #boolean
        theme_align = {0:"O", 1:"S"}
        #a bit inefficient to re-assign S to person prefix and prefix number when not inverted. But 2 v 1pl/2pl v 1pl -> central 1pl, so there is a mismatch that must be managed. Also, the functions are more modular this way
        h["Person_prefix"] = prefix_update(theme_align[int(not inversion)], **broad_analysis) #uninverted: prefix/central number slot = subj, inverted, prefix/central number slot = obj
        h["Central"] = vta_central_update(theme_align[int(not inversion)], **broad_analysis) #uninverted: prefix/central number slot = subj, inverted, prefix/central number slot = obj
        h["Theme_sign"] = vta_theme_update(inversion, **broad_analysis)
        if h["Theme_sign"] in ["ThmDir", "ThmInv"]: h["Periph"] = vta_peripheral_update(theme_align[int(inversion)], **broad_analysis)
        if broad_analysis["S"]["Pers"] == "0": h["Theme_sign"] += "+0"
    return h

def vti_adjustments(**broad_analysis):
    h = {"Person_prefix":"", "Central":"", "Periph":""}
    if broad_analysis["Order"] == "Cnj": h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]]) #it is the exact same VAIs, worthwhile to flag to user
    elif broad_analysis["Order"] == "Imp": 
        h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
        if h["Central"] == "21Pl": h["Periph"] = "".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])
        #Delayed imperative tag is treated as part of the Neg category, and so is handled in the front end conversion
    else:
        #no guidance on passive/unspecified subjects from Rand's book, worthwhile to flag to users
        h["Person_prefix"] = broad_analysis["S"]["Pers"]
        h["Central"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True)
        if broad_analysis["S"]["Pers"] == "0": #presumably inanimate subjects are treated as 3 subjects ... but this would create a "person" tie? worthwhile to flag to users
            h["Person_prefix"] = "3"
            h["Central"] = recreate_number_tags("3", broad_analysis["S"]["Num"], True)
        h["Periph"] = recreate_number_tags(broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"], False)
    return h

def vai_adjustments(**broad_analysis):
    h = {"Person_prefix":"", "Central":"", "Periph":""}
    if broad_analysis["Order"] == "Cnj": h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
    elif broad_analysis["Order"] == "Imp": 
        h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
        #Delayed imperative tag is treated as part of the Neg category, and so is handled in the front end conversion
    else:
        if broad_analysis["S"]["Pers"] in ["1", "2"]: 
            h["Person_prefix"] = broad_analysis["S"]["Pers"]
            h["Central"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True)
        else:
            h["Central"] = broad_analysis["S"]["Pers"]
            h["Periph"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], False)
    return h

def vaio_adjustments(**broad_analysis):
    h = {"Person_prefix":"", "Central":"", "Periph":""}
    if broad_analysis["Order"] == "Cnj": h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
    elif broad_analysis["Order"] == "Imp": 
        h["Central"] = "".join([broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"]])
        if h["Central"] == "21Pl" and broad_analysis["O"]["Num"] == "Pl": h["Periph"] = "".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])
    else:
        #no guidance on passive/unspecified subjects from Rand's book, worthwhile to flag to users
        h["Person_prefix"] = broad_analysis["S"]["Pers"]
        h["Central"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True)
        if broad_analysis["S"]["Pers"] == "3" and broad_analysis["O"]["Pers"] == "3": h["Periph"] = "3Obv" #nest of obviation restrictions worthwhile to flag to user. Rand's book is a bit inconsistent (positives are not marked as obv, but negatives are)
        elif not broad_analysis["S"]["Num"] and not broad_analysis["O"]["Num"] and not broad_analysis["Mode"]: h["Periph"] = broad_analysis["O"]["Pers"] #restriction to singular subjects worthwhile to flag to user. Rand's book is a bit inconsistent (positives have 3 v 0s, but not negatives)
        elif broad_analysis["O"]["Num"] == "Pl": h["Periph"] = "".join([broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"]])  #this implements an obviation restriction by omission (you can't specify obviative objects outside of the 3v3 context). worthwhile to flag to user. 
    return h

def vii_adjustments(**broad_analysis):
    h = {"Central":"0", "Periph":""}
    if broad_analysis["S"]["Num"].startswith("Obv"): h["Central"] += "Obv"
    if broad_analysis["Order"] != "Cnj" and broad_analysis["S"]["Num"].endswith("Pl"): h["Periph"] = "0Pl" #silently dropping 0Pl in cnj, worthwhile to flag to user
    return h

def n_adjustments(**broad_analysis):
    h = {
            "Person_prefix":broad_analysis["S"]["Pers"], 
            "ConDim":broad_analysis["ConDim"], 
            "PosTheme":broad_analysis["PosTheme"], 
            "Pejorative":broad_analysis["Pejorative"], 
            "Central":recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True), 
            "Mode":broad_analysis["Mode"] ,
            "Periph":broad_analysis["Periph"]
            }
    #worthwhile to flag requirement of prefixes on dependent stems
    if broad_analysis["Head"].endswith("D") and not h["Person_prefix"]: raise ValueError("dependent nouns require a possessor")
    if h["Person_prefix"] == "3" and broad_analysis["Periph"] == "Pl": h["Periph"] = "" #worthwhile to flag to user
    if not h["Person_prefix"] and h["PosTheme"]: h["PosTheme"] = "" #worthwhile to flag to user
    return h

def tag_assemble(**broad_analysis):
    algonquianized = {"Person_prefix": "",
                      #"Person_suffix": "", #for vai 3 -> or we could use Central, the number suffixes are in comp dist with 3, X
                      "Preverbs": "", 
                      "Reduplication": "", 
                      #"Stem": "", #this isn't being used thus far (dec 2025)
                      "POS": "",
                      "Order": "",
                      "PosTheme": "",
                      "Neg": "",
                      "Central": "", #this is the suffix region where number of the person_prefix argument in independent order verbs is realized. Person/number information in addition to the theme sign in cnjs is realized here
                      "Mode": "",
                      "Periph": "",
                      "ConDim": "",
                      "Pejorative": "",
                     }
    algonquianized["POS"] = broad_analysis["Head"]
    algonquianized["Order"] = broad_analysis["Order"]
    algonquianized["Neg"] = broad_analysis["Neg"]
    algonquianized["Mode"] = "+".join(broad_analysis["Mode"]) #Mode starts out as a list because you can have Dub, Prt, Prt Dub
    adjustments = {}
    if algonquianized["POS"] == "VTA": adjustments = vta_adjustments(**broad_analysis)
    elif algonquianized["POS"] == "VAI": adjustments = vai_adjustments(**broad_analysis)
    elif algonquianized["POS"] == "VAIO": adjustments = vaio_adjustments(**broad_analysis)
    elif algonquianized["POS"] == "VTI": adjustments = vti_adjustments(**broad_analysis)
    elif algonquianized["POS"] == "VII": adjustments = vii_adjustments(**broad_analysis)
    elif algonquianized["POS"].startswith("N"): adjustments = n_adjustments(**broad_analysis)
    for a in adjustments:
        if adjustments[a]: algonquianized[a] = adjustments[a]
    #if algonquianized["order"]:
    #    pass #special behavior for imperatives and conjuncts
    #elif broad_analysis["S"]["Pers"] != '0': #inanimate subjects (VTA, VII) are special (not indexed by prefix)
    #    inversion = False
    #    if algonquianized["POS"].startswith("VAI") and broad_analysis["S"]["Pers"] == "3": #including VAIOs
    #        algonquianized["periph"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], False)
    #        algonquianized["person_suffix"] = broad_analysis["S"]["Pers"]
    #        if algonquianized["mode"] == ["prt", "dub"] and broad_analysis["S"]["Num"] == "Pl": #And we need to catch other pret dubs going to changed conjunct
    #            algonquianized["periph"] = "2Pl" #BUT THE 2Pl NEEDS TO BE BEFORE THE MODE SUFFIXES ... WE CAN'T JUST ALWAYS PUT PERIPHERAL AFTER MODE
    #    else:
    #        algonquianized["person_prefix"] = broad_analysis["S"]["Pers"]
    #        algonquianized["central"] = recreate_number_tags(broad_analysis["S"]["Pers"], broad_analysis["S"]["Num"], True) #standard outputs from interpret() are just Pl instead of 3Pl, need to restore full tag
    #        hierarchy = {"1":2, "2":1, "3":3, "0": 4, "":5} #VAIOs?
    #        #does the broad analysis system handle inanimate subjects of VTAs right?
    #        if hierarchy[broad_analysis["S"]["Pers"]] > hierarchy[broad_analysis["O"]["Pers"]]:
    #            inversion = True
    #            algonquianized["person_prefix"] = broad_analysis["O"]["Pers"]
    #            algonquianized["central"] = recreate_number_tags(broad_analysis["O"]["Pers"], broad_analysis["O"]["Num"], True)
    return algonquianized

def tag_linearize(lemma, **algonquianized):
    suffix_slots = ["POS", "Order", "Neg", "Central", "Mode", "Periph"]
    if algonquianized["POS"] == "VTA": suffix_slots = ["POS", "Order", "Theme_sign", "Neg", "Central", "Mode", "Periph"]
    if algonquianized["POS"].startswith("N"): suffix_slots = ["POS", "ConDim", "PosTheme", "Pejorative", "Central", "Mode", "Periph"]
    h = [lemma]
    if algonquianized["Person_prefix"]: h = [algonquianized["Person_prefix"], lemma]
    for ss in suffix_slots: 
        if algonquianized[ss]: h.append(algonquianized[ss])
    return "+".join(h)

#if __name__ == "__main__":
#    #specs = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "DerivChain":"", "Head":"", "Order":"", "Neg":"", "Mode":[], "Periph":"", "Pcp":{"Pers":"", "Num":""}, "Else": []} #going to have to be careful with Mode, Else... #original layout from alg_morphological ummary
#    specs = {"S":{"Pers":"", "Num":""}, "O":{"Pers":"", "Num":""}, "Head":"", "Order":"", "Neg":"", "Mode":[], "Periph":"", "ConDim":"", "PosTheme":"", "Pejorative":"" } 
#    for x in sys.argv[2:]:
#        key, val = x.split(":")
#        if val[0] in ["1", "2", "3", "0"]:
#            specs[key]["Pers"] = val[0]
#            specs[key]["Num"] = val[1:]
#        elif key == "Mode": specs[key].append(val)
#        else: specs[key] = val
#    print(" ".join(sys.argv[1:]))
#    linearized = tag_linearize(sys.argv[1], **tag_assemble(**specs))
#    print(linearized)
#    output = parse.parse_native('../otw/src/morphophonologyclitics_generate.hfstol', linearized)
#    for o in output: print(output[o])
