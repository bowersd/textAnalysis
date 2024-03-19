import sys
import preprocess as pre

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        for line in f:
            for x in pre.sep_punct(line.lower().strip(), True).split():
                print(x)
