import os
import re
import sys
import argparse

# print only the words of a given length from a file
def filter_by_length(file, length):
    with open(file) as f:
        for line in f:
            for word in re.findall(r'\b\w+\b', line):
                if len(word) == length:
                    print(word)

# filter a file in the format "WORD: py1 py2 ... pyN" to skip the lines matching '地: .*de\s*$' or '得: .*de\s*$'
def filter_dedider(file):
    with open(file) as f:
        for line in f:
            line = line.strip()
            if re.match(r'.+地: .*de\s*$', line) or re.match(r'.+得: .*de\s*$', line):
                continue
            print(line)

if __name__ == '__main__':
    # Handle command line arguments with argparse
    # python filter_words.py <file>
    # --length <length>: print only the words of the given length
    # --filter_dedider: filter the words ending '地' and '得' characters
    parser = argparse.ArgumentParser(description='Print words of a given length from a file')
    parser.add_argument('file', type=str, help='The file to read words from')
    parser.add_argument('--length', type=int, help='The length of the words to print', default=0)
    parser.add_argument('--filter_dedider', action='store_true', help='Filter the words ending in "地" and "得" characters')
    args = parser.parse_args()

    if args.length:
        filter_by_length(args.file, args.length)
    elif args.filter_dedider:
        filter_dedider(args.file)
    else:
        parser.print_help()
        sys.exit(1)