import os
import re

# print only the words of a given length from a file
def filter_words(file, length):
    with open(file) as f:
        for line in f:
            for word in re.findall(r'\b\w+\b', line):
                if len(word) == length:
                    print(word)

# pass the file and the length of the words you want to print as command line arguments
if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('Usage: python filter_words.py <file> <length>')
    else:
        filter_words(sys.argv[1], int(sys.argv[2]))