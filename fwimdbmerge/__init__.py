#!/usr/bin/env python
# coding: utf-8

from .filmweb import Filmweb
from .imdb import Imdb


class Merger(object):
    def __init__(self, filepath):
        self.csv = filepath

    def process(self):
        fw = Filmweb(self.csv)
        df = fw.get_dataframe()
        imdb = Imdb()
        df = imdb.merge(df)
        return df
