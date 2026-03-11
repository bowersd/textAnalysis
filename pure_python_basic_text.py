import regex

def sep_punct(string, drop_punct): #diy tokenization, use nltk?
    if not drop_punct: return "'".join(regex.sub(r"(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", r" \g<1> ", string).split("’")) #separate all punc, then replace single quote ’ with '
    return "'".join(regex.sub(r"(\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", " ", string).split("’")) #remove all punc, then replace single quote ’ with '

def readin(filename):
    holder = []
    with open(filename, 'r') as f_in:
        for line in f_in:
            holder.append(line.strip())
    return holder
