# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
import os

PATTERNS = ['NN IN NNP']
infilename = 'D://tagged Wikipedia/tagged/englishEtiquetado_0_10000'
outfilename = 'D://tagged Wikipedia/expt1/englishEtiquetado_0_10000'


def work(article):
    out = {}
    if article:
        POSLines = ['']
        tokenLines = ['']
        for l in article:
            if l.strip():
                POSlines[-1] += ' ' + l.split(' ')[-2]
                tokenLines[-1] += ' ' + l.split(' ')[0]
            else:
                POSlines[-1] = POSlines[-1].strip()
                tokenLines[-1] = tokenLines[-1].strip()
                POSlines.append('')
                tokenLines.append('')
            for 
    i = 0
    for i in range(len(article)-3):
        if ' NN ' in article[i] and\
                ' IN ' in article[i+1] and\
                ' NNP ' in article[i+2]:
            k = ' '.join([article[i].split(' ')[0],
                          article[i+1].split(' ')[0]])
            v = article[i+2].split(' ')[0].replace('_', ' ')
            if k not in out:
                out[k] = ''
            else:
                out[k] = out[k] + ', '
            out[k] = out[k] + v
            i += 2
        i += 1
    return out


def supplyArticles(infilename, outfilename, limit=-1):
    """Extracts articles by reading the given data file line by line
        Works on each article
        Dumps processed articles in output file in the same sequence
    """
    article = []
    cnt = 0
    with open(infilename, "r") as infp, open(outfilename, "a") as outfp:
        for line in infp:
            if line.strip() == '</doc>':
                outcome = work(article)
                data = json.dumps(outcome)
                outfp.write(data + os.linesep)
                outfp.write(line + os.linesep)
                cnt += 1
            elif line.strip().startswith('<doc id='):
                outfp.write(line + os.linesep)
                article = []
            else:
                article.append(line)
            if cnt == limit:
                break
