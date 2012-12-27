"""
Kinds of version numbers we find in Humble filenames.
"""

class VersionNumber(object):
    def __init__(self, verno):
        self.raw_version = verno

    def __lt__(self, rhs):
        return type(self) == type(rhs) and self.raw_version < rhs.raw_version

class Timestamp(VersionNumber):
    pass

class DateString(VersionNumber):
    pass

class DebianVersion(VersionNumber):
    """Something like 1.6.1-3"""
    pass
