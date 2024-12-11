import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
import regex
import pyscript
import tabulate
import corbiere_lemmatized_corpus_20241210

def search(event):
    h = []
    #field = pyscript.document.querySelector("#foo")
    field = "lemmata"
    query = pyscript.document.querySelector("#query").value
    output_div = pyscript.document.querySelector("#search_output")
    for s in corbiere_lemmatized_corpus_20241210.data:
        if all([q in s[field] for q in query.split()]): h.append(s)
    rendered = ""
    for i in range(len(h)):
        print("stage 1")
        rendered += tabulate.tabulate([[str(i), ""],
            ["Original Sentence:"]+[h[i]["sentence"]],
            ["Translation:"]+[h[i]["english"]],], tablefmt='html')
        print("stage 2")
        rendered += tabulate.tabulate([
            ["\tAligned Sentence:"]+h[i]["chunked"],
            ["\tFiero/Rhodes Spelling:"]+h[i]["edited"],
            ["\tNarrow Analysis:"]+h[i]["m_parse_lo"],
            ["\tBroad Analysis:"]+h[i]["m_parse_hi"],
            ["\tNOD Header:"]+h[i]["lemmata"],
            ["\tTerse Translation"]+h[i]["tiny_gloss"],
            ], tablefmt = 'html')
        print("stage 3")
    output_div.innerHTML = rendered

