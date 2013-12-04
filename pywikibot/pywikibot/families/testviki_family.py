__author__ = 'raigo'

# -*- coding: utf-8  -*-
from pywikibot.pywikibot import family, config2 as config
import urllib
import pywikibot.pywikibot.families.family
# TestViki family
class TestvikiFamily(family.Family):
   def __init__(self):
       family.Family.__init__(self)
       self.name = 'testviki'
       self.langs = {
           'et': 'localhost',
          }
