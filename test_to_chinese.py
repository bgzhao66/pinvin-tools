# -*- coding: utf-8 -*-

import unittest
import convert_to_chinese as ct
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TestConvertToChinese(unittest.TestCase):
    def setUp(self):
        logging.info("test setUp.")
        self.db = ct.DB("txt/dict.db")
        self.searcher = ct.DAGViterbiSearcher(self.db)

    def tearDown(self):
        self.db.close()
        logging.info("test tearDown.")

    def test_split_pinyin(self):
        testcases = [
            ("uoo zay jiam, Lucy!", ["uoo", "zay", "jiam", "，",  "Lucy", "！"]),
            ("uoo zay jiam, Lucy! xieh xieh!", ["uoo", "zay", "jiam", "，", "Lucy", "！" ,"xieh", "xieh", "！"]),
        ]

        for pinyin_str, expected_result in testcases:
            with self.subTest(pinyin_str=pinyin_str):
                result = ct.split_pinyin_and_punct(pinyin_str)
                self.assertEqual(result, expected_result)

    def test_search(self):
        testcases = [
            ("nyi hau", "你好"),
            ("uoo aynyi", "我愛你"),
            ("zay jiam", "再見"),
            ("xieh xieh, Lucy!", "謝謝，Lucy！"),
            ("uoo heen hau", "我很好"),
            ("I piamgucherng vuamrem shan", "一片孤城萬仞山"),
            ("hauhauhauhauhauhaukam", "好好好好好好看"),
            ("nyihau John Smith", "你好John Smith"),
        ]

        for pinyin_str, expected_result in testcases:
            with self.subTest(pinyin_str=pinyin_str):
                pinyins = ct.split_pinyin_and_punct(pinyin_str)
                result = self.searcher.search(pinyins)
                self.assertEqual(ct.format_result(result), expected_result)

if __name__ == '__main__':
    unittest.main()
