import numpy

from analyse import tuplelib, numpylib


__author__ = 'raigo'

GOOD_PAGE = 1
AVERAGE_PAGE = -1


def predicted_label(train_result, page):
    return GOOD_PAGE if numpylib.prepare_x(numpy.array([tuplelib.page_features_(page)]), train_result.mean,
                                           train_result.std).dot(
        train_result.weights.T) > 0 else AVERAGE_PAGE


def predictions_wrong(train_result, test_models):
    test_result = (predicted_label(train_result, model) for model in test_models)
    wrong_predictions = 0

    for model_, label in zip(test_models, test_result):
        if model_.target != label:
            wrong_predictions += 1

    return wrong_predictions


def len_(iterator):
    length = 0
    for _ in iterator:
        length += 1
    return length