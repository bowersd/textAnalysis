#!/usr/bin/python
# vim: setfileencoding=utf-8
import re

def sep_punct(string, drop):
    #return "'".join(re.sub("(“|\()", "\g<1> ", re.sub("(”|…|\)|:|;|,|\*|\.|\?|!|/)", " \g<1>", string)).split("’")) #first separate trailing punc, then leading punc, then replace single quote ’ with '
    if not drop: return "'".join(re.split("‘|’", re.sub(r"(\{|\}|\[|\]|\"|“|\(|\)|”|—|…|:|;|,|\*|\.|\?|!|/)", r" \g<1> ", string))) #separate all punc, then replace single quote ’ with '
    return "'".join(re.split("‘|’", re.sub(r"(\{|\}|\[|\]|\"|“|\(|\)|”|—|…|:|;|,|\*|\.|\?|!|/)", " ", string))) #remove all punc, then replace single quote ’ with '
    #if not drop: return "'".join(re.split("‘|’|'", re.sub(r"('+($| )|(^| )'+(?=[^aeioAEIO])|\{|\}|\[|\]|\"|“|\(|\)|”|—|…|:|;|,|\*|\.|\?|!|/)", r" \g<1> ", string))) #separate all punc, then replace single quote ’ with '
    #return "'".join(re.split("‘|’|'", re.sub(r"('+($| )|(^| )'+(?=[^aeioAEIO])|\{|\}|\[|\]|\"|“|\(|\)|”|—|…|:|;|,|\*|\.|\?|!|/)", " ", string))) #remove all punc, then replace single quote ’ with '

def sent_break(*args):
    holder = []
    for a in args:
        for s in re.split(r"((\.|!|\?) )", a):
            holder.append(s)
    return holder
