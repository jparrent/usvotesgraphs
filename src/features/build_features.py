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
        y_labels = df['Party'].values
        X_data = df[cols].values
        return y_labels, X_data

    def plot_2D_tSNE(self, labels, data, n_features_SVD=50):
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

        vis_x = X_tSNE[:, 0]
        vis_y = X_tSNE[:, 1]

        colors = [0 if v == 'D' else 1 if v == 'R' else 2 for v in labels.tolist()]

        plt.scatter(vis_x, vis_y, c=colors, cmap=plt.cm.brg)
        plt.show()


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Script to explore dimensionality reduction using TruncatedSVD
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    congressional_features = Features(session_number)
    y_labels, X_data = congressional_features.load()
    congressional_features.plot_2D_tSNE(y_labels, X_data)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
