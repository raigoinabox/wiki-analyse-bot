#!/usr/bin/python -m
# -*- coding: utf-8  -*-

import pickle
import random
import time

import pywikibot
from pywikibot import pagegenerators
from pywikibot import catlib

from model import PageModel
import config
import analyser

__author__ = 'raigo'


def main():
    actions = {"train": train,
               "find": crawl,
               "analyse": analyse_page}
    gen_factory = pagegenerators.GeneratorFactory()
    args = []

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if not gen_factory.handleArg(arg):
            args.append(arg)

    site = pywikibot.Site()
    site.login()

    try:
        actions[args[0]](site, args[1:])
    except KeyError:
        pywikibot.showHelp()


def train(site, _=None):
    def get_pages():
        def get_random_page_gen(number):
            page_count = 0
            while page_count < number:
                gen = pagegenerators.RandomPageGenerator(number=number - page_count, site=site)
                for page in gen:
                    page_count += 1
                    yield page

        model_list = []
        cat = catlib.Category(site, title=u"Kategooria:Head_artiklid")
        gen = pagegenerators.CategorizedPageGenerator(cat, content=True)

        not_good_articles = (u"Vikipeedia:Hea artikli nõuded",
                             u"Vikipeedia:Head artiklid",
                             u"Vikipeedia:Heade artiklite kandidaadid",
                             u"Vikipeedia:Heade artiklite kandidaadid/Inimesed",
                             u"Vikipeedia:Heade artiklite kandidaadid/Loodus",
                             u"Mall:Head artiklid")
        for page in gen:
            if page.title() not in not_good_articles:
                model_list.append(PageModel(page, target=config.Classification.GOOD))

        # Random pages/Bad pages
        good_pages_size = len(model_list)
        gen = get_random_page_gen(good_pages_size)

        for page in gen:
            model_list.append(PageModel(page, target=config.Classification.BAD))
        return model_list

    def train_pages(page_list):
        analyser.train(page_list)

    def predict_pages(test_data):
        test_result = analyser.predict_list(test_data)
        wrong_predictions = 0

        for model_, label in zip(test_data, test_result):
            if model_.target != label:
                wrong_predictions += 1

        return wrong_predictions

    training_data = get_pages()

    random.shuffle(training_data)

    data_size = len(training_data)
    train_size = (data_size * 7) / 10

    train_pages(training_data[:train_size])

    miss_count = predict_pages(training_data[train_size:])

    pywikibot.output("Predictions wrong: " + str(miss_count) + "/" +
                     str(data_size - train_size), toStdout=True)


def crawl(site, rest):
    find_targets = {"good": config.Classification.GOOD,
                    "bad": config.Classification.BAD}

    find_target = find_targets[rest[0]]

    good_pages = []
    for page in site.allpages():
        try:
            model = PageModel(page)
            if model.target == find_target:
                good_pages.append(model)
        except pywikibot.PageRelatedError as e:
            pywikibot.output((e.message + "; skipping.") % page.title(asLink=True))

    with open("good_pages.pkl", "w") as f:
        pickle.dump(good_pages, f)


def analyse_page(site, rest):
    raise NotImplementedError
    gen_factory = pagegenerators.GeneratorFactory()

    # We will only work on a single page.
    page_title = ' '.join(rest)
    page = pywikibot.Page(pywikibot.Link(page_title, site))
    gen = iter([page])

    if not gen:
        gen = gen_factory.getCombinedGenerator()

    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        pywikibot.showHelp()


if __name__ == "__main__":
    try:
        start = time.clock()
        main()
        pywikibot.output("Run time: " + str(time.clock() - start) + " seconds")
    finally:
        pywikibot.stopme()
