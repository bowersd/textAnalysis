
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
        r.append([state, (,), 1])
    return r

if __name__ == "__main__":
    for r in initialize("cat", "call", "dog"): print(r)
