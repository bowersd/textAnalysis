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
import main

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
    form_values["Lemma"] = pyscript.document.querySelector("#lemma").value
    form_values["Head"] = pyscript.document.querySelector("#POS").value
    form_values["DerivChain"] = form_values["Head"] #not really available option now, but needed for post processing
    form_values["Order"] = pyscript.document.querySelector("#Order").value
    prt = pyscript.document.querySelector("#Mode:Prt")
    dub = pyscript.document.querySelector("#Mode:Dub")
    neg = pyscript.document.querySelector("#Neg")
    sub = pyscript.document.querySelector("#S")
    obj = pyscript.document.querySelector("#O")
    if form_values["Head"].startswith("N"): 
        sub = pyscript.document.querySelector("#Possessor")
        form_values["Periph"] = pyscript.document.querySelector("#Periph")
        form_values["ConDim"] = pyscript.document.querySelector("#ConDim")
        form_values["PosTheme"] = pyscript.document.querySelector("#PosThm")
        form_values["Pejorative"] = pyscript.document.querySelector("#Pej")
        nmode = pyscript.document.querySelector("#NMode")
        if nmode == "VocPl":
            form_values["Periph"] = "Pl"
            form_values["Mode"] = ["Voc"]
        else: form_values["Mode"] = ["Prt"]
    if sub: 
        form_values["S"]["Pers"] = sub[0]
        form_values["S"]["Num"] = sub[1:]
    if obj: 
        form_values["O"]["Pers"] = sub[0]
        form_values["O"]["Num"] = sub[1:]
    if form_values["Head"].startswith("V") and prt: form_values["Mode"].append("Prt")
    if form_values["Head"].startswith("V") and dub: form_values["Mode"].append("Dub")
    if form_values["Head"].startswith("V") and neg: form_values["Neg"] = "Neg"
    parameter_div = pyscript.document.querySelector("#parameters")
    output_div = pyscript.document.querySelector("#output")
    broad_analysis = main.formatted(form_values)
    narrow_analysis = tag_linearize(form_values["Lemma"], **tag_assemble(**form_values))
    output = main.parse_pyhfst("./morphophonologyclitics_generate.hfstol", narrow_analysis)
    table = [["Broad Analysis", broad_analysis], 
             ["Narrow Analysis", narrow_analysis],]
    i = 0
    while i < len(output):
        if i == 0 and len(output)==1: table.append(["Predicted form", output[i]])
        elif i == 0 and len(output)>1: table.append(["Predicted forms", output[i]])
        elif i != 0 and len(output)>1: table.append(["", output[i]])
    output_div.innerHTML = tabulate.tabulate(table, tablefmt="html")


