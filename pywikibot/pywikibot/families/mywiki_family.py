__author__ = 'raigo'

# -*- coding: utf-8  -*-
from pywikibot.pywikibot import family, config2 as config
import urllib
import pywikibot.pywikibot.families.family


class MyWikiFamily(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'mywiki'
        self.langs = {
            'et': 'localhost',
        }
