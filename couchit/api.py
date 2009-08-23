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

from werkzeug.utils import url_quote_plus
from pygments.lexers import get_all_lexers, get_lexer_for_filename
from pygments.styles import get_all_styles

from couchit.documents import Site, Page
from couchdbkit.resource import ResourceNotFound
from couchit.utils import utf8, make_hash
from couchit.utils.diff import diff_blocks


__all__ = ['get_site', 'get_page', 'get_pageof',
'all_pages', 'get_diff', 'LEXERS_CHOICE', 'get_changes', 
'validate_password', 'validate_token', 'spam']

def _get_lexers():
    lexers = get_all_lexers()
    nl = []
    ret=[]
    for l in lexers:
        if l[1][0] not in nl:
            ret.append((l[1][0],l[0]))
    ret.sort()
    ret = [('text', '------------')] + ret
    return ret

LEXERS_CHOICE = [('text', 'Plain text')] + _get_lexers()
ALL_LEXERS=get_all_lexers()

ALL_COLORSHEME = list(get_all_styles())

def get_site(name, by_alias=False):
    if by_alias:
        vn = 'site/alias'
    else:
        vn = 'site/by_cname'
    rows = Site.view(vn, key=name)
    lrows = list(iter(rows))
    if lrows:
        return lrows[0]
    return None
    
def validate_password(siteid, password):
    rows = Site.view('site/password', key=[siteid, make_hash(password)])
    lrows = list(iter(rows))
    if lrows:
        return True
    return False

def validate_token(siteid, token):
    rows = Site.view('site/token', key=[token, siteid])
    lrows = list(iter(rows))
    if lrows:
        return True
    return False

def get_page(siteid, name):
    rows = Page.view('page/by_slug', key=[siteid, name.lower()])
    lrows = list(iter(rows))
    if lrows:
        return lrows[0]
    return None
     
def get_pageof(cname, slug):
    site = get_site(db, cname)
    if site is None:
        return None
    return get_page(db, site._id, slug)
    
def all_pages(siteid):
    if siteid is None:
        return []
    rows = Page.view('page/all_pages', key=siteid)
    pages = list(iter(rows))
    if pages:
        pages.sort(lambda a,b: cmp(a.title, b.title))
    return pages
    
def spam(siteid):
    if siteid is None:
        return []
    rows = Page.view('page/spam', key=siteid)
    pages = list(iter(rows))
    if pages:
        pages.sort(lambda a,b: cmp(a.title, b.title))
    return pages
    
def get_changes(siteid):
    if siteid is None:
        return []
    rows = Page.view('page/all_pages', key=siteid, limit=50)
    result = list(iter(rows))
    if result: # order revisions
        result.sort(lambda a,b: cmp(a.updated, b.updated))
        result.reverse()
    return result
    
def get_diff(page, rev1, rev2):
    a = int(rev1)
    b = int(rev2)
    if b < a:
        a,b=b,a
    r1 = page.revision(a)
    r2 = page.revision(b)
    
    return diff_blocks(r1.content.splitlines(), r2.content.splitlines(), 3), r1, r2
    
    
    
    
