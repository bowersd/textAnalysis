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
