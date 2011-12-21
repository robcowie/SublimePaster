# -*- coding: utf-8 -*-


import httplib
import urllib
import urllib2
import api


class Pastie(api.PastebinImplementation):

    SYNTAXES = {
       #'syntax'     : 'pastie language code'
        'javascript' : 'javascript',
        'json'       : 'javascript',
        'rb'         : 'ruby',
        'hs'         : 'literate_haskell',
        'tst'        : 'plain_text',
        'plaintext'  : 'plain_text',
        'html5'      : 'html', 
        'shell-unix-generic' : 'shell-unix-generic'
    }

    def url(self):
        print self.config.get('url')
        return self.config.get('url') or 'http://pastie.org/'

    def upload(self, content):
        params = {
            'paste[authorization]': 'burger',
            'paste[parser]': 'plain_text',
            'paste[body]': content,
            'paste[restricted]': self.config.get('private') or 0
        }
        if self.config.get('username') is not None:
            params['paste[display_name]'] = self.config.get('username')

        connection = httplib.HTTPConnection('pastie.org')
        connection.request('POST', '/pastes/create', urllib.urlencode(params))
        response = connection.getresponse()
        return response.getheader('Location', '')

    def fetch(self, paste_id):
        raise api.TransportError('Not implemented')
