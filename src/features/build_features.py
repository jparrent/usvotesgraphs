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
# import glob2
# import json
# from collections import OrderedDict
# import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE

_ROOT = str(Path(os.getcwd()).parents[1])
_PROCESSED_DATA_PATH = os.path.join(_ROOT, 'data/processed/')


class Features:

    def __init__(self, session_number):

        self._session_number = session_number
        self._filehandle = '_'.join([str(self._session_number), 'dataframe.csv'])
        self._input_file = os.path.join(_PROCESSED_DATA_PATH, self._filehandle)
        self._data = pd.read_csv(self._input_file, encoding='utf-8')

    def load(self):

        metadata = self._data[['Name', 'Party', 'State']].values
        cols = self._data.columns.tolist()[3:]
        data = self._data[cols].values
        return metadata, data


@click.command()
@click.argument('session_number')
def main(session_number):
    """ Script to explore dimensionality reduction using TruncatedSVD
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # Retreive Congressional metadata and vote data for transforming
    metadata, data = Features(session_number).load()

    # Transforming 1800+ features (measures/bills) to 50 features using
    # truncated singular value decomposition (SVD)
    svd = TruncatedSVD(50)
    transformed_data = svd.fit_transform(data)

    # Building n-component t-distributed stochastic neighbor embedding (t-SNE)
    t_SNE = TSNE(n_components=2, random_state=0)
    np.set_printoptions(suppress=True)
    model.fit_transform(transformed_data)

    # // TODO plot results


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    main()
