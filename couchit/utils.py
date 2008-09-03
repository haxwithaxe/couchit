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

import binascii
from calendar import timegm
from datetime import datetime, time
from glob import glob
from time import strptime, struct_time
import os
import re
import sys
try:
    from hashlib import sha1 as _sha
except ImportError:
    import sha
    _sha = sha.new
import urllib
  
    
from werkzeug import Local, LocalManager
from werkzeug.routing import Map, Rule

from couchit import settings

_hex = binascii.hexlify  
local = Local()
local_manager = LocalManager([local])

_install_hooks = []


if sys.version_info < (2, 5):
    # Prior to Python 2.5, Exception was an old-style class
    def subclass_exception(name, parent, unused):
        return types.ClassType(name, (parent,), {})
else:
    def subclass_exception(name, parent, module):
        return type(name, (parent,), {'__module__': module})

    
def slugify(value):
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def datetimestr_topython(value):
    if isinstance(value, basestring):
        try:
            value = value.split('.', 1)[0] # strip out microseconds
            value = value.rstrip('Z') # remove timezone separator
            timestamp = timegm(strptime(value, '%Y-%m-%dT%H:%M:%S'))
            value = datetime.utcfromtimestamp(timestamp)
        except ValueError, e:
            raise ValueError('Invalid ISO date/time %r' % value)
    return value


def datetime_tojson(value):
    if isinstance(value, basestring):
        return value
    if isinstance(value, struct_time):
        value = datetime.utcfromtimestamp(timegm(value))
    elif not isinstance(value, datetime):
        value = datetime.combine(value, time(0))
    return value.replace(microsecond=0).isoformat() + 'Z'

def install_hook(f):
    _install_hooks.append(f)
    return f

def install():
    global _install_hooks
    print "Setup benoitc.org"
    for a in _install_hooks:
        sys.stderr.write("do %s\n" % a.__name__)
        a()

@install_hook
def create_db():
    """create the db if it don't exist"""
    from couchdb.client import Server
    couchdb_server = Server(settings.SERVER_URI)
    try:
        db = couchdb_server.create(settings.DATABASE_NAME)
    except:
        pass
        
def load_file(fname):
    f = file(fname, 'r')
    data = f.read()
    f.close
    return data
        
def load_views():
    from couchdb.client import Server
    
    couchdb_server = Server(settings.SERVER_URI)
    db = couchdb_server[settings.DATABASE_NAME]
    
    design_path = os.path.join(os.path.dirname(__file__), '_design')
    print "\nLoad CouchDB views ..."
    for name in os.listdir(design_path):
        path = os.path.join(design_path,name)
        views = {}
        for view in os.listdir(path):
            views[view] = {}
            for js in glob(os.path.join(path, view, '*.js')):
                if os.path.basename(js) == 'map.js':
                    views[view]['map'] = load_file(js)
                if os.path.basename(js) == 'reduce.js':
                    views[view]['reduce'] = load_file(js)
            print "add %s/%s" % (name, view)
        try:
            db['_design/%s' % name] = {
                'language': 'javascript',
                'views': views
            }
        except:
            v = db['_design/%s' % name] 
            v['views'] = views
            db['_design/%s' % name] = v

def utf8(text):
    """Encodes text in utf-8.
        
        >> utf8(u'\u1234') # doctest doesn't seem to like utf-8
        '\xe1\x88\xb4'

        >>> utf8('hello')
        'hello'
        >>> utf8(42)
        '42'
    """
    if isinstance(text, unicode):
        return text.encode('utf-8')
    elif isinstance(text, str):
        return text
    else:
        return str(text)
        
def to_str(s):
    """
    return a bytestring version of s, encoded in utf8
    """

    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            return unicode(s).encode('utf-8', 'strict')
    elif isinstance(s, unicode):
        return s.encode('utf-8', 'strict')
    else:
        return s

def get_tag_name_list(tag_names):
    """
    Finds tag names in the given string and return them as a list.
    """
    
    def _get_quoted_tags(terms_, str_):
        buf = []
        open_quote = False
        for c in str_:
            if c == u'"':
                if not open_quote:
                    open_quote = True
                    if buf:
                        # we try to split here
                        term_ = ''.join(buf)
                        if not u' ' in buf:
                            terms_.append(term_)
                        else:
                            terms_ += [term_ for term_ in ''.join(buf).split(' ') if term_]
                        buf = []
                elif buf:
                    term_ = ''.join(buf)
                    terms_.append(term_)
                    buf = []
                    open_quote = False
            elif c:
                buf.append(c)
        if buf:
            terms_.append(''.join(buf))
            
    if not tag_names:
        return []

    tag_names = utf8(tag_names)
    terms = []
    if u',' not in tag_names and u'"' not in tag_names:
        terms = [tag for tag in tag_names.split(" ") if tag]
        if not terms:
            return tag_names
        terms.sort()
        return terms
         
    if u',' in tag_names:
        terms = [term.strip() for term in tag_names.split(u',') if term]
        new_terms = []
        if u'"' in tag_names:
            for tag in terms:
                _get_quoted_tags(new_terms, tag)
        terms = new_terms
    else:
        _get_quoted_tags(terms, tag_names)
    terms.sort()
    return terms

def make_hash(*args):
    if len(args) <= 0:
        return None
    s = _sha()
    for arg in args:
        s.update(to_str(arg))

    return _hex(s.digest())
    
def short(node):
    return _hex(node[:6])
