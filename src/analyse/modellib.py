import collections


__author__ = 'raigo'

# self.page = pywikibot.Page(pywikibot.Link(self.page))
PageModel = collections.namedtuple("PageModel", ["page", "target"])

GOOD_PAGE = 1
AVERAGE_PAGE = -1


def good(page):
    return PageModel(page, GOOD_PAGE)


def average(page):
    return PageModel(page, AVERAGE_PAGE)