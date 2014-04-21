#!/usr/bin/env python
# -*- coding: utf-8  -*-

import time

import pywikibot
from analyse import voidlib


__author__ = 'raigo'


def main(args):
    site = pywikibot.Site()
    site.login()

    actions = {"train": voidlib.train,
               "find": voidlib.crawl}

    args = [arg for arg in pywikibot.handleArgs()]

    try:
        actions[args[0]](site, args[1:])
    except KeyError:
        pywikibot.showHelp()


if __name__ == "__main__":
    try:
        start = time.clock()
        main(pywikibot.handleArgs())
        pywikibot.output("Run time: " + str(time.clock() - start) + " seconds")
    finally:
        pywikibot.stopme()
