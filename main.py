#import pyodide
#await pyodide.loadPackage("micropip")
import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/e0/02/c10a69ff21d6679a6b6e28c42cd265bec2cdd9be3dcbbee830a10fa4b0e5/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.3.0-py2.py3-none-any.whl'
    #'https://files.pythonhosted.org/packages/eb/f5/3ea71e974dd0117b95a54ab2c79d781b4376d257d91e4c2249605f4a54ae/pyhfst-1.2.0-py2.py3-none-any.whl'
    #'./pyhfst-1.2.0-py2.py3-none-any.whl'
)
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
from pyweb import pydom
import pyscript
import asyncio
from pyodide.ffi.wrappers import add_event_listener
from pyodide.http import pyfetch
#from pyodide.http import open_url
#from pyscript import fetch
import regex
import pyhfst
import tabulate
import sentence_complexity as sc
import opd_links as opd
import pure_python_basic_text as ppbt
import pure_python_analysis as ppa
import pure_python_glossing as ppg
import js


# Post-render hook: lets standalone exportTables.js bind/refresh controls after innerHTML updates.
def _after_render():
    try:
        js.refreshExportControls()
    except Exception as e:
        # Keep app alive even if exportTables.js didn't load
        print("refreshExportControls unavailable:", e)

###functions and constants for doing things within the web page
#constants

gdict = ppg.mk_glossing_dict(*ppbt.readin("./copilot_otw2eng.txt"))
iddict = ppg.mk_glossing_dict(*ppbt.readin("./otw2nishID.txt"))
pos_regex = "".join(ppbt.readin("./pos_regex.txt"))
ciw_pos_regex_opd = "".join(ppbt.readin("./ciw_pos_regex_opd.txt"))
ciw_pos_regex_model = "".join(ppbt.readin("./ciw_pos_regex_model.txt"))
opd_manual_links = {}
for row in ppbt.readin("opd_manual_links.csv"):
    tabbed = row.split(',')
    opd_manual_links[(tabbed[0], tabbed[1])] = tabbed[2]

form_values = {
        "rhodes":{"order":"1", "url":"", "file":"./morphophonologyclitics_analyze.hfstol"},
        "rhodes_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_relaxed.hfstol", "file":None},
        "corbiere":{"order":"", "url":"", "file": "./morphophonologyclitics_analyze_mcor_spelling.hfstol"},
        "corbiere_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/syncopated_analyzer_mcor_relaxed.hfstol", "file":None},
        "no_deletion":{"order":"", "url":"",  "file": "./morphophonologyclitics_analyze_unsyncopated.hfstol"},
        "no_deletion_relaxed":{"order":"", "url":"https://raw.githubusercontent.com/bowersd/otw/releases/download/v.0.1.0-alpha/unsyncopated_analyzer_relaxed.hfstol",  "file":None},
        "western":{"order":"", "url":"",  "file": "./morphophonology_analyze_border_lakes.hfstol"},
        }

def interlinearize(parsed_data):
    revised = ""
    for i in range(len(parsed_data["m_parse_lo"])):
        table = [
                ["Original Material:"] + parsed_data["original"][i],
                ["Narrow Analysis:"] + parsed_data["m_parse_lo"][i], 
                ["Broad Analysis:"] + parsed_data["m_parse_hi"][i], 
                ["NOD/OPD Entry:"] + parsed_data["lemma_links"][i], 
                ["Terse Translation:"] + parsed_data["tinies"][i]
                ] 
        lines_out = tabulate.tabulate(table, tablefmt='html')
        for lo in lines_out.split('\n'): #a loop isn't really necessary here
            if "NOD/OPD Entry" in lo: revised += ppg.undo_html(lo)+'\n'
            #elif "Terse Translation" in lo and parsed_data["english"]: 
            #    revised += lo+'\n'
            #    transline = '<tr><td>Free Translation</td><td colspan="{0}">'+"'{1}'<td></tr>\n"
            #    revised += transline.format(str(len(parsed_data["m_parse_lo"])), parsed_data["english"][i])
            else: revised += lo+'\n'
    return revised

def interlinearize_blocks(parsed_data): #use kwargs
    ordered = []
    print("passed in data")
    print(parsed_data)
    for i in range(len(parsed_data["m_parse_lo"])):
        ordered.extend([
            ["Original Material:"] + parsed_data["original"][i],
            ["Narrow Analysis:"] + parsed_data["m_parse_lo"][i], 
            ["Broad Analysis:"] + parsed_data["m_parse_hi"][i], 
            ["NOD/OPD Entry:"] + parsed_data["lemma_links"][i], 
            ["Terse Translation:"] + parsed_data["tinies"][i]])
    return ordered

