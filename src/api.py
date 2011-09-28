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
        """Return the url to the new paste"""
        raise NotImplementedError()

    def fetch(self, id):
        """Return (content, syntax, url)"""
        raise NotImplementedError()

    def normalised_syntax(self):
        """Return our best guess given the language file path"""
        syntax = self.view.settings().get('syntax')
        syntax.lower()\
            .replace('.tmlanguage', '')\
            .replace(' ', '')\
            .rsplit('/', 1)[-1]

    def syntax(self):
        syntax = self.normalise_syntax(syntax)
        """Return a syntax known to the pastebin"""
        return self.SYNTAXES.get(syntax, '')
