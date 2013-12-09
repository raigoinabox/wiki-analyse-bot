import pickle
import numpy as np

import config


class TrainResult:
    def __init__(self, weights, mean, std):
        self.weights = weights
        self.mean = mean
        self.std = std


def predict_list(page_list):
    return (predict(page) for page in page_list)


def predict(page):
    global train_result
    if train_result is None:
        with open(config.TRAINING_DATA_FILE) as f:
            train_result = pickle.load(f)

    mean = train_result.mean
    std = train_result.std
    weights = train_result.weights
    x = normalise(np.array([page.get_scikit_format()]), mean, std)
    result = x.dot(weights.T)
    if result > 0:
        return 1
    else:
        return -1


def train(page_list):
    global train_result

    x = []
    y = []
    for page in page_list:
        x.append(page.get_scikit_format())
        y.append(page.target)

    numpy_x = np.array(x)
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    x_matrix = normalise(numpy_x, mean, std)
    y_matrix = np.array(y)

    iteration = gradient_descent(x_matrix, y_matrix)
    print('Number of iterations while training: {:}'.format(iteration.shape[0]))

    weights = iteration[-1]
    train_result = TrainResult(weights, mean, std)
    with open(config.TRAINING_DATA_FILE, "w")as f:
        pickle.dump(train_result, f)


def normalise(x, mean, std):
    subtracted = np.subtract(x, mean)
    result = np.divide(subtracted, std)
    return result


def gradient_descent(z, y, w_h=None, eta=0.5, max_iterations=10000, epsilon=0.001):
    if w_h == None:
        w_h = np.array([0.0 for i in range(z.shape[1])])

    # save a history of the weight vectors into an array
    w_h_i = [np.copy(w_h)]

    for i in range(max_iterations):
        subset_indices = range(z.shape[0])
        # subset_indices = np.random.permutation(z.shape[0])[:N/8] # uncomment for stochastic gradient descent

        grad_E_in = np.mean(np.tile(- y[subset_indices] /
                                    ( 1.0 + np.exp(y[subset_indices] * w_h.dot(z[subset_indices].T)) ),
                                    (z.shape[1], 1)).T *
                            z[subset_indices], axis=0)

        w_h -= eta * grad_E_in
        w_h_i.append(np.copy(w_h))

        if np.linalg.norm(grad_E_in) <= np.linalg.norm(w_h) * epsilon:
            break

    return np.array(w_h_i)

