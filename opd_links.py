import sys
import regex

def hyphens(string):
    return "-".join(regex.split( "'| ", regex.sub("(^')|('$)", "", string))).lower()

def stitch(lemma, pos):
    if pos == "VTI" and lemma.endswith("oon"): return hyphens(lemma)+"-"+"vti2"
    elif pos == "VTI" and lemma.endswith("in"): return hyphens(lemma)+"-"+"vti3"
    elif pos == "VAI" and lemma.endswith("am"): return hyphens(lemma)+"-"+"vai2"
    elif pos == "VAIPL": return hyphens(lemma)+"-"+"vai"
    elif pos == "VIIPL": return hyphens(lemma)+"-"+"vii"
    elif pos == "VAIO": return hyphens(lemma)+"-"+"vai-o"
    elif pos.startswith("ADV"): return hyphens(lemma)+"-"+pos[:3].lower()+"-"+pos[3:].lower()
    elif pos == "NUM": return hyphens(lemma)+"-"+"adv"+"-"+"num"
    elif pos.startswith("PC"): return hyphens(lemma)+"-"+pos[:2].lower()+"-"+pos[2:].lower()
    elif pos.startswith("PRON"): return hyphens(lemma)+"-"+pos[:4].lower()+"-"+pos[4:].lower()
    elif pos.startswith("Name"): return hyphens(lemma)+"-"+pos[:4].lower()+"-"+pos[4:].lower()
    else: return hyphens(lemma)+"-"+pos.lower()

def mk_opd_url(lemma, pos):
    return "https://ojibwe.lib.umn.edu/main-entry/"+stiched(lemma, pos)

if __name__ == "__main__":
    with open("opd_url_typo_check.txt", 'w') as ff_out:
        with open("opd_manual_links.csv", 'w') as f_out:
            for f in sys.argv[1:]:
                with open(f) as df:
                    for line in df:
                        x = line.strip().split(',')
                        stchd = stitch(x[0], x[2])
                        y = "https://ojibwe.lib.umn.edu/main-entry/"+stchd
                        if y != x[-1]: f_out.write(",".join([x[0], x[2], x[-1], '\n']))
                        pre = len("https://ojibwe.lib.umn.edu/main-entry/")
                        if stchd != x[-1][pre:pre+len(stchd)]:
                            ff_out.write(stchd+'\n')
                            ff_out.write(x[-1][pre:pre+len(stchd)]+'\n')
                            ff_out.write(x[-1]+'\n')
                            ff_out.write('\n')
                            
