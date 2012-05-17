# -*- coding: utf-8 -*-


import httplib
import urllib
import api


class Pastie(api.PastebinImplementation):

    def url(self):
        print self.config.get('url')
        return self.config.get('url') or 'http://pastie.org/'

    def upload(self, content):
        params = {
            'paste[authorization]': 'burger',
            'paste[parser]': 'plain_text',
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
