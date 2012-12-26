"""
property_builder.py: functions useful to build properties to access ElementTree

Ex.

import property_builder as p
class Section(object):
    title = p.text(p.find('div', 'title'))
"""

def find(*args, **kwargs):
    optional = kwargs.pop('optional', False)
    def wrapper(self):
        node = self.node.find(*args, **kwargs)
        if not optional and not node:
            raise ValueError, "couldn't find node {} {} at {}".format(
                args, kwargs, self.node)
        return node
    return wrapper

def text(element):
    def wrapper(self):
        return element(self).text.strip()
    return wrapper

def attr(name, element, strip_hash=False):
    def wrapper(self):
        node = element(self)
        if not node: return node
        ret = node[name]
        if strip_hash:
            ret = ret.strip('#')
        return ret
    return wrapper

def exists(element):
    def wrapper(self):
        return bool(element(self))
    return wrapper
