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

import re
import os

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
from css_parser import CSSParser

re_url = re.compile('url\s*\(([^\s"].*)\)')

def read_file(fname):
    f = open(fname, 'r')
    data = f.read()
    f.close()
    return data

class MergeCSS(object):
    def __init__(self, confile):
        confdata = ''
        try:
            confdata = read_file(confile)
        except:
            pass
            
        self.conf = load(confdata, Loader=Loader)
        self.path = self.conf['css_path']
        self.src_path = "%s/src" % self.path
        
    def replace_url(self, mo):
        if mo.group(0).startswith('url(../'):
            return "%s%s" % (mo.group(0)[0:4], mo.group(0)[7:])
            
    def run(self):
        for fname, src_files in self.conf['css'].iteritems():
            output_css = ''
            for src_fname in src_files:
                src_fpath = os.path.join(self.src_path, src_fname)
                if os.path.exists(src_fpath):
                    output_css += str(CSSParser(read_file(src_fpath)))
            
            output_css = re_url.sub(self.replace_url, output_css)
            
            dest_path = os.path.join(self.path, fname)
            f = open(dest_path, 'w')
            f.write(output_css)
