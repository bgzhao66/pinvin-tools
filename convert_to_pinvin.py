import sys
import os
import re
import argparse

# define constants for post-fixes
POSTFIX_MAPPING = """
ā a
á ar
ǎ aa
à ah
āi ai
ái air
ǎi ae
ài ay
ān an
án arn
ǎn aan
àn am
āng ang
áng arng
ǎng aang
àng amg
āo ao
áo aor
ǎo au
ào aw
ē e
é er
ě ee
è eh
ê ai
ê̄ ai
ế air
ê̌ ae
ề ay
ēi ei
éi eir
ěi ea
èi ey
ēn en
én ern
ěn een
èn em
ēng eng
éng erng
ěng eeng
èng emg
er el
ér erl
ěr eel
èr ehl
ḿ m
m̀ m
ń n
ň n
ǹ n
ńg ng
ňg ng
ǹg ng
ō o
ó or
ǒ oo
ò oh
ōng ong
óng orng
ǒng oong
òng omg
ōu ou
óu our
ǒu oa
òu ow
ī i
í ir
ǐ yi
ì ih
īn in
ín irn
ǐn yin
ìn im
īng ing
íng irng
ǐng ying
ìng img
iā ia
iá ya
iǎ iaa
ià iah
iān ian
ián yan
iǎn iaan
iàn iam
iāng iang
iáng yang
iǎng iaang
iàng iamg
iāo iao
iáo yao
iǎo iau
iào iaw
iē ie
ié ye
iě iee
iè ieh
iōng iong
ióng yong
iǒng ioong
iòng iomg
iōu iou
ióu you
iǒu ioa
iòu iow
iu iou
iū iou
iú you
iǔ ioa
iù iow
ū u
ú ur
ǔ wu
ù uh
uā ua
uá wa
uǎ uaa
uà uah
uāi uai
uái wai
uǎi uae
uài uay
uān uan
uán wan
uǎn uaan
uàn uam
uāng uang
uáng wang
uǎng uaang
uàng uamg
uēi uei
uéi wei
uěi uea
uèi uey
uī uei
uí wei
uǐ uea
uì uey
un uen
ūn uen
ún wen
ǔn ueen
ùn uem
uēn uen
uén wen
uěn ueen
uèn uem
uēng ueng
uéng weng
uěng ueeng
uèng uemg
uō uo
uó wo
uǒ uoo
uò uoh
ü eu
ǖ eu
ǘ eur
ǚ yu 
ǜ ew
üe eue
üē eue
üé yue
üě euee
üè eueh
ün euen
ǖn euen
ǘn yuen
ǚn eueen
ǜn euem
üan euan
üān euan
üán yuan
üǎn euaan
üàn euam
"""

#define constants for pre-fixes
PREFIX_MAPPING = """
yu ü
yū ü
yú ǘ
yǔ ǚ
yù ǜ
ju jü
jū jü
jú jǘ
jǔ jǚ
jù jǜ
qu qü
qū qü
qú qǘ
qǔ qǚ
qù qǜ
xu xü
xū xü
xú xǘ
xǔ xǚ
xù xǜ
w u
wu u
wū ū
wú ú
wǔ ǔ
wù ù
y i
yi i
yī ī 
yí í
yǐ ǐ
yì ì
"""

TONELESS_MAPPING = """
ā a
á a
ǎ a
à a
ē e
é e
ě e
è e
ê ai
ê̄ ai
ế ai
ê̌ ai
ề ai
ḿ m
m̀ m
ń n
ň n
ǹ n
ō o
ó o
ǒ o
ò o
ī i
í i
ǐ i
ì i
ū u
ú u
ǔ u
ù u
ü v
ǖ v
ǘ v
ǚ v
ǜ v
"""

STANDARD_CHINESE = "standard_chinese.txt"
PINYIN_CODE = "pinyin.txt"
PINYIN_SIMP_DICT = "pinyin_simp.dict.txt"
PINYIN_SIMP_EXT1_DICT = "pinyin_simp_ext1.dict.txt"
PINYIN_PHRASE = "pinyin_phrase.txt"

