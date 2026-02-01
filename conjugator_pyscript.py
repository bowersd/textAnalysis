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
        tries = [nish_trie.nod_entries_lemma_freq, nish_trie.nod_entries]
        guessers = [trie.predict_short, trie.predict]
        guesses = []
        pairs = ((0, 0), (0, 1), (1, 1)) #not searching for a short prediction with frequency less trie
        for p in pairs:
            guess = trie.main(chars, tries[p[0]], guessers[p[1]])
            if guess not in guesses: guesses.append(guess)
        predict_div.innerHTML = "Suggested words: {0}".format(", ".join(guesses))

def user_pos_confirmation(event):
    lemma = pyscript.document.querySelector("#lemma").value
    possible = conjugator.pos_check(lemma, analyzer, pos_regex)
    explanation = {
            "VAI": {
                "short": "a verb describing an action done by somebody, like <i>nmadbi</i> 's/he sits'", 
                "technical": "The technical description for this is a <b>Verb</b> with only an <b>Animate</b> subject, i.e. it is <b>Intransitive</b>."}, 
            "VTI": {
                "short": "a verb describing an action done to something, like <i>naadin</i> 's/he fetches it'", 
                "technical": "The technical description for this is a <b>Verb</b> that is <b>Transitive</b>, with an (<b>Inanimate</b>) object."}, 
            "VTA": {
                "short": "a verb describing an action done to somebody, like <i>naagaa'aan</i> 's/he delays him/her'",
                "technical": "The technical description for this is a <b>Verb</b> that is <b>Transitive</b>, with an (<b>Animate</b>) object."}, 
            "VII": {
                "short": "a verb describing an action done by something, like <i>biidaasin</i> 'it sails here'",
                "technical": "The technical description for this is a <b>Verb</b> with only an <b>Inanimate</b> subject, i.e. it is <b>Intransitive</b>."},
            "VAIO": {
                "short": "a verb describing an action done by somebody to another thing (not to you/me/us, etc), like <i>noopon</i> 's/he takes it for lunch'",
                "technical": "Strictly speaking, these verbs are a bit hard to classify with the (in)transitive/(in)animate system. They have an object, so they are transitive, but the object is not restricted to being animate or inanimate. In fact, the only restriction is that the subject be animate, which makes them like VAIs. These verbs resemble VAIs in other ways, so we call these <b>VAI</b> with an <b>Object</b>,"}, 
            "NI": {
                "short": "a noun describing something that isn't alive, like <i>jiimaan</i> 'boat'",
                "technical":"The technical description for this is a <b>Noun</b> that is <b>Inanimate</b>. There are exceptional cases where a noun that is not obviously living is classified as an NA, so the best check is to see if the plural ends in -n (only NIs do this) or -g/-k (only NAs do this)."}, 
            "NA": {
                "short": "a noun describing somebody that is alive, like <i>aamoo</i> 'bee'",
                "technical": "The technical description for this is a <b>Noun</b> that is <b>Animate</b>. There are exceptional cases where a noun that is not obviously living is classified as an NA, so the best check is to see if the plural ends in -n (only NIs do this) or -g/-k (only NAs do this)."},
                   "NID": {
                       "short": "a noun describing something that isn't alive and must be 'owned', like <i>ndahiim</i> 'my thing'",
                       "technical":"The technical description for this is a <b>Noun</b> that is <b>Inanimate</b> and <b>Dependent</b>. There are exceptional cases where a noun that is not obviously living is classified as an NA, so the best check is to see if the plural ends in -n (only NIs do this) or -g/-k (only NAs do this)."},
                   "NAD": {
                       "short": "a noun describing somebody that is alive and must be 'owned', like <i>noos</i> 'my father'",
                       "technical": "The technical description for this is a <b>Noun</b> that is <b>Animate</b> and <b>Dependent</b>. There are exceptional cases where a noun that is not obviously living is classified as an NA, so the best check is to see if the plural ends in -n (only NIs do this) or -g/-k (only NAs do this)."},
                   }
    if possible[0] == None: confirmation = "I don't know the word '{0}'... Can you double check the Nishnaabemwin Online Dictionary?".format(lemma)
    elif not (possible[0][:2] in ("NI", "NA") or possible[0].startswith("V")): confirmation = "The word '{0}' is not a noun or a verb, so it can't be conjugated.".format(lemma)
    elif len(possible) == 1: 
        generic = "verb"
        if possible[0][0] == "N": generic = "noun"
        confirmation = "The word <i>{0}</i> is a {2}. You can go straight to the {2} section in step 2. If you want more information about the specific word type, read on.<br>Specifically, <i>{0}</i> is {3}.<br>{4}<br><b>{1}</b> is the abbreviation for this.<br>Be careful to follow any specific instructions for {1}s in step 2.".format(lemma, possible[0], generic, explanation[possible[0]]["short"], explanation[possible[0]]["technical"])
    else:
        confirmation = "The word '{0}' could be one of several dictionary entries. The types of words that it could be are {2}, or {3}.<br>If you do nothing, {1} will be chosen.<br>If you want to specify another part of speech, pick a new value from the menu in step 1.1.<br>Whatever type of word you select, in step 2 the tool will only pay attention to the options you select for that type of word. If these abbreviations are unfamiliar, some further explanation is below:<br>{4}.".format(lemma, conjugator.pos_defaults(*[x for x in possible if x in ("VAI", "VTA", "VTI", "VII", "VAIO", "NA", "NAD", "NI", "NID")]), ", ".join([explanation[p]["short"]+" (abbreviated as <b>"+p+"</b>)" for p in possible[:-1]]), explanation[possible[-1]]["short"]+" ("+possible[-1]+")", "<br>".join([p+": "+explanation[p]["technical"] for p in possible]))
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
    if form_values["Head"] == "def": form_values["Head"] = conjugator.pos_defaults(*conjugator.pos_check(form_values["Lemma"], analyzer, pos_regex))
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


