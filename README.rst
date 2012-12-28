Humbug is a program to manage your git-annex'd Humble Indie Bundle
files as more Bundles are released and the old ones updated.

It relies on the property that when a file is updated on the Humble
Bundle site, its filename changes, usually in a predictable way (a
version number increases). If the filename on the Humble Bundle site
exists locally, we don't need to download it again.

At present, you have to visit the Humble Bundle site manually and save
the page as home.html to use it.

You might be more interested in `humblepie
<https://github.com/zendeavor/humblepie/blob/master/humblepie>`_ or
`t4b's HIB script
<http://t4b.me/posts/downloading-all-your-hib-games/>`_.

Dependencies
------------

- BeautifulSoup4 (python-bs4)
- Python 2.7 (OrderedDict)
