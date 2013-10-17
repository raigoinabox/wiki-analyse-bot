__author__ = 'raigo'

#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is not a complete bot; rather, it is a template from which simple
bots can be made. You can rename it to mybot.py, then edit it in
whatever way you want.

The following parameters are supported:

&params;

-dry              If given, doesn't do any real changes, but only shows
                  what would have been changed.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
#
# (C) Pywikipedia bot team, 2006-2011
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: 1d8bfab72b54cda532b5ec540b6142d968588dab $'
#

from pywikibot_core import pywikibot
from pywikibot_core.pywikibot import pagegenerators
from pywikibot_core.pywikibot import i18n
import analyser
import urllib2

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class BasicBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
        """
        self.generator = generator
        # Set the edit summary message
        self.summary = i18n.twtranslate(site, 'basic-changing')

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """
        Loads the given page and analyzes it.
        """
        text = self.load(page)
        if not text:
            return

        url = 'http://et.wikipedia.org/wiki/' + page.title(True)
        request = urllib2.Request(url, headers={"User-Agent": "AnalyseBot"})
        html_text = urllib2.urlopen(request)
        data = analyser.AnalyseData(page, text, html_text.read())

        print(data)

    def load(self, page):
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


def main():
    global site
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        # check if a standard argument like
        # -start:XYZ or -ref:Asdf was given.
        if not genFactory.handleArg(arg):
            pageTitleParts.append(arg)
    site = pywikibot.Site()
    site.login()
    if pageTitleParts != []:
        # We will only work on a single page.
        pageTitle = ' '.join(pageTitleParts)
        page = pywikibot.Page(pywikibot.Link(pageTitle, site))
        gen = iter([page])

    if not gen:
        gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        bot = BasicBot(gen)
        bot.run()
    else:
        pywikibot.showHelp()


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
