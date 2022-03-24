# Credit Risk Modelling

# About

An interactive tool demonstrating credit risk modelling.

Emphasis on:
* Building models
* Comparing techniques
* Interpretating results

## Built With

- [Streamlit](https://streamlit.io/)

### Hardware initially built on:
Processor: 11th Gen Intel(R) Core(TM) i7-1165G7 @2.80Ghz, 2803 Mhz, 4 Core(s), 8 Logical Processor(s)

Memory (RAM): 16GB 

## Local setup
### Obtain the repo locally and open its root folder
#### To potentially contribute
git clone https://github.com/pkiage/tool-credit-risk-modelling.git

or

gh repo clone pkiage/tool-credit-risk-modelling

#### Just to deploy locally
Download ZIP

### (optional) Setup virtual environment:
python -m venv venv

### (optional) Activate virtual environment:
#### If using Unix based OS run the following in terminal:  
.\venv\bin\activate

#### If using Windows run the following in terminal:
.\venv\Scripts\activate

### Install requirements by running the following in terminal:
#### Required packages
pip install -r requirements.txt

#### Complete graphviz installation
https://graphviz.org/download/ 

## Build and install local package
```shell
python setup.py build
```

```shell
python setup.py install
```

### Run the streamlit app (app.py) by running the following in terminal:

streamlit run app.py

## Deployed setup details
For faster model building and testing (particularly XGBoost) a local setup is recommended.

Free Heroku dyno type was used to deploy the app
https://devcenter.heroku.com/articles/dyno-types


Memory (RAM): 512 MB

CPU Share: 1x

Compute: 1x-4x 

Dedicated: no

Sleeps: yes

# Roadmap
Models:
- [ ] Add LightGBM
- [ ] Add Adabost
- [ ] Add Random Forest

Visualization:
- [ ] Add decision surface plot(s)

Documentation:
- [x] Add getting started and usage documentation
- [ ] Add documentation evaluating models
- [ ] Add design rationale(s)

Other:
- [x] Deploy app
- [ ] Add csv file data input
- [ ] Add tests
- [ ] Add test/code coverage badge
- [ ] Add continuous integration badge



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

## Political, Economic, Social, Technological, Legal and Environmental(PESTLE):

[Europe fit for the Digital Age: Commission proposes new rules and actions for excellence and trust in Artificial Intelligence](https://ec.europa.eu/commission/presscorner/detail/en/ip_21_1682)

[LAYING DOWN HARMONISED RULES ON ARTIFICIAL INTELLIGENCE (ARTIFICIAL INTELLIGENCE ACT) AND AMENDING CERTAIN UNION LEGISLATIVE ACTS](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:52021PC0206&from=EN)

> "(37) Another area in which the use of AI systems deserves special consideration is the access to and enjoyment of certain essential private and public services and benefits necessary for people to fully participate in society or to improve one’s standard of living. In particular, AI systems used to evaluate the credit score or creditworthiness of natural persons should be classified as high-risk AI systems, since they determine those persons’ access to financial resources or essential services such as housing, electricity, and telecommunication services. AI systems used for this purpose may lead to discrimination of persons or groups and perpetuate historical patterns of discrimination, for example based on racial or ethnic origins, disabilities, age, sexual orientation, or create new forms of discriminatory impacts. Considering the very limited scale of the impact and the available alternatives on the market, it is appropriate to exempt AI systems for the purpose of creditworthiness assessment and credit scoring when put into service by small-scale providers for their own use. Natural persons applying for or receiving public assistance benefits and services from public authorities are typically dependent on those benefits and services and in a vulnerable position in relation to the responsible authorities. If AI systems are used for determining whether such benefits and services should be denied, reduced, revoked or reclaimed by authorities, they may have a significant impact on persons’ livelihood and may infringe their fundamental rights, such as the right to social protection, non-discrimination, human dignity or an effective remedy. Those systems should therefore be classified as high-risk. Nonetheless, this Regulation should not hamper the development and use of innovative approaches in the public administration, which would stand to benefit from a wider use of compliant and safe AI systems, provided that those systems do not entail a high risk to legal and natural persons."

[Europe fit for the Digital Age: Commission proposes new rules and actions for excellence and trust in Artificial Intelligence](https://ec.europa.eu/commission/presscorner/detail/en/ip_21_1682)
> "High-risk AI systems will be subject to strict obligations before they can be put on the market:
>* Adequate risk assessment and mitigation systems;
>* High quality of the datasets feeding the system to minimise risks and discriminatory outcomes;
>* Logging of activity to ensure traceability of results;
>* Detailed documentation providing all information necessary on the system and its purpose for authorities to assess its compliance;
>* Clear and adequate information to the user;
>* Appropriate human oversight measures to minimise risk;
>* High level of robustness, security and accuracy."


# Docs creation
## [pydeps](https://github.com/thebjorn/pydeps) Python module depenency visualization

```shell
pydeps src --max-bacon=3 --cluster --max-cluster-size=3  --rankdir BT -o docs/module-dependency-graph/src.svg 
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
