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
        rendered += tabulate.tabulate([[str(i+1), ""],
            ["Original Sentence:"]+[h[i]["sentence"]],
            ["Translation:"]+[h[i]["english"]],], tablefmt='html')
        rendered += tabulate.tabulate([
            ["Aligned Sentence:"]+h[i]["chunked"],
            ["Fiero/Rhodes Spelling:"]+h[i]["edited"],
            ["Narrow Analysis:"]+h[i]["m_parse_lo"],
            ["Broad Analysis:"]+h[i]["m_parse_hi"],
            ["NOD Entry:"]+h[i]["lemmata"],
            ["Terse Translation"]+h[i]["tiny_gloss"],
            ], tablefmt = 'html')
    output_div.innerHTML = rendered

