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


import time
from werkzeug import Request, SharedDataMiddleware, ClosingIterator, redirect
from werkzeug.exceptions import HTTPException, NotFound

from couchdb.client import Server
from couchit.http import BCRequest, session_store
from couchit.utils import local, local_manager
from couchit.urls import all_views, urls_map
from couchit import settings
from couchit import context_processors
from couchit import views



class CouchitApp(object):
    def __init__(self):
        local.application = self
        self.views = all_views.copy()
        
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static': settings.STATIC_PATH
        })
    
    def dispatch(self, environ, start_response):
        local.request = request = BCRequest(self, environ)
        local.url_adapter = adapter = urls_map.bind_to_environ(environ)
        try:
            endpoint, args = adapter.match()
            response = self.views[endpoint](request, **args)
        except NotFound, e:
            response = views.not_found(request)
            response.status_code = 404
        except HTTPException, e:
            response = e

        if request.session.should_save:
            print 'here'
            permanent = request.session.get('permanent', True)
            max_age=None
            expires=None
            if permanent:
                max_age = settings.SESSION_COOKIE_AGE
                expires = time.time() + settings.SESSION_COOKIE_AGE
            session_store.save(request.session)
            response.set_cookie(
                settings.SESSION_COOKIE_NAME, 
                request.session.sid, 
                expires=expires, max_age = max_age,
                path=settings.SESSION_COOKIE_PATH, 
                domain=settings.SESSION_COOKIE_DOMAIN, 
                secure=settings.SESSION_COOKIE_SECURE
            )

        
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        local.application = self
        couchdb_server = Server(settings.SERVER_URI)
        local.db = couchdb_server[settings.DATABASE_NAME]
        return ClosingIterator(self.dispatch(environ, start_response),
                                [local_manager.cleanup])
