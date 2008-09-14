# -*- coding: utf-8 -
#
# Copyright 2008 by Benoît Chesneau <benoitc@e-engura.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime, timedelta
import base64
import md5
import random
import cPickle as pickle

from couchdb.client import ResourceNotFound
from werkzeug import Response, Request
from werkzeug.contrib.sessions import Session,SessionStore

from couchit import settings
from couchit.utils import local, datetime_tojson


__all__ = ['DatabaseSessionStore', 'BCRequest', 'BCResponse', 'session_store']

def _encode_session_data(session_data):
    """ encode session object using pickle and base64.
    We also sign them with md5 and SECRET_KEY defined
    in Amisphere settings """
    pickled = pickle.dumps(session_data)
    pickled_md5 = md5.new(pickled + settings.SECRET_KEY).hexdigest()
    return base64.encodestring(pickled + pickled_md5)

def _decode_session_data(session_data):
    """ decode session object from database """
    encoded_data = base64.decodestring(session_data)
    pickled, tamper_check = encoded_data[:-32], encoded_data[-32:]
    if md5.new(pickled + settings.SECRET_KEY).hexdigest() != tamper_check:
        raise SuspiciousOperation, "User tampered with session cookie."
    try:
        return pickle.loads(pickled)
    # Unpickling can cause a variety of exceptions. If something happens,
    # just return an empty dictionary (an empty session).
    except:
        return {}

class DatabaseSessionStore(SessionStore):
    """ database session store """

    def __init__(self, session_class=Session):
        SessionStore.__init__(self, session_class)

    def save(self, session):
        """ save session in couchdb database """
        s = None
        expire = datetime.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE)
        try:
            s = local.db["session/%s" % session.sid]
        except ResourceNotFound:
            pass
        
        if s is not None:
            s['session_data'] = _encode_session_data(dict(session))
            s['expire_date'] = datetime_tojson(expire)
        else:
            s = {
                    'session_key':session.sid, 
                    'session_data': _encode_session_data(dict(session)),
                    'expire_date': datetime_tojson(expire)            
                    }
        local.db['session/%s' % session.sid] = s

    def delete(self, session):
        """ delete session """
        try:
            del local.db['session/%s' % session.sid]
        except AttributeError:
            pass
       
    def get(self, sid):
        """ get session associated to sid. sid
        is retrieved from a secure cookie. Secure cookie name
        is defined in Amisphere settings. """
        s = None
        try:
            s = local.db['session/%s' % sid]
        except ResourceNotFound:
            pass
            
        if s is None or not self.is_valid_key(sid):
            return self.new()

        return self.session_class(_decode_session_data(s['session_data']), sid, False)
session_store = DatabaseSessionStore()
        
class BCResponse(Response):
    """
    An utf-8 response, with text/html as default mimetype.
    """
    charset = 'utf-8'
    default_mimetype = 'text/html'
    
class BCRequest(Request):
    charset = 'utf-8'
    
    def __init__(self, app, environ):
        super(BCRequest, self).__init__(environ)
        self.app = app
        self.sid = self.cookies.get(settings.SESSION_COOKIE_NAME)
        if not self.sid:
            self.session = session_store.new()
        else:
            self.session = session_store.get(self.sid)

            
            