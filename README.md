[![Build Status](https://travis-ci.org/jesse-toftum/cash_ml.svg?branch=master)](https://travis-ci.org/jesse-toftum/cash_ml)
[![Coverage Status](https://coveralls.io/repos/github/jesse-toftum/cash_ml/badge.svg?branch=master)](https://coveralls.io/github/jesse-toftum/cash_ml?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/98db6f1ed2d1fdbe1f91/maintainability)](https://codeclimate.com/github/jesse-toftum/cash_ml/maintainability)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d78d22630479478b8d8d26a89481d996)](https://app.codacy.com/app/jesse-toftum/cash_ml?utm_source=github.com&utm_medium=referral&utm_content=jesse-toftum/cash_ml&utm_campaign=Badge_Grade_Dashboard)


<!-- Stars badge?! -->

## Installation

Coming soon™
- `pip install cash_ml`

## Getting started

```python
from cash_ml import Predictor
from cash_ml.utils import get_boston_dataset

df_train, df_test = get_boston_dataset()

column_descriptions = {
    'MEDV': 'output',
    'CHAS': 'categorical'
}

ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

ml_predictor.train(df_train)

ml_predictor.score(df_test, df_test.MEDV)
```

## Show off some more features!

cash_ml is designed for production. Here's an example that includes serializing and loading the trained model, then getting predictions on single dictionaries, roughly the process you'd likely follow to deploy the trained model.

```python
from cash_ml import Predictor
from cash_ml.utils import get_boston_dataset
from cash_ml.utils_models import load_ml_model

# Load data
df_train, df_test = get_boston_dataset()

# Tell cash_ml which column is 'output'
# Also note columns that aren't purely numerical
# Examples include ['nlp', 'date', 'categorical', 'ignore']
column_descriptions = {
  'MEDV': 'output'
  , 'CHAS': 'categorical'
}

ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

ml_predictor.train(df_train)

# Score the model on test data
test_score = ml_predictor.score(df_test, df_test.MEDV)

# cash_ml is specifically tuned for running in production
# It can get predictions on an individual row (passed in as a dictionary)
# A single prediction like this takes ~1 millisecond
# Here we will demonstrate saving the trained model, and loading it again
file_name = ml_predictor.save()

trained_model = load_ml_model(file_name)

# .predict and .predict_proba take in either:
# A pandas DataFrame
# A list of dictionaries
# A single dictionary (optimized for speed in production evironments)
predictions = trained_model.predict(df_test)
print(predictions)
```

## 3rd Party Packages- Deep Learning with TensorFlow & Keras, XGBoost, LightGBM, CatBoost

cash_ml has all of these awesome libraries integrated!
Generally, just pass one of them in for model_names.
`ml_predictor.train(data, model_names=['DeepLearningClassifier'])`

Available options are
- `DeepLearningClassifier` and `DeepLearningRegressor`
- `XGBClassifier` and `XGBRegressor`
- `LGBMClassifier` and `LGBMRegressor`
- `CatBoostClassifier` and `CatBoostRegressor`

All of these projects are ready for production. These projects all have prediction time in the 1 millisecond range for a single prediction, and are able to be serialized to disk and loaded into a new environment after training.

Depending on your machine, they can occasionally be difficult to install, so they are not included in cash_ml's default installation. You are responsible for installing them yourself. cash_ml will run fine without them installed (we check what's installed before choosing which algorithm to use).


## Feature Responses
Get linear-model-esque interpretations from non-linear models. Currently the docs do not yet exist for this fork :(


## Classification

Binary and multiclass classification are both supported. Note that for now, labels must be integers (0 and 1 for binary classification). cash_ml will automatically detect if it is a binary or multiclass classification problem - you just have to pass in `ml_predictor = Predictor(type_of_estimator='classifier', column_descriptions=column_descriptions)`


## Feature Learning

Also known as "finally found a way to make this deep learning stuff useful for my business". Deep Learning is great at learning important features from your data. But the way it turns these learned features into a final prediction is relatively basic. Gradient boosting is great at turning features into accurate predictions, but it doesn't do any feature learning.

In cash_ml, you can now automatically use both types of models for what they're great at. If you pass `feature_learning=True, fl_data=some_dataframe` to `.train()`, we will do exactly that: train a deep learning model on your `fl_data`. We won't ask it for predictions (standard stacking approach), instead, we'll use it's penultimate layer to get it's 10 most useful features. Then we'll train a gradient boosted model (or any other model of your choice) on those features plus all the original features.

Across some problems, we've witnessed this lead to a 5% gain in accuracy, while still making predictions in 1-4 milliseconds, depending on model complexity.

`ml_predictor.train(df_train, feature_learning=True, fl_data=df_fl_data)`

This feature only supports regression and binary classification currently. The rest of cash_ml supports multiclass classification.

## Categorical Ensembling

Ever wanted to train one market for every store/customer, but didn't want to maintain hundreds of thousands of independent models? With `ml_predictor.train_categorical_ensemble()`, we will handle that for you. You'll still have just one consistent API, `ml_predictor.predict(data)`, but behind this single API will be one model for each category you included in your training data.

Just tell us which column holds the category you want to split on, and we'll handle the rest. As always, saving the model, loading it in a different environment, and getting speedy predictions live in production is baked right in.

`ml_predictor.train_categorical_ensemble(df_train, categorical_column='store_name')`


### More details available in the docs

Currently the docs do not yet exist for this fork :(


### Advice

Before you go any further, try running the code. Load up some data (either a DataFrame, or a list of dictionaries, where each dictionary is a row of data). Make a `column_descriptions` dictionary that tells us which attribute name in each row represents the value we're trying to predict. Pass all that into `cash_ml`, and see what happens!

Everything else in these docs assumes you have done at least the above. Start there and everything else will build on top. But this part gets you the output you're probably interested in, without unnecessary complexity.


## What this project does

Automates the whole machine learning process, making it super easy to use for both analytics, and getting real-time predictions in production.

A quick overview of buzzwords, this project automates:

- Analytics (pass in data, and cash_ml will tell you the relationship of each variable to what it is you're trying to predict).
- Feature Engineering (particularly around dates, and NLP).
- Robust Scaling (turning all values into their scaled versions between the range of 0 and 1, in a way that is robust to outliers, and works with sparse data).
- Feature Selection (picking only the features that actually prove useful).
- Data formatting (turning a DataFrame or a list of dictionaries into a sparse matrix, one-hot encoding categorical variables, taking the natural log of y for regression problems, etc).
- Model Selection (which model works best for your problem- we try roughly a dozen apiece for classification and regression problems, including favorites like XGBoost if it's installed on your machine).
- Hyperparameter Optimization (what hyperparameters work best for that model).
- Big Data (feed it lots of data- it's fairly efficient with resources).
- Unicorns (you could conceivably train it to predict what is a unicorn and what is not).
- Ice Cream (mmm, tasty...).
- Hugs (this makes it much easier to do your job, hopefully leaving you more time to hug those those you care about).


### Running the tests

If you've cloned the source code and are making any changes (highly encouraged!), or just want to make sure everything works in your environment, run
`nosetests -v tests`.

CI is also set up, so if you're developing on this, you can just open a PR, and the tests will run automatically on Travis-CI.

The tests are relatively comprehensive, though as with everything with cash_ml, I happily welcome your contributions here!