def interlinearize_format(*blocks):
    revised = ""
    for b in blocks:
        lines_out = tabulate.tabulate(b, tablefmt='html')
        for lo in lines_out.split('\n'): #a loop isn't really necessary here
            if "NOD/OPD Entry" in lo: revised += ppg.undo_html(lo)+'\n'
            else: revised += lo+'\n'
    return revised


def nu_lexical_perspective(parsed_data):
    lemmata = {}
    for i in range(len(parsed_data["lemmata"])): 
        for j in range(len(parsed_data["lemmata"][i])):
            if parsed_data["lemmata"][i][j] not in lemmata: 
                lemmata[parsed_data["lemmata"][i][j]] = {
                    "tokens":{parsed_data["original"][i][j]: [(i,j)]},
                    "link":parsed_data["lemma_links"][i][j],
                    "pos":parsed_data["m_parse_hi"][i][j].split()[0],
                    "tiny":parsed_data["tinies"][i][j]
                    }
            elif parsed_data["original"][i][j] not in lemmata[parsed_data["lemmata"][i][j]]["tokens"]: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]] = [(i, j)]
            else: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]].append((i, j))
    return lemmata

def nu_sublexical_perspective_init(token, coord, link, pos, tiny):
    #as you go through the text, assign new lemmata to this
    #update a lemma with new tokens by assigning x[lemma]["tokens"][coord] = token
    #COULD PUT EVERYTHING WORD-SPECIFIC HERE. SENTENCES WOULD JUST BE VECTORS OF 0 (unanalyzed), 1 (analyzed)
    #COULD JUST POPULATE THE ANALYSIS DICT WITH LEMMA INFORMATION, ETC WHEN IT IS BUILT (IT WOULD BE KEYED ON TOKENS INSTEAD OF TYPES)
    return {"tokens":{coord:token}, "link":link, "pos":pos, "tiny":tiny}

def nu_sentential_perspective(token, parse_results):
    return not parse_results[token][0].endswith('+?')

def lexical_perspective(parsed_data):
    lemmata = {}
    for i in range(len(parsed_data["lemmata"])): 
        for j in range(len(parsed_data["lemmata"][i])):
            if parsed_data["lemmata"][i][j] not in lemmata: 
                lemmata[parsed_data["lemmata"][i][j]] = {
                    "tokens":{
                        parsed_data["original"][i][j]: {
                            "cnt":1, 
                            "m_parse_hi":parsed_data["m_parse_hi"][i][j].strip("'"), 
                            "m_parse_lo":parsed_data["m_parse_lo"][i][j].strip("'"),
                            "addr":[(i,j)],
                            "exe":{tuple(parsed_data["original"][i]):[j]}
                            }},
                    "link":parsed_data["lemma_links"][i][j],
                    "pos":parsed_data["m_parse_hi"][i][j].split()[0].strip("'"),
                    "tiny":parsed_data["tinies"][i][j]
                    }
            elif parsed_data["original"][i][j] not in lemmata[parsed_data["lemmata"][i][j]]["tokens"]: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]] = {
                            "cnt":1, 
                            "m_parse_hi":parsed_data["m_parse_hi"][i][j], 
                            "m_parse_lo":parsed_data["m_parse_lo"][i][j],
                            "addr":[(i, j)],
                            "exe":{tuple(parsed_data["original"][i]):[j]}
                            }
            else: 
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["cnt"] += 1
                lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["addr"].append((i, j))
                if tuple(parsed_data["original"][i]) in lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"]: lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"][tuple(parsed_data["original"][i])].append(j)
                else: lemmata[parsed_data["lemmata"][i][j]]["tokens"][parsed_data["original"][i][j]]["exe"][tuple(parsed_data["original"][i])] = [j]
    return lemmata


def export_sorted_sentences_from_exes(exes):
    #if not exes:
    #    return ""
    #first_key = sorted(exes.keys())[0]
    #s = " ".join(exes[first_key])
    #return s.replace("<mark>", "").replace("</mark>", "")
    return "\n".join([" ".join(exe) for exe in sorted(exes)])

