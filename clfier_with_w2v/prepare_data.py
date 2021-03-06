#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 www.drcubic.com, Inc. All Rights Reserved
#
"""
File: prepare_data.py
Author: shileicao(shileicao@stu.xjtu.edu.cn)
Date: 17-2-4 下午8:51
"""
import json
import os
import random
import sys

import jieba
import w2v

from cnn_clfier import C_MAX_SENTENCE_LEN, C_MAX_WORD_LEN

SPLIT_RATE = 0.8

jieba.load_userdict(os.path.join('../data', 'words.txt'))


def tokenizer(sentence):
    return jieba.lcut(sentence, cut_all=False)


def stat_max_len(data):
    max_word_len = 0
    max_sentence_len = 0
    for key in data:
        for sentence in data[key]:
            temp_max_word_len = max(
                [len(word) for word in tokenizer(sentence)])
            temp_max_sentence_len = len(tokenizer(sentence))
            if max_word_len < temp_max_word_len:
                max_word_len = temp_max_word_len
            if max_sentence_len < temp_max_sentence_len:
                max_sentence_len = temp_max_sentence_len
    print 'max sentence len:%d, max word len:%d' % (max_sentence_len,
                                                    max_word_len)


def data_shuffle(x, y=None):
    indexes = range(len(x))
    random.shuffle(indexes)
    x_temp = [x[i] for i in indexes]
    if y:
        assert (len(x) == len(y))
        y_temp = [y[i] for i in indexes]
        return x_temp, y_temp
    else:
        return x_temp


def build_dataset(data):
    x_train_data = []
    x_test_data = []
    y_train_data = []
    y_test_data = []
    for key in data:
        y = str(int(key) - 1)
        one_label_data = data[key]
        one_label_data = data_shuffle(one_label_data)
        split_index = int(SPLIT_RATE * len(one_label_data))
        x_train_data.extend(one_label_data[:split_index])
        y_train_data.extend([y] * split_index)
        x_test_data.extend(one_label_data[split_index:])
        y_test_data.extend([y] * (len(one_label_data) - split_index))

    x_train_data, y_train_data = data_shuffle(x_train_data, y_train_data)
    x_test_data, y_test_data = data_shuffle(x_test_data, y_test_data)
    return zip(x_train_data, y_train_data), zip(x_test_data, y_test_data)


def process_line(x_text, word_vob, char_vob):
    words = tokenizer(x_text)
    nl = len(words)
    wordi = []
    chari = []
    if nl > MAX_SENTENCE_LEN2:
        nl = MAX_SENTENCE_LEN2
    for ti in range(nl):
        word = words[ti]
        word_idx = word_vob.GetWordIndex(word)
        wordi.append(str(word_idx))
        chars = list(word)
        nc = len(chars)
        if nc > MAX_WORD_LEN:
            lc = chars[nc - 1]
            chars[MAX_WORD_LEN - 1] = lc
            nc = MAX_WORD_LEN
        for i in range(nc):
            char_idx = char_vob.GetWordIndex(chars[i])
            chari.append(str(char_idx))
        for i in range(nc, MAX_WORD_LEN):
            chari.append("0")
    for i in range(nl, MAX_SENTENCE_LEN2):
        wordi.append("0")
        for ii in range(MAX_WORD_LEN):
            chari.append('0')
    return wordi, chari


def generate_net_input(data, out, word_vob, char_vob, output_type):
    #vob_size = word_vob.GetTotalWord()
    for x_text, y in data:
        wordi, chari = process_line(x_text, word_vob, char_vob)
        line = " ".join(wordi)
        line += " "
        line += " ".join(chari)
        line += " "
        input_line = line + y
        out.write("%s\n" % input_line)


def main(argc, argv):
    if argc < 6:
        print(
            "Usage:%s <data> <word_vob> <char_vob> <train_output> <test_output>"
            % (argv[0]))

    train_output = open(argv[4], "w")
    test_output = open(argv[5], "w")

    word_vob = w2v.Word2vecVocab()
    word_vob.Load(argv[2])
    char_vob = w2v.Word2vecVocab()
    char_vob.Load(argv[3])
    with open(argv[1], 'r') as f:
        data = json.load(f)
        stat_max_len(data)
        train_data, test_data = build_dataset(data)
        generate_net_input(train_data, train_output, word_vob, char_vob)
        generate_net_input(test_data, test_output, word_vob, char_vob)

    train_output.close()
    test_output.close()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
