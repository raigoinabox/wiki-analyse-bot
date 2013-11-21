#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn import svm
from sklearn.externals import joblib

import config


__author__ = 'raigo'


class PageData():
    def __init__(self, page, text, target=None, html_text=""):
        self.letter_count = len(text)
        self.target = target
        #self.images = page.imagelinks()
        #self.linked_pages = page.linkedPages()
        #self.external_links = page.extlinks()
        #self.version_history = page.getVersionHistory()
        #self.contributing_users = page.contributingUsers()
        #self.red_link_count = len(re.findall('<a[^>]+class="new"', html_text))


    def get_scikit_format(self):
        return [self.letter_count]

        #def __str__(self):
        #    return super.__str__(self) + \
        #           str({"letter_count": self.letter_count,
        #                "link_count": get_len(self.linked_pages),
        #                "image_count": get_len(self.images),
        #                "foreign_link_count": get_len(self.external_links),
        #                "red_link_count": self.red_link_count})


#def get_len(iterator):
#    length = 0
#    for _ in iterator:
#        length += 1
#    return length


def predict(site, data_list):
    clf = joblib.load(config.TRAINING_DATA_FILE)

    return [(clf.predict(data.get_scikit_format()), data.target)
            for data in data_list]


def train(data_list):
    train_data_list = []
    target_list = []
    for data in data_list:
        train_data_list.append(data.get_scikit_format())
        target_list.append(data.target)

    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(train_data_list, target_list)
    joblib.dump(clf, config.TRAINING_DATA_FILE)