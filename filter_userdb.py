import re
import sys
import argparse

def get_threshold(maxlength):
    if maxlength is None:
        return sys.maxsize
    return maxlength

# Read in a file line by line
def filter_file(path, maxlength=None):
    threshold = get_threshold(maxlength)
    words = dict()
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if re.match(r'#', line):
                print(line)
                continue
            codes = line.split("\t")[0].split()
            n = len(codes)
            if n not in words:
                words[n] = []
            words[n].append(line)

    for n in sorted(words.keys()):  # sort by the length of the code
        if n > threshold:
            continue
        print("# %d words" % n)
        for line in words[n]:
            print(line)

# python filter_userdb.py [FILENAME]
# --maxlength <NUM>: filter out words longer than <NUM>
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the file to filter")
    parser.add_argument("--maxlength", type=int, help="filter out words longer than <NUM>")

    args = parser.parse_args()
    filter_file(args.filename, maxlength=args.maxlength)

if __name__ == "__main__":
    main()
