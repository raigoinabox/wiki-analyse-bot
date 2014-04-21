import collections

from analyse import numberlib


__author__ = 'raigo'

# self.page = pywikibot.Page(pywikibot.Link(self.page))
PageModel = collections.namedtuple("PageModel", ["page", "target"])



def good(page):
    return PageModel(page, numberlib.GOOD_PAGE)


def average(page):
    return PageModel(page, numberlib.AVERAGE_PAGE)