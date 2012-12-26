import sys
import os.path
import argparse
from src.humble_page import HumblePage

# Assumes you run from inside the annex
ANNEX_LOCATION = './'
BOOKS_SUBDIR = 'Books/Humble Bundle/'
GAMES_SUBDIR = 'Games/'
MOVIES_SUBDIR = 'Videos/Movies/'
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

UNPACKED_NAMES = {
    'Kooky/Highest Quality MP4': 'Kooky [Top quality, 720p].mp4',
    'Kooky/Recommended MP4': 'Kooky [Normal quality, 720p].mp4',
}

class HumbugHandler(object):
    def __init__(self, application, item):
        self.application = application
        self.item = item
        self.title = self.clean_name(item.title)

    def clean_name(self, name):
        # Don't use ':' in filename. ':' is illegal in FAT/NTFS filenames
        # so limits the portability of your annex.
        # 'Amnesia: The Dark Descent' -> 'Amnesia - The Dark Descent',
        name = name.replace(':', ' -')

        # 'HD' is a format, not part of the game name.
        # 'Eufloria HD' -> 'Eufloria'
        if name.endswith(' HD'):
            name = name[:-3]

        return NAME_EXCEPTIONS.get(name, name)

    def get(self, item, dl, target_dir, target_filename=None):
        """Download from the link contained in `dl` a file to the path
        in target_dir."""
        if target_filename == None:
            target_filename = dl.filename
        full_path = os.path.join(target_dir, target_filename)

        # Use lexists because this could be a symlink that wasn't
        # annex-get'd on this machine
        if os.path.lexists(full_path):
            #print "  Exists:", target_filename
            pass
        else:
            print "  Get:", full_path, dl.type, dl.name, dl.md5, dl.modified


class BookHandler(HumbugHandler):
    def handle(self):
        assert not self.item.has_soundtrack
        print "Book:", self.item, self.title

class MovieHandler(HumbugHandler):
    def handle(self):
        item = self.item
        #print "Movie:", item, item.title
        versions = {}
        non_files = {}
        title = self.title
        for dl in item.downloads():
            if not dl.is_file:
                # Well, we can't download it. This could be a Stream
                # link, which is OK if it's accompanied by other
                # download links.
                # To be safe, let's flag it for the
                # user. But let's only flag it once per link.
                if dl.name in non_files:
                    continue
                print "Can't download non-file {} for {}".format(
                    dl.name, title)
                non_files[dl.name] = True
                continue
            if dl.md5 in versions:
                # Seems like these movies are being listed in each OS
                continue
            versions[dl.md5] = True

            # For some reason, the Humble Bundle people package their
            # movies as .zip files. In the annex they should be stored
            # unpacked.
            filename = UNPACKED_NAMES.get('{}/{}'.format(item.title, dl.name),
                                          dl.filename)

            target_dir = os.path.join(MOVIES_SUBDIR, title)
            self.get(item, dl, target_dir, filename)

class GameHandler(HumbugHandler):
    def handle(self):
        item = self.item
        assert not item.is_book
        title = self.title
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
            target_dir = os.path.join(GAMES_SUBDIR, title,
                                           type_dir)
            versions[md5] = True
            self.get(item, dl, target_dir)


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
