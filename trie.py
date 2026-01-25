
def initialize(*lexicon):
    r = {}
    for w in lexicon:
        state = ""
        for c in w:
            cand = (state, (c, state+c))
            state += c
            if cand not in r: r[cand] = 1
            else: r[cand] += 1
        final = (state, ())
        if final not in r: r[final] = 1
        else: r[final] += 1
    return r

#def merge(*rules):
#    h = []
#    last = max([r[0] for r in rules])
#    state = 0
#    to_amend = [r for r in rules]
#    while state <= last:
#        collapsible = [r for r in to_amend if r[0] == state]
#        while collapsible:
#            cur = collapsible.pop()
#            nu = [x for x in cur]
#            revise = []
#            for i in reversed(range(len(collapsible))):
#                if collapsible[i][1][:1] == cur[1][:1]: #ranges to work around final states having empty right-hand sides
#                    nu[-1] += cur[-1]
#                    if cur[1]: 
#                        for j in range(len(to_amend)):
#                            if to_amend[j][0] == collapsible[i][1][1]:
#                                to_amend[j][0] = nu[1][1]
#                    collapsible = collapsible[:i]+collapsible[i+1:]
#            h.append(nu)
#        state += 1
#    return h

#def trim_dead(*rules):
#    h = []
#    states = [0]
#    while states:
#        cur = states.pop()
#        for rule in rules:
#            if rule[0] == cur:
#                h.append(rule)
#                if rule[1]: states.append(rule[1][1])
#    return h

def probabilize(rules):
    h = []
    states = []
    for r in rules:
        if r[0] not in states: states.append(r[0])
    for s in states:
        adjust = [r for r in rules if r[0] == s]
        denom = sum([rules[r] for r in adjust])
        for r in adjust: h.append((r[0], r[1], rules[r]/denom))
    return tuple(h)

def traverse(chars, rules):
    state = [""]
    for c in chars:
        s = state.pop()
        for r in rules:
            if r[0] == s and c in r[1][:1]: state.append(r[1][1])
    return state

def is_final(state, rules):
    return any([r[:2] == (state, ()) for r in rules])

def predict(chars, state, rules):
    states = [(state, 1, chars)] #state, p, chars
    top_p = 0
    prediction = ""
    while states:
        s = states.pop()
        for r in rules:
            p = r[-1]*s[1]
            if r[0] == s[0] and p >= top_p: #so there could be a tie, but only one survives
                if not r[1]: 
                    prediction = s[-1]
                    top_p = p
                else:
                    states.append((r[1][1], p, s[-1]+r[1][0]))
    return prediction

def predict_short(chars, state, rules):
    states = [(state, 1, 0, chars)] #state, p, depth, chars
    top_p = 0
    predictions = []
    depth = float("inf")
    while states:
        s = states.pop()
        for r in rules:
            if r[0] == s[0] and s[2] <= depth:
                p = r[-1]*s[1]
                if not r[1]: 
                    print(r)
                    predictions.append((s[2], p, chars))
                    depth = s[2]
                else:
                    states.append((r[1][1], p, s[2]+1, s[-1]+r[1][0]))
    return sorted(sorted(predictions, reverse=True, key=lambda x: x[1]), key=lambda x: x[0])[0][-1]

def main(chars, rules, pred_func):
    s = traverse(chars, rules)
    if not s: return "I'm sorry, I don't know any words that start like that"
    else: return pred_func(chars, s[0], rules)

if __name__ == "__main__":
    print("initialization")
    init = initialize("cat", "call", "cats", "can", "con", "dog")
    print("probabilistic")
    p = probabilize(init)
    for x in p: print(x)
    print("prediction for 'ca'")
    print(predict('ca', traverse('ca', p)[0], p))
