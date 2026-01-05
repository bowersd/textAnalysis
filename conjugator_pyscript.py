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
import pure_python_tmp_container

#catch parameters from ux

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

def inflect_word(event):
    ###shunting around the values from the html form
    form_values["Lemma"] = pyscript.document.querySelector("#lemma").value
    form_values["Head"] = pyscript.document.querySelector("#POS").value
    form_values["DerivChain"] = form_values["Head"] #not really available option now, but needed for post processing
    form_values["Order"] = pyscript.document.querySelector("#Order").value
    prt = pyscript.document.querySelector("#ModePrt").value
    dub = pyscript.document.querySelector("#ModeDub").value
    neg = pyscript.document.querySelector("#Neg").value
    sub = pyscript.document.querySelector("#S").value
    obj = pyscript.document.querySelector("#O").value
    if form_values["Head"].startswith("N"): 
        sub = pyscript.document.querySelector("#Possessor").value
        form_values["Periph"] = pyscript.document.querySelector("#Periph").value
        form_values["ConDim"] = pyscript.document.querySelector("#ConDim").value
        form_values["PosTheme"] = pyscript.document.querySelector("#PosThm").value
        form_values["Pejorative"] = pyscript.document.querySelector("#Pej").value
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
    ###calculations on the values
    for v in form_values:
        print(v, form_values[v])
    broad_analysis = pure_python_tmp_container.formatted(form_values)
    narrow_analysis = conjugator.tag_linearize(form_values["Lemma"], **conjugator.tag_assemble(**form_values))
    output = pure_python_tmp_container.parse_pyhfst("./morphophonologyclitics_generate.hfstol", narrow_analysis)
    ###formatting the values
    table = [["Broad Analysis", broad_analysis], 
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


