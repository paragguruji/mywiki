# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 15:20:01 2016

@author: Parag
"""

from mywiki.src.dataset import DATA_DIR, TRAININGSET_FILE
import codecs
import os
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from nltk.stem.wordnet import WordNetLemmatizer

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
        doc['tags'][t_cleaned] = [mongofyKey(clean_sentence(s))
                                  for s in bag if s]
    return doc


def tag_bag():
    for line in infp:
        doc = wash_doc(json.loads(line))
        for t in doc['tags']:
            DB.bagfortag.update({'tag': t},
                                {'$addToSet':
                                    {'bag': {'$each': doc['tags'][t]}}},
                                upsert=True)


def tag_bag_val_new(docs=infp, coll=DB.tagfrequency):
    DB.counter.insert({"coll": 'tagfrequency', "count": 0})
    for line in docs:
        DB.counter.update({'coll': 'tagfrequency'}, {"$inc": {'count': 1}})
        doc = wash_doc(json.loads(line))
        for tag in doc['tags']:
            try:
                if not doc['tags'][tag]:
                    continue
                try:
                    res = coll.find_one({"tag": tag},
                                        dict([('bag.' + v, 1)
                                              for v in doc['tags'][tag]]))
                except:
                    print "exception in find_one for tag:", tag,\
                                "in doc of:", doc['title']
                if not res:
                    try:
                        coll.insert({"tag": tag,
                                     "bag": [{v: 1}
                                             for v in doc['tags'][tag]]})
                    except:
                        print "exception in insert first record for tag:",\
                            tag, "in doc of:", doc['title']
                    continue
                bag = {}
                if 'bag' in res and res['bag']:
                    bag = dict([(bg.keys()[0], bg.values()[0])
                                for bg in res['bag'] if bg])
                newbies = [v for v in doc['tags'][tag] if v not in bag.keys()]
                oldies = [v for v in doc['tags'][tag]
                          if v and v not in newbies]
                if newbies:
                    try:
                        coll.update({"tag": tag},
                                    {"$push":
                                        {"bag": {"$each": [{v: 1} for v
                                                           in newbies]}}})
                    except:
                        print "exception in $push newbies for tag:", tag,\
                                "in doc of:", doc['title']
                if oldies:
                    for val in oldies:
                        try:
                            coll.update({"tag": tag,
                                         "bag": {"$elemMatch":
                                                 {val: {"$exists": True}}}},
                                        {"$inc": {"bag.$." + val: 1}})
                        except:
                            print "exception in $inc oldie", val, "for tag:",\
                                tag, "in doc of:", doc['title']
            except:
                print "unknown exception for tag:", tag, "in doc of:",\
                    doc['title']


# def tag_bag_val_count():
#    for line in infp:
#        doc = wash_doc(json.loads(line))
#        for t in doc['tags']:
#            for val in doc['tags'][t]:
#                if not DB.bagfortag.find_one(
#                    {"tag": t,
#                     "bag.val": val}):
#                    DB.bagfortag.update({"tag": t},
#                                        {"$push":
#                                            {"bag": {{'val': val,
#                                                      'freq': 1}}}})
#                else:
#                    DB.update({"tag": t, "bag.val": val},
#                              {"$inc": {"bag.freq": 1}})


# def tag_bag_val_old(docs=infp, coll=DB.tagfrequency):
#    for line in docs:
#        doc = wash_doc(json.loads(line))
#        for tag in doc['tags']:
#            res = coll.find_one({"tag": tag},
#                                dict([('bag.' + v, 1)
#                                      for v in doc['tags'][tag]]))
#            if not res:
#                coll.insert({"tag": tag,
#                             "bag": [{v: 1} for v in doc['tags'][tag]]})
#                continue
#            for val in doc['tags'][tag]:
#                if not coll.find_one({"tag": tag,
#                                      "bag":
#                                          {"$elemMatch":
#                                              {val:
#                                                  {"$exists": True}}}}):
#                    coll.update({"tag": tag},
#                                {"$push":
#                                    {"bag": {val: 1}}})
#                else:
#                    coll.update({"tag": tag,
#                                 "bag": {"$elemMatch": {val:
#                                                        {"$exists": True}}}},
#                                {"$inc": {"bag.$." + val: 1}})

d1 = {}
d1['tag'] = 'tag1'
b1 = [{'v0': 6}, {'v1': 1}, {'v2': 2}]
d1['bag'] = b1
d2 = {}
d2['tag'] = 'tag2'
b2 = [{'u0': 3}, {'u1': 4}, {'v2': 5}]
d2['bag'] = b2


def test():
    DB.tagfrequency.insert([d1, d2])

v1 = {}
v1['title'] = 'title1'
v1['tags'] = {'tag1': ['v0', 'v1', 'u1'],
              'tag2': ['u2', 'v3', 'v4', 'v5', 'u0', 'v1'],
              'tag3': ['u1', 'v1', 'v6', 'v6', 'u4', 'u5', 'u6']}

v2 = {}
v2['title'] = 'title1'
v2['tags'] = {'tag4': ['v0', 'u1', 'u1'],
              'tag5': ['v2', 'v3', 'v4', 'v5', 'u0', 'v1'],
              'tag2': ['v1', 'v1', 'v6', 'u6', 'v4', 'u5']}

docs = [json.dumps(v1), json.dumps(v2)]

#tgs = DB['infoboxes'].distinct("tags")

#tags = [t for t in tgs]

#
#pipeline = [{'$group': {'_id': "$tags"}}];
#
#R = DB.command( 
#    {
#    "aggregate": "infoboxTemp" , 
#    "pipeline": pipeline,
#    "allowDiskUse": True
#    }
#);


#for i in range(1, 500):
#    r = DB.infoboxes.find_one({'id': i})
#    if r:
#        DB.infoboxTemp.insert_one(r)


