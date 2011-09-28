# -*- coding: utf-8 -*-

"""
"""

import sublime_plugin
import sublime

from src import api

api.load()


### THE COMMANDS ###
class PasterCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        super(PasterCommand, self).__init__(view)
        # self.window = self.view.window()
        self.window = sublime.active_window()
        self.settings = self.view.settings().get('pastebin')
        self.Paster = self.get_pastebin_implementation()

    def get_pastebin_implementation(self):
        mode = self.settings.get('mode')
        for impl in api.PastebinImplementation.plugins:
            if mode == impl._name:
                return impl
        raise ValueError('Unknown pastebin mode `%s`' % mode)

    def status(self, msg, clipboard=None):
        """Display message and optionally set clipboard contents"""
        if clipboard:
            sublime.set_clipboard(clipboard)
        sublime.status_message(msg)


class PastebinPostCommand(PasterCommand):
    """"""
    def run(self, edit):
        try:
            self.paster = self.Paster(self.view)
            self.content = self.selected_content()
            if not self.content:
                raise ValueError('No content to post')
            if not self.settings.get('prompt_on_post'):
                self.go()
            else:
                self.window.show_input_panel(
                    'Confirm post snippet? [y/n]', 'y', self.go, None, None)
        except Exception, exc:
            self.status(str(exc))

    def go(self, confirm_choice='y'):
        if confirm_choice.lower() == 'y':
            paste_url = self.paster.upload(self.content)
            if self.settings.get('copy_to_clipboard', True):
                self.status("%s. URL has been copied to the clipboard." % paste_url, paste_url)
            else:
                self.status(paste_url)
        else:
            self.status('Cancelled')

    def selected_content(self):
        """
        Return the selected region or the entire buffer contents
        if no region is selected.
        """
        content = u'\n'.join([self.view.substr(region) for region in self.view.sel()])
        if not content:
            content = self.view.substr(sublime.Region(0, self.view.size()))
        return content


class PastebinFetchCommand(PasterCommand):
    """"""
    def run(self, edit):
        self.edit = edit
        self.window.show_input_panel('Paste id', '', 
            self.on_paste_id, None, None)

    def on_paste_id(self, paste_id):
        try:
            paste_id = paste_id.strip()
            paster = self.Paster(self.view)
            data, lang, url = paster.fetch(paste_id)

            ## If view is empty set the syntax
            ## TODO: How to derive the syntax_file?
            # if not self.view.size() and lang:
                # self.view.set_syntax_file()

            ## Insert
            for region in self.view.sel():
                self.view.erase(self.edit, region)
                self.view.insert(self.edit, region.begin(), data)

            self.status("Fetched from %s" % url)
        except api.TransportError, exc:
            self.status(str(exc))
        except Exception, exc:
            self.status("Unable to fetch paste (%s)" % exc)
