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

class BackwardsDateString(DateString):
    """Like a DateString, only some doofus wrote it in MMDDYYYY format"""
    def __init__(self, verno):
        yyyy = verno % 10000
        verno = verno // 10000
        dd = verno % 100
        mm = verno // 100
        verno = ''.join([str(yyyy), '{:02d}'.format(mm), '{:02d}'.format(dd)])
        super(BackwardsDateString, self).__init__(int(verno))

class DebianVersion(VersionNumber):
    """Something like 1.6.1-3"""
    pass
