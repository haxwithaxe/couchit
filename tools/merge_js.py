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

from popen2 import popen2

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    


def read_file(fname):
    f = open(fname, 'r')
    data = f.read()
    f.close()
    return data
    

class MergeJS(object):
    def __init__(self, confile):
        confdata = ''
        try:
            confdata = read_file(confile)
        except:
            pass
            
        self.conf = load(confdata, Loader=Loader)
        self.path = self.conf['javascript_path']
        self.cmd_path = os.path.join(os.path.dirname(__file__), 'yuicompressor-2.3.5.jar')
    
    def compress(self, tempfile):
        cmd = "java -jar %s --type js %s" % (self.cmd_path, tempfile) 
        sout, sin = popen2(cmd)
        return sout.read()
           
    def run(self):
        for fname, src_files in self.conf['javascript'].iteritems():
            output_js = ''
            for src_fname in src_files:
                src_fpath = os.path.join(self.path, src_fname)
                if os.path.exists(src_fpath):
                    output_js += "/* %s */\n" % src_fpath
                    output_js += read_file(src_fpath)

            temp_output = os.path.join(self.path, "_%s" % fname)       
            f = open(temp_output, 'w')
            f.write(output_js)
            f.close()
            
            output_js = self.compress(temp_output)
            os.unlink(temp_output)
            
            dest_path = os.path.join(self.path, fname)
            f = open(dest_path, 'w')
            f.write(output_js)
            f.close()
