#!/usr/bin/python
# vim: setfileencoding=utf-8
import re

def sep_punct(string):
    #return "'".join(re.sub("(“|\()", "\g<1> ", re.sub("(”|…|\)|:|;|,|\*|\.|\?|!|/)", " \g<1>", string)).split("’")) #first separate trailing punc, then leading punc, then replace single quote ’ with '
    return "'".join(re.sub("(\{|\}|\[|\]|\"|“|\(|\)|”|…|:|;|,|\*|\.|\?|!|/)", " \g<1> ", string).split("’")) #separate all punc, then replace single quote ’ with '

def sent_break(*args):
    holder = []
    for a in args:
        for s in re.split("((\.|!|\?) )", a):
            holder.append(s)
    return holder
