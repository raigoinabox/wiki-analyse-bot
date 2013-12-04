__author__ = 'raigo'

import pywikibot
import analyser

class PageModel():
    def __init__(self, page, target=None, html_text=""):
        self.page = page
        self._target = target
        #self.images = page.imagelinks()
        #self.external_links = page.extlinks()
        #self.version_history = page.getVersionHistory()
        #self.contributing_users = page.contributingUsers()
        #self.red_link_count = len(re.findall('<a[^>]+class="new"', html_text))


    def get_scikit_format(self):
        return (len(self.page.get()),
                get_len(self.page.linkedPages()),
                get_len(self.page.getReferences()))


    @property
    def target(self):
        if self._target is None:
            self._target = analyser.predict_model(self)
        return self._target

    def __str__(self):
        return str(self.page)

    def __getstate__(self):
        mydict = self.__dict__.copy()
        mydict["page"] = self.page.title()
        return mydict

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.page = pywikibot.Page(pywikibot.Link(self.page))


#def load_text(page):
#    """
#    Loads the text of the given page.
#    """
#    try:
#        # Load the page
#        text = page.get()
#    except pywikibot.NoPage:
#        pywikibot.output(u"Page %s does not exist; skipping."
#                         % page.title(asLink=True))
#    except pywikibot.IsRedirectPage:
#        pywikibot.output(u"Page %s is a redirect; skipping."
#                         % page.title(asLink=True))
#    else:
#        return text
#    return None


def get_len(iterator):
    length = 0
    for _ in iterator:
        length += 1
    return length
