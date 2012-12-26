import urlparse
from bs4 import BeautifulSoup
from src import property_builder as P

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

    @property
    def type(self):
        """Return the OS that the binary corresponds to.

        Known values at present are linux, windows, mac, mac10.5,
        mac10.6+, air, flash.
        """
        a_node = self.node.find('a')
        if a_node.text.strip() == 'Download Air':
            return 'air'
        if a_node.text.strip() == 'Flash Package':
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
