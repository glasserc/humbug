class FileMatch(object):
    """Represents a match between a local file and a HumbugDownload.

    Individual subclasses represent different kinds of matches."""
    pass

class SameFile(FileMatch):
    """Represents that the local file is the file requested.

    Perhaps the filename is screwed up."""
    pass

class LinkMissing(FileMatch):
    """Represents that the file is a plausible match but can't be verified.

    Tell the user to "git annex get" the file and rerun."""
    pass

class OldVersion(FileMatch):
    """Represents that the local file matches an old version of the download.

    Blow the file away using git annex drop and git rm before downloading."""
    pass

class UserInvestigate(FileMatch):
    """Represents that someone's pulling some stupid.

    Maybe the file changed formats on the Humble Bundle page. The user
    should blow away the old format manually.
    """
    pass
