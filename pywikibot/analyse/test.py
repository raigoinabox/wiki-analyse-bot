__author__ = 'raigo'

import unittest

import analyser
import model


class MockPage(model.PageModel):
    def __init__(self, parameters, target=None):
        model.PageModel.__init__(self, None, target=target)
        self.parameters = parameters

    def get_scikit_format(self):
        return self.parameters


class TestTraining(unittest.TestCase):
    def setUp(self):
        self.train_list = (MockPage((100,), analyser.Label.GOOD),
                           MockPage((1,), analyser.Label.BAD))
        self.predict_list = ((MockPage((101,)), MockPage((2,)), MockPage((102,)), MockPage((103,))),
                             (analyser.Label.GOOD, analyser.Label.BAD, analyser.Label.GOOD, analyser.Label.GOOD))

    def test_training(self):
        analyser.train(self.train_list)

        prediction = analyser.predict_list(self.predict_list[0])
        self.assertEqual(self.predict_list[1], tuple(prediction))


if __name__ == "__main__":
    unittest.main()