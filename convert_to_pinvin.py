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
def get_chinese_code(file):
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

# get pinyin code of chinese characters
def get_pinyin_code_of_chars():
    words = get_pinyin_code_from_file(PINYIN_CODE)
    chinese_code = get_chinese_code(STANDARD_CHINESE)
    for word in chinese_code:
        if word not in words:
            words[word] = chinese_code[word]
        else:
            for pinyin in chinese_code[word]:
                if pinyin not in words[word]:
                    words[word].append(pinyin)
    return words

# get chinese code by get_chinese_code
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

# get the frequency of a character from freq_dict with default value 1.
def get_freq_of_word(word, toneless_code, freq_dict):
    if word not in freq_dict:
        return 1
    if toneless_code not in freq_dict[word]:
        return 1
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

# print the word_codes which is a dictionary of key,list into a file with the format of word code frequency
# word_codes: a dictionary of word and a list of tonal pinyin code sequences,
#               e.g. {'word': [['code1', 'code2'], ['code3', 'code4']]}
def print_word_codes(word_codes, words_freq, outfile=sys.stdout):
    codes = dict()
    for word in word_codes:
        for pinyin_seq in word_codes[word]:
            toneless = ' '.join(get_toneless_pinyin_seq(pinyin_seq))
            freq = get_freq_of_word(word, toneless, words_freq)
            for pinvin_seq in get_prepended_v_seqs(get_pinvin_seq(pinyin_seq)):
                code = ' '.join(pinvin_seq)
                if code not in codes:
                    codes[code] = dict()
                codes[code][word] = freq
    
    for code in get_sorted_keys(codes):
        for word in get_sorted_keys(codes[code]):
            freq = codes[code][word]
            print("%s\t%s\t%i" % (word, code, freq), file=outfile)

# print the chinese code in the same way
def print_chinese_code(char_codes, outfile=sys.stdout):
    kWordsFreq = get_frequency_from_file(PINYIN_SIMP_DICT)
    
    codes = dict()
    for word in char_codes:
        for code in char_codes[word]:
            if code not in codes:
                codes[code] = []
            codes[code].append(word)
            if begin_with_vowel(code):
                altcode = 'v' + code
                if altcode not in codes:
                    codes[altcode] = []
                codes[altcode].append(word)
    
    for code in get_sorted_keys(codes):
        for word in set(codes[code]):
            freq = get_freq_of_word(word, kWordsFreq)
            print("%s\t%s\t%i" % (word, code, freq), file=outfile)

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

if __name__ == "__main__":
    # control output with a argparser as follows:
    # python convert_to_pinyin.py --chinese_code <input_file>
    # --chinese_code: print chinese code
    # --name <name>: the name of the output file
    # --input_tables <input1>...<inputN>: the input tables
    # --pinyin_phrase: print pinyin phrase
    # --exclude_pinyin_phrase: exclude pinyin phrase
    # <input_file>: the input file

    parser = argparse.ArgumentParser()
    parser.add_argument("--chinese_code", help="print chinese code", action="store_true")
    parser.add_argument("--name", help="the name of the current table", required = True)
    parser.add_argument("--input_tables", nargs='+', help="the input tables", default=None)
    parser.add_argument("--pinyin_phrase", help="print pinyin phrase", action="store_true")
    parser.add_argument("--exclude_pinyin_phrase", help="exclude pinyin phrase", action="store_true")
    parser.add_argument("input_file", nargs="?", help="the input file", default=None)
    args = parser.parse_args()

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
            for word in pinyin_phrases:
                if word in word_codes:
                    del word_codes[word]
        words_freq = get_frequency_from_file(PINYIN_SIMP_EXT1_DICT)
        print_word_codes(word_codes, words_freq)
    elif args.pinyin_phrase:
        pinyin_phrases = get_pinyin_phrases()
        words_freq = get_frequency_from_file(PINYIN_SIMP_EXT1_DICT)
        print_word_codes(pinyin_phrases, words_freq)
