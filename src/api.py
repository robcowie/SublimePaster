# -*- coding: utf-8 -*-


def load():
    import lodgeit
    import dpaste


class TransportError(Exception):
    pass


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)
            if not hasattr(cls, '_name'):
                cls._name = cls.__name__.lower()


class PastebinImplementation(object):

    __metaclass__ = PluginMount

    SYNTAXES = {}

    def __init__(self, view):
        self.view = view
        self.config = self.view.settings().get('pastebin')

    def prepare(self, content):
        return content

    def upload(self, content):
        raise NotImplementedError()

    def fetch(self, id):
        raise NotImplementedError()

    def language(self):
        ##TODO: rename to syntax
        syntax = self.view.settings().get('syntax')
        syntax = syntax.lower()\
            .replace('.tmlanguage', '')\
            .replace(' ', '')\
            .rsplit('/', 1)[-1]
        return self.SYNTAXES.get(syntax)