def glossary_format(sentence_data, lemmata_data):
    header = (
        "<table>\n<tbody>\n<tr>\n<td>"
        + "</td>\n<td>".join(["NOD/OPD Entry", "Part of Speech", "Terse Translation", "Count", "Example Sentence"])
        + "</td>\n</tr>\n"
    )

    body = ""
    footer = "</tbody>\n</table>\n"
    for lem in sorted(lemmata_data):
        if lem == "'?'":
            continue
        lem_cnt = 0
        exes = {}
        for tok in lemmata_data[lem]["tokens"]:
            lem_cnt += lemmata_data[lem]["tokens"][tok]["cnt"]
            for (sent_i, word_i) in lemmata_data[lem]["tokens"][tok]["addr"]:
                targ = sentence_data["original"][sent_i]
                key = tuple(targ)
                if key not in exes:
                    exes[key] = [
                        f"<mark>{token}</mark>" if i == word_i else token
                        for i, token in enumerate(targ)
                    ]
                else:
                    exes[key][word_i] = f"<mark>{targ[word_i]}</mark>"
        click_label = "(click for examples)"
        body += (
            '<tr class="parent">\n<td>'
            + "</td>\n<td>".join([
                lemmata_data[lem]["link"],
                lemmata_data[lem]["pos"],
                lemmata_data[lem]["tiny"],
                str(lem_cnt),
            ])
            + f'</td>\n<td onclick="toggleRow(this)" data-export="{export_sorted_sentences_from_exes([e for e in exes])}">{click_label}</td>\n'
            + "</tr>\n"
        )

        body += (
            '<tr class="child" style="display: none;">\n'
            + '<td colspan="5">'
            + "<br>\n".join([" ".join(exes[e]) for e in exes])
            + "</td>\n</tr>\n"
        )

    return header + body + footer
#-    header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["NOD/OPD Entry", "Part of Speech",  "Terse Translation", "Count", "Show/Hide Examples"])+"</td>\n</tr>\n"
#     body = ""
#     footer = "</tbody>\n</table>\n"
#-    for lem in sorted(lemmata_data): #make a neatly sorted list
#-        if lem != "'?'":
#-            lem_cnt = 0 #sum([lemmata_data[lem]["tokens"][x]["cnt"] for x in lemmata_data[lem]["tokens"]]) #was going to use an accumulator and += in the for loop, but then I wouldn't have this value available for the unanalyzed forms #-> changed my mind, the unanalyzed forms should be handled differently anyway
#-            exes = {}
#-            for tok in lemmata_data[lem]["tokens"]:
#-                lem_cnt += lemmata_data[lem]["tokens"][tok]["cnt"]
#-                for a in lemmata_data[lem]["tokens"][tok]["addr"]: 
#-                    targ = sentence_data["original"][a[0]]
#-                    if tuple(targ) not in exes:
#-                        marked = []
#-                        for i in range(len(targ)):
#-                            if i == a[1]: marked.append("<mark>"+targ[i]+"</mark>")
#-                            else: marked.append(targ[i])
#-                        exes[tuple(targ)] = marked
#-                    else: exes[tuple(targ)][a[1]] = "<mark>"+targ[a[1]]+"</mark>" #no risk of double marking because the same index can't correspond to two tokens of a word
#-            body += '<tr class="parent">\n'+"<td>"+"</td>\n<td>".join([lemmata_data[lem]["link"], lemmata_data[lem]["pos"].strip("'"), lemmata_data[lem]["tiny"], str(lem_cnt)])+'</td>\n<td onclick="toggleRow(this)">'+"(click for examples)"+"</td>\n</tr>\n"
#-            body += '<tr class="child" style="display: none;">\n'+'<td></td>\n<td colspan="4">'+"<br>\n".join([" ".join(exes[e]) for e in exes])+'</td>\n</tr>\n'
#-            #body.append([lemmata_data[lem]["link"], lemmata_data[lem]["pos"].strip("'"), lemmata_data[lem]["tiny"], str(lem_cnt), [exes[e] for e in exes]])
#-    return header+body+footer

