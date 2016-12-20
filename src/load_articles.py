# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 23:22:12 2016

@author: Parag
"""

from mywiki.src.dataset import DATA_DIR, ARTICLES_FILE
import codecs
import os
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from nltk.stem.wordnet import WordNetLemmatizer

WNLemmatizer = WordNetLemmatizer()
MONGO = MongoClient(serverSelectionTimeoutMS=10)
DB = MONGO.mywiki


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


def wash_doc(doc):
    text = parseMarkup('\n'.join(doc))
    ret_text = ''
    for line in text.split('\n'):
        ret_text = ret_text + ' '.join([clean(w)
                                        for w in line.split(' ')]) + ' '
    return ret_text


def load_articles():
    in_infobox = False
    infobox_present = False
    in_para = False
    title = ''
    text = []
    infp = codecs.open(os.path.join(DATA_DIR, ARTICLES_FILE),
                       "r", encoding='utf-8')
    for line in infp:
        if not line.startswith('#'):
            continue
        if line.startswith("#e-doc") and title and text and infobox_present:
            DB.articles.insert_one({"title": title, "text": wash_doc(text)})
        if line.startswith("#s-doc"):
            title = line.split('\t')[2].strip()
            text = []
            infobox_present = False
        if line.startswith("#s-para"):
            in_para = True
        if line.startswith("#e-para"):
            in_para = False
        if line.startswith("#s-infobox"):
            in_infobox = True
            infobox_present = True
        if line.startswith("#e-infobox"):
            in_infobox = False
        if line.startswith("#s-sent") and in_para and not in_infobox:
            text.append(line.split('\t')[3].strip())


# s-doc	1	!!!	!!!.html	['Dance
# s-para	1
# s-sent	1	31	(pronounced as chk chk chk, to simulate mouth-clicking soun
