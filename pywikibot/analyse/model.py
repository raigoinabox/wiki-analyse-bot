__author__ = 'raigo'

import pywikibot
import analyser


class PageModel():
    def __init__(self, page, target=None, html_text=""):
        self.page = page
        self._target = target

    def get_scikit_format(self):
        return (1,) + self.get_features()

    def get_features(self):
        return (len(self.page.get()),
                get_len(self.page.getReferences()),
                get_len(self.page.linkedPages()),
                get_len(self.page.imagelinks()),
                get_len(self.page.extlinks()),
                len(self.page.templates()),
                get_len(self.page.categories()))

    @property
    def target(self):
        if self._target is None:
            self._target = analyser.predict(self)
        return self._target

    def __str__(self):
        return str(self.page)

    def __getstate__(self):
        mydict = self.__dict__.copy()
        mydict["page"] = self.page.title()
        return mydict

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.page = pywikibot.Page(pywikibot.Link(self.page))


def get_len(iterator):
    length = 0
    for _ in iterator:
        length += 1
    return length
