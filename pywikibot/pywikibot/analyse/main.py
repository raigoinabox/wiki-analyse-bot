#!/usr/bin/python
# -*- coding: utf-8  -*-
import random

import pywikibot
from pywikibot import pagegenerators

import analyser
from analyser import PageData
import config


__author__ = 'raigo'


def main():
    gen_factory = pagegenerators.GeneratorFactory()
    page_title_parts = []
    train_arg = False
    crawl = False

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith("-train"):
            train_arg = True
        elif arg.startswith("-crawl"):
            crawl = True
        # check if a standard argument like
        # -start:XYZ or -ref:Asdf was given.
        elif not gen_factory.handleArg(arg):
            page_title_parts.append(arg)
    site = pywikibot.Site()
    site.login()

    if train_arg:
        train(site)
    elif crawl:
        # Spider ability to analyze the whole wiki
        for page in site.allpages():
            print page
    elif page_title_parts:
        # We will only work on a single page.
        pageTitle = ' '.join(page_title_parts)
        page = pywikibot.Page(pywikibot.Link(pageTitle, site))
        gen = iter([page])

        if not gen:
            gen = gen_factory.getCombinedGenerator()

        if gen:
            # The preloading generator is responsible for downloading multiple
            # pages from the wiki simultaneously.
            gen = pagegenerators.PreloadingGenerator(gen)
        else:
            pywikibot.showHelp()


def train(site):
    training_data = []
    for title, class_ in config.TRAIN_DATA:
        page = get_page(title, site)
        training_data.append(PageData(page, load_text(page), class_))

    random.shuffle(training_data)

    train_size = (len(training_data) * 7) / 10

    analyser.train(training_data[:train_size])
    pywikibot.output("Training result: " + str(analyser.predict(site, training_data[train_size:])))


def get_page(title, site):
    return pywikibot.Page(pywikibot.Link(title, site))


def load_text(page):
    """
    Loads the text of the given page.
    """
    try:
        # Load the page
        text = page.get()
    except pywikibot.NoPage:
        pywikibot.output(u"Page %s does not exist; skipping."
                         % page.title(asLink=True))
    except pywikibot.IsRedirectPage:
        pywikibot.output(u"Page %s is a redirect; skipping."
                         % page.title(asLink=True))
    else:
        return text
    return None


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
