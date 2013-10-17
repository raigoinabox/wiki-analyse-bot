# -*- coding: utf-8  -*-
#
# (C) Pywikipedia bot team, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import os
from pywikibot import i18n
import shutil

from utils import unittest


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.msg_localized = {'en': u'test-localized EN',
                              'nl': u'test-localized NL',
                              'fy': u'test-localized FY'}
        self.msg_semi_localized = {'en': u'test-semi-localized EN',
                                   'nl': u'test-semi-localized NL'}
        self.msg_non_localized = {'en': u'test-non-localized EN'}
        self.msg_no_english = {'ja': u'test-no-english JA'}

    def testLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_localized),
                         u'test-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_localized),
                         u'test-localized NL')
        self.assertEqual(i18n.translate('fy', self.msg_localized),
                         u'test-localized FY')

    def testSemiLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_semi_localized),
                         u'test-semi-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_semi_localized),
                         u'test-semi-localized NL')
        self.assertEqual(i18n.translate('fy', self.msg_semi_localized),
                         u'test-semi-localized NL')

    def testNonLocalized(self):
        self.assertEqual(i18n.translate('en', self.msg_non_localized),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('fy', self.msg_non_localized),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('nl', self.msg_non_localized),
                         u'test-non-localized EN')
        self.assertEqual(i18n.translate('ru', self.msg_non_localized),
                         u'test-non-localized EN')

    def testNoEnglish(self):
        self.assertEqual(i18n.translate('en', self.msg_no_english),
                         u'test-no-english JA')
        self.assertEqual(i18n.translate('fy', self.msg_no_english),
                         u'test-no-english JA')
        self.assertEqual(i18n.translate('nl', self.msg_no_english),
                         u'test-no-english JA')


class TestTWTranslate(unittest.TestCase):
    def setUp(self):
        self.path = os.path.split(os.path.realpath(__file__))[0]
        shutil.copyfile(os.path.join(self.path, 'i18n', 'test.py'),
                        os.path.join(self.path, '..', 'scripts', 'i18n', 'test.py'))

    def tearDown(self):
        os.remove(os.path.join(self.path, '..', 'scripts', 'i18n', 'test.py'))

    def testLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-localized'),
                         u'test-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-localized'),
                         u'test-localized NL')
        self.assertEqual(i18n.twtranslate('fy', 'test-localized'),
                         u'test-localized FY')

    def testSemiLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-semi-localized'),
                         u'test-semi-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-semi-localized'),
                         u'test-semi-localized NL')
        self.assertEqual(i18n.twtranslate('fy', 'test-semi-localized'),
                         u'test-semi-localized NL')

    def testNonLocalized(self):
        self.assertEqual(i18n.twtranslate('en', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('fy', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('nl', 'test-non-localized'),
                         u'test-non-localized EN')
        self.assertEqual(i18n.twtranslate('ru', 'test-non-localized'),
                         u'test-non-localized EN')

    def testNoEnglish(self):
        self.assertRaises(i18n.TranslationError, i18n.twtranslate, 'en', 'test-no-english')


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
