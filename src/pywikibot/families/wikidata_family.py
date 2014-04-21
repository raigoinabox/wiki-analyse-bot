# -*- coding: utf-8  -*-

__version__ = '$Id$'

from pywikibot import family

# The wikidata family


class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'wikidata'
        self.langs = {
            'wikidata': 'www.wikidata.org',
            'test': 'test.wikidata.org',
        }

    def shared_data_repository(self, code, transcluded=False):
        """Always return a repository tupe. This enables testing whether
        the site object is the repository itself, see Site.is_data_repository()

        """
        if transcluded:
            return (None, None)
        else:
            return (code, self.name)

    def globes(self, code):
        """Supported globes for Coordinate datatype"""
        return {
            'earth': 'http://www.wikidata.org/entity/Q2',
            'mars': 'http://www.wikidata.org/entity/Q111',
            'mercury': 'http://www.wikidata.org/entity/Q308',
            'mimas': 'http://www.wikidata.org/entity/Q15034',
            'moon': 'http://www.wikidata.org/entity/Q405',
            'venus': 'http://www.wikidata.org/entity/Q313',
        }
