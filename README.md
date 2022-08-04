# Credit Risk Modelling

# About

An interactive tool demonstrating credit risk modelling.

Emphasis on:

- Building models
- Comparing techniques
- Interpretating results

## Built With

- [Streamlit](https://streamlit.io/)

#### Hardware initially built on:

Processor: 11th Gen Intel(R) Core(TM) i7-1165G7 @2.80Ghz, 2803 Mhz, 4 Core(s), 8 Logical Processor(s)

Memory (RAM): 16GB

## Local setup

### Obtain the repo locally and open its root folder

#### To potentially contribute

```shell
git clone https://github.com/pkiage/tool-credit-risk-modelling.git
```

or

```shell
gh repo clone pkiage/tool-credit-risk-modelling
```

#### Just to deploy locally

Download ZIP

### (optional) Setup virtual environment:

```shell
python -m venv venv
```

### (optional) Activate virtual environment:

#### If using Unix based OS run the following in terminal:

```shell
.\venv\bin\activate
```

#### If using Windows run the following in terminal:

```shell
.\venv\Scripts\activate
```

### Install requirements by running the following in terminal:

#### Required packages

```shell
pip install -r requirements.txt
```

#### Complete graphviz installation

https://graphviz.org/download/

## Build and install local package

```shell
python setup.py build
```

```shell
python setup.py install
```

### Run the streamlit app (app.py) by running the following in terminal (from repository root folder):

```shell
streamlit run src/app.py
```

## Deployed setup details

For faster model building and testing (particularly XGBoost) a local setup or on a more powerful server than free heroku dyno type is recommended. ([tutorials on servers for data science & ML](https://course.fast.ai))

[Free Heroku dyno type](https://devcenter.heroku.com/articles/dyno-types) was used to deploy the app

Memory (RAM): 512 MB

CPU Share: 1x

Compute: 1x-4x

Dedicated: no

Sleeps: yes

[Enabled Autodeploy from Github](https://devcenter.heroku.com/articles/github-integration)

[Manual deploy to Heroku](https://devcenter.heroku.com/articles/git#deploy-your-code)

From main branch:
```shell
heroku login

git push heroku main
```

From branch beside main:

```shell
heroku login

git push heroku branch_name:main
```

# Roadmap

To view/submit ideas as well as contribute please view issues.

# Docs creation

## [pydeps](https://github.com/thebjorn/pydeps) Python module depenency visualization

_Delete **init**.py and **main**.py_ then run the following

### App and clusters

```shell
pydeps src/app.py --max-bacon=5 --cluster --rankdir BT -o docs/module-dependency-graph/src-app-clustered.svg
```

### App and links

Features, models, & visualization links:

```shell
pydeps src/app.py --only features models visualization --max-bacon=4 --rankdir BT -o docs/module-dependency-graph/src-feature-model-visualization.svg
```

### Only features

```shell
pydeps src/app.py  --only features --max-bacon=5 --cluster --max-cluster-size=3  --rankdir BT -o docs/module-dependency-graph/src-features.svg
```

### Only models

```shell
pydeps src/app.py  --only models --max-bacon=5 --cluster --max-cluster-size=15  --rankdir BT -o docs/module-dependency-graph/src-models.svg
```

## [code2flow](https://github.com/scottrogowski/code2flow) Call graphs for a pretty good estimate of project structure

### Logistic

```shell
code2flow src/models/logistic_train_model.py -o docs/call-graph/logistic_train_model.svg
```

```shell
code2flow src/models/logistic_model.py -o docs/call-graph/logistic_model.svg
```

### Xgboost

```shell
code2flow src/models/xgboost_train_model.py -o docs/call-graph/xgboost_train_model.svg
```

```shell
code2flow src/models/xgboost_model.py -o docs/call-graph/xgboost_model.svg
```

### utils

```shell
code2flow src/models/util_test.py -o docs/call-graph/util_test.svg
```

```shell
code2flow src/models/util_predict_model_threshold.py -o docs/call-graph/util_predict_model_threshold.svg
```

```shell
code2flow src/models/util_predict_model.py -o docs/call-graph/util_predict_model.svg
```

```shell
code2flow src/models/util_model_comparison.py -o docs/call-graph/util_model_comparison.svg
```

# References

## Inspiration:

[Credit Risk Modeling in Python by Datacamp](https://www.datacamp.com/courses/credit-risk-modeling-in-python)

- General Methodology
- Data

[A Gentle Introduction to Threshold-Moving for Imbalanced Classification](https://machinelearningmastery.com/threshold-moving-for-imbalanced-classification/)

- Selecting optimal threshold using Youden's J statistic

[Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)

- Project structure

[GraphViz Buildpack](https://github.com/weibeld/heroku-buildpack-graphviz)

- Buildpack used for Heroku deployment
