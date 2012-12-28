import os.path
import argparse
from collections import OrderedDict
from src import filematch
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

    def __str__(self):
        return "Download {} to {}/{}".format(self.dl.filename, self.target_dir,
                                           self.target_filename)

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

        wont_do_queue, action_queue = self.resolve_missing()
        action_queue = self.display_actions(wont_do_queue, action_queue)

        if action_queue == None:
            print "Aborting by user request."
            return

        if len(action_queue) == 0:
            print "Exiting: Nothing to do."
            return

        for action in action_queue:
            print "Performing:", action

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
        # dir -> [actions]
        wont_do_queue = {}

        for dir in self.download_queue:
            hdl_list = self.download_queue[dir]
            # Assume that the handler for the first should be the handler for all of them
            handler = hdl_list[0].handler

            unknown_files = self.encountered_files.get(dir, [])
            action_list = handler.resolve_missing(
                hdl_list, unknown_files)
            this_dir_actions = []
            for action in action_list:
                unknown_files.remove(action.local_filename)
                hdl_list.remove(action.hdl)
                # execute action
                this_dir_actions.append(action)

            for hdl in hdl_list:
                this_dir_actions.append(hdl)

            if any(isinstance(action, filematch.FileMatchProblem)
                   for action in this_dir_actions):
                wont_do_queue[dir] = this_dir_actions
            else:
                action_queue.extend(this_dir_actions)

        return (wont_do_queue, action_queue)

    def display_actions(self, wont_do_queue, actions_queue):
        """
        Show the user the actions to be performed and get their confirmation.

        Return a list of actions to be performed. These actions can be
        HumbugDownloads, or SameFile or OldVersion actions.
        """
        print "Problems were found with these downloads:"
        for dir, actions in wont_do_queue.iteritems():
            # print problems before non-taken actions
            problems = [action for action in actions
                        if isinstance(action, filematch.FileMatchProblem)]

            # These should all be FileMatchActions or HumbugDownloads
            not_problems = [action for action in actions if
                            action not in problems]
            print "\n".join("  {!s}".format(problem) for problem in problems)

            if not_problems:
                print "\n".join("    - {!s} (other problems in this directory)".format(action)
                                for action in not_problems)

        print
        print "Will perform these actions:"
        print "\n".join("  {!s}".format(action) for action in actions_queue)

        print
        if actions_queue:
            resp = raw_input("Does this seem right? [y/N] ")
            if not resp.lower().startswith('y'):
                return None

        return actions_queue
