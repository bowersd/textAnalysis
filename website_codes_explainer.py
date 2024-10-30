import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
import regex
import pyscript
import tabulate
import grammar_codes

codes_div = pyscript.document.querySelector("#codes")
table = [["Code", "Technical Definition", "Informal Explanation", "Narrow/Broad Analysis"]]

for x in sorted(grammar_codes.abbreviations):
    row =  []
    narrow_only = x not in grammar_codes.abbreviations_high
    if narrow_only: row.append("Narrow Analyses Only")
    if not narrow_only: row.append("Narrow and Broad Analyses")
    if regex.search(r"\(.*\)", grammar_codes.abbreviations[x]):
        row.append(regex.search(r"\(.*\)", grammar_codes.abbreviations[x])[0][1:-1])
        row.append(regex.match(r"[^(]*", grammar_codes.abbreviations[x])[0])
    elif not regex.search(r"\(.*\)", grammar_codes.abbreviations[x]):
        row.append("")
        row.append(grammar_codes.abbreviations[x])
    row.append(x)
    table.append(reversed(row))

for x in sorted(grammar_codes.abbreviations_high):
    row =  []
    if x not in grammar_codes.abbreviations:
        row.append("Broad Analyses Only")
        if regex.search(r"\(.*\)", grammar_codes.abbreviations_high[x]):
            row.append(regex.search(r"\(.*\)", grammar_codes.abbreviations_high[x])[0][1:-1])
            row.append(regex.match(r"[^(]*", grammar_codes.abbreviations_high[x])[0])
        elif not regex.search(r"\(.*\)", grammar_codes.abbreviations_high[x]):
            row.append("")
            row.append(grammar_codes.abbreviations_high[x])
        row.append(x)
        table.append(reversed(row))

codes_div.innerHTML = tabulate.tabulate(table)
