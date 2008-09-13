# -*- coding: utf-8 -
# Copyright 2008 by Benoît Chesneau <benoitc@e-engura.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
                    output_css += "/* %s */\n" % src_fpath
                    output_css += str(CSSParser(read_file(src_fpath)))
            
            output_css = re_url.sub(self.replace_url, output_css)
            
            dest_path = os.path.join(self.path, fname)
            f = open(dest_path, 'w')
            f.write(output_css)
