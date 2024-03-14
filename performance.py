#how many words in dictionary have examples

def performance(lexicon, corpus):
    entries_w_exe = [0, 0]
    exes_matching_lex = 0
    flag = False
    used_exes = []
    for entry in lexicon:
        for i in range(len(corpus)):
            if entry in corpus[i]:
                exes_matching_lex += 1
                if i not in used_exes: used_exes.append(i)
                if not flag:
                    flag = True
                    entries_w_exe[0] += 1
        if not flag: entries_w_exe[1] += 1
    print("Percentage of lexicon entries with an example:", 100*round(entries_w_exe[0]/(entries_w_exe[0]+entries_w_exe[1]), 3))
    print("Average number of examples per lexicon entry:", round(exes_matching_lex/len(lexicon), 3))
    print("Number of examples with no matches at all:", len(corpus) - len(used_exes)) #this could be calculated by just testing for all Nones in sentence (if it has gone through my lemmatizer function)
    #performance[any([lemma in s for s in sentences])] += 1
    #for s in sentences:
    #    if lemma in s
