# -*- coding: utf-8 -*-

"""
"""

import sublime_plugin
import sublime

from src import api

api.load()


### THE COMMANDS ###
class PastebinPostCommand(sublime_plugin.TextCommand):
    """"""
    def __init__(self, view):
        super(PastebinPostCommand, self).__init__(view)

    def run(self, edit):
        try:
            ## Select the pastebin implementation
            implementation = self.get_pastebin_implementation()
            paster = implementation(self.view)
            ## Upload and set status
            content = self.selected_content()
            paste_url = paster.upload(content)
            sublime.set_clipboard(paste_url)
            sublime.status_message("%s. URL has been copied to the clipboard." % paste_url)
        except Exception, exc:
            sublime.error_message("Unable to create paste")
            # print('Exception: %s' % exc)
            raise

    def get_pastebin_implementation(self):
        mode_setting = self.view.settings().get('pastebin')['mode']
        for impl in api.PastebinImplementation.plugins:
            if mode_setting == impl._name:
                return impl
        raise ValueError('Unknown pastebin mode `%s`' % mode_setting)

    def selected_content(self):
        """
        Return the selected region or the entire buffer contents
        if no region is selected.
        """
        content = '\n'.join([self.view.substr(region) for region in self.view.sel()])
        if not content:
            content = self.view.substr(sublime.Region(0, self.view.size()))
        return content


class PastebinFetchCommand(sublime_plugin.TextCommand):
    """"""
    def run(self, edit):
        try:
            self.edit = edit
            self.view.window().show_input_panel('Paste id', '', self.on_paste_id, None, None)
        except Exception, exc:
            sublime.error_message("Unable to fetchpaste")
            print('Exception %s' % exc)

    def get_pastebin_implementation(self):
        mode_setting = self.view.settings().get('pastebin')['mode']
        for impl in api.PastebinImplementation.plugins:
            if mode_setting == impl._name:
                return impl
        raise ValueError('Unknown pastebin mode `%s`' % mode_setting)

    def on_paste_id(self, paste_id):
        implementation = self.get_pastebin_implementation()
        paster = implementation(self.view)
        try:
            data, lang, url = paster.fetch(paste_id)
        except api.TransportError, exc:
            sublime.status_message(str(exc))
            return

        ## If view is empty set the syntax
        ## TODO: How to derive the syntax_file?
        # if not self.view.size() and lang:
            # self.view.set_syntax_file()

        ## Insert
        for region in self.view.sel():
            self.view.erase(self.edit, region)
            self.view.insert(self.edit, region.begin(), data)

        sublime.status_message("Fetched from %s" % url)
