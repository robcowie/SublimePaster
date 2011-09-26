# -*- coding: utf-8 -*-
# Copyright (c) 2008, 2009, 2010 Sebastian Wiesner <lunaryorn@googlemail.com>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


"""
    lodgeitlib
    ==========

    A convenient client library for the Lodgeit_ pastebin software.

    .. _Lodgeit: http://dev.pocoo.org/projects/lodgeit/

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


__version__ = '0.6'


import re
import logging
import json
from collections import namedtuple
from urllib import urlencode
import urllib2
from urllib2 import urlopen, Request
from datetime import datetime
from urlparse import urlsplit, urljoin
from contextlib import closing


log = logging.getLogger(__name__)


class UnsupportedLanguageError(Exception):
    """Inidicate an unsupported language."""


class JSONProxy(object):
    def __init__(self, url, name=''):
        self._url = url
        self._name = name

    def __getattr__(self, attr):
        if attr.startswith('_'):
            return object.__getattr__(self, attr)
        name = '{0}.{1}'.format(self._name, attr) if self._name else attr
        return self.__class__(self._url, name=name)
    
    def _setup_authentication(self):
        pass
    
    def __call__(self, **kwargs):
        log.debug('calling %s with args %r at url %s',
                  self._name, kwargs, self._url)
        url = '{0}?{1}'.format(self._url, urlencode({'method': self._name}))
        request = Request(url, json.dumps(kwargs))
        request.add_header('Content-Type', 'application/json')
        with closing(urlopen(request)) as stream:
            response = json.loads(stream.read())
            log.debug('got response %r', response)
            return response['data']


_Paste = namedtuple('_Paste', 'lodgeit id parent_id code parsed_code '
                    'language publication_date relative_url')


class Paste(_Paste):
    """
    A :class:`~collections.namedtuple` for a single paste.
    """

    @classmethod
    def from_json_response(cls, lodgeit, response):
        """
        Create a :class:`Paste` object from a JSON RPC ``response``.

        ``lodgeit`` is the :class:`Lodgeit` instance, which performed the
        JSON RPC call.  ``response`` is a mapping as returned by the JSON RPC
        API.

        Return a :class:`Paste` object, or ``None``, if ``response`` is
        ``None``.
        """
        if not response:
            return None
        fields = dict(response)
        fields['lodgeit'] = lodgeit
        fields['id'] = fields.pop('paste_id')
        fields['relative_url'] = fields.pop('url')
        fields['publication_date'] = datetime.fromtimestamp(
            fields.pop('pub_date'))
        return cls(**fields)

    def get_parent(self):
        """
        Fetch the parent paste of this paste.

        Return the parent paste as :class:`Paste` instance, or ``None``, if
        this paste has no parent.
        """
        if self.parent_id is None:
            return None
        return self.lodgeit.get_paste_by_id(self.parent_id)

    def __repr__(self):
        return '<Paste({0!r}) at {1:#x}>'.format(self.id, id(self))

    def __str__(self):
        return self.code

    @property
    def url(self):
        """
        The complete url of this paste as string.
        """
        return (urljoin(self.lodgeit.url, self.relative_url)
                if self.relative_url else None)

    @property
    def language_desc(self):
        """
        The descriptive name of the language of this paste as string.
        """
        return (self.lodgeit.languages[self.language]
                if self.language else None)


class Lodgeit(object):
    """
    Client access to Lodgeit pastebins.

    This class uses the JSON RPC service to retrieve or create pastes in
    pastebins, which are based on the Lodgeit software.

    It performs internal caching, if :attr:`caching` is ``True``. If caching
    is enabled, pastes, which are fetched by id, are first looked up in an
    internal cache.

    .. note::

       :meth:`get_last_paste` and :meth:`get_recent_pastes` are not cached,
       because there is no way to determine the age of a paste from the
       cache.

    The list of available languages (see :attr:`languages`) is fetched, when
    it's first needed, and cached for any later access, even if
    :attr:`caching` is ``False``.  You may however use
    :meth:`reset_languages` to reset this cache.

    This class is not thread-safe, at least not if caching is
    enabled. Multiple threads should not access this pastebin without proper
    synchronisation.
    """

    URL_ID_PATTERN = re.compile('^/show/(.+)/$')

    def __init__(self, pastebin_url, username=None, password=None, 
                 service_url=None, caching=True):
        """
        Create a new :class:`Lodgeit` instance for the pastebin at the given
        url.

        ``pastebin_url`` is a string containing an url, which points to the
        a Lodgeit pastebin (to the starting page, not to any subpage).
        ``service_url`` is the url of the JSON RPC service for this
        pastebin.  If not given, the service url is derived from the
        pastebin url.  ``caching`` is a boolean (defaulting to ``True``),
        which indicates whether :class:`Paste` instances are cached.
        """
        self.url = pastebin_url
        self.service_url = service_url or urljoin(pastebin_url, 'json/')
        self._lodgeit = JSONProxy(self.service_url)
        self._cache = {}
        self._languages = None
        self.caching = caching
        if username and password:
            self._setup_authentication(username, password)
    
    def _setup_authentication(self, username, password):
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        top_level_url = self.url
        password_mgr.add_password(None, top_level_url, username, password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    @property
    def hostname(self):
        """
        The hostname of this paste as string.
        """
        return urlsplit(self.url).netloc

    def __repr__(self):
        return '<Lodgeit({0!r}) at {1!r}>'.format(self.service_url, id(self))

    def _get_paste_from_result(self, response):
        paste = Paste.from_json_response(self, response)
        if paste:
            self._cache[paste.id] = paste
        return paste

    def id_from_url(self, url):
        """
        Extract a paste id from the given ``url``.

        ``url`` is a string containing the url of a paste.

        Return the paste id as string, or raise
        :exc:`~exceptions.ValueError`, if a valid id could not be found in
        the given url.
        """
        components = urlsplit(url)
        if components.netloc != self.hostname:
            raise ValueError('not a url for {0!r}'.format(self.hostname))
        match = self.URL_ID_PATTERN.search(components.path)
        if not match:
            raise ValueError('could not parse url')
        paste_id = match.group(1)
        log.debug('extracted %s from url %s', paste_id, url)
        return paste_id

    def _to_id(self, id_or_url):
        if isinstance(id_or_url, basestring):
            try:
                return self.id_from_url(id_or_url)
            except ValueError:
                pass
        return id_or_url

    def get_paste_by_id(self, id_or_url):
        """
        Retrieve the paste with the given ID or URL.

        ``id_or_url`` is a string or integer containing a paste ID or a
        paste URL.

        The retrieved paste is cached, if :attr:`caching` is ``True``.

        Return the :class:`Paste` object for ``id`` or ``None``, if there is
        no such paste.
        """
        paste_id = self._to_id(id_or_url)
        log.debug('getting paste %s', paste_id)
        if self.caching and paste_id in self._cache:
            log.debug('found paste %s in cache', paste_id)
            return self._cache[paste_id]
        else:
            log.debug('fetching paste %s from server', paste_id)
            return self._get_paste_from_result(
                self._lodgeit.pastes.getPaste(paste_id=paste_id))

    def get_last_paste(self):
        """
        Retrieve the last paste and return it as :class:`Paste` object.

        The return value of this method is never cached.
        """
        log.debug('fetching last paste from server')
        return self._get_paste_from_result(self._lodgeit.pastes.getLast())

    def get_recent_pastes(self, amount=5):
        """
        Retrieve the most recent pastes.

        ``amount`` is an integer specifying how many of the most recent
        pastes should be retrieved.  This method is never cached.

        Return a list of :class:`Paste` objects.
        """
        log.debug('fetching %s most recent pastes from server', amount)
        pastes = self._lodgeit.pastes.getRecent(amount=amount)
        return map(self._get_paste_from_result, pastes)

    @property
    def languages(self):
        """
        The languages supported by the paste bin as a mapping from the
        language identifier to a descriptive name of this language.
        """
        if not self.has_languages:
            log.debug('querying supported languages from server')
            self._languages = dict(self._lodgeit.pastes.getLanguages())
        return self._languages

    @property
    def has_languages(self):
        """
        ``True``, if the internal language cache is filled, ``False``
        otherwise.
        """
        return bool(self._languages)

    def reset_languages(self):
        """
        Clear the internal language cache.
        """
        log.debug('clearing language cache')
        self._languages = None

    def new_paste(self, code, language, parent=None, filename='',
                  mimetype='', private=False):
        """
        Create a new paste.

        ``code`` is a unicode string with the code to be pasted.
        ``language`` is a string with the programming or markup language,
        the code is written in (used for server-side highlighting).
        ``parent`` is the parent paste, either a string or integer with a
        paste ID or URL, or as :class:`Paste` object.  ``filename`` and
        ``mimetype`` a strings providing the name of the file, the paste
        contents were read from, and the mimetype of the paste contents.
        ``private`` is a boolean inidicating, whether the paste should be
        private or not.

        Pastes can have a parent paste.  This is part of the \"paste reply\"
        functionality of the Lodgeit, which is described in detail under
        `Advanced features`_.

        Private pastes (``private`` is ``True``) do not get a nummeric id,
        but only a random hash, and do not appear in the list of all pastes.

        Return the id of the created paste as integer (public pastes) or as
        string (private pastes).  Raise :exc:`UnsupportedLanguageError`, if
        ``language`` is not supported (e.g. not contained in
        :attr:`languages`).

        .. _`Advanced features`: http://paste.pocoo.org/help/advanced/
        """
        if not isinstance(code, unicode):
            raise TypeError('code must be unicode')

        if language and language not in self.languages:
            raise UnsupportedLanguageError(language)

        if isinstance(parent, Paste):
            parent_id = parent.id
        else:
            parent_id = self._to_id(parent)
        log.debug('creating new paste with %r (language: %s, parent: %s, '
                  'mime-type: %s, filename: %s, private: %r)',
                  code, language, parent_id, mimetype, filename, private)
        paste_id = self._lodgeit.pastes.newPaste(
            language=language, code=code, parent_id=parent_id,
            filename=filename, mimetype=mimetype, private=private)
        if not private:
            paste_id = int(paste_id)
        return paste_id


#: An instance of :class:`Lodgeit` for http://paste.pocoo.org.
# pocoo_pastebin = lodgeit = Lodgeit('http://paste.pocoo.org')
#: An instance of :class:`Lodgeit` for http://bpaste.net
# bpaste_pastebin = Lodgeit('http://bpaste.net')

#: a list of :class:`Lodgeit` objects for all known lodgeit pastebins
# PASTEBINS = [pocoo_pastebin, bpaste_pastebin]