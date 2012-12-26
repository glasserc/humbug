import sys
import os.path
import argparse
from bs4 import BeautifulSoup

from src import property_builder as P

# Assumes you run from inside the annex
ANNEX_LOCATION = './'
BOOKS_SUBDIR = 'Books/Humble Bundle/'
GAMES_SUBDIR = 'Games/'

class HumbleNode(object):
    """Class corresponding a node in the Humble Bundle download page.

    Many classes can be defined as special kinds of HumbleNodes."""
    def __init__(self, node):
        self.node = node

class HumbleDownload(HumbleNode):
    # Absent on a couple of elements where the link goes to a different website
    md5 = property(
        P.attr('href', P.find('a', 'dlmd5'), strip_hash=True))

    modified = property(
        P.attr('data-timestamp', P.find('a', 'dldate', optional=True)))

    name = property(
        P.text(P.find('span', 'label')))

    @property
    def type(self):
        dlnode = self.node.parent  # <div class="downloads linux show">
        classes = dlnode['class']
        for cls in classes:
            if cls == 'downloads':
                continue

            if cls == 'show':
                # just indicates that the div is visible
                continue

            return cls

    @property
    def is_file(self):
        return self.node.find('a')['data-web']. \
            startswith('http://files.humblebundle.com')

class HumbleItem(HumbleNode):
    title = property(
        P.text(P.find('div', 'title')))
    is_book = property(
        P.exists(P.text(P.find('div', 'downloads ebook'))))
    has_soundtrack = property(
        P.exists(P.text(P.find('div', 'downloads audio'))))

    def downloads(self):
        return map(HumbleDownload,
                   self.node.find_all('div', 'download'))

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
        git_dir = os.path.join(ANNEX_LOCATION, '.git')
        annex_dir = os.path.join(git_dir, 'annex')
        if not os.path.exists(git_dir) or \
                not os.path.exists(annex_dir):
            print "This doesn't seem like a git annex."
            print "Couldn't find {} or {}.".format(git_dir, annex_dir)
            print "Please run from inside a git annex."
        page = HumblePage(self.config)
        print page.title
        for item in page.iteritems():
            if item.is_book:
                self.handle_book(item)
            else:
                self.handle_game(item)

    def handle_book(self, item):
        assert not item.has_soundtrack
        print "Book:", item, item.title

    def handle_game(self, item):
        assert not item.is_book
        print 'Game:', item, item.title, item.has_soundtrack
        for dl in item.downloads():
            md5 = ''
            if dl.is_file: md5 = dl.md5
            print "  ", dl.type, dl.name, md5, dl.modified


if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
