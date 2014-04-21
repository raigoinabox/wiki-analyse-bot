from analyse import numberlib

__author__ = 'raigo'


def page_features(page):
    return (1, ) + page_features(page)


def page_features_(page):
    return (len(page.get()),
            numberlib.len_(page.getReferences()),
            numberlib.len_(page.linkedPages()),
            numberlib.len_(page.imagelinks()),
            numberlib.len_(page.extlinks()),
            len(page.templates()),
            numberlib.len_(page.categories()))