import regex

def lemma_insert(lemma, tag_skeleton):
    return regex.sub(r'<>', lemma, tag_skeleton)

def tag_assemble(**broad_analysis):
    pass
