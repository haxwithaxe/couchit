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

__all__ = ['Page', 'Site']

def _genslug():
    charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    from random import choice
    return ''.join([choice(charset) for i in range(8)])


class Site(Document):
    cname = TextField()
    title = TextField()
    subtitle = TextField()
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
        else:
            db[self.id] = self._data
        self._data = db.get(docid)
        return self
                        
class Page(Document):
    site = TextField()
    title = TextField()
    content = TextField()
    parent = TextField(default='')
    created = DateTimeField()
    updated = DateTimeField()
    
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
                old_data['parent'] = self.id
                old_data['itemType'] = 'revision'
                print "ici %s" %old_data
                db.create(old_data)
                db[self.id] = self._data
        return self
                
            
            