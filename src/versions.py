"""
Kinds of version numbers we find in Humble filenames.
"""

class VersionNumber(object):
    def __init__(self, verno):
        self.raw_version = verno

class Timestamp(VersionNumber):
    pass

class DateString(VersionNumber):
    pass

class DebianVersion(VersionNumber):
    """Something like 1.6.1-3"""
    pass