def get_postfix_mapping():
    mapping = dict()
    for line in POSTFIX_MAPPING.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        pinyin, postfix = line.split()
        mapping[pinyin] = postfix
    return mapping

def get_prefix_mapping():
    mapping = dict()
    for line in PREFIX_MAPPING.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        pinyin, prefix = line.split()
        mapping[pinyin] = prefix
    return mapping

# get toneless mapping
def get_toneless_mapping():
    mapping = dict()
    for line in TONELESS_MAPPING.split('\n'):
        line = line.strip()
        if len(line) == 0:
            continue
        pinyin, toneless = line.split()
        mapping[pinyin] = toneless
    return mapping

kPostfixMampping = get_postfix_mapping()
kPrefixMapping = get_prefix_mapping()
kTonelessMapping = get_toneless_mapping()

# get the toneless pinyin from pinyin
def get_toneless_pinyin(pinyin):
    toneless = ''
    for c in pinyin:
        if c in kTonelessMapping:
            toneless += kTonelessMapping[c]
        else:
            toneless += c
    return toneless

# geth the tonal pinvin from pinyin
def get_pinvin(pinyin):
    # substitute the prefix from pinyin
    n = len(pinyin)
    for i in range(n):
        prefix = pinyin[:(n-i)]
        if prefix in kPrefixMapping:
            pinyin = kPrefixMapping[prefix] + pinyin[(n-i):]
            break
    # substitute the postfix from pinyin
    n = len(pinyin)
    for i in range(n):
        postfix = pinyin[i:]
        if postfix in kPostfixMampping:
            pinyin = pinyin[:i] + kPostfixMampping[postfix]
            break
    # substitute '[jqx]eu' to '[jqx]u'
    pinyin = re.sub(r'([jqx])eu', r'\1u', pinyin)
    return pinyin

# get the pinvin seq from pinyin seq with prefixing a 'v' to non-first elements beginning with 'a,o,e,i,u,y,w'
def get_pinvin_seq(pinyin_seq):
    pinvin_seq = []
    for i in range(len(pinyin_seq)):
        pinyin = pinyin_seq[i]
        pinvin = get_pinvin(pinyin)
        if i > 0 and begin_with_vowel(pinvin):
            pinvin = 'v' + pinvin
        pinvin_seq.append(pinvin)
    return pinvin_seq

# get the toneless pinyin seq from pinyin seq
def get_toneless_pinyin_seq(pinyin_seq):
    return [get_toneless_pinyin(pinyin) for pinyin in pinyin_seq]

# get chinese code from a file with format "pinyin: word1 word2 ..."
def get_standard_code_from_file(file):
    words = dict()
    # read the file line by line
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            #skip line beginning with '#' or empty line
            if len(line) == 0 or line[0] == '#':
                continue
            # split the line into words by spaces or commas or colons
            chars = re.split(r'[\s,:]', line)
            if len(chars) <= 1:
                continue
            pinyin = chars[0]
            for char in chars[1:]:
                if len(char.strip()) == 0:
                    continue
                if char not in words:
                    words[char] = []
                words[char].append(pinyin)
    return words

