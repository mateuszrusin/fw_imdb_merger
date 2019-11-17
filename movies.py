#!/usr/bin/env python
# coding: utf-8

from fwimdbmerge import Merger

merger = Merger('https://raw.githubusercontent.com/mateuszrusin/ml-filmweb-score/master/oceny.csv')
df = merger.process()
df.to_csv(r'fw_imdb_merged.csv')

print(df)


