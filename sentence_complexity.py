#initial plan: order Nishnaabemwin sentences, favoring short sentences, low transitivity and independent order 
#common readability scores in English weigh polysyllabicity and length of sentence
#this suggests favoring phonological simplicity too (with short words? simple clusters? few syncope alternations?)
#ordering, numerical score, enumerate components

import re

def nish_sort(*sentences):
    pos_score  = 0
    morph_score = 0
    phon_score = 0
    sent_length_score = 0
    word_length_score = 0
    scores = []
    for s in sentences: pass
    return scores
    
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
