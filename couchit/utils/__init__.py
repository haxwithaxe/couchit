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

def get_db():
    from couchdbkit import Server
    server = Server(settings.SERVER_URI)
    return server.get_or_create_db(settings.DATABASE_NAME)
db = get_db()

def subclass_exception(name, parent, module):
    return type(name, (parent,), {'__module__': module})

class CouchitUnicodeDecodeError(Exception):
    """ raised when unicode error"""

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
    from couchdbkit import Server
    server = Server(settings.SERVER_URI)
    try:
        db = server.create_db(settings.DATABASE_NAME)
    except:
        pass
        
@install_hook    
def install_designs():
    from couchdbkit import *
    from couchdbkit.loaders import FileSystemDocsLoader
    server = Server(settings.SERVER_URI)
    loader = FileSystemDocsLoader(settings.DESIGN_PATH)
    db = server[settings.DATABASE_NAME]
    loader.sync(db, verbose=True)
        
def load_file(fname):
    f = file(fname, 'r')
    data = f.read()
    f.close
    return data

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
        
def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int, long, datetime.datetime, datetime.date, datetime.time, float)):
        return s
    try:
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = ' '.join([force_unicode(arg, encoding, strings_only,
                            errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        raise CouchitUnicodeDecodeError(s, *e.args)
    return s

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
   
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
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
