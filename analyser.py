__author__ = 'raigo'


import re

class AnalyseData():
    def __init__(self, page, text, html_text):
        self.letter_count = len(text)
        self.images = page.imagelinks()
        self.linked_pages = page.linkedPages()
        self.external_links = page.extlinks()
        self.version_history = page.getVersionHistory()
        self.contributing_users = page.contributingUsers()
        self.red_link_count = len(re.findall('<a[^>]+class="new"', html_text))

    def __str__(self):
        return super.__str__(self) + \
               str({"letter_count": self.letter_count,
                    "link_count": get_len(self.linked_pages),
                    "image_count": get_len(self.images),
                    "foreign_link_count": get_len(self.external_links),
                    "red_link_count": self.red_link_count})


def get_len(iterator):
    length = 0
    for _ in iterator:
        length += 1
    return length