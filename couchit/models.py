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

__all__ = ['Page', 'Site']


class ArrayField(Field):
    _to_python = list

def _genslug():
    charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    from random import choice
    return ''.join([choice(charset) for i in range(8)])


class Site(Document):
    cname = TextField()
    title = TextField()
    subtitle = TextField()
    password = TextField()
    email = TextField()
    privacy = TextField(default='open')
    claimed = BooleanField(default=False)
    created = DateTimeField()
    updated = DateTimeField()
    
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
            old_hash = make_hash(old_data['content'])
            new_hash = make_hash(self.content)
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
                        print change
                        _changes.append(change)
                self.changes = _changes
                print self.changes
                db[self.id] = self._data
        return self

    def revisions(self, db):
        if not self.id or not self.previous:
            return []
        rows = self.view(db, '_view/page/revisions', key=self.id)
        result = list(iter(rows))
        print result
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