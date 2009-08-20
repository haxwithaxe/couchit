#!/usr/bin/env python

# -*- coding: utf-8 -
#
# Copyright (c) 2008,2009 Benoit Chesneau <benoitc@e-engura.com> 
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import os
import sys

from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

sys.path.append("../tools")
from merge_css import MergeCSS
from merge_js import MergeJS

if  __name__ == "__main__":
    # merge css and compact it
    merge_css = MergeCSS('couchit.yml')
    merge_css.run()
    
    # merge js and minify
    merge_js = MergeJS('couchit.yml')
    merge_js.run()
    
    # generate pygments styles
    
    for style in get_all_styles():
        highlight_css =  os.path.join("../static/css", "%s.css" % style)
        print "generate %s" % highlight_css
        css = HtmlFormatter(style=style).get_style_defs('.codehilite')
        f = open(highlight_css, 'w')
        f.write(css)
        f.close()
        
        