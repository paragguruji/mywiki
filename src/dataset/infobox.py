# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 19:04:39 2016

@author: Parag
"""

import os
import codecs
import json
from bs4 import BeautifulSoup as bs
from mywiki.src.dataset import DATA_DIR, INFOBOX_BEGIN_TAG, INFOBOX_END_TAG,\
    INFOBOX_FILE, TRAININGSET_FILE, INFOBOX_JSON_FILE


def extractInfoboxes(after=0,
                     limit=1,
                     output_file=INFOBOX_JSON_FILE,
                     purge=False,
                     dump=True,
                     ret=True):
    """Extracts and returns data for 'limit' number of infoboxes starting after
        the infobox with id number 'after' by reading the INFOBOX_FILE file
        line by line

        :Returns: a list of dicts with one infobox per entry (if ret=True)
        :Writes: (append mode) a text file with each line being a json string
            representing one infobox (if dump=True)

        :arg after: (int) (Optional) ID of infobox after which parsing
            starts (default: 0)
        :arg limit: (int) (Optional) Number of infoboxes to parse (default: 1)
        :arg output_file: (string) (Optional) Name of output file within
            data directory (default: INFOBOX_JSON_FILE)
        :arg purge: (bool) (Optional) Flag - When True, output file (if
            exists) is overwritten, appended otherwise (default: False)
        :arg dump: (bool) (Optional) Flag - When True, file output enabled
            (default: True)
        :arg ret: (bool) (Optional) Flag - When True, returns output list,
            returns None otherwise (default: True)
    """
    infoboxes = []
    start = False
    done_cnt = 0
    infp = codecs.open(os.path.join(DATA_DIR, INFOBOX_FILE),
                       "r", encoding='utf-8')
    outfp = codecs.open(os.path.join(DATA_DIR, output_file),
                        "w" if purge else "a", encoding='utf-8')
    for line in infp:
        if not start:
            if line.startswith(INFOBOX_BEGIN_TAG + '\t' + str(after + 1)):
                start = True
            else:
                continue
        if line.startswith(INFOBOX_BEGIN_TAG):
            headers = line.split('\t')
            cur_infobox = {'id': int(headers[1]),
                           'title': headers[2].strip(),
                           'lines': []}
            continue
        if line.startswith(INFOBOX_END_TAG):
            done_cnt += 1
            outfp.write(json.dumps(cur_infobox))
            outfp.write(os.linesep)
            infoboxes.append(cur_infobox)
            if done_cnt == limit:
                break
        cur_infobox['lines'].append(line)
    return infoboxes


def extractALLInfoboxes():
    """Caller function for bulk extraction of all infoboxes
    """
    extractInfoboxes(limit=-1, purge=True, ret=False)


def parseMarkup(token):
    title_token = text_token = token
    if '<a href=' in token:
        soup = bs(token, 'lxml')
        aes = soup.findAll('a')
        for a in aes:
            title_token = title_token.replace(a.__repr__(), a.get('href'))
            text_token = text_token.replace(a.__repr__(), a.getText())
    return [title_token.replace('_', ' '), text_token]


def parseInfobox(infobox):
    """Parse infobox to generate training data
    """
    infobox['tags'] = {}
    for line in infobox['lines']:
        tokens = line.split('\t')
        if len(tokens) == 2:
            temp = []
            for token in parseMarkup(tokens[1]):
                for t in token.split(','):
                    t = t.strip()
                    if t not in temp:
                        temp.append(t)
            infobox['tags'][parseMarkup(tokens[0])[0]] = temp
    infobox.pop('lines')
    return infobox


def parseAllInfoboxes(output_file=TRAININGSET_FILE,
                      purge=True,
                      dump=True,
                      ret=True):
    """Parses and returns training data for all infoboxes  by reading the
        INFOBOX_JSON file line by line

        :Returns: a list of dicts with one infobox per entry (if ret=True)
        :Writes: a text file with each line being a json string
            representing one infobox (subject to dump & purge flags)

        :arg output_file: (string) (Optional) Name of output file within
            data directory (default: TRAININGSET_FILE)
        :arg purge: (bool) (Optional) Flag - When True, output file (if
            exists) is overwritten, appended otherwise (default: False)
        :arg dump: (bool) (Optional) Flag - When True, file output enabled
            (default: True)
        :arg ret: (bool) (Optional) Flag - When True, returns output list,
            returns None otherwise (default: True)
    """
    infoboxes = []
    infp = codecs.open(os.path.join(DATA_DIR, INFOBOX_JSON_FILE),
                       "r", encoding='utf-8')
    outfp = codecs.open(os.path.join(DATA_DIR, output_file),
                        "w" if purge else "a", encoding='utf-8')
    for line in infp:
        infobox = parseInfobox(json.loads(line))
        if ret:
            infoboxes.append(infobox)
            if not len(infoboxes) % 100000:
                print str(len(infoboxes) / 100000), 'infoboxes processed.'
        if dump:
            outfp.write(json.dumps(infobox) + os.linesep)
    return infoboxes if ret else None
