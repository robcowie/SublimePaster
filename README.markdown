# Sublime Paster

A Sublime Text 2 plugin to provide Post/Fetch support for multiple pastebins, including Lodgeit and dpaste.com


# Install & Config

    $ cd /sublime/text/Packages/
    $ git clone https://robcowie@github.com/robcowie/sublime_paster.git

Add config to User file settings. Only required key is `mode`.

    "pastebin": {
        "mode": "dpaste",
        "copy_to_clipboard": true
    }

If the pastebin implementation needs further config, such as user credentials add it here, i.e.

    "pastebin": {
        "mode"       : "dpaste",
        "username"   : "Tim the Enchanter", 
        "password"   : "antioch", 
        "user_token" : "e4023a6b-a9fc-40d8-bdfb-357ea7bb60cb"
    }

A good example for using Pastie is:

    "pastebin": {
        "mode": "pastie",
        "username" : "Tim the Enchanter"
        "copy_to_clipboard": true,
        "prompt_on_post" : false,
        "private": true,
    }

# Usage

Default key bindings are shift+ctrl+p to post and shift+ctrl+f to fetch


# License

All of Sublime Package Control is licensed under the MIT license.

Copyright (c) 2011 Rob Cowie <szaz@mac.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.