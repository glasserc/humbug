import os.path
import urlparse
from bs4 import BeautifulSoup
from src import property_builder as P
from src.config import SOUNDTRACK_TYPES, VIDEO_TYPES

class HumbleNode(object):
    """Class corresponding a node in the Humble Bundle download page.

    Many classes can be defined as special kinds of HumbleNodes."""
    def __init__(self, node):
        self.node = node

class HumbleDownload(HumbleNode):
    """A HumbleNode corresponding to a <div class="download">.

    This corresponds to a button on the Humble Bundle website, which
    generally means a downloadable file, though occasionally just
    means a link to an affiliate website or a Stream link."""

    name = property(
        P.text(P.find('span', 'label')))

    # Absent on a couple of elements where the link goes to a different website
    md5 = property(
        P.attr('href', P.find('a', 'dlmd5'), strip_hash=True))

    modified = property(
        P.attr('data-timestamp', P.find('a', 'dldate', optional=True)))

    url = property(
        P.attr('data-web', P.find('a')))

    filesize = property(
        P.text(P.find('span', 'mbs')))

    @property
    def type(self):
        """Return the OS that the binary corresponds to.

        Known values at present are linux, windows, mac, mac10.5,
        mac10.6+, air, flash.
        """
        a_node = self.node.find('a')
        # Download Air and Flash Package happen to be the texts for
        # the buttons on Canabalt, which has the same files for all
        # operating systems, so we treat it as a separate OS.
        if a_node.text.strip() == 'Download Air':
            return 'air'
        # Some other games offer a "Flash" version as well as native
        # packages. Treat Flash ones as a separate OS.
        if 'Flash' in a_node.text:
            return 'flash'
        if 'Mac OS 10.5' in a_node.text:
            return 'mac10.5'
        if 'Mac OS 10.6+' in a_node.text:
            return 'mac10.6+'

        dlnode = self.node.parent  # <div class="downloads linux show">
        classes = dlnode['class']
        for cls in classes:
            if cls == 'downloads':
                continue

            if cls == 'show':
                # just indicates that the div is visible
                continue

            return cls

    @property
    def type_nice(self):
        """User-friendlier version of type"""
        return {'linux': "Linux",
                'mac': "OSX",
                'mac10.5': "OSX 10.5",
                'mac10.6+': "OSX 10.6+",
                'flash': "Flash",
                'air': 'Adobe Air',
                'windows': 'Windows',
                }.get(self.type, self.type)

    @property
    def filetype(self):
        """The extension or other cue that someone will be able to use
        to recognize the download in a local file.

        None means you're on your own. Hopefully you've kept this file
        by itself in a directory.."""
        # Try the name
        words = self.name.split()
        if len(words) == 1:
            # Maybe it's x86_64.deb
            words = os.path.splitext(words[0])
            if not words[-1]:
                # it was just .zip or .sh or something
                words = [words[0]]
        if words[-1].startswith('.'):
            return words[-1]
        if words[-1] in SOUNDTRACK_TYPES:
            return words[-1]
        if words[-1] in VIDEO_TYPES:
            return words[-1]

        if self.name in ['Download', 'Download Mobile']:
            return None
        if self.name in ['Download Installer']:
            return '.exe'
        if self.type in ['air', 'flash']:
            # Who knows what those files will look like
            return None

        print "This is weird. Can't figure out the filetype for", self.name, self.filename
        return None

    @property
    def arch(self):
        classes = self.node['class']
        if 'arc64' in classes:
            return '64-bit'

        if '64-bit' in self.name:
            return '64-bit'

        return '32-bit'

    @property
    def filename(self):
        a_node = self.node.find('a')
        href = a_node['data-web']
        parsed = urlparse.urlparse(href)
        return parsed.path.strip('/')

    @property
    def is_file(self):
        return self.node.find('a')['data-web']. \
            startswith('http://files.humblebundle.com')

    def __str__(self):
        download_name = self.name
        if 'Download' in download_name:
            if self.filetype and not self.filetype == '.exe':
                download_name = self.filetype
            else:
                download_name = self.type_nice
        if self.type == 'audio':
            download_name = "Soundtrack ({})".format(download_name)
        if download_name in VIDEO_TYPES:
            download_name = "{} format".format(download_name)
        return download_name

class HumbleItem(HumbleNode):
    title = property(
        P.text(P.find('div', 'title')))
    subtitle = property(
        P.text(P.find('div', 'subtitle')))
    is_book = property(
        P.exists(P.text(P.find('div', 'downloads ebook'))))
    has_soundtrack = property(
        P.exists(P.text(P.find('div', 'downloads audio'))))

    def downloads(self):
        return map(HumbleDownload,
                   self.node.find_all('div', 'download'))

class HumblePage(object):
    def __init__(self, config):
        self.tree = BeautifulSoup(file(config.filename))

    @property
    def title(self):
        return self.tree.title.text

    def iteritems(self):
        return map(HumbleItem, self.tree.find_all('div', 'row'))
