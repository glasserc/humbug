import os.path
import argparse
from collections import OrderedDict
from src.humble_page import HumblePage
from src.config import ANNEX_LOCATION
from src.handlers import GameHandler, MovieHandler, BookHandler

class HumbugDownload(object):
    def __init__(self, handler, item, dl, target_dir, target_filename, unpack):
        self.handler = handler
        self.item = item
        self.dl = dl
        self.target_dir = target_dir
        self.target_filename = target_filename
        self.unpack = unpack

class Humbug(object):
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(description="munge Humble Bundle page into a git annex")
        parser.add_argument('filename', type=str,
                            help="a saved version of the home.html page")
        self.config = parser.parse_args(args)
        # List of local files we had in the relevant directories.
        self.encountered_files = {}
        # List of local files we had that were matched.
        # dir -> set(files)
        self.found_files = {}
        # List of files we don't have already.
        # dir -> [hdl]
        self.download_queue = OrderedDict()

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

        self.resolve_missing()

    def found_file(self, target_dir, target_file):
        self.found_files.setdefault(target_dir, set()).add(target_file)

    def enqueue(self, handler, item, dl, target_dir, target_filename=None, unpack=False):
        """Download from the link contained in `dl` a file to the path
        in target_dir."""
        if target_filename == None:
            target_filename = dl.filename
        full_path = os.path.join(target_dir, target_filename)

        if os.path.exists(target_dir):
            self.encountered_files[target_dir] = os.listdir(target_dir)

        # Use lexists because this could be a symlink that wasn't
        # annex-get'd on this machine
        if os.path.lexists(full_path):
            #print "  Exists:", target_filename
            self.found_file(target_dir, target_filename)
        else:
            #print "  Get:", full_path, dl.type, dl.name, dl.md5, dl.modified
            self.download_queue.setdefault(target_dir, []).append(
                HumbugDownload(handler, item, dl, target_dir, target_filename, unpack))

    def resolve_missing(self):
        """See if the queued downloads correspond to extant files.

        A Handler can say that a download matches a file by returning
        SameFile, suggest that the file might match if the file were
        "git annex get"'d by returning LinkMissing, or say that the
        extant file needs to be blown away and replaced by returning
        OldVersion."""
        # Remove all the found files from self.encountered_files
        for dir, files in self.found_files.iteritems():
            for file in files:
                self.encountered_files[dir].remove(file)

        action_queue = []

        for dir in self.download_queue:
            hdl_list = self.download_queue[dir]
            # Assume that the handler for the first should be the handler for all of them
            handler = hdl_list[0].handler

            unknown_files = self.encountered_files.get(dir, [])
            action_list = handler.resolve_missing(
                hdl_list, unknown_files)

            for action in action_list:
                (action_type, hdl, file) = action
                unknown_files.remove(file)
                hdl_list.remove(hdl)
                # execute action
                action_queue.append(action)

            for hdl in hdl_list:
                action_queue.append(("Download", hdl, hdl.target_filename))

        for action in action_queue:
            # Execute action.
            #print action
            pass
