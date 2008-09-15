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
from couchit.api import *
from couchit import context_processors
from couchit import views
from couchit.template import template_env, url_for

class CouchitApp(object):
    def __init__(self):
        local.application = self
        self.views = all_views.copy()
        
        self.dispatch = SharedDataMiddleware(self.dispatch, {
            '/static': settings.STATIC_PATH
        })
    
    def dispatch(self, environ, start_response):
        local.request = request = BCRequest(self, environ)
        cur_path = [p for p in request.path.split('/') if p]
        
        # test if we are under a subdomain or domain alias
        cur_server_name = request.url.split("/")[2].split(':')[0].split('.')
        real_server_name = settings.SERVER_NAME.split(':', 1)[0].split('.')
        offset = -len(real_server_name)

        subdomain = ''
        site = None
        if cur_server_name[offset:] == real_server_name:
            subdomain = '.'.join(filter(None, cur_server_name[:offset]))
        else:
            subdomain = '.'.join(filter(None, cur_server_name))
        

        if subdomain and subdomain != 'www': # get alias
            request.alias = subdomain
            site = get_site(local.db, subdomain, by_alias=True)
        elif cur_path: # get shortname
            site = get_site(local.db, cur_path[0])
            
        if site is None: # create website
            response = self.views['home'](request, **request.args)
            return response(environ, start_response)
        
        request.site = site

        if subdomain:
            site_url = ''
        else:
            site_url = "/" + site.cname
        local.site_url = site_url
        
        if not subdomain:
            local.cname = cur_path[0]
            path_info = '/'.join(cur_path[1:])
            local.url_adapter = adapter = urls_map.bind(
                    settings.SERVER_NAME, 
                    environ.get('SCRIPT_NAME'),
                    None, 
                    environ['wsgi.url_scheme'],
                    environ['REQUEST_METHOD'],
                    path_info)
        else:
            local.url_adapter = adapter = urls_map.bind_to_environ(environ)
            
        authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
        can_edit = True 
        if request.site.privacy == "public" and not authenticated:
            can_edit = False
        request.can_edit = can_edit
        
        # process urls   
        try:
            endpoint, args = adapter.match()
            response = self.views[endpoint](request, **args)
        except NotFound, e:
            response = views.not_found(request)
            response.status_code = 404
        except HTTPException, e:
            response = e.get_response(environ)


        if request.session.should_save:
            permanent = request.session.get('permanent', False)
            max_age=None
            expires=None
            if permanent:
                max_age = settings.SESSION_COOKIE_AGE
                expires = time.time() + settings.SESSION_COOKIE_AGE
            session_store.save(request.session)
            response.set_cookie(
                settings.SESSION_COOKIE_NAME, 
                request.session.sid, 
                expires=expires, max_age=max_age,
                path=settings.SESSION_COOKIE_PATH, 
                domain=settings.SESSION_COOKIE_DOMAIN, 
                secure=settings.SESSION_COOKIE_SECURE
            )

        
        if request.site.privacy == "private" and not authenticated and endpoint!='site_login':
            response = redirect(url_for('site_login'))
        
        
            
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        local.application = self
        couchdb_server = Server(settings.SERVER_URI)
        local.db = couchdb_server[settings.DATABASE_NAME]
        return ClosingIterator(self.dispatch(environ, start_response),
                                [local_manager.cleanup])
