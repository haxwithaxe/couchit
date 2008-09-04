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

from couchdb.client import ResourceNotFound
from couchit.models import Site, Page
from couchit.utils import utf8
from couchit.utils.diff import diff_blocks


__all__ = ['get_site', 'get_page', 'get_pageof',
'all_pages', 'get_diff']

def get_site(db, name):
    rows = Site.view(db, '_view/site/by_cname', key=name)
    lrows = list(iter(rows))
    if lrows:
        return lrows[0]
    return None
    

def get_page(db, siteid, name):
    rows = Page.view(db, '_view/page/by_slug', key=[siteid, name])
    lrows = list(iter(rows))
    if lrows:
        return lrows[0]
    return None
     
def get_pageof(db, cname, slug):
    site = get_site(db, cname)
    if site is None:
        return None
    return get_page(db, site.id, slug)
    
def all_pages(db, siteid):
    if siteid is None:
        return []
    rows = Page.view(db, '_view/page/all_pages', key=siteid)
    return list(iter(rows))
    
    
def get_diff(db, page, rev1, rev2):
    a = int(rev1)
    b = int(rev2)
    if b < a:
        a,b=b,a
    r1 = page.revision(db, a)
    r2 = page.revision(db, b)
    
    return diff_blocks(r1.content.splitlines(), r2.content.splitlines(), 3)
    
    
    
    