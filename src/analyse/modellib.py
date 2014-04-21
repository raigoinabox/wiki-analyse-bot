import collections

import numpy

from analyse import numberlib, numpylib, tuplelib


__author__ = 'raigo'

# self.page = pywikibot.Page(pywikibot.Link(self.page))
PageModel = collections.namedtuple("PageModel", ["page", "target"])

GOOD_PAGE = 1
AVERAGE_PAGE = -1


def predictions_wrong(train_result, test_models):
    test_result = (predicted_label(train_result, model) for model in test_models)
    wrong_predictions = 0

    for model_, label in zip(test_models, test_result):
        if model_.target != label:
            wrong_predictions += 1

    return wrong_predictions


def predicted_label(train_result, page):
    return GOOD_PAGE if numpylib.prepare_x(numpy.array([tuplelib.page_features_(page)]), train_result.mean,
                                           train_result.std).dot(
        train_result.weights.T) > 0 else AVERAGE_PAGE


def good(page):
    return PageModel(page, numberlib.GOOD_PAGE)


def average(page):
    return PageModel(page, numberlib.AVERAGE_PAGE)