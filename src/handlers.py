"""
Handlers for different kind of items found in the Humble Bundle.
"""

import os.path
from src.config import NAME_EXCEPTIONS, SOUNDTRACK_TYPES
from src import utils

# BookHandler
from src.config import BOOKS_SUBDIR

# GameHandler
import re
from distutils import version
from src.config import GAMES_SUBDIR, GAME_TYPE_SUBDIR
from src.filematch import SameFile, LinkMissing, OldVersion, UserInvestigate
from src.versions import Timestamp, DateString, BackwardsDateString, DebianVersion

# MovieHandler
from src.config import MOVIES_SUBDIR, UNPACKED_NAMES, GAME_TYPE_SUBDIR
from src.filematch import UnpackedFile

# AlbumHandler
from src.config import ALBUMS_SUBDIR

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

    DISABLE_DOWNLOAD = True

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

            target_dir = self.download_path(dl)
            filename = self.download_filename(dl)
            unpack = self.should_unpack(dl)

            if dl.md5 in versions:
                # This dl was listed multiple times.
                # Movies are listed once per OS :(.
                # Some .sh files are listed under both 32-bit and 64-bit.
                # FIXME: if it's a .sh, maybe copy the symlink, or link to it?

                # At least mark the file as found if it does exist, so
                # we don't confuse it with anything else.
                if os.path.lexists(os.path.join(target_dir, filename)):
                    self.application.found_file(target_dir, filename)
                continue
            versions[dl.md5] = True

            self.application.enqueue(self, item, dl, target_dir, filename, unpack)

    def download_filename(self, dl):
        return dl.filename

    def download_path(self, dl):
        raise NotImplementedYetError, 'please override me'

    def should_unpack(self, dl):
        return False

    def resolve_missing(self, hdl_list, file_list):
        """Callback to check if any files match any HumbleDownloads.

        Returns a list of (FileMatch, hdl, filename)."""
        return []

    def filename_could_match(self, filename, filetype):
        # Don't match against any files. Force caller to fall back to
        # hoping there's only one file in the directory.
        if filetype == None: return False

        if filetype in SOUNDTRACK_TYPES:
            return filetype in filename or filetype.lower() in filename

        basename, ext = os.path.splitext(filename)
        if basename.endswith('.tar'):
            ext = '.tar' + ext

        if ext in ['.deb', '.rpm', '.tar.gz', '.tar.bz2', '.sh', '.bin', '.run',
                   '.exe', '.dmg', '.zip']:
            # We know this format.
            return ext == filetype

        # We don't know this format. It might match..?
        return True

    def find_closest_file(self, hdl, file_list):
        filetype = hdl.dl.filetype
        for filename in file_list:
            if self.filename_could_match(filename, filetype):
                return filename


    def resolve_missing_by_filetype(self, hdl_list, file_list):
        """A sample implementation of resolve_missing.

        You can use this directly if you want to, but be sure to
        implement does_match."""
        # For each download, if it has a filetype, and there is a file
        # in the directory that clearly matches that filetype, try to
        # match the two.
        #
        # If there is only one file in the directory and it doesn't
        # have a filetype, try to match it against all the
        # downloads. If it doesn't match any of them, return
        # UserInvestigate.
        #
        # If the download doesn't have any filetype and there is only
        # one download and only one file, try to match those two.
        actions = []
        file_list = file_list[:]
        hdl_list = hdl_list[:]

        while file_list and hdl_list:
            # Each time through the loop, we remove an element from
            # hdl_list.  We may also remove an element from file_list
            # if it seemed like the hdl matched it best.
            hdl = hdl_list[0]
            target_file = self.find_closest_file(hdl, file_list)
            if not target_file and len(file_list) != 1:
                # Presumably a new flavor -- .rpm when previously it
                # was just .deb or something.
                # Download it as new.
                hdl_list.pop(0)
                continue

            if target_file:
                # We're pretty sure this download corresponds to this file.
                hdl_to_try = [hdl]
            else:  # len(file_list) == 1
                # Otherwise, we're gonna have to try all the downloads.
                target_file = file_list[0]
                hdl_to_try = hdl_list

            for hdl in hdl_to_try:
                #print "Checking match:", hdl.target_filename, target_file
                action = self.does_match(hdl, target_file)
                if action:
                    break

            if not action:
                # We fell out of the loop and the file didn't match
                # any hdl.  Let's pick an arbitrary hdl (the last one)
                # and return UserInvestigate.
                action = UserInvestigate

            #print action, hdl, target_file
            file_list.remove(target_file)
            hdl_list.remove(hdl)
            actions.append(action(hdl, target_file))

        if file_list:
            # FIXME: this should be a warning. It might just be a
            # download that HIB doesn't offer any more, or it could be
            # a problem with humbug.
            print "Leftover files:", file_list

        return actions


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
        movie_path = os.path.join(MOVIES_SUBDIR, self.title)
        if dl.type == 'audio':
            movie_path = os.path.join(movie_path, GAME_TYPE_SUBDIR['audio'])
        return movie_path

    def download_filename(self, dl):
        # For some reason, the Humble Bundle people package their
        # movies as .zip files. In the annex they should be stored
        # unpacked.
        return UNPACKED_NAMES.get('{}/{}'.format(self.title, dl.name),
                                  dl.filename)

    def resolve_missing(self, *args, **kwargs):
        return self.resolve_missing_by_filetype(*args, **kwargs)

    def should_unpack(self, dl):
        # We keep soundtracks zipped. Movies should be unzipped.
        return not dl.type == 'audio' and dl.filetype not in ['FLAC', 'MP3']

    def does_match(self, hdl, filename):
        """Try to match two files up.

        If it's clearly a newer version based on version numbers,
        return OldVersion.  Otherwise, compare the md5s. If they're
        the same, return SameFile.  Otherwise, return False. Maybe the
        caller knows something we don't."""
        return UnpackedFile

