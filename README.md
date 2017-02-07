# USVotesGraphs

What is the clustering behavior of members of Congress in terms of their individual voting records, and what does it look like over time? Is one
party completely disparate from another in one chamber but not the other; what, if any, factions exist; and when did those groups peel off from the majority? Answers to some or all of these questions may be obvious to those tuned into current events, but it would be advantageous to visualize this using the available voting data from [govtrack.us](https://www.govtrack.us/developers/data). 

USVotesGraphs is a package that provides a visual report on the voting history of the US Congress, including past and present sessions. Currently the project only has bare-bones plotting utilities for t-distributed Stochastic Neighbor Embeddings. A "t-SNE" serves to preserve high-dimensional structures of the data at lower dimensions. I will soon expand this to include methods that generate animated gifs of the time-evolution of the clustering behaviors. This project also serves as a primer to budding data scientists who may be looking to capitalize on building scalable projects via Objected-oriented programming (OOP) with Python -- this as opposed to dilapidated, one-off scripts that not only break when touched, but resist any momentum in testing ideas. 

# Outline of README:

	1. OOP & Classes
	2. Data to Visual Pipeline
	3. Latest Graphs
	4. Project Organization
	
------------
## 1. OOP & Classes (abridged)

### 1.1 Why do Data Science with Classes?

More often than not, data scientits need to write one-off, bare-bones scripts to accomplish a specific or 
time-sensitive task. In order to add more functionality, refactoring the code is usually needed, particularly when the scripts are old. I have found it incredibly beneficial to start a project as close to a well-organized state as possible, and in terms of both setting up project directories and defining functions within a set of classes:

* organize a directory tree before coding anything (optional: [cookie-cutter](https://github.com/audreyr/cookiecutter))

* give specific 'classes' ownership of specific methods and variables so that `def main(): ...` reads like a series of clear commands, with as little logic as possible (preferably none)

Doing so will not necessarily ensure that you are utilizing all Object-oriented programming design patterns principles, much less following them in the most appropriate ways, but it will put you much closer to that end in the long run.

### 1.2 How and What?

Even if you are unfamiliar with OOP, study the following pattern until you know it:
```
class Dataset:
"""Class Description"""
	
	def __init__(self, *args, **kwargs):
		self.__data = {}
		
	def load(self, *args, **kwargs)
		pass
		return self.__data
		
	def filter(self, *args, **kwargs):
		pass
		
	def transform(self, *args, **kwargs):
		pass
		
	def plot(self, *args, **kwargs):
		pass
		
def main(*args, **kwargs):

	data = Dataset(*args, **kwargs).load()
	
	filtered_data = data.filter(*args, **kwargs)
	transform_data = data.transform(*args, **kwargs)
	
	data.plot(*args, **kwargs)
		
if __name__ == '__main__':
	
	main(*args, **kwargs)
```

Here we have the definition of a class, or a template for creating 'instances' of objects, followed by the primary instructions in `main()`. This is an example format that will likely keep the project well-organized over time. And with only four methods to build out, this class already has most everything a data scientist frequently uses when handling data.

The `__init__` is a special method that is used to initialize variables. Think of it as a method that stores whatever it is you need to keep track of, e.g., the data, today's date, or to call another method.

What is `self`? This is how to generalize a class's methods and attributes so that one instance of that class does not affect a separate instance. A class's method needs to be passed `self`, i.e. `def load(self, *args, **kwargs):`, to point to the instance when called via `data = Dataset.load(*args, **kwargs)`. And if you want to use a class's methods or attributes within the class itself, prepend `self.` to that method or attribute.

What are `*args` and `**kwargs`? This is how Python 'unpacks' a sequence of arguments and a dictionary of keyword arguments, respectively. You can think of them as placeholders until you figure out what variables you are going to pass. You can also leave them as is and handle within a given method's definition. 


### 1.3 Guiding Principles

**Abstraction** - This is the idea that methods have one job.

**Encapsulation** - Treating class attributes with care by using `self.__data` to store variables means that `Dataset().data = 0` will not result in overwriting the data, nor will `Dataset().__data = 0`. Instead build a method like `Dataset.load()` to retrieve `self.__data`, and in whatever format you want. 

**Inheritance** - One class can inherit all methods and attributes from one or more classes if so desired. 

**Polymorphism** - Say you have a Dataset class representing actions to be done on the raw and processed data, and a separate Features class which has the sole purpose of feature engineering and some exploratory plotting. Between the two classes, you may want to load a file in similar but slightly different ways. To save on scripting, you could accomplish this by having Features inherit the `load()` method from Dataset and modify it in Features:

```
class Features(Dataset):

	def __init__(self):
		super().__init__()
		self.__data = []  # {} for the base class of Dataset
		
```

### 1.4 Topics Not Covered (yet)

* Decorators

* Class and Static Methods

* Multiple Inheritance

------------
## 2. Data to Visual Pipeline:

Currently there are only two scripts for this project, `src/data/make_dataset.py` and `src/features/build_features.py`. The Dataset class in make_dataset.py processes the raw .json data in `src/data/raw/` and outputs .csv files to `data/processed/`. The end product is effectively a spreadsheet of congressional members (rows) and their votes cast on more than 1800 measures/bills (columns). Yea, Nay, and Abstain votes are represented as 1, 0, and -1, respectively. Some additional metadata about each member is also saved, namely their Party and State.

Given the data in `data/processed/`, the Features class in the build_features.py module is then used
to generate an exploratory 2-dimensional t-SNE plot using scikit-learn and matplotlib. To suppress noise and decrease computation time for t-SNE, I have utilized another of scikit-learn's tools, Truncated Singular Value Decomposition (SVD) to reduce the number of features (bills) from 1800+ to a representative set of 50 features. 

------------
## 3. Latest Graphs:

The transformations applied to the processed data have not yet been tuned, but are simply 'out of the box' implementations of both t-SNE and TruncatedSVD. It is also worth noting that [t-SNE plots can be misleading](http://distill.pub/2016/misread-tsne/), and in my opinion are best served as an animated series of iterations. That said, let's see the first graph from USVotesGraphs.

<p align="center">
  <img src="https://github.com/jparrent/usvotesgraphs/blob/master/src/features/senate_house_tSNE_SVD50_StandardScaler_20170202.png" alt="t-SNE of US Congressional Votes for the 113th Session"/>
</p>
------------
4. Project Organization

[Under construction]


    &#9500;&#9472;&#9472; LICENSE
    &#9500;&#9472;&#9472; Makefile           <- Makefile with commands like `make data` or `make train`
    &#9500;&#9472;&#9472; README.md          <- The top-level README for developers using this project.
    &#9500;&#9472;&#9472; data
    &#9474;   &#9500;&#9472;&#9472; external       <- Data from third party sources.
    &#9474;   &#9500;&#9472;&#9472; interim        <- Intermediate data that has been transformed.
    &#9474;   &#9500;&#9472;&#9472; processed      <- The final, canonical data sets for modeling.
    &#9474;   &#9492;&#9472;&#9472; raw            <- The original, immutable data dump.
    &#9474;
    &#9500;&#9472;&#9472; docs               <- A default Sphinx project; see sphinx-doc.org for details
    &#9474;
    &#9500;&#9472;&#9472; models             <- Trained and serialized models, model predictions, or model summaries
    &#9474;
    &#9500;&#9472;&#9472; notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    &#9474;                         the creator's initials, and a short `-` delimited description, e.g.
    &#9474;                         `1.0-jqp-initial-data-exploration`.
    &#9474;
    &#9500;&#9472;&#9472; references         <- Data dictionaries, manuals, and all other explanatory materials.
    &#9474;
    &#9500;&#9472;&#9472; reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    &#9474;   &#9492;&#9472;&#9472; figures        <- Generated graphics and figures to be used in reporting
    &#9474;
    &#9500;&#9472;&#9472; requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    &#9474;                         generated with `pip freeze > requirements.txt`
    &#9474;
    &#9500;&#9472;&#9472; src                <- Source code for use in this project.
    &#9474;   &#9500;&#9472;&#9472; __init__.py    <- Makes src a Python module
    &#9474;   &#9474;
    &#9474;   &#9500;&#9472;&#9472; data           <- Scripts to download or generate data
    &#9474;   &#9474;   &#9492;&#9472;&#9472; make_dataset.py
    &#9474;   &#9474;
    &#9474;   &#9500;&#9472;&#9472; features       <- Scripts to turn raw data into features for modeling
    &#9474;   &#9474;   &#9492;&#9472;&#9472; build_features.py
    &#9474;   &#9474;
    &#9474;   &#9500;&#9472;&#9472; models         <- Scripts to train models and then use trained models to make
    &#9474;   &#9474;   &#9474;                 predictions
    &#9474;   &#9474;   &#9500;&#9472;&#9472; predict_model.py
    &#9474;   &#9474;   &#9492;&#9472;&#9472; train_model.py
    &#9474;   &#9474;
    &#9474;   &#9492;&#9472;&#9472; visualization  <- Scripts to create exploratory and results oriented visualizations
    &#9474;       &#9492;&#9472;&#9472; visualize.py
    &#9474;
    &#9492;&#9472;&#9472; tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
