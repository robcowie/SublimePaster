# -*- coding: utf-8 -*-

"""
With thanks to brianriley
https://github.com/brianriley/sublime-dpaste
"""

import httplib
import urllib
import urllib2
import api


class Dpaste(api.PastebinImplementation):

    _name = 'dpaste'

    SYNTAXES = {
       #'syntax'     : 'dpaste language code'
        'apache'     : 'Apache',
        'python'     : 'Python',
        'django'     : 'DjangoTemplate',
        'sql'        : 'Sql',
        'javascript' : 'JScript',
        'json'       : 'JScript',
        'css'        : 'Css',
        'xml'        : 'Xml',
        'diff'       : 'Diff',
        'rb'         : 'Ruby',
        'rhtml'      : 'Rhtml',
        'hs'         : 'Haskell',
        'sh'         : 'Bash', 
        'plaintext'  : ''
    }

    def upload(self, content):
        params = urllib.urlencode({
            'content': content, 
            'language': self.syntax()
        })

        connection = httplib.HTTPConnection('dpaste.com')
        connection.request('POST', '/api/v1/', params)
        response = connection.getresponse()
        if response.status == 302:
            return response.getheader('Location', '')
        else:
            raise api.TransportError('There was an error. Please try again later.')

    def fetch(self, paste_id):
        # dpaste_to_subl_lang = dict((v, k) for k, v in self.SYNTAXES.iteritems())
        url = 'http://dpaste.com/%s/plain/' % paste_id
        try:
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            data = response.read().decode('utf8')
        except urllib2.HTTPError, exc:
            msg = str(exc)
            if exc.code == 404:
                msg = "Unknown paste id '%s'" % paste_id
            raise api.TransportError(msg)

        return (data, None, url)
