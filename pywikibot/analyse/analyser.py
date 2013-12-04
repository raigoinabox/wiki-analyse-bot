#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import math

from sklearn import svm

import config

__author__ = 'raigo'

clf = None
g_beta = None


class Population:
    def __init__(self, label_count, labels=None):
        self.n = 0
        self.y = (label_count - 1) * [0]
        self.pi = (label_count - 1) * [0]
        self.labels = labels

    def add_page(self, result):
        self.n += 1
        if result == config.Classification.GOOD:
            self.y[0] += 1


class Label:
    COUNT = 2
    LIST = range(COUNT)

    GOOD, BAD = LIST
    BASE = BAD

    def __init__(self, label, beta_vec=None):
        self.label = label
        self.beta = beta_vec


def predict(page):
    global g_beta
    if g_beta is None:
        with open(config.TRAINING_DATA_FILE) as f:
            g_beta = pickle.load(f)

    x_vec = (1,) + page.get_scikit_format()

    best_likelihood = 0
    best_label = Label.BASE

    for label in g_beta:
        likelihood = 0
        for beta, x in zip(label.beta, x_vec):
            likelihood += beta * x

        if likelihood > best_likelihood:
            best_likelihood = likelihood
            best_label = label

    return best_label


def predict_list(page_list):
    return (predict(page) for page in page_list)


def train(data_list):
    global g_beta

    max_beta = [1000000000, 1000000000, 1000000000, 1000000000]

    pop_dict = {}
    features = None

    for page in data_list:
        x_item = (1,) + page.get_scikit_format()

        if x_item not in pop_dict:
            pop_dict[x_item] = Population(Label.COUNT, labels=[Label(page.target)])

        pop_dict[x_item].add_page(page.target)
        features = len(x_item) - 1

    beta = log_regression(Label.COUNT, features, max_beta, pop_dict.items())

    g_beta = []
    for i in range(Label.COUNT - 1):
        tmp = []
        for j in range(features):
            tmp.append(beta[i * (features + 1) + j])

        g_beta.append(Label(i, beta_vec=tmp))

    with open(config.TRAINING_DATA_FILE, "w") as f:
        pickle.dump(g_beta, f)


def log_regression(J, K, xrange, pop_items):
    eps = 1e-8
    beta_len = (K + 1) * (J - 1)
    beta = [0 for _ in range(beta_len)]
    beta_inf = [0 for _ in range(beta_len)]
    xtwx = [[0 for _ in range(beta_len)] for _ in range(beta_len)]

    loglike = 0
    iter = 0
    max_iter = 30
    converged = False
    while iter < max_iter and not converged:
        beta_old = beta[:]

        loglike_old = loglike
        loglike = ln_likelihood(K, beta, J, pop_items)
        beta = newton_raphson(J, K, beta, xtwx, pop_items)

        if loglike < loglike_old and iter > 0:
            raise NotImplementedError("Backtracking")

        for k in range(beta_len):
            if beta_inf[k] != 0:
                beta[k] = beta_inf[k]
            elif (math.fabs(beta[k]) > (5 / xrange[k])) and (math.sqrt(xtwx[k][k]) >= (3 * math.fabs(beta[k]))):
                beta_inf[k] = beta[k]

        converged = True
        for k in range(beta_len):
            if math.fabs(beta[k] - beta_old[k]) > eps * math.fabs(beta_old[k]):
                converged = False
                break

        iter += 1

    return beta


def ln_likelihood(K, beta, label_count, pop_items):
    numer = [0 for _ in range(label_count - 1)]

    loglike = 0.0
    for x_row, result in pop_items:
        loglike += row_likelihood(K, beta, label_count, numer, result, x_row)

    return loglike


def row_likelihood(K, beta, label_count, numer, result, x_row):
    denom = 1
    for j in range(label_count - 1):
        tmp1 = 0
        for k in range(K + 1):
            tmp1 += x_row[k] * beta[j * (K + 1) + k]
        numer[j] = math.exp(tmp1)
        denom += numer[j]
    for j in range(label_count - 1):
        result.pi[j] = numer[j] / denom
    row_like = math.lgamma(result.n + 1)

    tmp1 = 0
    tmp2 = 0
    for j in range(label_count - 1):
        tmp1 += result.y[j]
        tmp2 += result.pi[j]
        row_like += -math.lgamma(result.y[j] + 1) + result.y[j] * math.log(result.pi[j])
    row_like += -math.lgamma(result.n - tmp1 + 1) + (result.n - tmp1) * math.log(1 - tmp2)

    return row_like


def newton_raphson(label_count, K, beta, xtwx, pop_items):
    beta_len = len(beta)

    beta_tmp, xtwx_tmp = derivatives(K, label_count, beta_len, pop_items)

    for k in range(beta_len):
        tmp1 = 0
        for j in range(beta_len):
            tmp1 += xtwx_tmp[k][j] * beta[j]

        beta_tmp[k] += tmp1

    new_beta = beta[:]
    for k in range(beta_len):
        tmp1 = 0
        for j in range(beta_len):
            tmp1 += xtwx[k][j] * beta_tmp[j]

        new_beta[k] = tmp1

    return new_beta


def derivatives(K, classes, beta_len, pop_items):
    beta_tmp = [0 for _ in range(beta_len)]
    xtwx_tmp = [[0 for _ in range(beta_len)] for _ in range(beta_len)]

    for pop, result in pop_items:
        jj = 0
        for j in range(classes - 1):
            tmp1 = result.y[j] - result.n * result.pi[j]
            w1 = result.n * result.pi[j] * (1 - result.pi[j])
            for k in range(K + 1):
                beta_tmp[jj] += tmp1 * pop[k]
                kk = jj - 1
                for kprime in range(k, K + 1):
                    kk += 1
                    xtwx_tmp[jj][kk] += w1 * pop[k] * pop[kprime]
                    xtwx_tmp[kk][jj] = xtwx_tmp[jj][kk]

                for jprime in range(j + 1, classes - 1):
                    w2 = -result.n * result.pi[j] * result.pi[jprime]
                    for kprime in range(K + 1):
                        kk += 1
                        xtwx_tmp[jj][kk] += w2 * pop[k] * pop[kprime]
                        xtwx_tmp[kk][jj] = xtwx_tmp[jj][kk]

                jj += 1

    return beta_tmp, xtwx_tmp