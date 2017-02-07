# USVotesGraphs

What is the clustering behavior of congressional members in terms of their individual voting records, and what does it look like? Is one
party completely disparate from another; what, if any, factions exist; and when did those groups peel off from the majority? Answers to some or all of these questions may be obvious to those tuned into current events, but it would be nice to visualize this using the available voting data from [link]. 

USVotesGraphs is a package that provides a visual report on the voting history of the US Congress, including past and present sessions. Currently the project only has barebones plotting utilities for t-distributed Stochastic Neighbor Embeddings. A "t-SNE" serves to preserve high-dimensional structures of the data at lower dimensions. I will soon expand this to include methods that generate animated gifs of the time-evolution of the clustering behaviors. This project also serves as a primer to budding data scientists who may be looking to capitalize on building scalable projects via Objected-oriented programming (OOP) with Python -- this as opposed to delapidated, one-off scripts that not only break when touched, but resist any momentum in testing ideas. 

# Outline of README:

	1. OOP & Classses
	2. Data to Visual Pipeline
	3. Latest Graphs
	4. Project Organization
	
------------
## 1. OOP & Classes (abridged)
------------

### 1.1 Why do Data Science with Classes

More often than not, data scientits need to write one-off, barebones scripts to accomplish a specific or 
time-sensitive task. In order to add more functionality, refactoring the code is usually needed, particularly when the scripts are old. I have found it most useful to start a project as close to a well-orgaized state as possible, and in terms of both setting up project directories and defining functions within a set of classes:

* organize a directory tree before coding anything (optional: [cookie-cutter](https://github.com/audreyr/cookiecutter))

* give specific 'classes' ownership of specific methods and variables so that `def main(): ...` reads like a series of clear commands, with as little logic as possible (preferrably none)

Doing so will not ensure that you are utilizing all Object-oriented programming design patterns principes, much less following them in the most appropriate ways, but it will put you much closer to that end in the long run.

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

Here we have the definition of a class, or a template for creating 'instances' of objects. This is also how the project will stay organized. And with only four methods to build out, this class already has most everything a data scientist frequently uses when handling data.

The `__init__` is a special method that is used to initialize variables. You can also think about it as a method that stores whatever it is you need to keep track of, e.g., the data, today's date, or to call another method.

What is `self`? This is how to generalize a class's methods and attributes so that one instance of that class does not affect a separate instance. A class's method needs to be passed `self`, i.e. `def load(self, *args, **kwargs):`, to point to the instance when called via `data = Dataset.load(*args, **kwargs)`. And if you want to use a class's methods or attributes within the class itself, prepend `self.` to that method or attribute.

What are `*args` and `**kwargs`? This is how Python 'unpacks' a sequence of arguments and a dictionary of keyword arguments, respectively. You can think of them as placeholders until you figure out what variables you are going to pass -- you can also leave them as is and handle within the method definition. 


### 1.3 Guiding Principles

[Under construction]

------------
## 2. Data to Visual Pipeline:
------------

Given the data in `data/processed`, the `src/data/build_features.py` module is currently used
to generate an exploratory 2-dimensional t-SNE plot.

[Under construction]

------------
## 3. Latest Graphs:
------------

[Under construction]

------------
4. Project Organization
------------

[Under construction]


    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
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
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
