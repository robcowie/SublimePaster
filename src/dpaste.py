# -*- coding: utf-8 -*-

"""
With thanks to brianriley
https://github.com/brianriley/sublime-dpaste
"""

import httplib
import urllib
import api


class Dpaste(api.PastebinImplementation):

    _name = 'dpaste'

    SYNTAXES = {
       #'syntax'     : 'dpaste language code'
        'python'     : 'Python',
        'sql'        : 'Sql',
        'javascript' : 'JScript',
        'json'       : 'JScript',
        'css'        : 'Css',
        'xml'        : 'Xml',
        'diff'       : 'Diff',
        'rb'         : 'Ruby',
        'rhtml'      : 'Rhtml',
        'hs'         : 'Haskell',
        'sh'         : 'Bash'
    }

    def upload(self, content):
        params = urllib.urlencode({
            'content': content, 
            'language': self.language() or ''
        })

        connection = httplib.HTTPConnection('dpaste.com')
        connection.request('POST', '/api/v1/', params)
        response = connection.getresponse()
        if response.status == 302:
            return response.getheader('Location', '')
        else:
            raise api.TransportError('There was an error. Please try again later.')
