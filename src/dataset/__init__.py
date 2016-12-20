# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 19:04:15 2016

@author: Parag
"""

import os

DATA_DIR = os.path.abspath(os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            os.pardir,
                            os.pardir,
                            'data',
                            'wikipediaTC'))

LOG_DIR = os.path.abspath(os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            os.pardir,
                            os.pardir,
                            'logs'))

INFOBOX_FILE = 'infoboxes.txt'
ARTICLES_FILE = 'wikipedia_tagged.txt'
INFOBOX_JSON_FILE = 'infobox_jsonlines.txt'
TRAININGSET_FILE = 'infobox_knowledge.txt'  # Each line is a json dict
TAG_LIST_FILE = 'infobox_keys.txt'
TAGBAG_FILE = 'bags_of_tags.txt'
TAG_GROUPS_FILE = 'tag_groups.txt'
INFOBOX_BEGIN_TAG = '#start-infobox'
INFOBOX_END_TAG = '#end-infobox'
LOG_FOR_THREADS = 'threadlogs.txt'
