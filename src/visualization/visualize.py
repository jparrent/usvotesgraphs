# -*- coding: utf-8 -*-

"""
visualize.py
---------------------
Functions for creating animated t-SNE.
"""
import os
from pathlib import Path
import click
import logging
import json
import datetime
import unicodedata as ucd
from collections import defaultdict
import numpy as np
import pandas as pd
import sklearn
from numpy import linalg
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn_pandas import DataFrameMapper
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.animation import FuncAnimation
from tsne_animate import tsneAnimate
import matplotlib.animation as animation
import seaborn as sns
sns.set_style('darkgrid')
sns.set_palette('muted')
sns.set_context("notebook", font_scale=1.5,
                rc={"lines.linewidth": 2.5})


def getSteps(self, X, y):
    # based on https://github.com/oreillymedia/t-SNE-tutorial
    old_grad = sklearn.manifold.t_sne._gradient_descent
    positions = []

    def _gradient_descent(objective, p0, it, n_iter, objective_error=None,
                          n_iter_check=1, n_iter_without_progress=50,
                          momentum=0.5, learning_rate=1000.0, min_gain=0.01,
                          min_grad_norm=1e-7, min_error_diff=1e-7, verbose=0,
                          args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        p = p0.copy().ravel()
        update = np.zeros_like(p)
        gains = np.ones_like(p)
        error = np.finfo(np.float).max
        best_error = np.finfo(np.float).max
        best_iter = 0

        for i in range(it, n_iter):
            # We save the current position.
            positions.append(p.copy())

            new_error, grad = objective(p, *args, **kwargs)
            grad_norm = linalg.norm(grad)

            inc = update * grad >= 0.0
            dec = np.invert(inc)
            gains[inc] += 0.05
            gains[dec] *= 0.95
            np.clip(gains, min_gain, np.inf)
            grad *= gains
            update = momentum * update - learning_rate * grad
            p += update

            if (i + 1) % n_iter_check == 0:
                if new_error is None:
                    new_error = objective_error(p, *args)
                error_diff = np.abs(new_error - error)
                error = new_error

                if verbose >= 2:
                    m = "[t-SNE] Iteration %d: error = %.7f, gradient norm = %.7f"
                    print(m % (i + 1, error, grad_norm))

                if error < best_error:
                    best_error = error
                    best_iter = i
                elif i - best_iter > n_iter_without_progress:
                    if verbose >= 2:
                        print("[t-SNE] Iteration %d: did not make any progress "
                              "during the last %d episodes. Finished."
                              % (i + 1, n_iter_without_progress))
                    break
                if grad_norm <= min_grad_norm:
                    if verbose >= 2:
                        print("[t-SNE] Iteration %d: gradient norm %f. Finished."
                              % (i + 1, grad_norm))
                    break
                if error_diff <= min_error_diff:
                    if verbose >= 2:
                        m = "[t-SNE] Iteration %d: error difference %f. Finished."
                        print(m % (i + 1, error_diff))
                    break

            if new_error is not None:
                error = new_error

        return p, error, i

    # Replace old gradient func
    sklearn.manifold.t_sne._gradient_descent = _gradient_descent
    X_proj = self.tsne.fit_transform(X)
    self.isfit = True
    # return old gradient descent back
    sklearn.manifold.t_sne._gradient_descent = old_grad
    return positions

tsneAnimate.getSteps = getSteps


def animate(self, X, y, congressmen, session_number, chamber):

    pos = self.getSteps(X, y)
    y_mapping = {i: n for n, i in enumerate(set(y))}

    last_iter = pos[len(pos) - 1].reshape(-1, 2)
    lims = np.max(last_iter, axis=0), np.min(last_iter, axis=0)
    NCOLORS = len(y_mapping)
    fig = plt.figure()
    plt.title('Congress: ' + session_number)
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    brg = plt.get_cmap('brg')
    alpha = 0.5
    cNorm = colors.Normalize(vmin=0, vmax=NCOLORS)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=brg)

    annotation = ax.annotate('', xy=(0, 0))
    annotation.set_animated(True)
    annotations_dict = {j: ax.annotate(j, xy=(0, 0), xytext=(5, 5),
                                       textcoords='offset points') for j in congressmen}

    A, B = np.array(list(zip(*pos[0].reshape(-1, 2))))

    def getDots(A, B, X, y, NCOLORS, alpha, congressmen):
        dots_list = []

        for i in range(NCOLORS):
            colorVal = scalarMap.to_rgba(i)
            a, b = A[y['Party'] == i], B[y['Party'] == i]
            dots, = ax.plot(b, a, 'o', color=colorVal, alpha=alpha)
            dots_list.append(dots)

        if congressmen:
            for j in congressmen:
                a, b = A[y['Name'] == j], B[y['Name'] == j]
                dots, = ax.plot(b, a, '*', markersize=20, color='black')
                dots_list.append(dots)

        return dots_list

    def init():
        ax.set_xlim([lims[0][0], lims[1][0]])
        ax.set_ylim([lims[0][1], lims[1][1]])
        ax.axis('off')
        return [i for i in dots_list], annotation

    def update(i):
        for j in range(len(dots_list)):
            a, b = np.array(list(zip(*pos[i].reshape(-1, 2))))
            a, b = a[y['Party'] == j], b[y['Party'] == j]
            dots_list[j].set_xdata(a)
            dots_list[j].set_ydata(b)

        if congressmen:
            annotation_list = []
            num_cmen = len(congressmen)
            for k, j in enumerate(congressmen):
                a, b = np.array(list(zip(*pos[i].reshape(-1, 2))))
                a, b = a[y['Name'] == j], b[y['Name'] == j]

                annotations_dict[j].xy = (a, b)
                annotation_list.append(annotations_dict[j])

                dots_list[-num_cmen + k].set_xdata(a)
                dots_list[-num_cmen + k].set_ydata(b)

        return [i for i in dots_list] + [ax], annotation_list

    dots_list = getDots(A, B, X, y, NCOLORS, alpha, congressmen)
    frames = np.arange(0, len(pos) - 1)

    anim = FuncAnimation(fig, update,
                         frames=frames, init_func=init, interval=50)

    # plt.show()

    today = datetime.date.today().strftime("%Y%m%d")
    outfile = '_'.join((session_number, chamber, today))
    outfile = '.'.join((outfile, 'gif'))
    anim.save(outfile, dpi=80, writer='imagemagick')

