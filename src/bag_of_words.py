# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 21:41:55 2016

@author: Parag
"""

from pymongo import MongoClient
from threading import Thread
import codecs
from mywiki.src.dataset import LOG_DIR, LOG_FOR_THREADS
import os
import time

MONGO = MongoClient(serverSelectionTimeoutMS=10)
DB = MONGO.mywiki

fw = codecs.open(os.path.join(LOG_DIR, LOG_FOR_THREADS),
                 "a", encoding='utf-8')


def clean(b):
    return b.replace('<a href=', ' ').replace('</a>', ' ').replace('"', ' ')\
        .replace('<', ' ').replace('>', ' ').replace('  ', ' ').strip().lower()


def bag4tag(tag, db=DB):
    """for all docs having this tag, return corresponding list of words
    """
    bag = []
    docs = db.infoboxes.find({"tags." + tag: {'$exists': 1}})
    for doc in docs:
        bag.extend(doc['tags'][tag])
    return list(set([clean(b) for b in bag]))


def get_mc():
    try:
        mc = MongoClient()
        return mc
    except:
        return None


def worker(n, tags):
    mc = None
    while not mc:
        time.sleep(5)
        mc = get_mc()
    db = mc.mywiki
    many = []
    print "in worker for:", str(n)
    for tag in tags:
        many.append({'tag': tag, 'bag': bag4tag(tag, db=db)})
    db.tagbag.insert(many)
    mc.close()


def masterWorker():
    all_tags = [t['tag'] for t in DB.tags.find({})]
    l = str(len(all_tags)) + " tags found" + os.linesep + os.linesep
    fw.write(l)
    print "logging:", l
    batches = [all_tags[i:i + 3000] for i in range(0, len(all_tags), 3000)]
    for i in range(len(batches)):
        Thread(target=worker, args=(i, batches[i],)).start()
