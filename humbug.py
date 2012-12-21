import sys
import argparse
from bs4 import BeautifulSoup

class HumblePage(object):
    def __init__(self, config):
        self.tree = BeautifulSoup(file(config.filename))


class Humbug(object):
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(description="munge Humble Bundle page into a git annex")
        parser.add_argument('filename', type=str,
                            help="a saved version of the home.html page")
        self.config = parser.parse_args(args)

    def go(self):
        page = HumblePage(self.config)
        print page.tree.title


if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
