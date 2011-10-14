# -*- coding: utf-8 -*-


import api
from vendor import lodgeitlib


class Lodgeit(api.PastebinImplementation):

    ## Lodgeit supports all languages pygments does, so the normalised 
    ## syntax name is tried if no match here
    SYNTAXES = {
       #'syntax'     : 'lodgeit language code'
        'python'     : 'python',
        'sql'        : 'sql',
        'javascript' : 'js',
        'json'       : 'js',
        'css'        : 'css',
        'xml'        : 'xml',
        'diff'       : 'diff',
        'rb'         : 'ruby',
        'rhtml'      : 'rhtml',
        'hs'         : 'literate-haskell',
        'sh'         : 'bash', 
        'ini'        : 'ini', 
        'tst'        : 'text',
        'plaintext'  : 'text',
        'yaml'       : 'yaml', 
        'html'       : 'html', 
        'html5'      : 'html', 
    }

    def __init__(self, view):
        super(Lodgeit, self).__init__(view)
        self.pastebin = lodgeitlib.Lodgeit(
            self.config.get('url'), 
            username=self.config.get('username'), 
            password=self.config.get('password')
        )

    def upload(self, content):
        lang = self.syntax() or self.normalised_syntax()
        content = self.prepare(content)
        paste_id = self.pastebin.new_paste(
            content, lang, parent=None, 
            filename='', mimetype='', private=False)
        new_paste = self.pastebin.get_paste_by_id(paste_id)
        return new_paste.url

    def fetch(self, paste_id):
        """Return a 3-tuple with paste content (unicode), the sublime text 
        language if known and the paste url.
        e.g. (u'interesting content', 'plain', 'http://')
        """
        lodgeit_to_subl_lang = dict((v, k) for k, v in self.SYNTAXES.iteritems())
        p = self.pastebin.get_paste_by_id(paste_id)
        if not p:
            raise api.TransportError("Cannot fetch paste id '%s'" % paste_id)
        return (p.code, lodgeit_to_subl_lang.get(p.language, None), p.url)