tsneAnimate.animate = animate


class Animation:
    """Class used to build animated gifs for t-SNE.
    """

    def __init__(self, session_number, chamber):

        self._ROOT = str(Path(os.getcwd()).parents[1])
        self._input_data_path = os.path.join(self._ROOT, 'data/processed/')
        self._supplemental_path = os.path.join(self._ROOT, 'data/supplemental/')
        self._session_number = str(session_number)
        self._chamber = 'Senate' if chamber == 's' else 'House'
        self._filehandle = '_'.join([str(self._session_number), 'dataframe.csv'])
        self._input_file = os.path.join(self._input_data_path, self._filehandle)
        self._data = pd.read_csv(self._input_file, encoding='utf-8')
        # self._sens, self._reps, self._senate_majority, self._house_majority = self.load_select_congressmen()
        # self._congressmen, self._majority = self.load_select_congressmen(chamber)

    @property
    def data(self):
        return self._data

    @property
    def supplemental_path(self):
        return self._supplemental_path

    @property
    def session_number(self):
        return self._session_number

    @property
    def chamber(self):
        return self._chamber

    def load_data(self, chamber):
        """Read input dataframe.csv files (Votes Records) in
        ../../data/processed/ and return Party (y_labels) and votes cast (X_data)
        """

        df = self.data  # .set_index('Name')
        # df.index = df.index.map(lambda x: ucd.normalize('NFKD', x.title()))
        df.Party = df.Party.map({'Democrat': 'D', 'D': 'D', 'Republican': 'R',
                                 'R': 'R', 'Independent': 'I', 'I': 'I'})
        df_chamber = df[df.Chamber == chamber]

        return df_chamber

    def load_select_congressmen(self, chamber):
        """Load congressmen presets in select_congressmen.json to be plotted.
        """

        jfilename = os.path.join(self.supplemental_path, 'select_congressmen.json')

        with open(jfilename) as jfile:

            data = json.load(jfile)
            session = data[self.session_number]

            if chamber == 's':

                congressmen = session['Senate']['Members']
                majority = session['Senate']['Majority']

            elif chamber == 'h':

                congressmen = session['House']['Members']
                majority = session['House']['Majority']

        return congressmen, majority

    @staticmethod
    def transform(df, option, n_features_SVD=50, n_components=2, scale=None):
        """
        option = 'svd' : Transform 1800+ features (measures/bills) to 50 features using
        truncated singular value decomposition (SVD).

        option = 'tsne': Transform 50 features using t-distributed stochastic neighbor
        embedding (t-SNE).
        """

        cols = df.columns.tolist()
        data_cols = df.columns.tolist()[4:]

        if option is not None:

            if option == 'svd':

                svd = TruncatedSVD(n_features_SVD)
                svd_mapper = DataFrameMapper([(data_cols, svd)])
                X_transform = svd_mapper.fit_transform(df.copy())

            if option == 'tsne':

                RS = 42     # Random state.
                tsne = TSNE(n_components=n_components, random_state=RS)
                np.set_printoptions(suppress=True)

                X_data = df.ix[:, 3:].as_matrix()
                X_transform = TSNE(random_state=RS).fit_transform(X_data)

        else:

            print('Specify the option param as either svd or tsne.')

        if scale is not None:

            if scale != 'robust':

                X_transform = StandardScaler().fit_transform(X_transform)

            else:

                X_transform = RobustScaler().fit_transform(X_transform)

        df_X_transform = pd.DataFrame(X_transform, index=df.index)
        df_transform = pd.concat([df[['Name', 'Party', 'State']], df_X_transform], axis=1)

        le = preprocessing.LabelEncoder()
        df_transform['Party'] = le.fit_transform(df_transform['Party'])

        return df_X_transform, df_transform[['Name', 'Party', 'State']]


@click.command()
@click.option('--session', default=1, help='Which session of Congress? (int)')
@click.option('--chamber', help='Which chamber? s for senate, h for house')
@click.option('--scale', help='What scale? standard or robust?')
def main(session, chamber, scale):
    """ Script to create t-SNE animation.
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    animation = Animation(session, chamber)
    congressmen, majority = animation.load_select_congressmen(chamber)

    df = animation.load_data(chamber=chamber)
    df_X, df_y = animation.transform(df, option='svd')

    tsne = tsneAnimate(TSNE(random_state=42, learning_rate=1000))
    tsne.animate(df_X, df_y, congressmen, animation.session_number, animation.chamber)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    main()
