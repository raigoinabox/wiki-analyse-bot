import numpy

__author__ = 'raigo'


def prepare_x(x, mean, std):
    normalised = numpy.divide(numpy.subtract(x, mean), std)
    return numpy.hstack((numpy.ones((normalised.shape[0], 1)), normalised))


def gradient_descent(z, y, w_h=None, eta=0.5, max_iterations=10000, epsilon=0.001):
    if w_h is None:
        w_h = numpy.array([0.0 for i in range(z.shape[1])])

    # save a history of the weight vectors into an array
    w_h_i = [numpy.copy(w_h)]

    for i in range(max_iterations):
        subset_indices = range(z.shape[0])
        # subset_indices = np.random.permutation(z.shape[0])[:N/8] # uncomment for stochastic gradient descent

        grad_E_in = numpy.mean(numpy.tile(- y[subset_indices] /
                                          ( 1.0 + numpy.exp(y[subset_indices] * w_h.dot(z[subset_indices].T)) ),
                                          (z.shape[1], 1)).T *
                               z[subset_indices], axis=0)

        w_h -= eta * grad_E_in
        w_h_i.append(numpy.copy(w_h))

        if numpy.linalg.norm(grad_E_in) <= numpy.linalg.norm(w_h) * epsilon:
            break
    else:
        raise Exception("Hit max iterations")

    return numpy.array(w_h_i)