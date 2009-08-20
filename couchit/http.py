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

from datetime import datetime, timedelta
import base64
from hashlib import md5
import random
import cPickle as pickle

from couchdbkit.resource import ResourceNotFound
from werkzeug import Response, Request
from werkzeug.contrib.sessions import Session,SessionStore

from couchit import settings
from couchit.utils import db, local, datetime_tojson


__all__ = ['DatabaseSessionStore', 'BCRequest', 'BCResponse', 'session_store']

def _encode_session_data(session_data):
    """ encode session object using pickle and base64.
    We also sign them with md5 and SECRET_KEY defined
    in Amisphere settings """
    pickled = pickle.dumps(session_data)
    pickled_md5 = md5(pickled + settings.SECRET_KEY).hexdigest()
    return base64.encodestring(pickled + pickled_md5)

def _decode_session_data(session_data):
    """ decode session object from database """
    encoded_data = base64.decodestring(session_data)
    pickled, tamper_check = encoded_data[:-32], encoded_data[-32:]
    if md5(pickled + settings.SECRET_KEY).hexdigest() != tamper_check:
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
        expire = datetime.now() + timedelta(seconds=settings.SESSION_COOKIE_AGE)
        try:
            db["session/%s" % session.sid] = {
                    'session_key':session.sid, 
                    'session_data': _encode_session_data(dict(session)),
                    'expire_date': datetime_tojson(expire)            
            }
        except:
            s = db["session/%s" % session.sid]
            s['session_data'] = _encode_session_data(dict(session))
            s['expire_date'] = datetime_tojson(expire)
            db['session/%s' % session.sid] = s
       
    def delete(self, session):
        """ delete session """
        try:
            del db['session/%s' % session.sid]
        except AttributeError:
            pass
       
    def get(self, sid):
        """ get session associated to sid. sid
        is retrieved from a secure cookie. Secure cookie name
        is defined in Amisphere settings. """
        s = None
        try:
            s = db['session/%s' % sid]
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

            
            