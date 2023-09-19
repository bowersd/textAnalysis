def winnow(analysis_in, *wheat):
    #translation suite does not cover preverbs, clitics, reduplication, participles, derivational morphology (and others)
    #to allow the translation suite to function, we separate what it can handle from what it can't
    h = []
    chaff = []
    for a in analysis_in:
        if a in wheat: h.append(a)
        else: chaff.append(a)
    return (h, chaff)
