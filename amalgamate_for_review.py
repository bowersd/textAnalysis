#take a (series of) text(s), pass each word through analyzer, write each word on a line with preceding, following context, outcome of analyzer, index in sentence, sentence length (so reverse indexing is possible), index of sentence, index of text

#Currently: table of words  -> table of sentences
#           entry           -> sentences containing exact match of entry headword
           
#Ideally:   entry           -> sentences containing match to lemma of entry headword
#so... add a field to the sentences table featuring lemma for every word in the real sentence field
    #do we also need to include field with headword ids in case of homophony?
#since we are at it, we might as well include grammatical analysis, gloss
#so: match in lemma (and id), display full sentence, gloss/lemma(which ever is practical)+grammatical analysis free translation
