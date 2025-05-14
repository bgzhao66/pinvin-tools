from collections import defaultdict
import math
import unicodedata
import argparse
import re
import logging
import sqlite3
import sys


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
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        self.init_db()
        logging.debug("Database initialized.")

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dict (
                pinyin TEXT NOT NULL,
                word TEXT NOT NULL,
                freq INTEGER DEFAULT 0,
                PRIMARY KEY (pinyin, word)
            )
        """)
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_pinyin ON dict(pinyin)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_word ON dict(word)")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        self.conn.commit()

    def update_meta(self, total_freq):
        self.cursor.execute("""
            INSERT OR REPLACE INTO meta (key, value) VALUES
                ('total_freq', ?)
        """, ([total_freq]))
        self.conn.commit()

    # 读取词典文本文件並寫入Db，格式：<pinyin>\t<word>\t<freq>
    def import_data(self, path):
        entries = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                py, word, freq = line.strip().split('\t')
                freq = int(freq)
                entries.append((py.lower(), word, freq))

        BATCH_SIZE = 1000
        for i in range(0, len(entries), BATCH_SIZE):
            batch = entries[i:i + BATCH_SIZE]
            placeholders = ','.join(['?'] * len(batch[0]))
            sql = f"INSERT OR REPLACE INTO dict (pinyin, word, freq) VALUES ({placeholders})"
            self.cursor.executemany(sql, batch)
        self.conn.commit()

        self.cursor.execute("SELECT SUM(freq + 1) FROM dict")
        total_freq = self.cursor.fetchone()[0]
        self.update_meta(total_freq)
        logging.debug(f"Imported {len(entries)} entries into the database.")

    def get_total_freq(self):
       self.cursor.execute("SELECT value FROM meta WHERE key = 'total_freq'")
       total_freq = self.cursor.fetchone()[0]
       return total_freq

    # check cache self.pinyin_to_words at first, if not found, then query from sqlDB
    # and cache it
    def get_word_freq(self, pinyin):
        if pinyin in self.pinyin_to_words:
            return self.pinyin_to_words[pinyin]
        else:
            self.cursor.execute("SELECT word, freq FROM dict WHERE pinyin = ?", (pinyin,))
            results = self.cursor.fetchall()
            if results:
                for word, freq in results:
                    self.pinyin_to_words[pinyin].append((word, freq))
                return self.pinyin_to_words[pinyin]
            else:
                return []

    # prefetch (word, freq) from sqlDB for a given list of pinyins in batch mode, and cache them
    def prefetch_word_freq(self, pinyin_list):
        BATCH_SIZE = 1000
        for i in range(0, len(pinyin_list), BATCH_SIZE):
            batch = pinyin_list[i:i + BATCH_SIZE]
            placeholders = ','.join(['?'] * len(batch))
            sql = f"SELECT pinyin, word, freq FROM dict WHERE pinyin IN ({placeholders})"
            self.cursor.execute(sql, batch)
            results = self.cursor.fetchall()
            for py, word, freq in results:
                self.pinyin_to_words[py.lower()].append((word, freq))
        logging.debug(f"Prefetched {len(pinyin_list)} pinyin entries from the database.")

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()
        logging.debug("Database connection closed.")

class DAGViterbiSearcher:
    def __init__(self, db):
        self.db = db
        self.total_freq = self.db.get_total_freq()

    # 创建 DAG
    def create_dag(self, pinyin_list):
        N = len(pinyin_list)
        dag = defaultdict(list)
        for i in range(N):
            for j in range(i + 1, N + 1):
                seg = ''.join(p.lower() for p in pinyin_list[i:j])
                word_freqs = self.db.get_word_freq(seg)
                if word_freqs:
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
                word_freqs = self.db.get_word_freq(seg)
                if word_freqs:
                    prob = max(math.log((freq + 1) / self.total_freq) for word, freq in word_freqs)
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
            word_freqs = self.db.get_word_freq(word_pinyin_seg)
            if word_freqs:
                best_word = max(word_freqs, key=lambda x: x[1])[0]
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
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict', default='txt/dict.db', help='词典文件路径')
    parser.add_argument('--import_data', default=None, help='需要導入的數據文件')
    parser.add_argument('--input', default=None, help='输入拼音文件路径')
    args = parser.parse_args()

    db = DB(args.dict)

    if args.import_data:
        db.import_data(args.import_data)
        print("Ok, Data imported!")
        sys.exit(0)

    if not args.input:
        parser.print_help()
        sys.stderr.write("Error: --input is required\n")
        sys.exit(-1)

    dvsearcher = DAGViterbiSearcher(db)

    with open(args.input, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            pinyin_list = split_pinyin_and_punct(line)
            # 预取词频数据
            db.prefetch_word_freq(pinyin_list)
            result = dvsearcher.search(pinyin_list)
            print(format_result(result))

    db.close()
