import regex

def mk_glossing_dict(*strings):
    gd = {}
    for s in strings:
        chunked = s.split("\t")
        if chunked[0] not in gd: gd[chunked[0]] = chunked[1]
        #else: gd[chunked[0]] = gd[chunked[0]] + " HOMOPHONE DEFINITION>" + chunked[1]
        else: gd[chunked[0]] = gd[chunked[0]] + "/" + chunked[1]
    return gd


def retrieve_glosses(*lemmata, **gloss_dict):
    tinies = []
    for l in lemmata:
        try: gloss = gloss_dict[l]
        except KeyError:
            if "+" in l: 
                gloss = "-".join(retrieve_glosses(*l.split("+"), **gloss_dict, ))
            else: gloss = "?"
        tinies.append(gloss)
    return tinies

def wrap_glosses(*glosses):
    return ["'"+g+"'" for g in glosses]

def wrap_nod_entry_url(*lemmata, **nishIDdict):
    h = []
    #gotta split up the complex lemmata somehow
    for l in lemmata:
        tot = []
        #if '+' in l: tot.append(l)
        cmpd = l.split("+") #this can't do what is intended (split the IDs of conjuncts), and it is crashes when the word is not found in the dictionary
        for c in cmpd:
        #else:
            #cmpd = regex.split("(?<=n)-(?=n)", nishIDdict[l]) #this can't do what is intended (split the IDs of conjuncts), and it is crashes when the word is not found in the dictionary
            #for c in cmpd:
            try: 
                alts = regex.split("(?<=n)/(?=n)", nishIDdict[c])
                for i in range(len(alts)):
                    if i == 0: 
                        tot.append('<a href='+"'https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/{0}' target='_blank' rel='noopener noreferrer'>{1}</a>".format(alts[i], c))
                    else: tot.append('<a href='+"'https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/{0}' target='_blank' rel='noopener noreferrer'>(alt {1})</a>".format(alts[i], str(i)))
            except KeyError: tot.append(c)
        h.append(" ".join(tot))
    return h
    #return ['<a href="https://dictionary.nishnaabemwin.atlas-ling.ca/#/entry/'+ln[1]+'">'+ln[0]+'</a>' for ln in lemmataAndNishIDs]

def undo_html(string):
    return regex.sub('&\#x27;', "'", regex.sub('&lt;', '<', regex.sub('&gt;', '>', string)))
    #return regex.sub('&quot;', '', regex.sub('&lt;', '<', regex.sub('&gt;', '>', string)))


