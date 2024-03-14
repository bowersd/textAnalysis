
def readin(filename):
    holder = []
    with open(filename, 'r') as f_in:
        for line in f_in:
            holder.append(line.strip())
    return holder

def burn_metadata(burn_target, *lines):
    return lines[burn_target:]

def writeout(filename, *lines):
    with open(filename, 'w') as f_out:
        for l in lines:
            f_out.write(l+"\n")

