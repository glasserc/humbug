"""
Handlers for different kind of items found in the Humble Bundle.
"""

import os.path
from src.config import BOOKS_SUBDIR
from src.config import GAMES_SUBDIR, GAME_TYPE_SUBDIR
from src.config import MOVIES_SUBDIR, UNPACKED_NAMES
from src.config import NAME_EXCEPTIONS

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

    def sanity_check(self):
        """Hook to let you make sure that you're handling the right
        kind of object."""
        pass

    def handle(self):
        """Superclass handle method.

        Iterate over all the downloads available for this object,
        signalling non-files to the user and ignoring duplicate files.

        Call self.download_filename(item, filename) and
        self.download_path(item, filename) to figure out where to
        download this item to."""
        self.sanity_check()
        item = self.item
        #print self.__class__.__name__, ":", item, item.title
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
                print "Can't download non-file '{}' (for '{}')".format(
                    dl.name, title)
                non_files[dl.name] = True
                continue

            if dl.md5 in versions:
                # This dl was listed multiple times.
                # Movies are listed once per OS :(.
                # Some .sh files are listed under both 32-bit and 64-bit.
                # FIXME: if it's a .sh, maybe copy the symlink, or link to it?
                continue
            versions[dl.md5] = True

            target_dir = self.download_path(dl)
            filename = self.download_filename(dl)
            unpack = self.should_unpack(dl)

            self.get(item, dl, target_dir, filename)

    def download_filename(self, dl):
        return dl.filename

    def download_path(self, dl):
        raise NotImplementedYetError, 'please override me'

    def should_unpack(self, dl):
        return False

class BookHandler(HumbugHandler):
    def sanity_check(self):
        assert not self.item.has_soundtrack

    def download_path(self, dl):
        author_name = self.clean_name(self.item.subtitle)
        # We keep '&' as a valid part of a name for a work, but for
        # authors it's generally better to have 'and'
        author_name = author_name.replace('&', 'and')

        return os.path.join(BOOKS_SUBDIR, author_name,
                            self.title)

class MovieHandler(HumbugHandler):
    def download_path(self, dl):
        return os.path.join(MOVIES_SUBDIR, self.title)

    def download_filename(self, dl):
        # For some reason, the Humble Bundle people package their
        # movies as .zip files. In the annex they should be stored
        # unpacked.
        return UNPACKED_NAMES.get('{}/{}'.format(self.title, dl.name),
                                  dl.filename)

    def should_unpack(self, dl):
        return not dl.type == 'audio'

class GameHandler(HumbugHandler):
    def sanity_check(self):
        assert not self.item.is_book

    def download_path(self, dl):
        type_dir = GAME_TYPE_SUBDIR[dl.type]
        if isinstance(type_dir, dict):
            type_dir = type_dir[dl.arch]
        target_dir = os.path.join(GAMES_SUBDIR, self.title,
                                  type_dir)
        return target_dir
