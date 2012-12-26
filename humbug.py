import sys
import os.path
import argparse
from src.humble_page import HumblePage

# Assumes you run from inside the annex
ANNEX_LOCATION = './'
BOOKS_SUBDIR = 'Books/Humble Bundle/'
GAMES_SUBDIR = 'Games/'

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
