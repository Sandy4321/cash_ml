import os
import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path

os.environ['is_test_suite'] = 'True'

from cash_ml import Predictor

import dill
from nose.tools import assert_equal, assert_not_equal, with_setup
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import tests.utils_testing as utils


def test_predict_uncertainty_true():
    np.random.seed(0)

    df_boston_train, df_boston_test = utils.get_boston_regression_dataset()

    column_descriptions = {'MEDV': 'output', 'CHAS': 'categorical'}

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train, predict_intervals=True)

    intervals = ml_predictor.predict_intervals(df_boston_test)

    assert isinstance(intervals, pd.DataFrame)
    assert intervals.shape[0] == df_boston_test.shape[0]

    result_list = ml_predictor.predict_intervals(df_boston_test, return_type='list')

    assert isinstance(result_list, list)
    assert len(result_list) == df_boston_test.shape[0]
    for idx, row in enumerate(result_list):
        assert isinstance(row, list)
        assert len(row) == 3

    singles = df_boston_test.head().to_dict('records')

    for row in singles:
        result = ml_predictor.predict_intervals(row)
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert 'interval_0.05' in result
        assert 'interval_0.95' in result

    for row in singles:
        result = ml_predictor.predict_intervals(row, return_type='list')
        assert isinstance(result, list)
        assert len(result) == 3

    df_intervals = ml_predictor.predict_intervals(df_boston_test, return_type='df')
    assert isinstance(df_intervals, pd.DataFrame)

    try:
        ml_predictor.predict_intervals(df_boston_test, return_type='this will not work')
        assert False
    except ValueError:
        assert True


def test_prediction_intervals_actually_work():
    np.random.seed(0)

    df_boston_train, df_boston_test = utils.get_boston_regression_dataset()

    column_descriptions = {'MEDV': 'output', 'CHAS': 'categorical'}

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train, predict_intervals=[0.05, 0.95])

    df_boston_test = df_boston_test.reset_index(drop=True)
    intervals = ml_predictor.predict_intervals(df_boston_test)
    actuals = df_boston_test.MEDV

    count_under = 0
    count_over = 0
    # print(intervals)
    for idx, row in intervals.iterrows():
        actual = actuals.iloc[idx]

        if actual < row['interval_0.05']:
            count_under += 1
        if actual > row['interval_0.95']:
            count_over += 1

    len_intervals = len(intervals)

    pct_under = count_under * 1.0 / len_intervals
    pct_over = count_over * 1.0 / len_intervals
    # There's a decent bit of noise since this is such a small dataset
    assert pct_under < 0.2
    assert pct_over < 0.1


def test_prediction_intervals_lets_the_user_specify_number_of_intervals():
    np.random.seed(0)

    df_boston_train, df_boston_test = utils.get_boston_regression_dataset()

    column_descriptions = {'MEDV': 'output', 'CHAS': 'categorical'}

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train, predict_intervals=True, prediction_intervals=[.2])

    intervals = ml_predictor.predict_intervals(df_boston_test, return_type='list')

    assert len(intervals[0]) == 2


def test_predict_intervals_should_fail_if_not_trained():
    np.random.seed(0)

    df_boston_train, df_boston_test = utils.get_boston_regression_dataset()

    column_descriptions = {'MEDV': 'output', 'CHAS': 'categorical'}

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train)

    try:
        intervals = ml_predictor.predict_intervals(df_boston_test)
        assert False
    except ValueError:
        assert True


def test_predict_intervals_takes_in_custom_intervals():
    np.random.seed(0)

    df_boston_train, df_boston_test = utils.get_boston_regression_dataset()

    column_descriptions = {'MEDV': 'output', 'CHAS': 'categorical'}

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    # df_boston_train = pd.concat([df_boston_train, df_boston_train, df_boston_train])

    ml_predictor.train(df_boston_train, predict_intervals=[0.4, 0.6])

    custom_intervals = ml_predictor.predict_intervals(df_boston_test, return_type='list')

    assert isinstance(custom_intervals, list)

    singles = df_boston_test.head().to_dict('records')

    acceptable_keys = set(['prediction', 'interval_0.4', 'interval_0.6'])
    for row in singles:
        result = ml_predictor.predict_intervals(row)
        assert isinstance(result, dict)
        assert 'prediction' in result
        assert 'interval_0.4' in result
        assert 'interval_0.6' in result
        for key in result.keys():
            assert key in acceptable_keys

    for row in singles:
        result = ml_predictor.predict_intervals(row, return_type='list')
        assert isinstance(result, list)
        assert len(result) == 3

    df_intervals = ml_predictor.predict_intervals(df_boston_test, return_type='df')
    assert df_intervals.shape[0] == df_boston_test.shape[0]
    assert isinstance(df_intervals, pd.DataFrame)

    # Now make sure that the interval values are actually different
    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train, predict_intervals=True)

    default_intervals = ml_predictor.predict_intervals(df_boston_test, return_type='list')

    # This is a super flaky test, because we've got such a small datasize, and we're trying to get distributions from it
    len_intervals = len(custom_intervals)
    num_failures = 0
    for idx, custom_row in enumerate(custom_intervals):
        default_row = default_intervals[idx]

        if custom_row[1] <= default_row[1]:
            num_failures += 1
            print('{} should be higher than {}'.format(custom_row[1], default_row[1]))
        if custom_row[2] >= default_row[2]:
            print('{} should be lower than {}'.format(custom_row[1], default_row[1]))
            num_failures += 1

    assert num_failures < 0.18 * len_intervals
