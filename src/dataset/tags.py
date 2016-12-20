# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 19:23:46 2016

@author: Parag
"""

import os
import codecs
import json
from bs4 import BeautifulSoup as bsljsdnvlslvnlsnvl
from mywiki.src.dataset import DATA_DIR, INFOBOX_BEGIN_TAG, INFOBOX_END_TAG,\
    INFOBOX_FILE, TRAININGSET_FILE, INFOBOX_JSON_FILE, TAG_LIST_FILE

from pymongo import MongoClient
MONGO = MongoClient(serverSelectionTimeoutMS=10)

DB = MONGO.mywiki
tags = []

fr = codecs.open(os.path.join(DATA_DIR, TRAININGSET_FILE),
                 "r", encoding='utf-8')
fw = codecs.open(os.path.join(DATA_DIR, TAG_LIST_FILE),
                 "w", encoding='utf-8')

for line in fr:
    ib = json.loads(line)
    for tag in ib['tags']:
        if tag not in tags:
            DB.tags.insert_one({"tag": tag})
            tags.append(tag)
            fw.write(tag + os.linesep)
