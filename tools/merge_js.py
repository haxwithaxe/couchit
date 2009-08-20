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
        self.cmd_path = os.path.join(os.path.dirname(__file__), 'yuicompressor-2.4.2.jar')
    
    def compress(self, tempfile):
        print tempfile
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
