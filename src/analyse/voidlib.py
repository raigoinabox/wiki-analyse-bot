import pickle
import random

from analyse import listlib, numberlib, train_resultlib, modellib
import pywikibot


__author__ = 'raigo'

TRAINING_DATA_FILE = "train.pkl"
GOOD_PAGES_FILE = "good_pages.pkl"


def train(site, _=None):
    training_data = listlib.training_models(site)

    random.shuffle(training_data)

    data_size = len(training_data)
    train_size = (data_size * 7) / 10

    train_result = train_resultlib.train_result(training_data[:train_size])

    miss_count = numberlib.predictions_wrong(train_result, training_data[train_size:])

    pywikibot.output("Predictions wrong: " + str(miss_count) + "/" +
                     str(data_size - train_size), toStdout=True)
    with open(TRAINING_DATA_FILE, "w")as f:
        pickle.dump(train_result, f)


def find(site, _):
    with open(TRAINING_DATA_FILE) as f:
        train_result = pickle.load(f)

    good_pages = []
    for page in site.allpages():
        try:
            if numberlib.predicted_label(train_result, page) == numberlib.GOOD_PAGE:
                good_pages.append(page.title())
        except pywikibot.PageRelatedError as e:
            pywikibot.warning((e.message + "; skipping.") % page.title(asLink=True))

    with open(GOOD_PAGES_FILE, "w") as f:
        pickle.dump(good_pages, f)

    pywikibot.output(str(good_pages))


# def analyse_page(site, rest):
#     raise NotImplementedError
#     gen_factory = pagegenerators.GeneratorFactory()
#
#     # We will only work on a single page.
#     page_title = ' '.join(rest)
#     page = pywikibot.Page(pywikibot.Link(page_title, site))
#     gen = iter([page])
#
#     if not gen:
#         gen = gen_factory.getCombinedGenerator()
#
#     if gen:
#         # The preloading generator is responsible for downloading multiple
#         # pages from the wiki simultaneously.
#         gen = pagegenerators.PreloadingGenerator(gen)
#     else:
#         pywikibot.showHelp()
