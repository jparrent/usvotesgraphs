# -*- coding: utf-8 -*-

"""
build_features.py
---------------------
Functions for exploratory data analysis, e.g., feature engineering and
dimensionality reduction.
"""
import os
from pathlib import Path
import click
import logging
import json
import datetime
import unicodedata as ucd
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Features:

    def __init__(self, session):

        self._ROOT = str(Path(os.getcwd()).parents[1])
        self._input_data_path = os.path.join(self._ROOT, 'data/processed/')
        self._supplemental_path = os.path.join(self._ROOT, 'data/supplemental/')
        self._session_number = session
        self._filehandle = '_'.join([str(self._session_number), 'dataframe.csv'])
        self._input_file = os.path.join(self._input_data_path, self._filehandle)
        self._data = pd.read_csv(self._input_file, encoding='utf-8')
        self._sens, self._reps, self._senate_majority, self._house_majority = self.load_select_congressmen()

    @property
    def data(self):
        return self._data

    @property
    def sens(self):
        return self._sens

    @property
    def reps(self):
        return self._reps

    @property
    def senate_majority(self):
        return self._senate_majority

    @property
    def house_majority(self):
        return self._house_majority

    @property
    def supplemental_path(self):
        return self._supplemental_path

    @property
    def session_number(self):
        return self._session_number

    def load_select_congressmen(self):
        """Load congressmen presets in select_congressmen.json to be plotted.
        """

        jfilename = os.path.join(self.supplemental_path, 'select_congressmen.json')

        with open(jfilename) as jfile:

            data = json.load(jfile)

            try:

                session = data[self.session_number]

            except KeyError:

                return False, False, '', ''

            senators = session['Senate']['Members']
            senate_majority = session['Senate']['Majority']
            representatives = session['House']['Members']
            house_majority = session['House']['Majority']

        return senators, representatives, senate_majority, house_majority

    def load_records(self):
        """Read input dataframe.csv files (Votes Records) in
        ../../data/processed/ and return Party (y_labels) and votes cast (X_data)
        """

        df = self.data.set_index('Name')
        df.index = df.index.map(lambda x: ucd.normalize('NFKD', x.title()))
        df.Party = df.Party.map({'Democrat': 'D', 'D': 'D', 'Republican': 'R',
                                 'R': 'R', 'Independent': 'I', 'I': 'I'})

        return df

    def transform_SVD_tSNE(self, df, chamber, n_features_SVD=50,
                           n_components=2, scale='standard'):
        """Transform 1800+ features (measures/bills) to 50 features using
        truncated singular value decomposition (SVD). This is followed by
        creating and returning a t-distributed stochastic neighbor embedding
        (t-SNE).
        """

        df = df[df.Chamber == chamber]
        data_cols = df.columns.tolist()[3:]

        svd = TruncatedSVD(n_features_SVD)
        svd_mapper = DataFrameMapper([(data_cols, svd)])
        X_trunc = svd_mapper.fit_transform(df.copy())

        tSNE = TSNE(n_components=n_components, random_state=0)
        np.set_printoptions(suppress=True)
        X_tSNE = tSNE.fit_transform(X_trunc)

        if scale != 'robust':

            X_tSNE = StandardScaler().fit_transform(X_tSNE)

        else:

            X_tSNE = RobustScaler().fit_transform(X_tSNE)

        df_X_tSNE = pd.DataFrame(X_tSNE, index=df.index)
        df_tSNE = pd.concat([df[['Party', 'State']], df_X_tSNE], axis=1)

        return df_tSNE

    def plot_congressman(self, df, plt, members, markers, groups, labels):
        """Add congressmen to plot generated by plot_2D_tSNE().
        """

        for p, person in enumerate(members):

            vis_x, vis_y = df[(df.index == person.title())].values[0, 2:]
            party = df.Party[(df.index == person.title())].values[0]
            party = ''.join(['(', party, ')'])
            point = plt.scatter(vis_x, vis_y, s=75,
                                marker=markers[p], c='black')
            label = ' '.join([person, party])
            groups.append(point)
            labels.append(label)

        return groups, labels

    def plot_2D_tSNE(self, df_senate, df_house, session_number):
        """Plot tSNE for senate and house.
        """

        f, (senate, house) = plt.subplots(2, sharex=False, sharey=False)
        marker = '.'
        alpha = 0.5
        labels = ['Dem', 'Reb', 'Ind']
        colors = ['b', 'r', 'm']
        # senate_markers = ['+', 'x', '*', '^', '1', '3', '4', '8']
        senate_markers = '+ x * ^ 1 3 4 8'.split()
        house_markers = 'v < > D s * d p'.split()
        # house_markers = ['v', '<', '>', 'D', 's', '*', 'd', 'p']

        """Senate
        """
        df_dems_senate = df_senate[(df_senate.Party == 'D')]
        vis_x_dems_senate = df_dems_senate[0].values
        vis_y_dems_senate = df_dems_senate[1].values

        df_reps_senate = df_senate[(df_senate.Party == 'R')]
        vis_x_reps_senate = df_reps_senate[0].values
        vis_y_reps_senate = df_reps_senate[1].values

        df_inds_senate = df_senate[(df_senate.Party == 'I')]
        vis_x_inds_senate = df_inds_senate[0].values
        vis_y_inds_senate = df_inds_senate[1].values

        """House
        """
        df_dems_house = df_house[(df_house.Party == 'D')]
        vis_x_dems_house = df_dems_house[0].values
        vis_y_dems_house = df_dems_house[1].values

        df_reps_house = df_house[(df_house.Party == 'R')]
        vis_x_reps_house = df_reps_house[0].values
        vis_y_reps_house = df_reps_house[1].values

        df_inds_house = df_house[(df_house.Party == 'I')]
        vis_x_inds_house = df_inds_house[0].values
        vis_y_inds_house = df_inds_house[1].values

        """Senate Scatter Plot
        """
        Dems = senate.scatter(vis_x_dems_senate, vis_y_dems_senate, c=colors[0],
                              marker=marker, alpha=alpha)
        Reps = senate.scatter(vis_x_reps_senate, vis_y_reps_senate, c=colors[1],
                              marker=marker, alpha=alpha)
        Inds = senate.scatter(vis_x_inds_senate, vis_y_inds_senate, c=colors[2],
                              marker=marker, alpha=alpha)
        senate.set_title('{} {}'.format(self.senate_majority, 'Senate'))

        """House Scatter Plot
        """
        house.scatter(vis_x_dems_house, vis_y_dems_house, c=colors[0],
                      marker=marker, alpha=alpha)
        house.scatter(vis_x_reps_house, vis_y_reps_house, c=colors[1],
                      marker=marker, alpha=alpha)
        house.scatter(vis_x_inds_house, vis_y_inds_house, c=colors[2],
                      marker=marker, alpha=alpha)
        house.set_title('{} {}'.format(self.house_majority, 'House'))

        f.subplots_adjust(hspace=0.3)
        senate.axes.get_xaxis().set_ticks([])
        senate.axes.get_yaxis().set_ticks([])
        house.axes.get_xaxis().set_ticks([])
        house.axes.get_yaxis().set_ticks([])
        senate.axis('off')
        house.axis('off')

        groups = [Dems, Reps, Inds]

        if self.sens:

            groups, labels = self.plot_congressman(df_senate, senate, self.sens,
                                                   senate_markers, groups, labels)

        else:

            groups, labels = [], []

        if self.reps:

            groups, labels = self.plot_congressman(df_house, house, self.reps,
                                                   house_markers, groups, labels)

        else:

            groups, labels = [], []

        f.legend(groups,
                 labels,
                 title='{}: {}'.format('Session', self.session_number),
                 scatterpoints=1,
                 loc='upper left',
                 prop={'size': 8},
                 labelspacing=0.5,
                 bbox_to_anchor=(0.01, 0.7),
                 fancybox=True,
                 shadow=True,
                 borderaxespad=0.,
                 ncol=1,
                 fontsize=10)

        today = datetime.date.today().strftime("%Y%m%d")
        outfile = '_'.join((session_number, 'senate_house', today))
        plt.savefig(outfile, bbox_inches='tight')

        # plt.show()


@click.command()
# @click.argument('session_number')
# def main(session_number):
@click.option('--session', default='113', help='Which session of Congress? (int)')
@click.option('--all', is_flag=True, help='Process all available sessions data.')
def main(session, all):
    """ Script to explore dimensionality reduction using TruncatedSVD
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    if all:

        for x in range(75, 114):

            session = str(x)
            congressional_votes = Features(session)
            df = congressional_votes.load_records()

            df_tSNE_senate = congressional_votes.transform_SVD_tSNE(df, chamber='s', scale='robust')
            df_tSNE_house = congressional_votes.transform_SVD_tSNE(
                df, chamber='h', scale='standard')

            congressional_votes.plot_2D_tSNE(df_tSNE_senate, df_tSNE_house, session)

    else:

        congressional_votes = Features(session)
        df = congressional_votes.load_records()

        df_tSNE_senate = congressional_votes.transform_SVD_tSNE(df, chamber='s', scale='robust')
        df_tSNE_house = congressional_votes.transform_SVD_tSNE(df, chamber='h', scale='standard')

        congressional_votes.plot_2D_tSNE(df_tSNE_senate, df_tSNE_house, session)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
