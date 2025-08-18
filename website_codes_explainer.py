import micropip
await micropip.install(
    'https://files.pythonhosted.org/packages/40/44/4a5f08c96eb108af5cb50b41f76142f0afa346dfa99d5296fe7202a11854/tabulate-0.9.0-py3-none-any.whl'
)
import regex
import pyscript
import tabulate
import grammar_codes

codes_narrow_broad_div = pyscript.document.querySelector("#codes_narrow_broad")
codes_narrow_div = pyscript.document.querySelector("#codes_narrow")
codes_broad_div = pyscript.document.querySelector("#codes_broad")
codes_narrow_anishinaabemowin_div = pyscript.document.querySelector("#codes_narrow_anishinaabemowin")
col_header = ["Code", "Technical Definition", "Informal Explanation"]
table_narrow_broad = [col_header]
table_narrow = [col_header]
table_broad = [col_header]
table_narrow_anishinaabemowin = [col_header]

def row_prep(header, explanation):
    row =  [header]
    if regex.search(r"\(.*\)", explanation):
        row.append(regex.match(r"[^(]*", explanation)[0])
        row.append(regex.search(r"\(.*\)", explanation)[0][1:-1])
    elif not regex.search(r"\(.*\)", explanation):
        row.append(explanation)
        row.append("")
    return row

for x in sorted(grammar_codes.abbreviations):
    row = row_prep(x, grammar_codes.abbreviations[x])
    narrow_only = x not in grammar_codes.abbreviations_high
    if narrow_only: table_narrow.append(row)
    if not narrow_only: table_narrow_broad.append(row)

for x in sorted(grammar_codes.abbreviations_high):
    if x not in grammar_codes.abbreviations: table_broad.append(row_prep(x, grammar_codes.abbreviations_high[x]))

for x in sorted(grammar_codes.ciw_abbreviations):
    if x not in grammar_codes.abbreviations or grammar_codes_ciw_abbreviations[x] != grammar_codes.abbreviations[x]: table_narrow_anishinaabemowin.append(row_prep(x, grammar_codes.ciw_abbreviations[x]))

codes_narrow_broad_div.innerHTML = tabulate.tabulate(table_narrow_broad, tablefmt='html')
codes_narrow_div.innerHTML = tabulate.tabulate(table_narrow, tablefmt='html')
codes_broad_div.innerHTML = tabulate.tabulate(table_broad, tablefmt='html')
codes_narrow_anishinaabemowin_div.innerHTML = tabulate.tabulate(table_narrow_anishinaabemowin, tablefmt='html')
