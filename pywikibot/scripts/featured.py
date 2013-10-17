#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

 Task commands:

-featured         use this script for featured articles. Default task if no task
                  command is specified

-good             use this script for good articles.

-lists            use this script for featured lists.

-former           use this script for removing {{Link FA|xx}} from former
                  fearured articles

                  NOTE: you may have all of these commands in one run

 Option commands:

-interactive:     ask before changing each page

-nocache          doesn't include cache files file to remember if the article
                  already was verified.

-nocache:xx,yy    you may ignore language codes xx,yy,... from cache file

-fromlang:xx,yy   xx,yy,zz,.. are the languages to be verified.
-fromlang:ar--fi  Another possible with range the languages
                  (sorry, not implemented yet)

-fromall          to verify all languages.

-tolang:xx,yy     xx,yy,zz,.. are the languages to be updated

-after:zzzz       process pages after and including page zzzz
                  (sorry, not implemented yet)

-side             use -side if you want to move all {{Link FA|lang}} next to the
                  corresponding interwiki links. Default is placing
                  {{Link FA|lang}} on top of the interwiki links.
                  (This option is deprecated with wikidata)

-count            Only counts how many featured/good articles exist
                  on all wikis (given with the "-fromlang" argument) or
                  on several language(s) (when using the "-fromall" argument).
                  Example: featured.py -fromlang:en,he -count
                  counts how many featured articles exist in the en and he
                  wikipedias.
                  (sorry, not implemented yet)

-quiet            no corresponding pages are displayed.

