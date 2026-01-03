import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/e0/02/c10a69ff21d6679a6b6e28c42cd265bec2cdd9be3dcbbee830a10fa4b0e5/pyhfst-1.3.0-py2.py3-none-any.whl'
)
import pyscript
import asyncio
import conjugator

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
               "Pejorative":"" } 

def inflect_word(event):
    form_values["Lemma"] = pyscript.document.querySelector("#lemma").value
    form_values["Head"] = pyscript.document.querySelector("#POS").value
    form_values["Order"] = pyscript.document.querySelector("#Order").value
    prt = pyscript.document.querySelector("#Mode:Prt")
    dub = pyscript.document.querySelector("#Mode:Dub")
    neg = pyscript.document.querySelector("#Neg")
    sub = pyscript.document.querySelector("#S")
    obj = pyscript.document.querySelector("#O")
    if form_values["Head"].startswith("N"): 
        sub = pyscript.document.querySelector("#Possessor")
        per = pyscript.document.querySelector("#Periph")
        form_values["ConDim"] = pyscript.document.querySelector("#ConDim")
        form_values["PosTheme"] = pyscript.document.querySelector("#PosThm")
        form_values["Pejorative"] = pyscript.document.querySelector("#Pej")
    if sub: 
        form_values["S"]["Pers"] = sub[0]
        form_values["S"]["Num"] = sub[1:]
    if obj: 
        form_values["O"]["Pers"] = sub[0]
        form_values["O"]["Num"] = sub[1:]
