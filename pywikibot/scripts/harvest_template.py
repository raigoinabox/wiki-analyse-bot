#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Usage:

python harvest_template.py -lang:nl -template:"Taxobox straalvinnige" orde P70 familie P71 geslacht P74

This will work on all pages that transclude the template in the article
namespace

You can use any typical pagegenerator to provide with a list of pages:

python harvest_template.py -lang:nl -cat:Sisoridae -template:"Taxobox straalvinnige" -namespace:0 orde P70 familie P71 geslacht P74

"""
#
# (C) 2013 Multichill, Amir
# (C) 2013 Pywikipediabot team
#
# Distributed under the terms of MIT License.
#
__version__ = '$Id$'
#

import re
import json
import pywikibot
from pywikibot import pagegenerators as pg


class HarvestRobot:
    """
    A bot to add Wikidata claims
    """
    def __init__(self, generator, templateTitle, fields):
        """
        Arguments:
            * generator     - A generator that yields Page objects.
            * templateTitle - The template to work on
            * fields        - A dictionary of fields that are of use to us

        """
        self.generator = pg.PreloadingGenerator(generator)
        self.templateTitle = templateTitle.replace(u'_', u' ')
        # TODO: Make it a list which also includes the redirects to the template
        self.fields = fields
        self.repo = pywikibot.Site().data_repository()
        self.cacheSources()

    def getSource(self, lang):
        """
        Get the source for the specified language,
        if possible
        """
        if lang in self.source_values:
            source = pywikibot.Claim(self.repo, 'p143')
            source.setTarget(self.source_values.get(lang))
            return source

    def cacheSources(self):
        """
        Fetches the sources from the onwiki list
        and stores it internally
        """
        page = pywikibot.Page(self.repo, u'Wikidata:List of wikis/python')
        self.source_values = json.loads(page.get())
        self.source_values = self.source_values['wikipedia']
        for source_lang in self.source_values:
            self.source_values[source_lang] = pywikibot.ItemPage(self.repo,
                                                                 self.source_values[source_lang])

    def run(self):
        """
        Starts the robot.
        """
        self.templateTitles = self.getTemplateSynonyms(self.templateTitle)
        for page in self.generator:
            try:
                self.procesPage(page)
            except Exception, e:
                pywikibot.exception(tb=True)

    def getTemplateSynonyms(self, title):
        """
        Fetches redirects of the title, so we can check against them
        """
        pywikibot.output('Finding redirects...')  # Put some output here since it can take a while
        temp = pywikibot.Page(pywikibot.Site(), title, ns=10)
        if temp.isRedirectPage():
            temp = temp.getRedirectTarget()
        titles = [page.title(withNamespace=False)
                  for page
                  in temp.getReferences(redirectsOnly=True, namespaces=[10], follow_redirects=False)]
        titles.append(temp.title(withNamespace=False))
        return titles

    def procesPage(self, page):
        """
        Proces a single page
        """
        item = pywikibot.ItemPage.fromPage(page)
        pywikibot.output('Processing %s' % page)
        if not item.exists():
            pywikibot.output('%s doesn\'t have a wikidata item :(' % page)
            #TODO FIXME: We should provide an option to create the page
        else:
            pagetext = page.get()
            templates = pywikibot.extract_templates_and_params(pagetext)
            for (template, fielddict) in templates:
                # Clean up template
                template = pywikibot.Page(page.site, template,
                                          ns=10).title(withNamespace=False)
                # We found the template we were looking for
                if template in self.templateTitles:
                    for field, value in fielddict.items():
                        field = field.strip()
                        value = value.strip()
                        # This field contains something useful for us
                        if field in self.fields:
                            # Check if the property isn't already set
                            claim = pywikibot.Claim(self.repo, self.fields[field])
                            if claim.getID() in item.get().get('claims'):
                                pywikibot.output(
                                    u'A claim for %s already exists. Skipping'
                                    % claim.getID())
                                # TODO FIXME: This is a very crude way of dupe
                                # checking
                            else:
                                if claim.getType() == 'wikibase-item':
                                    # Try to extract a valid page
                                    match = re.search(pywikibot.link_regex, value)
                                    if match:
                                        try:
                                            link = pywikibot.Link(match.group(1))
                                            linkedPage = pywikibot.Page(link)
                                            if linkedPage.isRedirectPage():
                                                linkedPage = linkedPage.getRedirectTarget()
                                            linkedItem = pywikibot.ItemPage.fromPage(linkedPage)
                                            claim.setTarget(linkedItem)
                                        except pywikibot.exceptions.NoPage:
                                            pywikibot.output('[[%s]] doesn\'t exist so I can\'t link to it' % (linkedItem.title(),))
                                            continue
                                elif claim.getType() == 'string':
                                    claim.setTarget(value.strip())
                                else:
                                    print "%s is not a supported datatype." % claim.getType()
                                    continue

                                pywikibot.output('Adding %s --> %s' % (claim.getID(), claim.getTarget()))
                                item.addClaim(claim)
                                # A generator might yield pages from multiple sites
                                source = self.getSource(page.site.language())
                                if source:
                                    claim.addSource(source, bot=True)


def main():
    gen = pg.GeneratorFactory()
    commandline_arguments = list()
    templateTitle = u''
    for arg in pywikibot.handleArgs():
        if arg.startswith('-template'):
            if len(arg) == 9:
                templateTitle = pywikibot.input(
                    u'Please enter the template to work on:')
            else:
                templateTitle = arg[10:]
        elif gen.handleArg(arg):
            continue
        else:
            commandline_arguments.append(arg)

    if len(commandline_arguments) % 2 or not templateTitle:
        raise ValueError  # or something.
    fields = dict()

    for i in xrange(0, len(commandline_arguments), 2):
        fields[commandline_arguments[i]] = commandline_arguments[i + 1]

    generator = gen.getCombinedGenerator()
    if not generator:
        # TODO: Build a transcluding generator based on templateTitle
        return

    bot = HarvestRobot(generator, templateTitle, fields)
    bot.run()

if __name__ == "__main__":
    main()
