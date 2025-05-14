from collections import defaultdict
import math
import unicodedata
import argparse

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

# 构造 DAG
def create_dag(pinyin_list, pinyin_to_words):
    N = len(pinyin_list)
    dag = defaultdict(list)
    for i in range(N):
        for j in range(i + 1, N + 1):
            seg = ''.join(p.lower() for p in pinyin_list[i:j])
            if seg in pinyin_to_words:
                dag[i].append(j)
        if not dag[i]:
            dag[i].append(i + 1)  # 无匹配时，按单个拼音前进
    return dag

# Viterbi 计算最优路径
def calc_route(pinyin_list, dag, pinyin_to_words):
    N = len(pinyin_list)
    route = {N: (0, 0)}
    for i in range(N - 1, -1, -1):
        candidates = []
        for j in dag[i]:
            seg = ''.join(p.lower() for p in pinyin_list[i:j])
            if seg in pinyin_to_words:
                prob = max(math.log(freq + 1) for word, freq in pinyin_to_words[seg])
            else:
                prob = -10.0 * (j - i)  # 惩罚未知拼音组合
            candidates.append((prob + route[j][0], j))
        route[i] = max(candidates)
    return route

# 回溯路径并生成汉字或原始拼音输出
def decode_pinyin_path(pinyin_list, route, pinyin_to_words):
    N = len(pinyin_list)
    result = []
    idx = 0
    after_matched = True
    while idx < N:
        # 如果当前是标点符号，直接保留
        if not pinyin_list[idx][0].isalpha():
            result.append(pinyin_list[idx])
            idx += 1
            continue
        next_idx = route[idx][1]
        word_pinyin_seg = ''.join(p.lower() for p in pinyin_list[idx:next_idx])
        if word_pinyin_seg in pinyin_to_words:
            best_word = max(pinyin_to_words[word_pinyin_seg], key=lambda x: x[1])[0]
            result.append(best_word)
            after_matched = True
        else:
            result.append('' if after_matched else ' ')
            result.append(' '.join(pinyin_list[idx:next_idx]))  # 保留原始大小写
            after_matched = False
        idx = next_idx
    return result

# 主流程
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict', default='txt/dict.txt', help='词典文件路径')
    parser.add_argument('--input', required=True, help='输入拼音文件路径')
    args = parser.parse_args()

    pinyin_to_words, word_freq = load_dict(args.dict)

    with open(args.input, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            pinyin_list = split_pinyin_and_punct(line)
            dag = create_dag(pinyin_list, pinyin_to_words)
            route = calc_route(pinyin_list, dag, pinyin_to_words)
            result = decode_pinyin_path(pinyin_list, route, pinyin_to_words)
            print(''.join(result))

