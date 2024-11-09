#initial plan: order Nishnaabemwin sentences, favoring short sentences, low transitivity and independent order 
#common readability scores in English weigh polysyllabicity and length of sentence
#this suggests favoring phonological simplicity too (with short words? simple clusters? few syncope alternations?)
#ordering, numerical score, enumerate components

import regex

def interface(postags, *m_parse_los):
    h = []
    assert all([type(m) == list for m in m_parse_los])
    for s in m_parse_los:
        distilled = []
        for m in s:
            formatted = {"analysis":m}
            if regex.search(r"({0})(.*({0}))?".format(postags), m): 
                formatted["pos"] = [x for x in regex.search(r"({0})(.*({0}))?".format(postags), m)[0].split("+") if x][-1] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
                if formatted["pos"] in ["VAI", "VAIO", "VTA", "VTI", "VII"] and regex.search(r"(Imp|Cnj)", m): 
                    formatted["order"] = regex.search(r"(Imp|Cnj)", m)[0] #Denominal words may contain Dim, etc, but plain nouns will omit this if only POS tags are used as boundaries
                elif formatted["pos"] in ["VAI", "VAIO", "VTA", "VTI", "VII"] and not regex.search(r"(Imp|Cnj)", m): formatted["order"] = "Ind"
                else: 
                    formatted["order"] = ""
            if not regex.search(r"({0})(.*({0}))?".format(postags), m): 
                formatted["pos"] = ""
                formatted["order"] = ""
            distilled.append(formatted)
        h.append(distilled)
    return h
    
def alg_morph_counts(*sentences):
    scores = []
    for s in sentences: 
        s_score = [
                [0,0,0,0,0],[0,0,0], [0]#pos (VTA,VAI,VAIO,VTI,VII),order (cnj,ind,imp), total morphemes
                #[0] #number of words with stress shift alternations
                #preverbs? mood? discontinuous person/number realization?
                ]
        for w in s:
            if w["pos"] == "VTA": s_score[0][0] += 1
            if w["pos"] == "VAIO": s_score[0][1] += 1
            if w["pos"] == "VTI": s_score[0][2] += 1
            if w["pos"] == "VAI": s_score[0][3] += 1
            if w["pos"] == "VII": s_score[0][4] += 1
            if w["order"] == "Cnj": s_score[1][0] += 1
            if w["order"] == "Ind": s_score[1][1] += 1
            if w["order"] == "Imp": s_score[1][2] += 1
            #if w["alts"]: s_score[2][0] += 1
            s_score[2][0] += morpheme_count(w["analysis"])
        scores.append(s_score)
    return scores

def morpheme_count(analysis):
    return len(analysis.split("+"))

def alg_morph_score_rate(*counts):
    at_bats = 0.001
    total_bases_pos = 0
    main_order_counts = [0, 0]
    total_morphemes = 0
    for c in counts:
        if sum(c[0]) == 0: print("degenerate verb-less sentence detected")
        at_bats += sum(c[0])
        total_bases_pos += c[0][0]*4 #vtas are 'home run', way more complex than the others
        total_bases_pos += c[0][1]*3 #vaios are 'double' kind of a weird corner case addition to VAIs, more complex only in the sense that you have to add another wrinkle (so maybe a triple)?
        total_bases_pos += c[0][2]*3 #vtis are 'double', a fairly straightforward variant of VAIs
        total_bases_pos += c[0][3]*2   #vais are 'single', your run of the mill verb
        total_bases_pos += c[0][4]   #viis are 'out', a super simple type of verb
        main_order_counts[0] += c[1][0] #cnj has irregular phonology, difficult to explain context of use
        main_order_counts[1] += c[1][1] #ind has long distance dependencies, stronger ripple effect phonology, simpler context of use
        #imperatives are not worth tracking
        total_morphemes += c[2][0] #maybe take out the core morphemes present in the verb? (or at least don't count the pos tags?) all just makes things more complicated...
    if main_order_counts[0] > main_order_counts[1]: order_sign = 1
    elif main_order_counts[0] <= main_order_counts[1]: order_sign = -1
    return [round(total_bases_pos/at_bats, 1), round((order_sign*(max(main_order_counts)/at_bats)), 1), round(total_morphemes/len(counts), 1)] #slugging pct pos complexity, pct independent/cnj (negative for mostly independent, positive for mostly cnj), average sentence length in morphemes

def flesch_reading_ease_score(*sentences):
    word_count = 0
    sentence_count = 0
    syllable_count = 0
    for s in sentences:
        sentence_count += 1
        for word in s:
            word_count += 1
            syllable_count += len(regex.findall(r"(^|[^aeioAEIO])[aeioAEIO]", word))
    return (206.835 - (1.015*(word_count/sentence_count))-(84.6*(syllable_count/word_count)))

def flesch_reading_grade_level(*sentences):
    word_count = 0
    sentence_count = 0
    syllable_count = 0
    for s in sentences:
        sentence_count += 1
        for word in s:
            word_count += 1
            syllable_count += len(regex.findall(r"(^|[^aeioAEIO])[aeioAEIO]", word))
    return ((0.39*(word_count/sentence_count))+(11.8*(syllable_count/word_count)))-15.59
