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

from datetime import datetime
from couchdb.schema import *
from couchit.utils import make_hash
from couchit.utils.diff import unified_diff, diff_blocks

__all__ = ['Page', 'Site', 'PasswordToken', 'PageExist',
'AliasExist', 'AliasPage' ]

class PageExist(Exception):
    """ raised when a page exist """
    
class AliasExist(Exception):
    """ raised when an alias exist for this pagename """

class ArrayField(Field):
    _to_python = list

def _genslug():
    charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    from random import choice
    return ''.join([choice(charset) for i in range(8)])

class PasswordToken(Document):
    site = TextField()
    itemType = TextField(default='token')

class Site(Document):
    alias = TextField()
    cname = TextField()
    title = TextField(default='')
    subtitle = TextField(default='')
    password = TextField()
    email = TextField(default='')
    privacy = TextField(default='open')
    claimed = BooleanField(default=False)
    created = DateTimeField()
    updated = DateTimeField()
    default_theme = BooleanField(default=True)
    theme = DictField(Schema.build(
        background_color = TextField(default='E7E7E7'),
        text_color = TextField(default='000000'),
        link_color = TextField(default='14456E'),
        border_color = TextField(default='D4D4D4'),
        page_fill_color = TextField(default='FFFFFF'),
        page_text_color = TextField(default='000000'),
        page_link_color = TextField(default='14456E'),
        menu_inactive_color = TextField(default='666666')
    ))
    
    itemType = TextField(default='site')
    
    def store(self, db):
        self.updated = datetime.utcnow()
        if self.id is None:
            self.created = datetime.utcnow()
            if not self.cname:
                cname = None
                while 1:
                    cname = _genslug()
                    rows = iter(db.view('_view/site/by_cname', key=cname))
                    try:
                        row = rows.next()
                    except StopIteration:
                        self.cname = cname
                        break
            docid = db.create(self._data)
            self._data = db.get(docid)
        else:
            db[self.id] = self._data
        
        return self

class AliasPage(Document):
    title = TextField()
    site = TextField()
    page = TextField()
    
    itemType = TextField(default='alias_page')  
    
    def get_alias(cls, db, siteid, pagename):
        rows = cls.view(db, '_view/page/alias', key=[siteid, pagename.lower()])
        lrows = list(iter(rows))
        if lrows:
            return lrows[0]
        return None
    get_alias = classmethod(get_alias)   
    
    def is_exist(cls, db, siteid, pagename):
        if cls.get_alias(db, siteid, pagename) is not None:
            return True
        return False
    is_exist = classmethod(is_exist)
        
                      
class Page(Document):
    site = TextField()
    title = TextField()
    content = TextField(default='')
    parent = TextField(default='')
    previous = TextField(default='')
    created = DateTimeField()
    updated = DateTimeField()
    changes = ArrayField(default=[])
    nb_revision = IntegerField(default=0)
    
    itemType = TextField(default='page')
    
    def store(self, db):
        self.updated = datetime.utcnow()
        if self.id is None:
            self.created = datetime.utcnow()
            docid = db.create(self._data)
            self._data = db.get(docid)
        else:
            old_data = db.get(self.id)
            self.created = datetime.utcnow()
            old_hash = make_hash(old_data['title'], old_data['content'])
            new_hash = make_hash(self.title, self.content)
            if old_hash != new_hash:
                del old_data['_id']
                del old_data['_rev']
                
                old_data['parent'] = self.id
                old_data['itemType'] = 'revision'
                _previous = db.create(old_data)
                
                # increment revision number
                self.nb_revision = int(old_data['nb_revision']) + 1
                
                # save previous revision id, could be usefull
                self.previous = _previous
                
                # get changes 
                changes = diff_blocks(old_data['content'].splitlines(),
                    self.content.splitlines(), 3, 8, 1, 0, 1)
                
                _changes = []
                for row in changes:
                    for change in row:
                        _changes.append(change)
                self.changes = _changes
                db[self.id] = self._data
        return self

    def revisions(self, db):
        if not self.id or not self.previous:
            return []
        rows = self.view(db, '_view/page/revisions', key=self.id)
        result = list(iter(rows))
        if result: # order revisions
            result.sort(lambda a,b: cmp(a.updated, b.updated))
            result.reverse()
        return result
        
        
    def revision(self, db, revid):
        if not self.id:
            return None
        rows = self.view(db, '_view/page/nb_revision', key=[self.id, revid])
        rows = list(iter(rows))
        if rows:
            return rows[0]
        return None
    
    def get_pagename(cls, db, siteid, pagename):
        rows = cls.view(db, '_view/page/by_slug', key=[siteid, pagename.lower()])
        lrows = list(iter(rows))
        if lrows:
            return lrows[0]
        return None
    get_pagename = classmethod(get_pagename)
        
    def is_exist(cls, db, siteid, pagename):
        page = cls.get_pagename(db, siteid, pagename)
        if page is not None:
            return True
        return False
    is_exist=classmethod(is_exist)
        
    def rename(self, db, new_title):
        if not self.id:
            return False
        pagename =  new_title.replace(" ", "_")
        if self.is_exist(db, self.site, pagename):
            raise PageExist
            
        alias = AliasPage.get_alias(db, self.site, pagename)
        if alias is not None: # if an alias exist, we remove it.
            del db[alias.id]
            
        new_alias = AliasPage(
            title=self.title,
            site=self.site,
            page=self.id
        )
        new_alias.store(db)
        
        self.title = new_title
        self.store(db)
        return self

