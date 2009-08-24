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
from datetime import datetime
from couchdbkit import *
from couchit.utils import db, make_hash
from couchit.utils.diff import unified_diff, diff_blocks

__all__ = ['Theme', 'Page', 'Site', 'PasswordToken', 'PageExist',
'AliasExist', 'AliasPage', 'UserInfos']

class PageExist(Exception):
    """ raised when a page exist """
    
class AliasExist(Exception):
    """ raised when an alias exist for this pagename """
    
class PageConflict(Exception):
    """ raised when there's conflict during update """

def _genslug():
    charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    from random import choice
    return ''.join([choice(charset) for i in range(8)])

class PasswordToken(Document):
    site = StringProperty()
    itemType = StringProperty(default='token')

class Theme(DocumentSchema):
    background_color = StringProperty(default='E7E7E7')
    text_color = StringProperty(default='000000')
    link_color = StringProperty(default='14456E')
    border_color = StringProperty(default='D4D4D4')
    page_fill_color = StringProperty(default='FFFFFF')
    page_text_color = StringProperty(default='000000')
    page_link_color = StringProperty(default='14456E')
    menu_inactive_color = StringProperty(default='666666')
    syntax_style = StringProperty(default='default')
    
class UserInfos(DocumentSchema):
    ip = StringProperty()
    ua = StringProperty()
    
class Site(Document):
    alias = StringProperty()
    cname = StringProperty()
    title = StringProperty(default='')
    subtitle = StringProperty(default='')
    password = StringProperty()
    email = StringProperty(default='')
    privacy = StringProperty(default='open')
    claimed = BooleanProperty(default=False)
    created = DateTimeProperty()
    updated = DateTimeProperty()
    akismet_key = StringProperty(default='')
    allow_javascript = BooleanProperty(default=False)
    default_theme = BooleanProperty(default=True)
    theme = SchemaProperty(Theme)
    
    itemType = StringProperty(default='site')
    
    def save(self, **params):
        self.updated = datetime.utcnow()
        if not '_id' in self._doc:
            self.created = datetime.utcnow()
            if not self.cname:
                cname = None
                while 1:
                    cname = _genslug()
                    rows = iter(self._db.view('site/by_cname', key=cname))
                    try:
                        row = rows.next()
                    except StopIteration:
                        self.cname = cname
                        break
        super(Site, self).save(**params)

class AliasPage(Document):
    title = StringProperty()
    site = StringProperty()
    page = StringProperty()
    
    itemType = StringProperty(default='alias_page')  
    
    @classmethod
    def get_alias(cls, siteid, pagename):
        rows = cls.view('page/alias', key=[siteid, pagename.lower()])
        lrows = list(iter(rows))
        if lrows:
            return lrows[0]
        return None
    
    @classmethod
    def is_exist(cls, siteid, pagename):
        if cls.get_alias(siteid, pagename) is not None:
            return True
        return False
                                  
class Page(Document):
    site = StringProperty()
    title = StringProperty()
    content = StringProperty(default='')
    parent = StringProperty(default='')
    previous = StringProperty(default='')
    created = DateTimeProperty()
    updated = DateTimeProperty()
    changes = ListProperty()
    nb_revision = IntegerProperty(default=0)
    is_spam = BooleanProperty(default=False)
    user = SchemaProperty(UserInfos)
    
    itemType = StringProperty(default='page')
    
    def save(self, **params):
        self.updated = datetime.utcnow()
        if not '_id' in self._doc:
            self.created = datetime.utcnow()
        else:
            revision = Page.get(self._id)
            self.created = datetime.utcnow()
            old_hash = make_hash(revision.title, revision.content)
            new_hash = make_hash(self.title, self.content)
            if old_hash != new_hash:
                del revision._doc['_id']
                del revision._doc['_rev']
                
                revision.parent = self._id
                revision.itemType = 'revision'
                revision.save()
                
                _previous = revision._id
                
                # increment revision number
                # TODO : use revisionid in latest CouchDB
                self.nb_revision = revision.nb_revision + 1
                
                # save previous revision id, could be usefull
                self.previous = _previous
                
                # get changes 
                changes = diff_blocks(revision.content.splitlines(),
                    self.content.splitlines(), 3, 8, 1, 0, 1)
                
                _changes = []
                for row in changes:
                    for change in row:
                        _changes.append(change)
        super(Page, self).save(**params)

    def revisions(self):
        if not self._id or not self.previous:
            return []
        rows = self.view('page/revisions', key=self._id)
        result = list(iter(rows))
        if result: # order revisions
            result.sort(lambda a,b: cmp(a.updated, b.updated))
            result.reverse()
        return result
        
        
    def revision(self, revid):
        if not self._id:
            return None
        rows = self.view('page/nb_revision', key=[self._id, revid])
        rows = list(iter(rows))
        if rows:
            return rows[0]
        return None
    
    @classmethod
    def get_pagename(cls, siteid, pagename):
        rows = cls.view('page/by_slug', key=[siteid, pagename.lower()])
        lrows = list(iter(rows))
        if lrows:
            return lrows[0]
        return None
        
    @classmethod
    def is_exist(cls, siteid, pagename):
        page = cls.get_pagename(siteid, pagename)
        if page is not None:
            return True
        return False
        
    def rename(self, new_title):
        if not self._id:
            return False
        pagename =  new_title.replace(" ", "_")
        if self.is_exist(self.site, pagename):
            raise PageExist
            
        alias = AliasPage.get_alias(self.site, pagename)
        if alias is not None: # if an alias exist, we remove it.
            del db[alias._id]
            
        new_alias = AliasPage(
            title=self.title,
            site=self.site,
            page=self._id
        )
        new_alias.save()
        
        self.title = new_title
        self.save()
        return self

db.contain(PasswordToken, Site, AliasPage, Page)