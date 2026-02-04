import readwrite
import trie

if __name__ == "__main__":
    data = readwrite.readin('nish_words.txt')
    init = trie.initialize(*data)
    lemmata = readwrite.readin('lemmata_dataset.txt')
    misfits = []
    for lem in lemmata:
        if (lem, ()) in init:
            init[(lem, ())] += 1
            for i in range(len(lem)):
                init[(lem[:i], (lem[i], lem[:i+1]))] += 1
        elif lem not in misfits: misfits.append(lem)
    p = trie.probabilize(init)
    print("nod_entries_lemma_freq = ", p)
    print("#######")
    print("####misfits###")
    print("#######")
    for m in misfits: print(m)

