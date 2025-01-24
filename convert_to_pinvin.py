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

CHINESE_CODE = "chinese_code.txt"
PINYIN_SIMP_DICT = "pinyin_simp.dict.txt"
PINYIN_SIMP_EXT1_DICT = "pinyin_simp_ext1.dict.txt"

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

kPostfixMampping = get_postfix_mapping()
kPrefixMapping = get_prefix_mapping()

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

def get_chinese_code(file):
    words = dict()
    # read the file line by line
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
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

# get chinese code by get_chinese_code
def get_chinese_pinvin_code():
    words = get_chinese_code(CHINESE_CODE)
    for word in words:
        # convert the pinyin to pinvin
        words[word] = [get_pinvin(pinyin) for pinyin in words[word]]
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

def get_code_of_words(words):
    chinese_code = get_chinese_pinvin_code()
    word_codes = dict()
    for word in words:
        word_codes[word] = []
        encodes = []

        on_error = False
        for char in word:
            if char not in chinese_code:
                print(char, "Not found", file=sys.stderr)
                on_error = True
                break
            encodes.append(chinese_code[char])
        if on_error:
            continue

        for product in get_descartes_products(encodes):
            product = prepend_v(product)
            word_code = ' '.join(product)
            word_codes[word].append(word_code)

            if begin_with_vowel(word_code):
                alt_word_code = 'v' + word_code
                word_codes[word].append(alt_word_code)  
    return word_codes

# get the frequency of words from a file
def get_freq_from_file(file):
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
def get_freq_of_word(word, freq_dict):
    if word not in freq_dict:
        return 1
    return sum(freq_dict[word].values())

# get the sorted keys of a dictionary
def get_sorted_keys(dict):
    keys = list(dict.keys())
    keys.sort()
    return keys

# print the word_codes which is a dictionary of key,list into a file with the format of word code frequency
def print_word_codes(word_codes, outfile=sys.stdout):
    word_freq = get_freq_from_file(PINYIN_SIMP_EXT1_DICT)

    codes = dict()
    for word in word_codes:
        for code in word_codes[word]:
            if code not in codes:
                codes[code] = []
            codes[code].append(word)
    
    for code in get_sorted_keys(codes):
        for word in codes[code]:
            freq = get_freq_of_word(word, word_freq)
            print("%s\t%s\t%i" % (word, code, freq), file=outfile)

# print the chinese code in the same way
def print_chinese_code(chinese_code, outfile=sys.stdout):
    word_freq = get_freq_from_file(PINYIN_SIMP_DICT)
    
    codes = dict()
    for word in chinese_code:
        for code in chinese_code[word]:
            if code not in codes:
                codes[code] = []
            codes[code].append(word)
            if begin_with_vowel(code):
                altcode = 'v' + code
                if altcode not in codes:
                    codes[altcode] = []
                codes[altcode].append(word)
    
    for code in get_sorted_keys(codes):
        for word in codes[code]:
            freq = get_freq_of_word(word, word_freq)
            print("%s\t%s\t%i" % (word, code, freq), file=outfile)

if __name__ == "__main__":
    # control output with a argparser as follows:
    # python convert_to_pinyin.py --chinese_code <input_file>
    # --chinese_code: print chinese code
    # <input_file>: the input file

    parser = argparse.ArgumentParser()
    parser.add_argument("--chinese_code", help="print chinese code", action="store_true")
    parser.add_argument("input_file", help="the input file")
    args = parser.parse_args()
    if args.chinese_code:
        chinese_code = get_chinese_pinvin_code()
        print_chinese_code(chinese_code)

    if args.input_file:
        words = get_words_from_file(args.input_file)
        word_codes = get_code_of_words(words)
        print_word_codes(word_codes)
