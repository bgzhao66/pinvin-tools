from collections import defaultdict
import math
import unicodedata
import argparse
import re
import logging

# 英文标点转中文标点
PUNCTUATION_MAP = {
    ',': '，',
    '.': '。',
    '?': '？',
    '!': '！',
    ':': '：',
    ';': '；',
    '"': '“',
    "'": '‘',
    '(': '（',
    ')': '）',
    '[': '【',
    ']': '】',
    '{': '｛',
    '}': '｝',
    '<': '《',
    '>': '》'
}

INITIAL_TEXT = """
b (玻)	d (得)	g (哥)	j (基)	zh (知)	z (资)	s (思)
p (坡)	t (特)	k (科)	q (欺)	ch (蚩)	c (雌)
m (摸)	n (讷)	h (喝)	x (希)	sh (诗)
f (佛)	l (勒)			r (日)
"""

FINALS_TEXT = """
a (啊)	a	ar	aa	ah
o (喔)	o	or	oo	oh
e (鹅)	e	er	ee	eh
ai (哀)	ai	air	ae	ay
ei (欸)	ei	eir	ea	ey
ao (熬)	ao	aor	au	aw
ou (欧)	ou	our	oa	ow
el (儿)	el	erl	eel	ehl
an (安)	an	arn	aan	am
en (恩)	en	ern	een	em
ang (昂)	ang	arng	aang	amg
eng (亨的韵母)	eng	erng	eeng	emg
ong (轰的韵母)	ong	orng	oong	omg
i (衣)	i	ir	yi	ih
in (因)	in	irn	yin	im
ing (英)	ing	irng	ying	img
ia (呀)	ia	ya	iaa	iah
ie (耶)	ie	ye	iee	ieh
iao (腰)	iao	yao	iau	iaw
iou (忧)	iou	you	ioa	iow
ian (烟)	ian	yan	iaan	iam
iang (央)	iang	yang	iaang	iamg
iong (雍)	iong	yong	ioong	iomg
u (乌)	u	ur	wu	uh
ua (蛙)	ua	wa	uaa	uah
uo (窝)	uo	wo	uoo	uoh
uai (歪)	uai	wai	uae	uay
uei (威)	uei	wei	uea	uey
uan (弯)	uan	wan	uaan	uam
uen (温)	uen	wen	ueen	uem
uang (汪)	uang	wang	uaang	uamg
ueng (翁)	ueng	weng	ueeng	uemg
eu (迂)	eu	eur	yu	ew
eue (约)	eue	yue	euee	eueh
euan (冤)	euan	yuan	euaan	euam
euen (晕)	euen	yuen	eueen	euem
"""

# 解析拼音表with REGEX
def get_syllable_table():
    initials = set(re.findall(r'[a-z]*', INITIAL_TEXT))
    finals = set(re.findall(r'[a-z]*', FINALS_TEXT))
    initials.add('')  # 添加空字符串作为初始音节
    finals.discard('')

    syllables = set()
    for initial in initials:
        for final in finals:
            syllable = re.sub(r'([jqx])eu', r'\1u', initial + final)  # 处理特殊拼音
            syllables.add(syllable)
    for final in finals:
        syllables.add("v" + final)  # 添加带v的拼音
    return syllables

# 读取拼音表
SYLLABLES = get_syllable_table()

# 尝试将拼音分割为音节, RMM 算法
def try_split_tosyllables(word, syllable_dict=SYLLABLES, max_len=7):
    syllables = []
    matched = False
    i = len(word)
    word = word.lower()

    while i > 0:
        for j in range(min(max_len, i), 0, -1):
            cand = word[i-j:i]
            if cand not in syllable_dict:
                matched = False
                continue
            syllables.append(cand)
            i -= j
            matched = True
            break
        if not matched:
            return [] # fail
    syllables.reverse()
    return syllables

# 分离标点和拼音
def split_pinyin_and_punct(text):
    tokens = []
    current_token = ''
    for char in text:
        if unicodedata.category(char).startswith('P') or char in PUNCTUATION_MAP:
            if current_token:
                tokens.extend(current_token.strip().split())
                current_token = ''
            tokens.append(PUNCTUATION_MAP.get(char, char))
        else:
            current_token += char
    if current_token:
        tokens.extend(current_token.strip().split())
    return tokens

