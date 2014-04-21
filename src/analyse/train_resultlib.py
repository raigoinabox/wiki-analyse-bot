import collections

import numpy

from analyse import tuplelib, numpylib


__author__ = 'raigo'

TrainResult = collections.namedtuple("TrainResult", ["weights", "mean", "std"])


def train_result(model_list):
    x = [tuplelib.page_features_(model.page) for model in model_list]

    mean = numpy.mean(x, axis=0)
    std = numpy.std(x, axis=0)

    iteration = numpylib.gradient_descent(numpylib.prepare_x(numpy.array(x), mean, std),
                                          numpy.array([model.target for model in model_list]))

    print('Number of iterations while training: {:}'.format(iteration.shape[0]))

    return TrainResult(iteration[-1], mean, std)
