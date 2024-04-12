# USVotesGraphs

What is the clustering behavior of members of Congress in terms of their individual voting records, and what does it look like over time? Is one
party completely disparate from another in one chamber but not the other; what, if any, factions exist; and when did those groups peel off from the majority? Answers to some or all of these questions may be obvious to those tuned into current events, but it would be advantageous to visualize this using the available voting data from [govtrack.us](https://www.govtrack.us/developers/data). 

USVotesGraphs is a package that provides a visual report on the voting history of the US Congress, including past and present sessions. Currently the project only has bare-bones plotting utilities for t-distributed Stochastic Neighbor Embeddings. A "t-SNE" serves to preserve high-dimensional structures of the data at lower dimensions. 

<a id='Pipeline'></a>
## 2. Data to Visual Pipeline:

Currently there are only two scripts for this project, `src/data/make_dataset.py` and `src/features/build_features.py`. The Dataset class in make_dataset.py processes the raw .json data in `src/data/raw/` and outputs .csv files to `data/processed/`. The end product is effectively a spreadsheet of congressional members (rows) and their votes cast on more than 1800 measures/bills (columns). Yea, Nay, and Abstain votes are represented as 1, 0, and -1, respectively. Some additional metadata about each member is also saved, namely their Party and State.

Given the data in `data/processed/`, the Features class in the build_features.py module is then used
to generate an exploratory 2-dimensional t-SNE plot using scikit-learn and matplotlib. To suppress noise and decrease computation time for t-SNE, I have utilized another of scikit-learn's tools, Truncated Singular Value Decomposition (SVD) to reduce the number of features (bills) from 1800+ to a representative set of 50 features.

To plot both the Senate and House separately on similar scales, which separately vote on a different set of measures, I have opted toward using either StandScalar or RobustScaler from scikit-learn. To see what it looks like when both the Senate and House are treated as one body, see [here](https://github.com/jparrent/usvotesgraphs/blob/master/src/features/All_Congress_tSNE_SVD50_20170201.png).

---
<a id='Graphs'></a>
## 3. Latest Graphs:

The transformations applied to the processed data have not yet been tuned, but are simply 'out of the box' implementations of both t-SNE and TruncatedSVD. It is also worth noting that [t-SNE plots can be misleading](http://distill.pub/2016/misread-tsne/), and in my opinion are best served as an animated series of iterations. That said, let's see the first graph from USVotesGraphs.

<p align="center">
  <img src="https://github.com/jparrent/usvotesgraphs/blob/master/src/visualization/113_Senate_20170308.gif" alt="t-SNE of US Congressional Votes for the 113th Session in the Senate"/>
</p>

<p align="center">
  <img src="https://github.com/jparrent/usvotesgraphs/blob/master/src/visualization/113_House_20170308.gif" alt="t-SNE of US Congressional Votes for the 113th Session in the House"/>
</p>

Pending further tuning and the creation of an animated series of t-SNE iterations, below are some take away points about the 113th session of Congress (2013-2015):

* The Senate is not nearly as polarized as the House.

* The description, 'Mainstream', is accurate for, e.g., Senators Reid (D) and McConnell (R), and Representatives Cantor (R), Pelosi (D), and Wasserman-Schultz (D). 

* Senator Sanders (I) is an outlier for both parties in the Senate.

* Representative Boehner (R), then House Minority Leader, is an outlier from the Republican party. This could possibly reflect [tumultuous relations between him and the 'Freedom Caucus'](http://www.newyorker.com/magazine/2015/12/14/a-house-divided) (R) at the time. It is unclear if the stream of points Boehner is neighbors with is artificial or not; this could be due to too many features given to t-SNE (re: 50), or [it could disappear upon additional iterations](http://distill.pub/2016/misread-tsne/). Similarly, it is unclear if the Freedom Caucus is a part of the right-most cluster of Reps and Dems in the House. 

These and other points will be revisited and updated soon. 

---
<a id='Organization'></a>
## 4. Project Organization

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train` (currently not in use)
    ├── README.md          <- The top-level README for developers using this project.
    ├── data		   <- This directory is omitted from this repo due to large file sizes.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original .json data from www.govtrack.us.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details (currently empty)
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries (empty)
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc. (empty)
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py (empty)
    │   │   └── train_model.py (empty)
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py (empty)
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