def crib_format(sentence_data, lemmata_data):
    header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["Word", "NOD/OPD Entry",  "Broad Analysis", "Terse Translation", "Count", "Show/Hide Examples"])+"</td>\n</tr>\n"
    body = ""
    footer = "</tbody>\n</table>\n"
    nu_crib = []
    for lem in lemmata_data: 
        if lem != "'?'":
            for tok in lemmata_data[lem]["tokens"]: 
                exes = {}
                for a in lemmata_data[lem]["tokens"][tok]["addr"]: 
                    targ = sentence_data["original"][a[0]]
                    if tuple(targ) not in exes:
                        marked = []
                        for i in range(len(targ)):
                            if i == a[1]: marked.append("<mark>"+targ[i]+"</mark>")
                            else: marked.append(targ[i])
                        exes[tuple(targ)] = marked
                    else: exes[tuple(targ)][a[1]] = "<mark>"+targ[a[1]]+"</mark>" #no risk of double marking because the same index can't correspond to two tokens of a word
                nu_crib.append(([tok, lemmata_data[lem]["link"], lemmata_data[lem]["tokens"][tok]["m_parse_hi"], lemmata_data[lem]["tiny"], str(lemmata_data[lem]["tokens"][tok]["cnt"])], exes)) #DAB 3/4/2026: second element was originally [" ".join(exes[e]) for e in exes], but we need to access the dictionary directly (data-export works on the keys, child works on the values ... NB neither is truly the original sentence, capitalization and punctuation have been stripped out
    for pair in sorted(nu_crib):
        body += '<tr class="parent">\n'+"<td>"+"</td>\n<td>".join(pair[0])+f'</td>\n<td onclick="toggleRow(this)" data-export="{export_sorted_sentences_from_exes([e for e in pair[1]])}">'+"(click for examples)"+"</td>\n</tr>\n"
        body += '<tr class="child" style="display: none;">\n'+'<td colspan="6">'+"<br>\n".join([" ".join(pair[1][e]) for e in pair[1]])+'</td>\n</tr>\n'
    return header+body+footer

def frequency_format(sentence_data, lemmata_data):
    header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["Entry Count", "NOD/OPD Entry", "Word Count", "Actual Word", "Show/Hide Examples"])+"</td>\n</tr>\n"
    body = ""
    footer = "</tbody>\n</table>\n"
    nu_cnts = []
    for lem in lemmata_data: #make a neatly sorted list
        if lem != "'?'":
            for tok in lemmata_data[lem]["tokens"]:
                exes = {}
                for a in lemmata_data[lem]["tokens"][tok]["addr"]: 
                    targ = sentence_data["original"][a[0]]
                    if tuple(targ) not in exes:
                        marked = []
                        for i in range(len(targ)):
                            if i == a[1]: marked.append("<mark>"+targ[i]+"</mark>")
                            else: marked.append(targ[i])
                        exes[tuple(targ)] = marked
                    else: exes[tuple(targ)][a[1]] = "<mark>"+targ[a[1]]+"</mark>" #no risk of double marking because the same index can't correspond to two tokens of a word
                nu_cnts.append(([sum([lemmata_data[lem]["tokens"][x]["cnt"] for x in lemmata_data[lem]["tokens"]]), lem, str(lemmata_data[lem]["tokens"][tok]["cnt"]), tok], exes ))
    nu_cnts = sorted(sorted(sorted(sorted(nu_cnts, key = lambda x: x[0][3]), key = lambda x: x[0][2], reverse = True), key = lambda x: x[0][1]), key = lambda x: x[0][0], reverse = True) #alphabetize tokens, then sort tokens by reverse frequency, then alphabetize lemmata, then sort lemmata by reverse frequency
    prev = ""
    for i in range(len(nu_cnts)): #zap out redundant header information on lines beneath the header, make strings where appropriate, add in lemma links
        p, c = nu_cnts[i]
        p[0] = str(p[0])
        p[2] = str(p[2])
        new = p[1]
        if new != prev: 
            prev = new
            p[1] = lemmata_data[p[1]]["link"]
        elif new == prev: 
            p[0] = ""
            p[1] = ""
        body += '<tr class="parent">\n'+"<td>"+"</td>\n<td>".join(p)+f'</td>\n<td onclick="toggleRow(this)" data-export="{export_sorted_sentences_from_exes([e for e in c])}">'+"(click for examples)"+"</td>\n</tr>\n"
        body += '<tr class="child" style="display: none;">\n'+'<td colspan="5">'+"<br>\n".join([" ".join(c[e]) for e in c])+'</td>\n</tr>\n'
    return header+body+footer

