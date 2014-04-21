from pywikibot import pagegenerators

__author__ = 'raigo'


def random_pages(site, number):
    page_count = 0
    while page_count < number:
        gen = pagegenerators.RandomPageGenerator(number=number - page_count, site=site)
        for page in gen:
            page_count += 1
            yield page