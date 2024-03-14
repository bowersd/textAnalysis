import subprocess
#import externalcommand
import hfst
import re

def parse(fst_file, fst_format, *strings):
    com = ['hfst-lookup', "-q"]
    #no foma option...
    if fst_format == "xfst": com = ['lookup', '-q', '-flags', 'mbTT']
    #this can produce a hang by clogging buffers
    with open('__tmp.txt', 'w') as file_out: file_out.write("\n".join(strings))
    echo = subprocess.Popen(('cat', '__tmp.txt'), stdout=subprocess.PIPE)
    parse = subprocess.check_output(com + [fst_file], stdin=echo.stdout)
    echo.wait() #forces echo to wait until parse has completed
                #unclear why needed, as value of interest is in parse
    return parse
    #slimmer
    #return subprocess.check_output(com+[fst_file], stdin=echo.stdout)
    #alternatively actually write a string with a pipe 
    #though shell=True poses security risks:
    #com = " ".join(["echo", "\n".join(strings), "|"]) + " ".join(com)
    #parse = subprocess.Popen(com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #return parse.communicate()[0] #0=std out, 1=stderr

def parse_native(transducer, *strings):
    parser = hfst.HfstInputStream(transducer).read()
    print("optimizing transducer")
    parser.lookup_optimize()
    h = {}
    print("looking up strings")
    for s in strings: 
        if s not in h: 
            h[s] = []
            for p in parser.lookup(s): h[s].append((re.sub("@.*?@", "" ,p[0]), p[1])) #filtering out flag diacritics, which the hfst api does not do as of dec 2023
    return h
