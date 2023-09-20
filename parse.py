import subprocess
#import externalcommand

def parse(fst_file, fst_format, *strings):
    com = ['hfst-lookup', "-q"]
    #no foma option...
    if fst_format == "xfst": com = ['lookup', '-q', '-flags', 'mbTT']
    #this can produce a hang by clogging buffers
    echo = subprocess.Popen(('echo', "\n".join(strings)), stdout=subprocess.PIPE)
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

