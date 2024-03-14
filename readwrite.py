
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

def convert_interlinear_corrections_to_json(filename_in, *keys):
    with open(filename_in) as data:
        for i in range(len(data)): pass #cycle through the keys as a modulus

