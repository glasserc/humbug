import sys
import argparse
from bs4 import BeautifulSoup

from src import property_builder as P

class HumbleItem(object):
    def __init__(self, node):
        self.node = node

    title = property(
        P.text(P.find('div', 'title')))
    is_book = property(
        P.exists(P.text(P.find('div', 'downloads ebook'))))
    has_soundtrack = property(
        P.exists(P.text(P.find('div', 'downloads audio'))))

class HumblePage(object):
    def __init__(self, config):
        self.tree = BeautifulSoup(file(config.filename))

    @property
    def title(self):
        return self.tree.title.text

    def iteritems(self):
        return map(HumbleItem, self.tree.find_all('div', 'row'))

class Humbug(object):
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(description="munge Humble Bundle page into a git annex")
        parser.add_argument('filename', type=str,
                            help="a saved version of the home.html page")
        self.config = parser.parse_args(args)

    def go(self):
        page = HumblePage(self.config)
        print page.title
        for item in page.iteritems():
            print item, item.title, item.is_book, item.has_soundtrack


if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
