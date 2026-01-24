import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/e0/02/c10a69ff21d6679a6b6e28c42cd265bec2cdd9be3dcbbee830a10fa4b0e5/pyhfst-1.3.0-py2.py3-none-any.whl'
)
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
import pyscript
import asyncio
import tabulate
import pyhfst
import conjugator
import pure_python_tmp_container as pp
import trie
import nish_trie

pos_regex = "".join(pp.readin("./pos_regex.txt"))
analyzer = "./morphophonologyclitics_analyze_mcor_spelling.hfstol"


def user_prediction(event):
    chars = pyscript.document.querySelector("#lemma").value
    if len(chars) > 3:
        predict_div = pyscript.document.querySelector("#prediction_output")
        predict_div.innerHTML = "Looking for this word: {0}?".format(trie.main(chars, nish_trie.nod_entries))

def user_pos_confirmation(event):
    lemma = pyscript.document.querySelector("#lemma").value
    possible = conjugator.pos_check(lemma, analyzer, pos_regex)
    if not possible: confirmation = "I don't know the word '{0}'... Can you double check the Nishnaabemwin Online Dictionary?".format(lemma)
    elif len(possible) == 1: confirmation = "The word '{0}' is a {1}. You don't need to specify the Part of Speech information".format(lemma, possible[0])
    else: 
        confirmation = "The word '{0}' could be one of the following: {1}. Please specify the Part of Speech information in the menu below".format(lemma, ", ".join(possible))
    confirmation_div = pyscript.document.querySelector("#confirmation_output")
    confirmation_div.innerHTML = confirmation
    


def inflect_word(event):
    #initialize to zero (values were persisting across instances)
    form_values = {"Lemma":"",
                   "S":{"Pers":"", "Num":""}, 
                   "O":{"Pers":"", "Num":""}, 
                   "Head":"", 
                   "Order":"", 
                   "Neg":"", 
                   "Mode":[], 
                   "Periph":"", 
                   "ConDim":"", 
                   "PosTheme":"", 
                   "Pejorative":"" , 
                   "DerivChain":"", #options on this line and below are not available options now, but needed for post processing 
                   "Pcp":{"Pers":"", "Num":""}, 
                   "Else":[]
               } 
    ###shunting around the values from the html form
    form_values["Lemma"] = pyscript.document.querySelector("#lemma").value
    form_values["Head"] = pyscript.document.querySelector("#POS").value
    pos_values = conjugator.pos_check(form_values["Lemma"], analyzer, pos_regex)
    if len(pos_values) == 1: form_values["Head"] = pos_values[0]
    form_values["DerivChain"] = form_values["Head"] #not really available option now, but needed for post processing
    form_values["Order"] = pyscript.document.querySelector("#Order").value
    prt = pyscript.document.querySelector("#ModePrt:checked")
    dub = pyscript.document.querySelector("#ModeDub:checked")
    neg = pyscript.document.querySelector("#Neg:checked")
    delayed = pyscript.document.querySelector("#Del:checked")
    sub = pyscript.document.querySelector("#S").value
    obj = pyscript.document.querySelector("#O").value
    if form_values["Head"].startswith("N"): 
        sub = pyscript.document.querySelector("#Possessor").value
        form_values["Periph"] = pyscript.document.querySelector("#Periph").value
        form_values["ConDim"] = pyscript.document.querySelector("#ConDim").value
        if pyscript.document.querySelector("#PosThm:checked"): form_values["PosTheme"] = "PosThm"
        if pyscript.document.querySelector("#Pejorative:checked"): form_values["Pejorative"] = "Pej"
        form_values["Else"] = [x for x in [form_values["ConDim"], form_values["PosTheme"], form_values["Pejorative"]] if x]
        nmode = pyscript.document.querySelector("#NMode").value
        if nmode == "NModeVocPl":
            form_values["Periph"] = "Pl"
            form_values["Mode"] = ["Voc"]
        elif nmode ==  "NModePrt": form_values["Mode"] = ["Prt"]
    if sub: 
        form_values["S"]["Pers"] = sub[0]
        form_values["S"]["Num"] = sub[1:]
    if obj: 
        form_values["O"]["Pers"] = obj[0]
        form_values["O"]["Num"] = obj[1:]
    if form_values["Head"].startswith("V") and prt: form_values["Mode"].append("Prt")
    if form_values["Head"].startswith("V") and dub: form_values["Mode"].append("Dub")
    if form_values["Head"].startswith("V") and neg: form_values["Neg"] = "Neg"
    if form_values["Head"].startswith("V") and delayed: form_values["Neg"] = "Del"
    ###calculations on the values
    for v in form_values:
        print(v, form_values[v])
    broad_analysis = pp.formatted(form_values)
    narrow_analysis = conjugator.tag_linearize(form_values["Lemma"], **conjugator.tag_assemble(**form_values))
    generator = pyscript.document.querySelector("#generator").value
    output = pp.parse_pyhfst(generator, narrow_analysis)
    ###formatting the values
    table = [["Broad Analysis", form_values["Lemma"]+" "+broad_analysis], 
             ["Narrow Analysis", narrow_analysis],]
    i = 0
    total_variants = len(output[narrow_analysis])
    while i < total_variants:
        if i == 0 and total_variants==1: table.append(["Predicted form", output[narrow_analysis][i][0]])
        elif i == 0 and total_variants>1: table.append(["Predicted forms", output[narrow_analysis][i][0]])
        elif i != 0 and total_variants>1: table.append(["", output[narrow_analysis][i][0]])
        i += 1
    ###printing the values
    output_div = pyscript.document.querySelector("#output")
    output_div.innerHTML = tabulate.tabulate(table, tablefmt="html")

def narrow_generate(event):
    narrow_input = pyscript.document.querySelector("#narrow_input").value
    generator = pyscript.document.querySelector("#generator").value
    output = pp.parse_pyhfst(generator, narrow_input)
    ###formatting the values
    table = [["Narrow Analysis", narrow_input]]
    i = 0
    total_variants = len(output[narrow_input])
    while i < total_variants:
        if i == 0 and total_variants==1: table.append(["Predicted form", output[narrow_input][i][0]])
        elif i == 0 and total_variants>1: table.append(["Predicted forms", output[narrow_input][i][0]])
        elif i != 0 and total_variants>1: table.append(["", output[narrow_input][i][0]])
        i += 1
    ###printing the values
    narrow_output_div = pyscript.document.querySelector("#narrow_output")
    narrow_output_div.innerHTML = tabulate.tabulate(table, tablefmt="html")