"""
__version__ = '$Id$'

#
# (C) Maxim Razin, 2005
# (C) Leonardo Gregianin, 2005-2008
# (C) xqt, 2009-2013
# (C) Pywikipedia bot team, 2005-2012
#
# Distributed under the terms of the MIT license.
#

import os.path
import pickle
import re
import sys
from copy import copy
import pywikibot
from pywikibot import i18n
from pywikibot import config
from pywikibot.pagegenerators import PreloadingGenerator


def CAT(site, name, hide):
    name = site.namespace(14) + ':' + name
    cat = pywikibot.Category(site, name)
    for article in cat.articles(endsort=hide):
        yield article
    if hide:
        for article in cat.articles(startFrom=unichr(ord(hide) + 1)):
            yield article


def BACK(site, name, hide):
    p = pywikibot.Page(site, name, ns=10)
    return [page for page in p.getReferences(follow_redirects=False,
                                             onlyTemplateInclusion=True)]


def DATA(site, name, hide):
    dp = pywikibot.ItemPage(site.data_repository(), name)
    try:
        title = dp.getSitelink(site)
    except pywikibot.PageNotFound:
        return
    cat = pywikibot.Category(site, title)
    for article in cat.articles(endsort=hide):
        yield article
    if hide:
        for article in cat.articles(startFrom=unichr(ord(hide) + 1)):
            yield article


# not implemented yet
def TMPL(site, name, hide):
    return


# ALL wikis use 'Link FA', and sometimes other localized templates.
# We use _default AND the localized ones
template = {
    '_default': ['Link FA'],
    'als': ['LinkFA'],
    'an': ['Destacato', 'Destacau'],
    'ar': [u'وصلة مقالة مختارة'],
    'ast': ['Enllaz AD'],
    'az': ['Link FM'],
    'br': ['Liamm PuB', 'Lien AdQ'],
    'ca': [u'Enllaç AD', 'Destacat'],
    'cy': ['Cyswllt erthygl ddethol', 'Dolen ED'],
    'eo': ['LigoElstara'],
    'en': ['Link FA', 'FA link'],
    'es': ['Destacado'],
    'eu': ['NA lotura'],
    'fr': ['Lien AdQ'],
    'fur': ['Leam VdC'],
    'ga': ['Nasc AR'],
    'hi': ['Link FA', 'Lien AdQ'],
    'is': [u'Tengill ÚG'],
    'it': ['Link AdQ'],
    'no': ['Link UA'],
    'oc': ['Ligam AdQ', 'Lien AdQ'],
    'ro': [u'Legătură AC', u'Legătură AF'],
    'sv': ['UA', 'Link UA'],
    'tr': ['Link SM'],
    'vi': [u'Liên kết chọn lọc'],
    'vo': [u'Yüm YG'],
    'yi': [u'רא'],
}

template_good = {
    '_default': ['Link GA'],
    'ar': [u'وصلة مقالة جيدة'],
    'da': ['Link GA', 'Link AA'],
    'eo': ['LigoLeginda'],
    'es': ['Bueno'],
    'fr': ['Lien BA'],
    'is': ['Tengill GG'],
    'it': ['Link VdQ'],
    'nn': ['Link AA'],
    'no': ['Link AA'],
    'pt': ['Bom interwiki'],
##    'tr': ['Link GA', 'Link KM'],
    'vi': [u'Liên kết bài chất lượng tốt'],
    'wo': ['Lien BA'],
}

template_lists = {
    '_default': ['Link FL'],
    'no': ['Link GL'],
}

featured_name = {
    'wikidata': (DATA, u'Q4387444'),
}

good_name = {
    'wikidata': (DATA, 'Q7045856'),
}

lists_name = {
    'wikidata': (TMPL, 'Q5857568'),
    'ar': (BACK, u'قائمة مختارة'),
    'da': (BACK, u'FremragendeListe'),
    'de': (BACK, u'Informativ'),
    'en': (BACK, u'Featured list'),
    'fa': (BACK, u"فهرست برگزیده"),
    'id': (BACK, u'Featured list'),
    'ja': (BACK, u'Featured List'),
    'ksh': (CAT,  u"Joode Leß"),
    'no': (BACK, u'God liste'),
    'pl': (BACK, u'Medalista'),
    'pt': (BACK, u'Anexo destacado'),
    'ro': (BACK, u'Listă de calitate'),
    'ru': (BACK, u'Избранный список или портал'),
    'tr': (BACK, u'Seçkin liste'),
    'uk': (BACK, u'Вибраний список'),
    'vi': (BACK, u'Sao danh sách chọn lọc'),
    'zh': (BACK, u'特色列表'),
}

# Third parameter is the sort key indicating articles to hide from the given
# list
former_name = {
    'ca': (CAT, u"Arxiu de propostes de la retirada de la distinció"),
    'en': (CAT, u"Wikipedia former featured articles", "#"),
    'es': (CAT, u"Wikipedia:Artículos anteriormente destacados"),
    'fa': (CAT, u"مقاله‌های برگزیده پیشین"),
    'hu': (CAT, u"Korábbi kiemelt cikkek"),
    'pl': (CAT, u"Byłe artykuły na medal"),
    'pt': (CAT, u"!Ex-Artigos_destacados"),
    'ru': (CAT, u"Википедия:Устаревшие избранные статьи"),
    'th': (CAT, u"บทความคัดสรรในอดีต"),
    'tr': (CAT, u"Vikipedi eski seçkin maddeler"),
    'zh': (CAT, u"已撤销的特色条目"),
}


class FeaturedBot(pywikibot.Bot):
    # Bot configuration.
    # Only the keys of the dict can be passed as init options
    # The values are the default values

    def __init__(self, **kwargs):
        """ Only accepts options defined in availableOptions """

        self.availableOptions.update({
            'async':  False,  # asynchron putting a page?
            'count': False,   # featuredcount
            'featured': False,
            'former': False,
            'fromall': False,
            'fromlang': None,
            'good': False,
            'lists': False,
            'nocache': list(),
            'side': False,    # not template_on_top
            'quiet': False,
        })

        super(FeaturedBot, self).__init__(**kwargs)
        self.editcounter = 0
        self.fromlang = None
        self.cache = dict()
        self.filename = None
        self.site = pywikibot.Site()

    def hastemplate(self, task):
        add_tl, remove_tl = self.getTemplateList(self.site.lang, task)
        for tl in add_tl:
            tp = pywikibot.Page(self.site, tl, ns=10)
            if not tp.exists():
                return
        for tl in remove_tl:
            tp = pywikibot.Page(self.site, tl, ns=10)
            if not tp.exists():
                return
        return True

    def readcache(self, task):
        if not self.getOption('nocache') is True:
            self.filename = pywikibot.config.datafilepath("cache", task)
            try:
                f = open(self.filename, "rb")
                self.cache = pickle.load(f)
                f.close()
                pywikibot.output(u'Cache file %s found with %d items.'
                                 % (self.filename, len(self.cache)))
            except IOError:
                pywikibot.output(u'Cache file %s not found.' % self.filename)

    def writecache(self):
        if not self.getOption('nocache') is True:
            pywikibot.output(u'Writing %d items to cache file %s.'
                             % (len(self.cache), self.filename))
            f = open(self.filename, "wb")
            pickle.dump(self.cache, f)
            f.close()
        self.cache = dict()

    def run(self):
        done = False
        if self.getOption('good'):
            self.run_good()
            done = True
        if self.getOption('lists'):
            self.run_list()
            done = True
        if self.getOption('former'):
            self.run_former()
            done = True
        if self.getOption('featured') or not done:
            self.run_featured()
        pywikibot.output(u'%d pages written.' % self.editcounter)

    def run_good(self):
        task = 'good'
        if not self.hastemplate(task):
            pywikibot.output(u'\nNOTE: % arcticles are not implemented at %.'
                             % (task, self.site))
            return

        if self.getOption('fromall'):
            item_no = good_name['wikidata'][1]
            dp = pywikibot.ItemPage(pywikibot.Site().data_repository(), item_no)
            dp.get()

            ### Quick and dirty hack - any ideas?
            # use wikipedia sites only
            self.fromlang = [lang.replace('_', '-') for (lang, fam) in
                             [key.split('wiki') for key in dp.sitelinks.keys()]
                             if not fam]
        else:
            return  # 2DO
        self.fromlang.sort()
        self.readcache(task)
        for code in self.fromlang:
            try:
                self.treat(code, task)
            except KeyboardInterrupt:
                pywikibot.output('\nQuitting featured treat...')
                break
        self.writecache()

    # not implemented yet
    def run_list(self):
        return

    # not implemented yet
    def run_former(self):
        return

    def run_featured(self):
        task = 'featured'
        if not self.hastemplate(task):
            pywikibot.output(u'\nNOTE: % arcticles are not implemented at %.'
                             % (task, self.site))
            return

        if self.getOption('fromall'):
            item_no = featured_name['wikidata'][1]
            dp = pywikibot.ItemPage(pywikibot.Site().data_repository(), item_no)
            dp.get()

            ### Quick and dirty hack - any ideas?
            # use wikipedia sites only
            self.fromlang = [lang.replace('_', '-') for (lang, fam) in
                             [key.split('wiki') for key in dp.sitelinks.keys()]
                             if not fam]
        else:
            return  # 2DO
        self.fromlang.sort()
        self.readcache(task)
        for code in self.fromlang:
            try:
                self.treat(code, task)
            except KeyboardInterrupt:
                pywikibot.output('\nQuitting featured treat...')
                break
        self.writecache()

    def treat(self, code, process):
        fromsite = pywikibot.Site(code)
        if fromsite != self.site:
            self.featuredWithInterwiki(fromsite, process)

    def featuredArticles(self, site, task, cache):
        wikidata = False
        code = site.lang
        articles = []
        if task == 'good':
            info = good_name
            code = 'wikidata'
        elif task == 'former':
            info = former_name
        elif task == 'list':
            info = lists_name
        else:
            info = featured_name
            code = 'wikidata'
        try:
            method = info[code][0]
        except KeyError:
            pywikibot.error(
                u'language %s doesn\'t has %s category source.'
                % (code, task))
            return
        name = info[code][1]
        # hide #-sorted items on en-wiki
        try:
            hide = info[code][2]
        except IndexError:
            hide = None
        for p in method(site, name, hide):
            if p.namespace() == 0:  # Article
                articles.append(p)
            # Article talk (like in English)
            elif p.namespace() == 1 and site.lang != 'el':
                articles.append(pywikibot.Page(p.site,
                                p.title(withNamespace=False)))
        pywikibot.output(
            '\03{lightred}** %s has %i %s articles\03{default}'
            % (site, len(articles), task))
        for p in articles:
            if p.title() < afterpage:
                continue

            if u"/" in p.title() and p.namespace() != 0:
                pywikibot.output(u"%s is a subpage" % p.title())
                continue

            if p.title() in cache:
                pywikibot.output(u"(cached) %s -> %s" % (p.title(),
                                                         cache[p.title()]))
                continue
            yield copy(p)

    def findTranslated(self, page, oursite=None):
        quiet = self.getOption('quiet')
        if not oursite:
            oursite = self.site
        if page.isRedirectPage():
            page = page.getRedirectTarget()

        ourpage = None
        for link in page.iterlanglinks():
            if link.site == oursite:
                ourpage = pywikibot.Page(link)
                break

        if not ourpage:
            if not quiet:
                pywikibot.output(u"%s -> no corresponding page in %s"
                                 % (page.title(), oursite))
            return

        if ourpage.section():
            pywikibot.output(u"%s -> our page is a section link: %s"
                             % (page.title(), ourpage.title()))
            return

        if not ourpage.exists():
            pywikibot.output(u"%s -> our page doesn't exist: %s"
                             % (page.title(), ourpage.title()))
            return

        if ourpage.isRedirectPage():
            ourpage = ourpage.getRedirectTarget()
        pywikibot.output(u"%s -> corresponding page is %s"
                         % (page.title(), ourpage.title()))
        if ourpage.namespace() != 0:
            pywikibot.output(u"%s -> not in the main namespace, skipping"
                             % page.title())
            return

        if ourpage.isRedirectPage():
            pywikibot.output(u"%s -> double redirect, skipping" % page.title())
            return

        if not ourpage.exists():
            pywikibot.output(u"%s -> page doesn't exist, skipping"
                             % ourpage.title())
            return

        backpage = None
        for link in ourpage.iterlanglinks():
            if link.site == page.site:
                backpage = pywikibot.Page(link)
                break

        if not backpage:
            pywikibot.output(u"%s -> no back interwiki ref" % page.title())
            return

        if backpage == page:
            # everything is ok
            return ourpage
        if backpage.isRedirectPage():
            backpage = backpage.getRedirectTarget()
        if backpage == page:
            # everything is ok
            return ourpage
        pywikibot.output(u"%s -> back interwiki ref target is %s"
                         % (page.title(), backpage.title()))

    def getTemplateList(self, lang, task):
        add_templates = []
        remove_templates = []
        if task == 'featured':
            try:
                add_templates = template[lang]
                add_templates += template['_default']
            except KeyError:
                add_templates = template['_default']
            try:
                remove_templates = template_good[lang]
                remove_templates += template_good['_default']
            except KeyError:
                remove_templates = template_good['_default']
        elif task == 'good':
            try:
                add_templates = template_good[lang]
                add_templates += template_good['_default']
            except KeyError:
                add_templates = template_good['_default']
            try:
                remove_templates = template[lang]
                remove_templates += template['_default']
            except KeyError:
                remove_templates = template['_default']
        elif task == 'list':
            try:
                add_templates = template_lists[lang]
                add_templates += template_lists['_default']
            except KeyError:
                add_templates = template_lists['_default']
        else:  # task == 'former'
            try:
                remove_templates = template[lang]
                remove_templates += template['_default']
            except KeyError:
                remove_templates = template['_default']
        return add_templates, remove_templates

    def featuredWithInterwiki(self, fromsite, task):
        """Place or remove the Link_GA/FA template on/from a page"""

        def compile_link(site, templates):
            """compile one link template list"""
            findtemplate = '(%s)' % '|'.join(templates)
            return re.compile(ur"\{\{%s\|%s\}\}"
                              % (findtemplate.replace(u' ', u'[ _]'),
                                 site.code), re.IGNORECASE)

        quiet = self.getOption('quiet')
        tosite = self.site
        if not fromsite.lang in self.cache:
            self.cache[fromsite.lang] = {}
        if not tosite.lang in self.cache[fromsite.lang]:
            self.cache[fromsite.lang][tosite.lang] = {}
        cc = self.cache[fromsite.lang][tosite.lang]
        if self.getOption('nocache') is True or \
           fromsite.code in self.getOption('nocache'):
            cc = {}
        add_tl, remove_tl = self.getTemplateList(tosite.code, task)
        re_Link_add = compile_link(fromsite, add_tl)
        re_Link_remove = compile_link(fromsite, remove_tl)
        gen = self.featuredArticles(fromsite, task, cc)
        gen = PreloadingGenerator(gen)
        pairs = []
        for a in gen:
            if a.isRedirectPage():
                a = a.getRedirectTarget()

            if not a.exists():
                pywikibot.output(u"source page doesn't exist: %s"
                                 % a.title())
                continue

            atrans = self.findTranslated(a, tosite)
            if not atrans:
                continue

            text = atrans.get()
            m1 = add_tl and re_Link_add.search(text)
            m2 = remove_tl and re_Link_remove.search(text)
            changed = False
            if add_tl:
                if m1:
                    pywikibot.output(u"(already added)")
                else:
                    # insert just before interwiki
                    if (not interactive or
                        pywikibot.input(
                            u'Connecting %s -> %s. Proceed? [Y/N]'
                            % (a.title(), atrans.title())) in ['Y', 'y']):
                        if self.getOption('side'):
                            # Placing {{Link FA|xx}} right next to
                            # corresponding interwiki
                            text = (text[:m1.end()] +
                                    u" {{%s|%s}}" % (add_tl[0], fromsite.code) +
                                    text[m1.end():])
                        else:
                            # Moving {{Link FA|xx}} to top of interwikis
                            iw = pywikibot.getLanguageLinks(text, self.site)
                            text = pywikibot.removeLanguageLinks(text, self.site)
                            text += u"\r\n{{%s|%s}}\r\n" % (add_tl[0],
                                                            fromsite.code)
                            text = pywikibot.replaceLanguageLinks(text,
                                                                  iw, self.site)
                        changed = True
            if remove_tl:
                if m2:
                    if (not interactive or
                        pywikibot.input(
                            u'Connecting %s -> %s. Proceed? [Y/N]'
                            % (a.title(), atrans.title())) in ['Y', 'y']):
                        text = re.sub(re_Link_add, '', text)
                        changed = True
                elif task == 'former':
                    pywikibot.output(u"(already removed)")
            cc[a.title()] = atrans.title()
            if changed:
                comment = i18n.twtranslate(self.site, 'featured-' + task,
                                           {'page': unicode(a)})
                try:
                    atrans.put(text, comment)
                except pywikibot.LockedPage:
                    pywikibot.output(u'Page %s is locked!'
                                     % atrans.title())
                except pywikibot.PageNotSaved, e:
                    pywikibot.output(u"Page not saved")


def main(*args):
    global interactive, afterpage
    interactive = 0
    afterpage = u"!"

    featuredcount = False
    fromlang = []
    processType = 'featured'
    part = False
    options = {}
    for arg in pywikibot.handleArgs():
        if arg == '-interactive':
            interactive = 1
        elif arg.startswith('-fromlang:'):
            fromlang = arg[10:].split(",")
            part = True
        elif arg.startswith('-after:'):
            afterpage = arg[7:]
        elif arg.startswith('-nocache:'):
            options[arg[1:8]] = arg[9:].split(",")
        else:
            options[arg[1:].lower()] = True

    if part:
        try:
            # BUG: range with zh-min-nan (3 "-")
            if len(fromlang) == 1 and fromlang[0].index("-") >= 0:
                start, end = fromlang[0].split("--", 1)
                if not start:
                    start = ""
                if not end:
                    end = "zzzzzzz"
                if processType == 'good':
                    fromlang = [lang for lang in good_name.keys()
                                if lang >= start and lang <= end]
                elif processType == 'list':
                    fromlang = [lang for lang in lists_name.keys()
                                if lang >= start and lang <= end]
                elif processType == 'former':
                    fromlang = [lang for lang in former_name.keys()
                                if lang >= start and lang <= end]
                else:
                    fromlang = [lang for lang in featured_name.keys()
                                if lang >= start and lang <= end]
        except:
            pass

##        for ll in fromlang:
##            fromsite = pywikibot.getSite(ll)
##            if featuredcount:
##                try:
##                    featuredArticles(fromsite, processType).next()
##                except StopIteration:
##                    continue
    if options:
        bot = FeaturedBot(**options)
        bot.run()
    else:
        pywikibot.showHelp()


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
