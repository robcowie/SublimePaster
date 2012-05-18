# -*- coding: utf-8 -*-


import httplib
import urllib
import api


class Pastie(api.PastebinImplementation):

    SYNTAXES = {
       #'syntax'     : 'pastie language code'
       'apache'     : 'apache',
       'python'     : 'python',
       'php'        : 'php',
       'sql'        : 'sql',
       'javascript' : 'javascript',
       'json'       : 'javascript',
       'css'        : 'css',
       'xml'        : 'html',
       'html'       : 'html',
       'diff'       : 'diff',
       'rb'         : 'ruby',
       'hs'         : 'haskell',
       'sh'         : 'shell-unix-generic',
       'java'       : 'java',
       'plaintext'  : 'plain_text'
       }

    def url(self):
        print self.config.get('url')
        return self.config.get('url') or 'http://pastie.org/'

    def upload(self, content):
        syntax = 'plain_text'

        if self.syntax() in self.SYNTAXES:
            syntax = self.SYNTAXES[self.syntax()]

        params = {
            'paste[authorization]': 'burger',
            'paste[parser]': syntax,
            'paste[body]': content,
            'paste[restricted]': abs(self.config.get('private')) or 0
        }
        if self.config.get('username') is not None:
            params['paste[display_name]'] = self.config.get('username')

        connection = httplib.HTTPConnection('pastie.org')
        connection.request('POST', '/pastes/create', urllib.urlencode(params))
        response = connection.getresponse()
        return response.getheader('Location', '')

    def fetch(self, paste_id):
        raise api.TransportError('Not implemented')
