# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-26 16:24:35 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-26 16:24:35 
"""
import pickle
import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import sklearn_crfsuite
import random
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics



global label2idx, idx2label, risk2idx, idx2risk, tfidf_model, svc_model, lr_model, fault_model, risk_model, entity_model
label2idx = {
    'Bias': 0,
    'Drift': 1,
    'Performance degradation': 2,
    'Freezing': 3,
    'Calibration error': 4,
    'Lock in place': 5,
    'Float': 6,
    'Hard over': 7,
    'Loss of Effectiveness': 8,
    '失误操作': 9,
    '电池故障': 10,
    '信号干扰': 11,
    '避障失效': 12,
    '返航故障': 13,
    '其他': 14
}
idx2label = [
    'Bias',
    'Drift',
    'Performance degradation',
    'Freezing',
    'Calibration error',
    'Lock in place',
    'Float',
    'Hard over',
    'Loss of Effectiveness',
    '失误操作',
    '电池故障',
    '信号干扰',
    '避障失效',
    '返航故障',
    '其他'
]


risk2idx = {
    '1类': 0,
    '1R类': 1,
    '2类': 2,
    '3类': 3,
    '4类': 4
}

idx2risk = [
    '1类',
    '1R类',
    '2类',
    '3类',
    '4类'
]

with open('static/data/posts_data.pkl','rb') as f:
    posts_data = pickle.load(f)

with open('static/data/bio_data.pkl','rb') as f:
    bio_data = pickle.load(f)

all_texts = [' '.join(jieba.cut(text)) for text in posts_data['posts']]
tfidf_model = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.9)
tfidf_model.fit(all_texts)

train_vec = tfidf_model.transform(all_texts)
train_fault = posts_data['fault']
train_risk = posts_data['risk']

fault_model = LogisticRegression(C=2)
fault_model.fit(train_vec,train_fault)

risk_model = LogisticRegression(C=2)
risk_model.fit(train_vec,train_risk)


def get_test_vec(texts):
    texts = [' '.join(jieba.cut(text)) for text in texts]
    test_vec = tfidf_model.transform(texts)
    return test_vec


def predict_fault(test_vecs):
    pred_indexs = fault_model.predict(test_vecs)
    pred_labels = [idx2label[int(idx)] for idx in pred_indexs]
    return pred_labels

def predict_fault_proba(test_vecs):
    pred_probas = fault_model.predict_proba(test_vecs)
    return pred_probas

def predict_risk(test_vecs):
    pred_indexs = risk_model.predict(test_vecs)
    pred_labels = [idx2risk[int(idx)] for idx in pred_indexs]
    return pred_labels    

def predict_risk_proba(test_vecs):
    pred_probas = risk_model.predict_proba(test_vecs)
    return pred_probas    

def word2features(sent, i):
    word = sent[i][0]
    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
    }
    if i > 0:
        word1 = sent[i-1][0]
        features.update({
            '-1:word':word1,
            '-1:word.lower()': word1.lower(),
            '-1:word.isupper()': word1.isupper(),
        })
    elif i > 1:
        word2 = sent[i-2][0]
        features.update({
            '-2:word':word2,
            '-2:word.lower()': word2.lower(),
            '-2:word.isupper()': word2.isupper(),
        })
    elif i > 2:
        word3 = sent[i-3][0]
        features.update({
            '-3:word':word3,
            '-3:word.lower()': word3.lower(),
            '-3:word.isupper()': word3.isupper(),
        })               
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        features.update({
            '+1:word':word1,
            '+1:word.lower()': word1.lower(),
            '+1:word.isupper()': word1.isupper()

        })
    elif i<len(sent)-2:
        word2 = sent[i+2][0]
        features.update({
            '+2:word':word2,
            '+2:word.lower()': word2.lower(),
            '+2:word.isupper()': word2.isupper()
        })
    elif i<len(sent)-3:
        word3 = sent[i+3][0]
        features.update({
            '+3:word':word3,
            '+3:word.lower()': word3.lower(),
            '+3:word.isupper()': word3.isupper()
        })
    else:
        features['EOS'] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, label in sent]

def sent2tokens(sent):
    return [token for token, label in sent]


def get_sents(bio_data):
    sents = []
    for item in bio_data:
        sent = [(s,label) for s,label in zip(list(item[0]),item[1].split(' '))]
        sents.append(sent)
    return sents


def biotags_to_spans(bio_list):
    span_start = 0
    span_end = 0
    active_conll_tag = None
    spans = set()
    for index,string_tag in enumerate(bio_list):
        bio_tag = string_tag[0]
        conll_tag = string_tag[2:]
        if bio_tag == "O":
            if active_conll_tag is not None:
                if conll_tag == active_conll_tag:
                    spans.add((active_conll_tag,span_start,span_end+1))
                else:
                    spans.add((active_conll_tag,span_start,span_end))
                active_conll_tag = None
                continue
        elif bio_tag == 'B':
            if active_conll_tag is not None:
                spans.add((active_conll_tag,span_start,span_end))
            active_conll_tag = conll_tag
            span_start = index
            span_end = index
        elif bio_tag == 'I' and conll_tag == active_conll_tag:
            span_end += 1
        else:
            if active_conll_tag is not None:
                spans.add((active_conll_tag,span_start,span_end))
            active_conll_tag = conll_tag
            span_start = index
            span_end = index
    if active_conll_tag is not None:
        spans.add((active_conll_tag,span_start,span_end))
    return list(spans)





def get_predict_entity_list(texts):
    sents = []
    for text in texts:
        sent = [(s,0) for s in list(text)]
        sents.append(sent)
    test_features = [sent2features(s) for s in sents]
    bio_lists = entity_model.predict(test_features)
    entity_list = []
    
    for i,bio_list in enumerate(bio_lists):
        text = texts[i]
        spans = biotags_to_spans(bio_list)
        entity_dict = {0:[],1:[],2:[],3:[],4:[]}
        for span in spans:
            label = int(span[0])
            start = span[1]
            end = span[2]
            entity_dict[label].append(text[start:end+1])
        entity_dict_tmp = {}
        for key,value in entity_dict.items():
            entity_string = ','.join(list(set(value)))
            entity_dict_tmp[key] = entity_string
        entity_list.append(entity_dict_tmp)
    return entity_list


with open('static/data/bio_data.pkl','rb') as f:
    bio_data = pickle.load(f)
#print(bio_data[0])
sents_tmp = get_sents(bio_data)
random.shuffle(sents_tmp)
sents = sents_tmp+sents_tmp+sents_tmp+sents_tmp+sents_tmp

print(sents[0])
tr_size = int(0.99*len(sents))
train_sents = sents[:tr_size]
test_sents = sents[tr_size:]
X_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]

X_test = [sent2features(s) for s in test_sents]
y_test = [sent2labels(s) for s in test_sents]
entity_model = sklearn_crfsuite.CRF(
        algorithm='lbfgs',
        c1=0.1,
        c2=0.1,
        max_iterations=200,
        all_possible_transitions=True,
        verbose=10
)
entity_model.fit(X_train, y_train)







if __name__ == '__main__':
    content = '上周射桨炸的悟2还没有修好，今天又出现这个事情。侧面撞信号塔，断了一点桨叶。然后还可以飞，半路上掉楼顶。撞了后面的塔，然后落在那个屋顶上屋顶的救援过程，全程航拍。'
    entity_list = get_predict_entity_list([content])[0]
    test_vecs = get_test_vec([content])
    fault_probas = predict_fault_proba(test_vecs)
    risk_probas = predict_risk_proba(test_vecs)
    fault = predict_fault(test_vecs)
    risk = predict_risk(test_vecs)
    print(entity_list,fault_probas,risk_probas,fault,risk)