def verb_collation_format(lemmata_data):
    h = []
    verbcats = ["VII", "VAI", "VAIO", "VTI", "VTA" ]
    verbdict = {x:[] for x in verbcats}
    for lem in lemmata_data:
        if lemmata_data[lem]["pos"] in verbcats:
            for t in lemmata_data[lem]["tokens"]:
                verbdict[lemmata_data[lem]["pos"]].append((t, lemmata_data[lem]["tokens"][t]["m_parse_hi"], lemmata_data[lem]["tokens"][t]["exe"])) 
    for j, c in enumerate(verbcats):
        preamble = "<p>Table {1}: Found these verbs of category {0}:</p>\n".format(c, str(j+1))
        header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["Word", "Broad Analysis", "Show/Hide Examples"])+"</td>\n</tr>\n"
        body = ""
        footer = "</tbody>\n</table>\n"
        for row in sorted(verbdict[c], key = lambda x: x[1]):
            body += '<tr class="parent">\n'+"<td>"+"</td>\n<td>".join(row[0:2])+f'</td>\n<td onclick="toggleRow(this)" data-export="{export_sorted_sentences_from_exes([e for e in row[2]])}">'+"(click for examples)"+"</td>\n</tr>\n"
            marked_exes = []
            for e in row[2]:
                marked = []
                for i in range(len(e)):
                    if i in row[2][e]: marked.append("<mark>"+e[i]+"</mark>")
                    else: marked.append(e[i])
                marked_exes.append(" ".join(marked))
            body += '<tr class="child" style="display: none;">\n'+'<td colspan="3">'+"<br>\n".join(marked_exes)+'</td>\n</tr>\n'
        h.append(preamble+header+body+footer)
    return "\n".join(h)

#this is only called in commented out lines
def retrieve_addrs(lexical_perspective, *keys):
    unanalyzed_token_addresses = []
    for key in keys:
        for t in sorted(lexical_perspective[key]["tokens"]):
            unanalyzed_token_addresses.extend(lexical_perspective["'?'"]["tokens"][t]["addr"])
    return unanalyzed_token_addresses

def unanalyzed_format(sentence_data, **tokens): #sentence data needed because we are assembling various pieces of analysis information for whole example sentences, and for historical reasons, that is where the information is
    preamble = "<p>Context table for unanalyzed words:</p>\n"
    header = "<table>\n<tbody>\n<tr>\n<td>"+"</td>\n<td>".join(["Word", "Context", "Show/Hide Analysis"])+"</td>\n</tr>\n"
    body = ""
    footer = "</tbody>\n</table>\n"
    for t in sorted(tokens):
        targets = {x[0]:[] for x in tokens[t]["addr"]}
        first = True
        for cur_l, cur_w in tokens[t]["addr"]: targets[cur_l].append(cur_w)
        for tar in sorted(targets):
            parent = []
            child = [[],[],[]]
            for i in range(len(sentence_data["original"][tar])):
                parent.append(sentence_data["original"][tar][i])
                pad = max([len(sentence_data["original"][tar][i]), len(sentence_data["tinies"][tar][i]), len(sentence_data["m_parse_hi"][tar][i])])
                child[0].append(f'{sentence_data["original"][tar][i]: <{pad}}')
                child[1].append(f'{sentence_data["m_parse_hi"][tar][i]: <{pad}}')
                child[2].append(f'{sentence_data["tinies"][tar][i]: <{pad}}')
            for j in targets[tar]:
                parent[j] = "<mark>"+parent[j]+"</mark>"
                child[0][j] = "<mark>"+child[0][j]+"</mark>"
            if first: 
                body += '<tr class="parent">\n<td>'+t+"</td>\n<td>"+" ".join(parent)+"</td>\n"+'<td onclick="toggleRow(this)">'+"(click for analysis)"+"</td></tr>\n" 
                first = False
            else: body += '<tr class="parent">\n<td>'"</td>\n<td>"+" ".join(parent)+"</td>\n"+'<td onclick="toggleRow(this)">'+"(click for analysis)"+"</td></tr>\n" 
            body += '<tr class="child" style="display: none;">\n<td>'+"<br>\n".join(["Original", "Broad Analysis", "Terse Translation"])+'</td>\n<td colspan="2">\n'+"<pre>\n"+"<br>\n".join([" ".join(x) for x in child])+"</pre>"+"</td>\n</tr>\n" #also want to get the index of the token for highlighting
    return preamble+header+body+footer

def vital_statistics_format(vital_statistics):
    return "<p>Overall word count: {0}<br>Analyzed word count: {1} ({2} without repetitions/variants)<br>Unanalyzed word count: {3} </p>".format(*[str(x) for x in vital_statistics])


def _example_preview(exes: dict):
    """
    exes is a dict like { tuple(sentence_tokens): [token_or_<mark>token</mark>, ...], ... }
    Returns a single example sentence string, or "" if none.
    """
    if not exes:
        return ""
    # stable-ish: sort by the sentence tuple
    first_key = sorted(exes.keys())[0]
    return " ".join(exes[first_key])