class DB:
    def __init__(self, path):
        self.path = path
        self.pinyin_to_words = defaultdict(list)
        self.word_freq = {}
        self.total_freq = 0

    # 读取词典文件，格式：<pinyin>\t<word>\t<freq>
    def load_dict(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            for line in f:
                py, word, freq = line.strip().split('\t')
                freq = int(freq)
                self.pinyin_to_words[py.lower()].append((word, freq))
                self.word_freq[word] = freq
        self.total_freq = sum(freq + 1 for freq in self.word_freq.values())

# 读取词典文件，格式：<pinyin>\t<word>\t<freq>
def load_dict(path):
    pinyin_to_words = defaultdict(list)
    word_freq = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            py, word, freq = line.strip().split('\t')
            freq = int(freq)
            pinyin_to_words[py.lower()].append((word, freq))
            word_freq[word] = freq
    return pinyin_to_words, word_freq

class DAGViterbiSearcher:
    def __init__(self, pinyin_to_words, total_freq):
        self.pinyin_to_words = pinyin_to_words
        self.total_freq = total_freq

    # 创建 DAG
    def create_dag(self, pinyin_list):
        N = len(pinyin_list)
        dag = defaultdict(list)
        for i in range(N):
            for j in range(i + 1, N + 1):
                seg = ''.join(p.lower() for p in pinyin_list[i:j])
                if seg in self.pinyin_to_words:
                    dag[i].append(j)
            if not dag[i]:
                dag[i].append(i + 1)  # 无匹配时，按单个拼音前进
        return dag

    # Viterbi 计算最优路径
    def calc_route(self, pinyin_list, dag):
        N = len(pinyin_list)
        route = {N: (0, 0)}
        for i in range(N - 1, -1, -1):
            candidates = []
            for j in dag[i]:
                seg = ''.join(p.lower() for p in pinyin_list[i:j])
                if seg in self.pinyin_to_words:
                    prob = max(math.log((freq + 1) / self.total_freq) for word, freq in self.pinyin_to_words[seg])
                else:
                    prob = math.log(1 / self.total_freq) * (j - i) # 惩罚未知拼音组合
                candidates.append((prob + route[j][0], j))
            route[i] = max(candidates)
        return route

    # 回溯路径并生成汉字或原始拼音输出
    def decode_pinyin_path(self, pinyin_list, route,  within_deepsearch=False):
        N = len(pinyin_list)
        result = []
        idx = 0
        while idx < N:
            # 如果当前是标点符号，直接保留
            if not pinyin_list[idx][0].isalpha():
                result.append(pinyin_list[idx])
                idx += 1
                continue
            next_idx = route[idx][1]
            word_pinyin_seg = ''.join(p.lower() for p in pinyin_list[idx:next_idx])
            if word_pinyin_seg in self.pinyin_to_words:
                best_word = max(self.pinyin_to_words[word_pinyin_seg], key=lambda x: x[1])[0]
                result.append(best_word)
            else:
                if within_deepsearch:
                    return []  # 深度搜索失败
                unmatched_list = pinyin_list[idx:next_idx]
                sub_result = self.search_onceagain_with_segment(unmatched_list)
                result.extend(sub_result)
            idx = next_idx
        return result

    # 尝试分割未知拼音, 并且通过DAG—Viterbi算法检索最佳匹配, 如果成功返回结果, 否则返回原始拼音
    def search_onceagain_with_segment(self, unmatched_list):
        pinyin_list = []
        for token in unmatched_list:
            syllables = try_split_tosyllables(token)
            if not syllables:
                return unmatched_list # 无法分割
            pinyin_list.extend(syllables)

        result = self.search(pinyin_list, within_deepsearch=True)
        # 如果在深度搜索中没有找到匹配的词，返回原始拼音
        return result if result else unmatched_list

    # DAG Viterbi 搜索器
    def search(self, pinyin_list, within_deepsearch=False):
        dag = self.create_dag(pinyin_list)
        route = self.calc_route(pinyin_list, dag)
        result = self.decode_pinyin_path(pinyin_list, route, within_deepsearch)
        return result

def is_latin_alnum(char):
    return char.isascii() and char.isalnum()

# 格式化输出带空格的文本
def format_result(result):
    output = []
    for i, token in enumerate(result):
        if i > 0 and token and is_latin_alnum(result[i - 1][-1]) and is_latin_alnum(token[0]):
            output.append(' ')
        output.append(token)
    return ''.join(output)

# 主流程
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict', default='txt/dict.txt', help='词典文件路径')
    parser.add_argument('--input', required=True, help='输入拼音文件路径')
    args = parser.parse_args()

    # 读取词典
    db = DB(args.dict)
    db.load_dict()

    dvsearcher = DAGViterbiSearcher(db.pinyin_to_words, db.total_freq)

    with open(args.input, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            pinyin_list = split_pinyin_and_punct(line)
            result = dvsearcher.search(pinyin_list)
            print(format_result(result))