# get pinyin code from a file with format "UNICODE: py1,py2 # word"
def get_pinyin_code_from_file(file):
    words = dict()
    with open(file  , 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            parts = re.split(r'\s+', line)
            if len(parts) < 4:
                continue
            word = parts[3].strip()
            pinyins = re.split(r',', parts[1])
            if word not in words:
                words[word] = []
            for pinyin in pinyins:
                words[word].append(pinyin)
    return words

# get pinyin phrase from a file with format "word: py1 py2 ..."
# return a dictionary of word and a list of pinyin code sequences, e.g. {'word': [['py1', 'py2'], ['py3', 'py4']]}
def get_pinyin_phrase_from_file(file):
    words = dict()
    with open(file , 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            parts = re.split(r':\s+', line)
            if len(parts) < 2:
                continue
            word = parts[0].strip()
            pinyins = re.split(r'\s+', parts[1])
            if word not in words:
                words[word] = []
            words[word].append(pinyins)
    return words

# get pinyin phrases
def get_pinyin_phrases():
    return get_pinyin_phrase_from_file(PINYIN_PHRASE)

kPinyinCodes = get_pinyin_code_from_file(PINYIN_CODE)
kStandardCodes = get_standard_code_from_file(STANDARD_CHINESE)

# check if the codes of a word is consistent with the code of characters, if not, return false; otherwise, return true
# word: a list of characters, e.g. ['character1', 'character2']
# word_code: a list of tonal pinyin code sequences, e.g. [['code1', 'code2'], ['code3', 'code4']]
# char_codes: a dictionary of characters and a list of pinyin code sequences, e.g. {'character': ['code1', 'code2']}
# Notes: a word is a list of characters, and the function should not use get_descartes_products
def is_consistent(word, word_code, char_codes, strict=True):
    if len(word) != len(word_code):
        return False
    for i in range(len(word)):
        if word[i] not in char_codes:
            return False
        if strict and word_code[i] not in char_codes[word[i]]:
            return False
        if not strict:
            if word_code[i] not in kPinyinCodes[word[i]]:
                if not (word[i] in kStandardCodes and word_code[i] in kStandardCodes[word[i]]):
                    return False
            return True
    return True

# purge inconsistent phrases
def purge_inconsistent_phrases(words, strict=True):
    char_codes = get_pinyin_code_of_chars()
    for word in get_sorted_keys(words):
        for pinyin_seq in words[word]:
            if not is_consistent(word, pinyin_seq, char_codes, strict = strict):
                del words[word]
                break

# get inconsistent phrases, with input of a dictionary of word and a list of pinyin code sequences,
#   e.g. {'word': [['code1', 'code2'], ['code3', 'code4']]}
#  If strict is True, if any character of the word is not found in the char_codes, the word is inconsistent;
#  otherwise, only when the first character is not found in the char_codes, the word is inconsistent.
def get_inconsistent_phrases(words, strict=True):
    char_codes = get_pinyin_code_of_chars()
    inconsistent = dict()
    for word in get_sorted_keys(words):
        for pinyin_seq in words[word]:
            if not is_consistent(word, pinyin_seq, char_codes, strict = strict):
                if word not in inconsistent:
                    inconsistent[word] = []
                inconsistent[word].append(pinyin_seq)
    return inconsistent

# get pinyin code of chinese characters
def get_pinyin_code_of_chars():
    words = get_pinyin_code_from_file(PINYIN_CODE)
    standard_code = get_standard_code_from_file(STANDARD_CHINESE)
    # prefer the standard code if different
    for word in standard_code:
        words[word] = standard_code[word]
    return words

# get pinyin codes of characters
# return a dictionary of word and a list of pinyin code sequences
def get_code_of_chars_in_list():
    words = get_pinyin_code_of_chars()
    for word in words:
        words[word] = [[pinyin] for pinyin in words[word]]
    return words
 
 # read words from file
def get_words_from_file(file):
    words = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            word = re.split(r'\s+', line)
            if len(word) == 0:
                continue
            words.append(word[0])
    return words

def begin_with_vowel(encode):
    return encode[0] in ['a', 'o', 'e', 'i', 'u', 'y', 'w']

# prepend 'v' to non-first elements in a list of encodes beginning with 'a,o,e,i,u,y,w'
def prepend_v(encodes):
    for i in range(1, len(encodes)):
        encode = encodes[i]
        if begin_with_vowel(encode):
            encodes[i] = 'v' + encode
    return encodes

# get all descartes products of encodes which is a list of list of elements
def get_descartes_products(encodes):
    descartes = [[]]
    for encode in encodes:
        new_descartes = []
        for descarte in descartes:
            for element in encode:
                new_descartes.append(descarte + [element])
        descartes = new_descartes
    return descartes

# get the pinyin code of words from a list of words
# return a dictionary of word and a list of tonal pinyin code sequences
def get_code_of_words(words: list) -> dict:
    char_codes = get_pinyin_code_of_chars()
    word_codes = dict()
    for word in words:
        word_codes[word] = []
        encodes = []

        on_error = False
        for char in word:
            if char not in char_codes:
                print(char, "Not found", file=sys.stderr)
                on_error = True
                break
            encodes.append(char_codes[char])
        if on_error:
            continue
        word_codes[word] = get_descartes_products(encodes)
    return word_codes

# get the frequency of words from a file
def get_frequency_from_file(file):
    freq = dict()
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            word, code, frequency = line.split('\t')
            if word not in freq:
                freq[word] = dict()
            if code not in freq[word]:
                freq[word][code] = 0
            freq[word][code] += int(frequency)
    return freq

# get the frequency of a character from freq_dict with default value 0.
def get_freq_of_word(word, toneless_code, freq_dict):
    if word not in freq_dict:
        return 0
    if toneless_code not in freq_dict[word]:
        return 0
    return freq_dict[word][toneless_code]

# get the sorted keys of a dictionary
def get_sorted_keys(dict):
    keys = list(dict.keys())
    keys.sort()
    return keys

def get_prepended_v_seqs(pinvin_seq):
    res = [pinvin_seq]
    if begin_with_vowel(pinvin_seq[0]):
        res.append(['v' + pinvin_seq[0]] + pinvin_seq[1:])
    return res

# Get all the character in words with its inconsistent pinyin, with
# output of a dictionary of pinyin and a dictionary of word
#   e.g. {'pinyin': {'char': ['word1', 'word2']}}
def get_inconsistent_chars():
    pinyin_phrases = get_pinyin_phrases()
    codes = get_pinyin_code_of_chars()
    inconsistent = get_inconsistent_phrases(pinyin_phrases, strict = False)
    chars = dict()
    for word in inconsistent:
        for pinyin_seq in inconsistent[word]:
            for i in range(len(word)):
                py = pinyin_seq[i]
                ch = word[i]
                if ch not in codes or py in codes[ch]:
                    continue
                # add the character to the inconsistent list
                if py not in chars:
                    chars[py] = dict()
                if ch not in chars[py]:
                    chars[py][ch] = []
                chars[py][ch].append(word)
    return chars

# print the word_codes which is a dictionary of key,list into a file with the format of word code frequency
# word_codes: a dictionary of word and a list of tonal pinyin code sequences,
#               e.g. {'word': [['code1', 'code2'], ['code3', 'code4']]}
def print_word_codes(word_codes, words_freq, fluent=True, outfile=sys.stdout):
    codes = dict()
    for word in word_codes:
        length = len(word)
        for pinyin_seq in word_codes[word]:
            toneless = ' '.join(get_toneless_pinyin_seq(pinyin_seq))
            freq = get_freq_of_word(word, toneless, words_freq)
            for pinvin_seq in get_prepended_v_seqs(get_pinvin_seq(pinyin_seq)):
                sep = ' ' if fluent else ''
                code = sep.join(pinvin_seq)
                if length not in codes:
                    codes[length] = dict()
                if code not in codes[length]:
                    codes[length][code] = dict()
                codes[length][code][word] = freq

    for length in get_sorted_keys(codes):
        for code in get_sorted_keys(codes[length]):
            for word in get_sorted_keys(codes[length][code]):
                freq = codes[length][code][word]
                print("%s\t%s\t%i" % (word, code, freq), file=outfile)

def show_inconsistent_chars(type):
    chars = get_inconsistent_chars()
    pinyin_codes = get_pinyin_code_from_file(PINYIN_CODE)
    for py in get_sorted_keys(chars):
        for ch in get_sorted_keys(chars[py]):
            if ch not in pinyin_codes:
                print(ch, ": Not found in pinyin", file=sys.stderr)
                continue
            if type == '0': # in pinyin codes format
                print("UNICODE: ", py, " # ",  ch, file=sys.stdout)
            elif type == '1': # in standard codes format
                if ch not in kStandardCodes:
                    print(py,": ", ch, "Not found in standard", file=sys.stderr)
                    continue
                print(py,": ", ch, file=sys.stdout)
            else: # in words format
                for word in chars[py][ch]:
                    print(word, file=sys.stdout)

def get_header(name, input_tables):
    hdr = f"""# rime dictionary
# encoding: utf-8

---
name: {name}
version: "0.1"
sort: by_weight
"""
    if input_tables:
        hdr += "import_tables:\n"
        for table in input_tables:
            hdr += f"  - {table}\n"
    hdr += "...\n"
    return hdr

# compare the code of standard chinese and pinyin, if not match, print both of them
def compare_code():
    char_codes = get_pinyin_code_of_chars()
    standard_code = get_standard_code_from_file(STANDARD_CHINESE)
    for word in standard_code:
        if word not in char_codes:
            print(word, "Not found", file=sys.stderr)
            continue

        standard_code[word].sort()
        char_codes[word].sort()
        if standard_code[word] != char_codes[word]:
            print(word, standard_code[word], char_codes[word], file=sys.stdout)

if __name__ == "__main__":
    # control output with a argparser as follows:
    # python convert_to_pinyin.py --chinese_code <input_file>
    # --chinese_code: print chinese code
    # --name <name>: the name of the output file
    # --input_tables <input1>...<inputN>: the input tables
    # --pinyin_phrase: print pinyin phrase
    # --exclude_pinyin_phrase: exclude pinyin phrase
    # --check_pinyin: check pinyin phrase
    # --show_inconsistent <type>: show inconsistent characters and words, with 0 for characters, otherwise for words
    # --compare_code: compare code of standard chinese and pinyin
    # --fluent: whether to print in fluent mode
    # <input_file>: the input file

    parser = argparse.ArgumentParser()
    parser.add_argument("--chinese_code", help="print chinese code", action="store_true")
    parser.add_argument("--name", help="the name of the current table", required = False)
    parser.add_argument("--input_tables", nargs='+', help="the input tables", default=None)
    parser.add_argument("--pinyin_phrase", help="print pinyin phrase", action="store_true")
    parser.add_argument("--exclude_pinyin_phrase", help="exclude pinyin phrase", action="store_true")
    parser.add_argument("--check_pinyin", help="check pinyin phrase", action="store_true")
    parser.add_argument("--show_inconsistent", nargs='?', help="show inconsistent characters and words", default=None)
    parser.add_argument("--compare_code", help="compare code of standard chinese and pinyin", action="store_true")
    parser.add_argument("--fluent", help="whether to print in fluent mode", action="store_true")
    parser.add_argument("input_file", nargs="?", help="the input file", default=None)
    args = parser.parse_args()

    if args.compare_code:
        compare_code()
        sys.exit(0)

    if not args.show_inconsistent:
        print(get_header(args.name, args.input_tables), file=sys.stdout)

    if args.chinese_code:
        char_codes = get_code_of_chars_in_list()
        words_freq = get_frequency_from_file(PINYIN_SIMP_DICT)
        print_word_codes(char_codes, words_freq)

    if args.input_file:
        words = get_words_from_file(args.input_file)
        word_codes = get_code_of_words(words)
        if args.exclude_pinyin_phrase:
            pinyin_phrases = get_pinyin_phrases()
            purge_inconsistent_phrases(pinyin_phrases)
            for word in pinyin_phrases:
                if word in word_codes:
                    del word_codes[word]
        words_freq = get_frequency_from_file(PINYIN_SIMP_EXT1_DICT)
        print_word_codes(word_codes, words_freq, fluent=args.fluent)
    elif args.pinyin_phrase:
        pinyin_phrases = get_pinyin_phrases()
        if args.check_pinyin:
            purge_inconsistent_phrases(pinyin_phrases, strict = False)
        words_freq = get_frequency_from_file(PINYIN_SIMP_EXT1_DICT)
        print_word_codes(pinyin_phrases, words_freq, fluent=args.fluent)
    elif args.show_inconsistent:
        type = args.show_inconsistent
        show_inconsistent_chars(type)
