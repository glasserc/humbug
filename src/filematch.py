class FileMatch(object):
    """Represents a match between a local file and a HumbugDownload.

    Individual subclasses represent different kinds of matches."""
    def __init__(self, hdl, local_filename):
        super(FileMatch, self).__init__()
        self.hdl = hdl
        self.local_filename = local_filename

class FileMatchAction(FileMatch):
    """This represents FileMatches that will perform some kind of action"""
    pass

class SameFile(FileMatchAction):
    """Represents that the local file is the file requested.

    Perhaps the filename is screwed up."""
    def __str__(self):
        return "Action: Rename {} to {}".format(
            self.local_filename, self.hdl.target_filename)

class OldVersion(FileMatchAction):
    """Represents that the local file matches an old version of the download.

    Blow the file away using git annex drop and git rm before downloading."""
    def __str__(self):
        return "Action: Delete {} and replace with version {}".format(
            self.local_filename, self.hdl.target_filename)

class FileMatchProblem(FileMatch):
    """This represents FileMatches that indicate a problem with data on-disk"""
    pass

class LinkMissing(FileMatchProblem):
    """Represents that the file is a plausible match but can't be verified.

    Tell the user to "git annex get" the file and rerun."""
    def __str__(self):
        return 'Problem: couldn\'t verify that {} was {} ("git annex get" and retry)'.format(
            self.local_filename, self.hdl.target_filename)

class UserInvestigate(FileMatchProblem):
    """Represents that someone's pulling some stupid.

    Maybe the file changed formats on the Humble Bundle page. The user
    should blow away the old format manually.
    """
    def __str__(self):
        return "Problem: couldn't figure out {}, please investigate " \
            "(perhaps version of {}?)".format(
            self.local_filename, self.hdl.target_filename)
