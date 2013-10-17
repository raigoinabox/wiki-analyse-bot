#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Legoktm
Copyright (C) 2013 Pywikipediabot team

Distributed under the MIT License

Usage:

python claimit.py [pagegenerators] P1 Q2 P123 Q456

You can use any typical pagegenerator to provide with a list of pages

Then list the property-->target pairs to add.
"""
import json
import pywikibot
from pywikibot import pagegenerators


class ClaimRobot:
    """
    A bot to add Wikidata claims
    """
    def __init__(self, generator, claims):
        """
        Arguments:
            * generator    - A generator that yields Page objects.
            * claims       - A list of wikidata claims

        """
        self.generator = generator
        self.claims = claims
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
        for page in self.generator:
            item = pywikibot.ItemPage.fromPage(page)
            pywikibot.output('Processing %s' % page)
            if not item.exists():
                pywikibot.output('%s doesn\'t have a wikidata item :(' % page)
                # TODO FIXME: We should provide an option to create the page
            else:
                for claim in self.claims:
                    if claim.getID() in item.get().get('claims'):
                        pywikibot.output(
                            u'A claim for %s already exists. Skipping'
                            % (claim.getID(),))
                        #TODO FIXME: This is a very crude way of dupe checking
                    else:
                        pywikibot.output('Adding %s --> %s'
                                         % (claim.getID(), claim.getTarget()))
                        item.addClaim(claim)
                        # A generator might yield pages from multiple languages
                        source = self.getSource(page.site.language())
                        if source:
                            claim.addSource(source, bot=True)
                        # TODO FIXME: We need to check that we aren't adding a
                        # duplicate


def main():
    gen = pagegenerators.GeneratorFactory()
    commandline_claims = list()
    for arg in pywikibot.handleArgs():
        if gen.handleArg(arg):
            continue
        commandline_claims.append(arg)
    if len(commandline_claims) % 2:
        raise ValueError  # or something.
    claims = list()

    repo = pywikibot.Site().data_repository()

    for i in xrange(0, len(commandline_claims), 2):
        claim = pywikibot.Claim(repo, commandline_claims[i])
        if claim.getType() == 'wikibase-item':
            target = pywikibot.ItemPage(repo, commandline_claims[i + 1])
        elif claim.getType() == 'string':
            target = commandline_claims[i + 1]
        else:
            raise NotImplementedError(
                "%s datatype is not yet supported by claimit.py"
                % claim.getType())
        claim.setTarget(target)
        claims.append(claim)

    generator = gen.getCombinedGenerator()
    if not generator:
        # FIXME: Should throw some help
        return

    bot = ClaimRobot(generator, claims)
    bot.run()

if __name__ == "__main__":
    main()