class AlbumHandler(HumbugHandler):
    def download_path(self, dl):
        return os.path.join(ALBUMS_SUBDIR, self.title)

    def should_unpack(self, dl):
        # We can't really unpack albums, because the version is in the
        # zip filename.
        return False

class GameHandler(HumbugHandler):
    def download_path(self, dl):
        type_dir = GAME_TYPE_SUBDIR[dl.type]
        if isinstance(type_dir, dict):
            type_dir = type_dir[dl.arch]
        target_dir = os.path.join(GAMES_SUBDIR, self.title,
                                  type_dir)
        return target_dir

    FILEPART_RE = re.compile('[-_.]')
    NUMBER_RE = re.compile('(\d+)')
    def get_version_number(self, filename):
        """String munging function that gets to figure out if any part
        of this filename can be treated as a version number.

        Returns a list of potential version numbers, sorted in order
        of canonicality"""
        parts = self.FILEPART_RE.split(filename)
        current_versions = []
        # Will be turned into a DebianVersion at the end
        current_numbers = []
        for part in parts:
            if part in ['amd64', 'i386', 'x86', '32bit', '64bit', '64']:
                continue

            i_part = None
            num_found = self.NUMBER_RE.search(part)
            if num_found:
                i_part = int(num_found.group(1))

            # If any part looks like a timestamp, return that immediately.
            if i_part > 1000000000:
                current_versions.append(Timestamp(i_part))
                continue

            # Ditto for dates.
            if 20100000 < i_part < 20300000:
                current_versions.append(DateString(i_part))
                continue


            if  1012010 < i_part < 12312099:
                i_part_year = i_part % 10000
                if i_part_year // 100 == 20:
                    current_versions.append(BackwardsDateString(i_part))

            if i_part:
                current_numbers.append(i_part)

        if current_numbers:
            current_versions.append(DebianVersion(current_numbers))

        current_versions.append(parts[0])
        return current_versions

    def resolve_missing(self, *args, **kwargs):
        return self.resolve_missing_by_filetype(*args, **kwargs)

    def does_match(self, hdl, filename):
        """Try to match two files up.

        If it's clearly a newer version based on version numbers,
        return OldVersion.  Otherwise, compare the md5s. If they're
        the same, return SameFile.  Otherwise, return False. Maybe the
        caller knows something we don't."""
        hdl_version = self.get_version_number(hdl.target_filename)[0]
        # Try to find the same type of version number as in the remote version
        for local_version in self.get_version_number(filename):
            if type(hdl_version) == type(local_version) and \
                    hdl_version > local_version:
                return OldVersion

        # See if the MD5s are the same.
        local_path = os.path.join(hdl.target_dir, filename)
        if not os.path.exists(local_path):
            return LinkMissing

        if hdl.dl.md5 == utils.md5_file(local_path):
            return SameFile

        return False
