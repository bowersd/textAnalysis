
def initialize(*lexicon):
    r = []
    total = 0
    for w in lexicon:
        state = 0
        for c in w:
            prev = state
            nxt = total+1
            r.append([state, (c, nxt), 1])
            total = nxt
            state = nxt
        r.append([state, (), 1])
    return r

def merge(*rules):
    h = []
    last = max([r[0] for r in rules])
    state = 0
    to_amend = [r for r in rules]
    while state <= last:
        collapsible = [r for r in to_amend if r[0] == state]
        while collapsible:
            cur = collapsible.pop()
            nu = [x for x in cur]
            revise = []
            for i in reversed(range(len(collapsible))):
                if collapsible[i][1][:1] == cur[1][:1]: #ranges to work around final states having empty right-hand sides
                    nu[-1] += cur[-1]
                    if cur[1]: revise.append(collapsible[i][1][1])
                    collapsible = collapsible[:i]+collapsible[i+1:]
            h.append(nu)
            for s in revise:
                for i in range(len(to_amend)):
                    if to_amend[i][0] == s:
                        to_amend[i][0] = nu[1][1]

        state += 1
    return h

def trim_dead(*rules):
    h = []
    states = [0]
    while states:
        cur = states.pop()
        for rule in rules:
            if rule[0] == cur:
                h.append(rule)
                if rule[1]: states.append(rule[1][1])
    return h

def probabilize(*rules):
    h = []
    states = []
    for r in rules:
        if r[0] not in states: states.append(r[0])
    for s in states:
        adjust = [r for r in rules if r[0] == s]
        denom = sum([r[-1] for r in adjust])
        for r in adjust: h.append([r[0], r[1], r[2]/denom])
    return h

def traverse(chars, rules):
    state = [0]
    for c in chars:
        s = state.pop()
        for r in rules:
            if r[0] == s and c in r[1][:1]: state.append(r[1][1])
    return state

def is_final(state, rules):
    return any([r[:2] == [state, ()] for r in rules])

def predict(chars, state, rules):
    states = [(state, 1, chars)]
    top_p = 0
    prediction = ""
    while states:
        s = states.pop()
        for r in rules:
            p = r[-1]*s[1]
            if r[0] == s[0] and p >= top_p:
                if not r[1]: 
                    prediction = s[-1]
                    top_p = p
                else:
                    states.append((r[1][1], p, s[-1]+r[1][0]))
    return prediction

def main(chars, rules):
    s = traverse(chars, rules)
    if not s: return "I'm sorry, I don't know any words that start like that"
    else: return predict(chars, s[0], rules)

if __name__ == "__main__":
    print("initialization")
    init = initialize("cat", "call", "cats", "dog")
    for i in init: print(i)
    print("merge")
    m = merge(*init)
    for x in m: print(x)
    print("trim")
    t = trim_dead(*m)
    for x in t: print(x)
    print("probabilistic")
    p = probabilize(*t)
    for x in p: print(x)
    print("prediction for 'ca'")
    print(predict('ca', traverse('ca', p)[0], p))
