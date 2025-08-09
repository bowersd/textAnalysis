def hyphens(string):
    return "-".join(string.split("'")).lower()

def stitch(lemma, pos):
    if pos == "VTI" and lemma.endswith("oon"): return hyphens(lemma)+"-"+"vti2"
    elif pos == "VTI" and lemma.endswith("in"): return hyphens(lemma)+"-"+"vti3"
    elif pos == "VAI" and lemma.endswith("am"): return hyphens(lemma)+"-"+"vai2"
    elif pos == "VAIPL": return hyphens(lemma)+"-"+"vai"
    elif pos == "VAIO": return hyphens(lemma)+"-"+"vai-o"
    elif pos.startswith("ADV"): return hyphens(lemma)+"-"+pos[:3].lower()+"-"+pos[3:].lower()
    elif pos == "NUM": return hyphens(lemma)+"-"+"adv"+"-"+"num"
    elif pos.startswith("PC"): return hyphens(lemma)+"-"+pos[:2].lower()+"-"+pos[2:].lower()
    elif pos.startswith("PRON"): return hyphens(lemma)+"-"+pos[:5].lower()+"-"+pos[5:].lower()
    elif pos.startswith("Name"): return hyphens(lemma)+"-"+pos[:5].lower()+"-"+pos[5:].lower()
    else: return hyphens(lemma)+"-"+pos.lower()

if __name__ == "__main__":
    pass
    