##this is the main function. it puts everything together
def parse_words_expanded(event):
    form_values["rhodes"]["order"] = pyscript.document.querySelector("#rhodes").value
    #form_values["rhodes_relaxed"]["order"] = pyscript.document.querySelector("#rhodes_relaxed").value
    form_values["corbiere"]["order"] = pyscript.document.querySelector("#corbiere").value
    #form_values["corbiere_relaxed"]["order"] = pyscript.document.querySelector("#corbiere_relaxed").value
    form_values["no_deletion"]["order"] = pyscript.document.querySelector("#no_deletion").value
    #form_values["no_deletion_relaxed"]["order"] = pyscript.document.querySelector("#no_deletion_relaxed").value
    form_values["western"]["order"] = pyscript.document.querySelector("#western").value
    analyzers = []
    for x in sorted(form_values, key = lambda y: form_values[y]["order"]):
        #if form_values[x]["order"] and form_values[x]["url"]:
        #    form_values[x]["file"] = await pyfetch(form_values[x]["url"])
        if form_values[x]["order"] and form_values[x]["file"]: analyzers.append(form_values[x]["file"])
    #separator = pyscript.document.querySelector("#english_separator").value
    #english = []
    input_text = pyscript.document.querySelector("#larger_text_input")
    freeNish = input_text.value
    #if separator:
    #    print("sep is ", separator)
    #    freeNish = ""
    #    for it in input_text.value.split('\n'):
    #        chopped = it.split(separator)
    #        freeNish += chopped[0]+'\n'
    #        if len(chopped) > 1: english.append(chopped[1])
    #        else: english.append("")
    to_analyze = ppbt.sep_punct(freeNish.lower(), True).split()
    parses = {}
    model_credit = {} #as of aug 2025, only using this data to allow correct formatting of western (OPD-based) lemmata urls vs eastern (NOD-based) lemmata. It could be nice to flag misspelled words either to indicate less certainty or to encourage spelling improvement
    for i in range(len(analyzers)):
        analyzed = ppa.parse_pyhfst(analyzers[i], *to_analyze)
        to_analyze = []
        for w in analyzed:
            if analyzed[w][0][0].endswith('+?') and i+1 < len(analyzers): to_analyze.append(w)
            elif analyzed[w][0][0].endswith('+?') and i+1 == len(analyzers): 
                parses[w] = analyzed[w]
                model_credit[w] = "unanalyzed" 
            #elif (not analyzed[w][0][0].endswith('+?')) and i+1 == len(analyzers): 
            #    parses[w] = analyzed[w]
            #    model_credit[w] = analyzers[i]
            else: 
                parses[w] = analyzed[w]
                model_credit[w] = analyzers[i]
    h = {"original":[],
         "m_parse_lo":[],
         "m_parse_hi":[],
         "lemmata":[],
         "lemma_links":[],
         "tinies":[],
         #"english":english
         }
    for line in freeNish.lower().split('\n'):
        local = []
        for w in ppbt.sep_punct(line, True).split(): local.append(parses[w][ppa.disambiguate(ppa.min_morphs(*parses[w]), ppa.min_morphs, *parses[w])][0])
        h["original"].append(ppbt.sep_punct(line, True).split())
        h["m_parse_lo"].append(local)
        his = []
        lemms = []
        lem_links = []
        for i in range(len(local)):
            if model_credit[ppbt.sep_punct(line, True).split()[i]] == "./morphophonology_analyze_border_lakes.hfstol": 
                lem = ppa.extract_lemma(local[i], ciw_pos_regex_opd)
                pos = ppa.extract_pos(local[i], ciw_pos_regex_opd)
                lemms.append(lem)
                #populate hi
                if regex.search("({0})(.*({0}))?".format(ciw_pos_regex_model), local[i]): his.append("'"+ppa.formatted(ppa.interpret_ciw(local[i], ciw_pos_regex_model))+"'")
                if not regex.search("({0})(.*({0}))?".format(ciw_pos_regex_model), local[i]): his.append("'?'")
                #populate lem
                if (lem, pos) in opd_manual_links: lem_links.append(opd.wrap_opd_url(opd_manual_links[(lem, pos)], lem)) 
                else: lem_links.append(opd.wrap_opd_url(opd.mk_opd_url(lem, pos), lem)) 
            else: 
                #populate lem
                lem = ppa.extract_lemma(local[i], pos_regex)
                if not lem: lem = "'?'"
                lemms.append(lem)
                lem_links.append(ppg.wrap_nod_entry_url(lem, **iddict)[0])
                #populate hi
                if ppa.analysis_dict(local[i]): his.append("'"+ppa.formatted(ppa.interpret(ppa.analysis_dict(local[i])))+"'")
                if not ppa.analysis_dict(local[i]): his.append("'?'")
        h["m_parse_hi"].append(his) 
        h["lemmata"].append(lemms) 
        h["lemma_links"].append(lem_links) 
        h["tinies"].append(ppg.wrap_glosses(*ppg.retrieve_glosses(*h["lemmata"][-1], **gdict)))
        #tinies = []
        #for l in h["lemmata"][-1]:
        #    try: gloss = gdict[l]
        #    except KeyError:
        #        gloss = "?"
        #    tinies.append("'"+gloss+"'")
        #h["tinies"].append(tinies)
    #this is yet another routine to collate information. it is inefficient to run through the data this many times. everything here could be collected at other points. trying to integrate it into the various other points was resulting in little bits of spaghetti code duplicated all over the place
    vital_stats = [
            0, # "Overall raw word count"], -> to_analyze gets reset as you work through the cascade, so the count needs to be here
            0,#, "Analyzed raw word count"],
            0,#, "Analyzed processed word count (not counting repetititions/variants of 'the same word')"],
            0,#, "Unanalyzed raw word count"],
            ]
    general_lemmata = []
    for w in ppbt.sep_punct(freeNish.lower(), True).split():
        vital_stats[0] += 1
        if w in parses and not parses[w][0][0].endswith('+?'): 
            vital_stats[1] += 1
        else: 
            vital_stats[3] += 1
    for i in range(len(h["lemmata"])):
        for j in range(len(h["lemmata"][i])):
            if h["lemmata"][i][j] not in general_lemmata:
                general_lemmata.append(h["lemmata"][i][j])
        vital_stats[2] = len(general_lemmata)
    analysis_mode = pyscript.document.querySelector("#analysis_mode")
    output_div = pyscript.document.querySelector("#output")
    if analysis_mode.value == "interlinearize":
        output_div.innerHTML = interlinearize(h)+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "glossary": 
        lp = lexical_perspective(h)
        unanalyzed_context_table = ""
        if "'?'" in lp: unanalyzed_context_table = unanalyzed_format(h, **lp["'?'"]['tokens'])
        output_div.innerHTML = glossary_format(h, lp)+unanalyzed_context_table+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "crib": 
        lp = lexical_perspective(h)
        unanalyzed_context_table = ""
        if "'?'" in lp: unanalyzed_context_table = unanalyzed_format(h, **lp["'?'"]['tokens'])
        output_div.innerHTML = crib_format(h, lp)+unanalyzed_context_table+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "frequency": 
        lp = lexical_perspective(h)
        unanalyzed_context_table = ""
        if "'?'" in lp: unanalyzed_context_table = unanalyzed_format(h, **lp["'?'"]['tokens'])
        output_div.innerHTML = frequency_format(h, lp)+unanalyzed_context_table+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "verb_sort":
        comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
        c_order = ["VTA", "VAIO", "VTI", "VAI", "VII", "(No verbs found)"] #need to specify order in order to sort by count of verb in the relevant category
        categorized = {x:[] for x in c_order}
        for i in range(len(comp_counts)):
            if comp_counts[i][0][0]: categorized["VTA"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][1]: categorized["VAIO"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][2]: categorized["VTI"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][3]: categorized["VAI"].append((comp_counts[i], h["original"][i]))
            if comp_counts[i][0][4]: categorized["VII"].append((comp_counts[i], h["original"][i]))
            if not any(comp_counts[i][0]): categorized["(No verbs found)"].append((comp_counts[i], h["original"][i]))
        sectioned = [["Sentences", "Target Verb Count", "Complexity Score"]]
        for i in range(len(c_order)-1): #need to skip the last category, because there is no corresponding bin in the verb counts for when there is nothing
            sectioned.append([">>These sentences have verbs of the following category: {}".format(c_order[i]), "", ""])
            for x in sorted(sorted(categorized[c_order[i]], key = lambda y: y[0][-1][0]), key = lambda z: z[0][0][i]): sectioned.append([" ".join(x[1]), str(x[0][0][i]), str(x[0][-1][0])]) #sorting by morphological complexity, then count of relevant verb category
        sectioned.append([">>These sentences had no verbs found in them"])
        for x in sorted(categorized["(No verbs found)"], key = lambda y: y[0][-1][0]):
            sectioned.append([" ".join(x[1])])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "complexity":
        comp_counts = sc.alg_morph_counts(*sc.interface(pos_regex, *h["m_parse_lo"]))
        overall_score = sc.alg_morph_score_rate(*comp_counts)
        sectioned = [["Overall Score (Features per Sentence):",  str(overall_score[2])]]
        for ssp in sorted([x for x in zip(comp_counts, h["original"])], key = lambda y: y[0][-1][0]): sectioned.append([" ".join(ssp[1]), ssp[0][-1][0]])
        output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value == "verb_collate":
        #faced = sc.interface(pos_regex, *h["m_parse_lo"])
        #verbcats = ["VAI", "VTA", "VII", "VAIO", "VTI"]
        #verbdict = {x:[] for x in verbcats}
        #for i in range(len(faced)):
        #    for j in range(len(faced[i])):
        #        if faced[i][j]["pos"] in verbdict: 
        #            if (h["original"][i][j], h["m_parse_hi"][i][j]) not in verbdict[faced[i][j]["pos"]]: verbdict[faced[i][j]["pos"]].append((h["original"][i][j], h["m_parse_hi"][i][j]))
        #sectioned = [["Verbs", "Broad Analysis"]]
        #for c in verbcats:
        #    sectioned.append(["Found these verbs of category {}:".format(c), ""])
        #    for v in sorted(verbdict[c], key = lambda x: x[1]): sectioned.append([v[0], v[1]])
        #output_div.innerHTML = tabulate.tabulate(sectioned, tablefmt="html")+vital_statistics_format(vital_stats)
        output_div.innerHTML = verb_collation_format(lexical_perspective(h))+vital_statistics_format(vital_stats)
        _after_render()
    elif analysis_mode.value in ["triage", "reversed_triage"]:
        recall_errors = []
        for i in range(len(h["original"])):
            for j in range(len(h["original"][i])):
                if h["m_parse_lo"][i][j].endswith("+?"):
                    error = [(h["original"][i][j], i, " ".join(h["original"][i][:j]), h["original"][i][j], " ".join(h["original"][i][j+1:]))]
                    error.append(["", "", " ".join(h["m_parse_lo"][i][:j]), "",                " ".join(h["m_parse_lo"][i][j+1:])])
                    error.append(["", "", " ".join(h["m_parse_hi"][i][:j]), "",                " ".join(h["m_parse_hi"][i][j+1:])])
                    error.append(["", "", " ".join(h["lemmata"][i][:j]), "",                   " ".join(h["lemmata"][i][j+1:])])
                    error.append(["", "", " ".join(h["tinies"][i][:j]), "",                    " ".join(h["tinies"][i][j+1:])])
                    recall_errors.append(error)
        ordered_recall_errors = []
        if analysis_mode.value == "triage":
            for x in sorted(recall_errors): ordered_recall_errors.extend(x) #[x[0], x[1], x[2], x[3], x[4] for x in sorted(recall_errors)]
        elif analysis_mode.value == "reversed_triage":
            for x in sorted(recall_errors, key=lambda z: [y for y in reversed(z[0][0])]): ordered_recall_errors.extend(x) #[x[0], x[1], x[2], x[3], x[4] for x in sorted(recall_errors)]
        #forwards = ""
        #for r in sorted(recall_errors):
        #    forwards += tabulate.tabulate([[r[0][0], r[0][2]]+r[1], ["", ""]+r[2], ["", ""]+r[3], ["", ""]+r[4], ["", ""]+r[5]], headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        #forwards = tabulate.tabulate([[[r[0][0], r[0][2]]+r[1], ["", ""]+r[2], ["", ""]+r[3], ["", ""]+r[4], ["", ""]+r[5]] for r in sorted(recall_errors)], headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        forwards = tabulate.tabulate(ordered_recall_errors, headers = ["error", "sentence_no", "left_context", "locus", "right_context"], tablefmt = "html")
        output_div.innerHTML = forwards+vital_statistics_format(vital_stats)
        _after_render()
        
           
def _autorun_parse_words_expanded_from_query():
    try:
        params = js.URLSearchParams.new(js.window.location.search)
        q = params.get("q")
        if q is None:
            return
        q_text = str(q)
        if q_text in ["", "null", "undefined"]:
            return
        input_text = pyscript.document.querySelector("#larger_text_input")
        if input_text is not None:
            input_text.value = q_text
            parse_words_expanded(None)
    except Exception as e:
        print("query autorun skipped:", e)


_autorun_parse_words_expanded_from_query()