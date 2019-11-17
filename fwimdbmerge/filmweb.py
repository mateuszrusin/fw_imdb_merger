#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from fwapi.film import Film
from .utils import to_list


class Filmweb(object):
    def __init__(self, filepath):
        self.csv = filepath

    def get_dataframe(self):
        df = pd.read_csv(self.csv)
        df = df.drop(columns=['Komentarz'])
        df = df[df.Ocena != 'brak oceny']
        df['Ulubione'] = self.label_encode(df.Ulubione.fillna(''))
        df['Ocena'] = df.Ocena.astype(int)

        df = df.reset_index(drop=True)
        df = df.join(self.dummies(df['Gatunek']), how='outer')
        df = df.join(self.dummies(df['Kraj produkcji']), how='outer')
        df = df.join(self.get_scrapped(df), how='outer')

        df['topics_count'] = df.topics_count.fillna(0).astype(int)
        df['group'] = self.make_groups(df)
        df['budget'] = self.fill_mean(df, 'budget')
        df['boxoffice'] = self.fill_mean(df, 'boxoffice')

        return df.drop(columns=['group'])

    def get_scrapped(self, df):
        if False:
            # warning - takes long time (a lot filmweb api calls)
            new_columns = ['budget', 'boxoffice', 'topics_count']

            scrapped = pd.DataFrame(columns=new_columns)
            scrapped[new_columns] = df.apply(lambda x: self.movie_info(int(x.ID)), axis=1, result_type='expand')
            scrapped[new_columns] = scrapped[new_columns].apply(lambda x: x.fillna(x.mean()), axis=0).astype(int)
            return scrapped
        else:
            return pd.read_csv(
                'https://raw.githubusercontent.com/mateuszrusin/ml-filmweb-score/dw-poznan-project/oceny_scraped.csv')

    def dummies(self, series):
        data = pd.get_dummies(series.apply(to_list).apply(pd.Series).stack()).sum(level=0)
        return data

    def label_encode(self, series):
        encoder = LabelEncoder()
        encoder.fit(series)
        return encoder.transform(series)

    def movie_info(self, id):
        try:
            film = Film.get_by_id(id)
            film.populate()
            return film.budget, film.boxoffice, film.topics_count
        except Exception:
            return None, None, None

    def make_groups(self, df):
        minidf = df.drop(
            columns=['budget', 'boxoffice', 'ID', 'Gatunek', 'Kraj produkcji', 'Tytuł polski', 'Tytuł oryginalny', 'Data',
                     'Ulubione', 'Rok produkcji'])
        kmeans = KMeans(n_jobs=-1, n_clusters=5)
        kmeans.fit(minidf)
        return kmeans.predict(minidf)

    @staticmethod
    def fill_mean(df, column):
        return df.groupby('group')[column].apply(lambda x: x.fillna(x.mean())).astype(int)
