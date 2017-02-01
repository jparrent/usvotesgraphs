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
        # // TODO pass label variable to select between metadata labels

        df = self._data.set_index('Name')
        cols = df.columns.tolist()[2:]
        # metadata = self._data[['Name', 'Party', 'State']].values
        names = df.index.values
        y_labels = df['Party'].values
        X_data = df[cols].values
        return names, y_labels, X_data

    def plot_2D_tSNE(self, names, labels, data, congressman=[], n_features_SVD=50):
        """Transform 1800+ features (measures/bills) to 50 features using
        truncated singular value decomposition (SVD). This is followed by
        creating a t-distributed stochastic neighbor embedding (t-SNE), and
        plotting the resulting 2D array.
        """
        # // TODO pass n_features_SVD and labels logic and color mapping

        svd = TruncatedSVD(n_features_SVD)
        X_trunc = svd.fit_transform(data)

        t_SNE = TSNE(n_components=2, random_state=0)
        np.set_printoptions(suppress=True)
        X_tSNE = t_SNE.fit_transform(X_trunc)

        dems_idx = [i for i, v in enumerate(labels) if v == 'D']
        vis_x_dems = [X_tSNE[i, 0] for i in dems_idx]
        vis_y_dems = [X_tSNE[i, 1] for i in dems_idx]

        reps_idx = [i for i, v in enumerate(labels) if v == 'R']
        vis_x_reps = [X_tSNE[i, 0] for i in reps_idx]
        vis_y_reps = [X_tSNE[i, 1] for i in reps_idx]

        inds_idx = [i for i, v in enumerate(labels) if v == 'I']
        vis_x_inds = [X_tSNE[i, 0] for i in inds_idx]
        vis_y_inds = [X_tSNE[i, 1] for i in inds_idx]

        colors = ['b', 'r', 'm']
        legend_labels = ['Dem', 'Reb', 'Ind']

        Dems = plt.scatter(vis_x_dems, vis_y_dems, c=colors[0], alpha=0.5)
        Reps = plt.scatter(vis_x_reps, vis_y_reps, c=colors[1], alpha=0.5)
        Inds = plt.scatter(vis_x_inds, vis_y_inds, c=colors[2], alpha=0.5)

        legend_groups = [Dems, Reps, Inds]

        if congressman:

            markers = ['*', '+', 'x', '^', 'v', '<', '>', 'D']

            for p, person in enumerate(congressman):

                idx = [i for i, v in enumerate(names) if v.lower() == person.lower()]
                vis_x = [X_tSNE[i, 0] for i in idx]
                vis_y = [X_tSNE[i, 1] for i in idx]

                point = plt.scatter(vis_x, vis_y, s=75, marker=markers[p], c='black')
                legend_labels.append(person)
                legend_groups.append(point)

        plt.legend(legend_groups,
                   legend_labels,
                   scatterpoints=1,
                   loc='upper center',
                   bbox_to_anchor=(0.5, 1.14),
                   fancybox=True,
                   shadow=True,
                   borderaxespad=0.,
                   ncol=5,
                   fontsize=10)

        plt.show()


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Script to explore dimensionality reduction using TruncatedSVD
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    congressional_features = Features(session_number)
    names, y_labels, X_data = congressional_features.load()
    congressmen = ['Sanders',
                   'Reid',
                   'McConnell',
                   'Boehner',
                   'Pelosi',
                   'Cantor',
                   'Wasserman']
    congressional_features.plot_2D_tSNE(names, y_labels, X_data, congressmen)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
