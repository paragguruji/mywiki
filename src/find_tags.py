# -*- coding: utf-8 -*-
"""
Created on Sun Dec 18 15:14:58 2016

@author: Parag
"""

from mywiki.src.dataset import DATA_DIR, TRAININGSET_FILE
import codecs
import os
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import bigrams, trigrams
import operator

WNLemmatizer = WordNetLemmatizer()

MONGO = MongoClient(serverSelectionTimeoutMS=10)

DB = MONGO.mywiki

infp = codecs.open(os.path.join(DATA_DIR, TRAININGSET_FILE),
                   "r", encoding='utf-8')


def clean(b):
    b = b.replace('a href=', ' ').replace('</a>', ' ').replace('"', ' ')\
        .replace('<', ' ').replace('>', ' ').replace('  ', ' ').strip()
    b = b if b.isupper() else b.lower()
    return WNLemmatizer.lemmatize(b)


def parseMarkup(token):
    text_token = token
    if '<a href=' in token:
        soup = bs(token, 'lxml')
        aes = soup.findAll('a')
        for a in aes:
            text_token = text_token.replace(a.__repr__(), a.getText())
    return text_token


def clean_sentence(text):
    ret = []
    for w in text.split(' '):
        ret.append(clean(parseMarkup(w)))
    return ' '.join(ret)


def mongofyKey(key):
    if key.startswith("$"):
        key = "<DOLLAR>"+key[1:]
    return key.replace(".", "<DOT>")


def wash_doc(doc):
    for t in doc['tags'].keys():
        if len(t) > 50:
            doc['tags'].pop(t)
            continue
        t_cleaned = clean(parseMarkup(t))
        bag = doc['tags'].pop(t)
        doc['tags'][t_cleaned] = [clean_sentence(s) for s in bag if s]
    return doc


def isValidTag(tag):
    if tag.startswith("born:") or ":" in tag:
        return False
    return True


def get_tags(doc):
    if not doc:
        return {"title": "NOT FOUND", "tags": []}
    text = clean_sentence(doc["text"])
    unis = text.split(' ')
    bis = bigrams(unis)
    tris = trigrams(unis)
    tagRank = {}
    for term in unis + [" ".join([b[0], b[1]])
                        for b in bis] + \
                       [" ".join([t[0], t[1], t[2]])
                        for t in tris]:
        res = DB.bagfortag.find({"bag": term}, {"_id": 0, "bag": 0})
        res = [r for r in res]
        tags = [r['tag'] for r in res]
        len_tags = len(tags)
        tags = [t for t in tags if isValidTag(t)]
        for tag in tags:
            if tag not in tagRank:
                tagRank[tag] = 0
            tagRank[tag] = tagRank[tag] + 1.0/len_tags
    return {"title": doc["title"], "tags": tagRank}


def get_article(title):
    return DB.articles.find_one({"title": title}, {"_id": 0})


def rankTags(doc):
    tags = doc['tags']
    sorted_tags = sorted(tags.items(), key=operator.itemgetter(1))
    start = -1 * len(sorted_tags)/100
    return {"title": doc["title"], "tags": sorted_tags[start:]}


def work(title):
    return rankTags(get_tags(get_article(title)))
