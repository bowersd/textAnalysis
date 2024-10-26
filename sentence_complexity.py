#initial plan: order Nishnaabemwin sentences, favoring short sentences, low transitivity and independent order 
#common readability scores in English weigh polysyllabicity and length of sentence
#this suggests favoring phonological simplicity too (with short words? simple clusters? few syncope alternations?)
#ordering, numerical score, enumerate components

import re

def alg_morph_counts(*sentences):
    pos_score  = 0
    morph_score = 0
    phon_score = 0
    sent_length_score = 0
    word_length_score = 0
    scores = []
    for s in sentences: 
        s_score = [
                [0,0,0,0,0],[0,0,0],#pos (VTA,VAI,VAIO,VTI,VII),order (cnj,ind,imp)
                #[0] #number of words with stress shift alternations
                #preverbs? mood? discontinuous person/number realization?
                ]
        for w in s:
            if w["pos"] == "VTA": s_score[0][0] += 1
            if w["pos"] == "VAIO": s_score[0][1] += 1
            if w["pos"] == "VTI": s_score[0][2] += 1
            if w["pos"] == "VAI": s_score[0][3] += 1
            if w["pos"] == "VII": s_score[0][4] += 1
            if w["order"] == "cnj": s_score[1][0] += 1
            if w["order"] == "ind": s_score[1][2] += 1
            if w["order"] == "imp": s_score[1][1] += 1
            #if w["alts"]: s_score[2][0] += 1
        scores.append(s_score)
    return scores

def alg_morph_score_rate(*counts):
    at_bats = 0
    total_bases_pos = 0
    order_bases = [0, 0]
    for c in counts:
        at_bats += sum(cnts[0])
        total_bases_pos += c[0][0]*4 #vtas are 'home run', way more complex than the others
        total_bases_pos += c[0][1]*3 #vaios are 'triple', kind of a weird corner case addition to VAIs
        total_bases_pos += c[0][2]*2 #vtis are 'double', a fairly straightforward variant of VAIs
        total_bases_pos += c[0][3]   #vais are 'single', your run of the mill verb
        #total_bases_pos += c[0][4]   #viis are 'out', a super simple type of verb
        order_bases[0] += c[1][0] #cnj has irregular phonology, difficult to explain context of use
        order_bases[1] += c[1][1] #ind has long distance dependencies, stronger ripple effect phonology, simpler context of use
        #imp is basic, not counted
    return [total_bases_pos/at_bats, (order_bases[0]-order_bases[1]/abs(order_bases[0]-order_bases[1]))(*(max(order_bases)/at_bats))] #slugging pct pos complexity, pct independent/cnj (negative for mostly independent, positive for mostly cnj)

    
def flesch_reading_ease_score(*sentences):
    word_count = 0
    sentence_count = 0
    syllable_count = 0
    for s in sentences:
        sentence_count += 1
        for word in s:
            word_count += 1
            syllable_count += len(re.findall(r"(^|[^aeioAEIO])[aeioAEIO]", word)
    return (206.835 - (1.015*(word_count/sentence_count))-(84.6*(syllable_count/word_count)))

def flesch_reading_grade_level(*sentences):
    word_count = 0
    sentence_count = 0
    syllable_count = 0
    for s in sentences:
        sentence_count += 1
        for word in s:
            word_count += 1
            syllable_count += len(re.findall(r"(^|[^aeioAEIO])[aeioAEIO]", word)
    return ((0.39*(word_count/sentence_count))+(11.8*(syllable_count/word_count)))-15.59
