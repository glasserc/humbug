"""
property_builder.py: functions useful to build properties to access ElementTree

Ex.

import property_builder as p
class Section(object):
    title = p.text(p.find('div', 'title'))
"""

def find(*args, **kwargs):
    def wrapper(self):
        return self.node.find(*args, **kwargs)
    return wrapper

def text(element):
    def wrapper(self):
        return element(self).text.strip()
    return wrapper

def exists(element):
    def wrapper(self):
        return bool(element(self))
    return wrapper
