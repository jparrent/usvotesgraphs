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
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt


class Features:

    def __init__(self, session_number):

        self._ROOT = str(Path(os.getcwd()).parents[1])
        self._input_data_path = os.path.join(self._ROOT, 'data/processed/')
        self._session_number = session_number
        self._filehandle = '_'.join([str(self._session_number), 'dataframe.csv'])
        self._input_file = os.path.join(self._input_data_path, self._filehandle)
        self._data = pd.read_csv(self._input_file, encoding='utf-8')

    def load(self):
        """Read input dataframe.csv files (Votes Records) in
        ../../data/processed/ and return Party (y_labels) and votes cast (X_data)
        """

        df = self._data.set_index('Name')
        return df

    def transform_SVD_tSNE(self, df, chamber, n_features_SVD=50,
                           n_components=2, scale='standard'):
        """Transform 1800+ features (measures/bills) to 50 features using
        truncated singular value decomposition (SVD). This is followed by
        creating and returning a t-distributed stochastic neighbor embedding
        (t-SNE).
        """

        df = df[df.Chamber == chamber]
        cols = df.columns.tolist()[3:]

        svd = TruncatedSVD(n_features_SVD)
        svd_mapper = DataFrameMapper([(df.columns[3:], svd)])
        X_trunc = svd_mapper.fit_transform(df.copy())

        tSNE = TSNE(n_components=n_components, random_state=0)
        np.set_printoptions(suppress=True)
        X_tSNE = tSNE.fit_transform(X_trunc)

        if scale != 'robust':

            X_tSNE = StandardScaler().fit_transform(X_tSNE)

        X_tSNE = RobustScaler().fit_transform(X_tSNE)

        df_X_tSNE = pd.DataFrame(X_tSNE, index=df.index)
        df_tSNE = pd.concat([df[['Party', 'State']], df_X_tSNE], axis=1)

        return df_tSNE

    def plot_2D_tSNE(self, df_senate, df_house, senators=[], representatives=[]):
        """Plot tSNE for senate and house.
        """

        f, (senate, house) = plt.subplots(2, sharex=False, sharey=False)
        marker = '.'
        alpha = 0.7
        legend_labels = ['Dem', 'Reb', 'Ind']
        colors = ['b', 'r', 'm']
        senate_markers = ['*', '+', 'x', '^']
        house_markers = ['v', '<', '>', 'D']

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
        senate.set_title('t-SNE of US Senate Votes')

        """House Scatter Plot
        """
        house.scatter(vis_x_dems_house, vis_y_dems_house, c=colors[0],
                      marker=marker, alpha=alpha)
        house.scatter(vis_x_reps_house, vis_y_reps_house, c=colors[1],
                      marker=marker, alpha=alpha)
        house.scatter(vis_x_inds_house, vis_y_inds_house, c=colors[2],
                      marker=marker, alpha=alpha)
        house.set_title('t-SNE of US House Votes')

        f.subplots_adjust(hspace=0.3)
        senate.axes.get_xaxis().set_ticks([])
        senate.axes.get_yaxis().set_ticks([])
        house.axes.get_xaxis().set_ticks([])
        house.axes.get_yaxis().set_ticks([])
        senate.axis('off')
        house.axis('off')

        legend_groups = [Dems, Reps, Inds]

        if senators:

            for p, person in enumerate(senators):

                vis_x, vis_y = df_senate[(df_senate.index == person)].values[0, 2:]
                point = senate.scatter(vis_x, vis_y, s=75,
                                       marker=senate_markers[p], c='black')
                legend_groups.append(point)
                legend_labels.append(person)

        if representatives:

            for p, person in enumerate(representatives):

                vis_x, vis_y = df_house[(df_house.index == person)].values[0, 2:]
                point = house.scatter(vis_x, vis_y, s=70,
                                      marker=house_markers[p], c='black')
                legend_groups.append(point)
                legend_labels.append(person)

        f.legend(legend_groups,
                 legend_labels,
                 scatterpoints=1,
                 loc='upper left',
                 prop={'size': 10},
                 labelspacing=0.5,
                 bbox_to_anchor=(0.01, 0.7),
                 fancybox=True,
                 shadow=True,
                 borderaxespad=0.,
                 ncol=1,
                 fontsize=10)

        plt.show()


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Script to explore dimensionality reduction using TruncatedSVD
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    congressional_votes = Features(session_number)
    df = congressional_votes.load()
    senators = ['Sanders',
                'Reid',
                'McConnell',
                ]
    representatives = ['Boehner',
                       'Pelosi',
                       'Cantor',
                       'Wasserman'
                       ]
    scale = 'robust'

    df_tSNE_senate = congressional_votes.transform_SVD_tSNE(df, chamber='s', scale=scale)
    df_tSNE_house = congressional_votes.transform_SVD_tSNE(df, chamber='h', scale=scale)

    congressional_votes.plot_2D_tSNE(df_tSNE_senate, df_tSNE_house,
                                     senators, representatives)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
