# -*- coding: utf-8 -*-


import httplib
import urllib
import api


class Pastie(api.PastebinImplementation):

    SYNTAXES = {
       #'syntax'     : 'pastie language code'
       'apache'     : '22',
       'python'     : '16',
       'php'        : '15',
       'sql'        : '14',
       'javascript' : '10',
       'json'       : '10',
       'css'        : '8',
       'xml'        : '11',
       'html'       : '11',
       'diff'       : '5',
       'rb'         : '3',
       'hs'         : '29',
       'sh'         : '13',
       'java'       : '9',
       'plaintext'  : '6'
       }

    def url(self):
        return self.config.get('url') or 'pastie.org'

    def upload(self, content):
        syntax = '6'
        if self.syntax() in self.SYNTAXES:
            syntax = self.SYNTAXES[self.syntax()]

        params = {
            'utf8': '&#x2713;',
            'paste[authorization]': 'burger',
            'paste[access_key]': 'hidden',
            'paste[parser_id]': syntax,
            'paste[body]': content,
            'paste[restricted]': abs(self.config.get('private', 0)) or 0
        }

        connection = httplib.HTTPConnection(self.url())
        connection.request('POST', '/pastes', urllib.urlencode(params))
        response = connection.getresponse()
        return response.getheader('Location', '')

    def fetch(self, paste_id):
        raise api.TransportError('Not implemented')
