import re
import needleman

def parser_out_string_dict(string):
    """reformats STRING in output FORM to dict keyed by first word"""
    proc = {}
    for line in string.split('\n'):
        if not line: continue 
        split = line.split()
        if split[0] not in proc: proc[split[0]] = [split[1:]]
        elif split[1:] not in proc[split[0]]: proc[split[0]].append(split[1:]) 
    return proc

def minimal_filter(*msds):
    return [m for m in msds if m[1] == msds[0][1]]

def min_edits(typed, *generated):
    h = []
    for g in generated:
        alnd = needleman.align(typed, g, -1, needleman.make_id_matrix(typed, g))
        h.append(sum([alnd[0][i] != alnd[1][i] for i in range(len(alnd[0]))]))
    return min(h)

def min_morphs(*msds):
    """the length of the shortest morphosyntactic description"""
    return min([m[0].count("+") for m in msds])

def disambiguate(target, f, *msds): 
    """the earliest of the morphosyntactic descriptions|f(m) = target"""
    #prioritizing order allows weighting schemes to be exploited
    for i in range(len(msds)):
        if f(msds[i]) == target: return i
    #first default
    return 0

def extract_regex(string, regex):
    """pull regex out of string"""
    #generalized to allow searches for +V+AI, or +VAI
    if re.search(regex, string): return re.search(regex, string).group(0)
    return None

def extract_lemma(string, pos_regex):
    """pull lemma out of string"""
    #lemma is always followed by Part Of Speech regex
    #lemma may be preceeded by prefixes, else word initial
    #if re.search(pos_regex, string): return re.search("(^|\+)(.*?)"+pos_regex, string).group(2)
    if "+Cmpd" in string:
        cmpd = []
        for x in re.split("\+Cmpd", string):
            cmpd.append(re.split(pos_regex, x)[0].split("+")[-1])
            #return "+".join([re.split(pos_regex, x)[0].split("+")[-1] for x in re.split("+Cmpd", string)])
        #print(cmpd)
        return "+".join(cmpd)
    if re.search(pos_regex, string): return re.split(pos_regex, string)[0].split("+")[-1] #last item before pos tag, after all other morphemes, is lemma
    return None

def extract_msd(string, pos_regex):
    """pull morphosyntactic description out of string"""
    #need everything but the lemma and pos tag
    #two lines for readability
    if re.search(pos_regex, string):
        pos = "\+".join(re.search(pos_regex, string).group(0).split("+")) #need to escape + or interpreted as Kleene +
        #pos = re.search(pos_regex, string).group(0).encode('string-escape') #need to escape + or interpreted as Kleene +
        l = brackets(re.split(pos_regex, string)[0].split("+")[-1]) #lemma
        #l = re.split(pos_regex, string)[0].split("+")[-1].encode('string-escape') #lemma
        lpos = "".join([l, pos])
        r = re.search("(.*)"+lpos+"(.*)", string)
        #print string, pos, l, r
        if not (r.group(1) or r.group(2)): return None
        if not (r.group(1) and r.group(2)): return "".join([r.group(1), r.group(2)])
        #leaves a _ to demarcate where lemma was
        return "_".join([r.group(1), r.group(2)])
    return None

def plus_to_dot(string):
    if string: return ".".join(string.strip("+").split("+"))
    return None

def slash_to_e(string):
    if string: return "".join(string.split('/'))

def brackets(string):
    if string == "("  or string == ")": return "\\"+string
    return string

