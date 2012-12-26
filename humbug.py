import sys
import os.path
import argparse
from src.humble_page import HumblePage

# Assumes you run from inside the annex
ANNEX_LOCATION = './'
BOOKS_SUBDIR = 'Books/Humble Bundle/'
GAMES_SUBDIR = 'Games/'
GAME_TYPE_SUBDIR = {
    'android': 'Android',
    'windows': 'Windows - i386',
    'linux': {
        '64-bit': 'Linux - x86_64',
        '32-bit': 'Linux - i386',
        },
    'mac': 'OSX',
    'mac10.5': 'OSX 10.5',
    'mac10.6+': 'OSX 10.6+',
    'air': 'Air',
    'flash': 'Flash',
    'audio': 'Soundtrack',
}

NAME_EXCEPTIONS = {
    # Penumbra Overture is really "Penumbra: Overture", which should
    # be a hyphen as above.
    'Penumbra Overture': 'Penumbra - Overture',

    # Don't keep prefix'd "The", and downcase 'Of'
    'The Binding Of Isaac': 'Binding of Isaac',
    'The Binding of Isaac + Wrath of the Lamb DLC': 'Binding of Isaac + Wrath of the Lamb DLC',

    # Correct capitalization according to website.
    'FTL - Faster than Light': 'FTL - Faster Than Light',
    # Correct capitalization, according to World of Goo website
    'World Of Goo': 'World of Goo',
}

def clean_name(name):
    # Don't use ':' in filename. ':' is illegal in FAT/NTFS filenames
    # so limits the portability of your annex.
    # 'Amnesia: The Dark Descent' -> 'Amnesia - The Dark Descent',
    name = name.replace(':', ' -')

    # 'HD' is a format, not part of the game name.
    # 'Eufloria HD' -> 'Eufloria'
    if name.endswith(' HD'):
        name = name[:-3]

    return NAME_EXCEPTIONS.get(name, name)

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
            elif item.title == 'Kooky' or item.title.startswith('Indie Game'):
                self.handle_movie(item)
            else:
                self.handle_game(item)

    def handle_book(self, item):
        assert not item.has_soundtrack
        print "Book:", item, item.title

    def handle_movie(self, item):
        print "Movie:", item, item.title

    def handle_game(self, item):
        assert not item.is_book
        title = item.title
        title = clean_name(title)
        #print 'Game:', item, item.has_soundtrack
        # md5 -> True if we've already dealt with this.
        # Necessary because sometimes .sh files show up in both a 32-bit download
        # and a 64-bit download.
        versions = {}
        for dl in item.downloads():
            if not dl.is_file:
                # Well, we can't download it.  Sometimes this is a
                # link to another website, so the user has to deal
                # with it.
                print "Can't download non-file {} for {}".format(
                    dl.name, title)
                continue
            md5 = dl.md5
            if md5 in versions:
                # we've already seen this one
                # FIXME: symlink new to existing version, or copy symlink?
                continue
            type_dir = GAME_TYPE_SUBDIR[dl.type]
            if isinstance(type_dir, dict):
                type_dir = type_dir[dl.arch]
            target_filename = os.path.join(GAMES_SUBDIR, title,
                                           type_dir,
                                           dl.filename)
            versions[md5] = True
            # Use lexists because this could be a symlink that wasn't
            # annex-get'd on this machine
            if os.path.lexists(target_filename):
                #print "  Exists:", target_filename
                pass
            else:
                print "  Get:", target_filename, dl.type, dl.name, md5, dl.modified


if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
