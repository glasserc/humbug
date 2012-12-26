import sys
import os.path
import argparse
from src.humble_page import HumblePage
from src.config import ANNEX_LOCATION
from src.handlers import GameHandler, MovieHandler, BookHandler

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
                handler = BookHandler
            elif item.title == 'Kooky' or item.title.startswith('Indie Game'):
                handler = MovieHandler
            else:
                handler = GameHandler

            handler(self, item).handle()

if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
