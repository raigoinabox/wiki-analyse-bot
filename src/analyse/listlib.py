# -*- coding: utf-8  -*-

from analyse import generatorlib, modellib
from pywikibot import pagegenerators, catlib

__author__ = 'raigo'


def training_models(site):
    meta_articles = (u"Vikipeedia:Hea artikli nõuded",
                     u"Vikipeedia:Head artiklid",
                     u"Vikipeedia:Heade artiklite kandidaadid",
                     u"Vikipeedia:Heade artiklite kandidaadid/Inimesed",
                     u"Vikipeedia:Heade artiklite kandidaadid/Loodus",
                     u"Mall:Head artiklid")

    model_list = [modellib.good(page) for page in
                  pagegenerators.CategorizedPageGenerator(catlib.Category(site, title=u"Kategooria:Head_artiklid"),
                                                          content=True) if page.title() not in meta_articles]

    return model_list + [modellib.average(page) for page in
                         generatorlib.random_pages(site, len(model_list))]