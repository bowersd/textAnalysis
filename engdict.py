
def mk_glossing_dict(*strings):
    gd = {}
    for s in strings:
        chunked = s.split("\t")
        if chunked[0] not in gd: gd[chunked[0]] = chunked[1]
        #else: gd[chunked[0]] = gd[chunked[0]] + " HOMOPHONE DEFINITION>" + chunked[1]
        else: gd[chunked[0]] = gd[chunked[0]] + "/" + chunked[1]
    return gd

def gloss_fix(**gloss_dict):
    nu_dict = {}
    for key in gloss_dict:
        nu_dict[key] = "&#x20;".join(gloss_dict[key].split())
    return nu_dict
