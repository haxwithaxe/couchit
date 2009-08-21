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


import time
from werkzeug import Request, SharedDataMiddleware, ClosingIterator, redirect
from werkzeug.exceptions import HTTPException, NotFound

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

        response = None
        subdomain = ''
        site = None
        alias = None
        cname = None
        if cur_server_name[offset:] == real_server_name:
            subdomain = '.'.join(filter(None, cur_server_name[:offset]))
            alias = subdomain 
        else: # redirect to main server if it isn't a subdomain
            response = redirect('http://%s' % settings.SERVER_NAME)
            return response(environ, start_response)
            
        if subdomain in views.FORBIDDEN_CNAME:
            response = redirect('http://%s' % settings.SERVER_NAME)
            return response(environ, start_response)

        if subdomain and subdomain != 'www' and subdomain not in views.FORBIDDEN_CNAME: # get alias
            request.alias = subdomain
            site = get_site(subdomain, by_alias=True)
        elif cur_path: # get shortname
            site = get_site(cur_path[0])
            cname = cur_path[0]
            
        if site is None: # create website
            if alias is None or not alias and cname in ['help', 'find', 'about']:
                response = self.views['couchit_%s' % cname](request, **request.args)
            else:
                response = self.views['home'](request, cname=cname, alias=alias, **request.args)
        
        args = {}
        endpoint=''
        if response is None:
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

        if hasattr(request, 'site'):
            if request.site.privacy == "private" and not authenticated and endpoint!='site_login' and endpoint!='forgot_password' and endpoint !='change_password':
                back = ''
                if endpoint:
                    back = url_for(endpoint, **args)
                response = redirect(url_for('site_login', back=back))
            elif not subdomain and request.site.alias:
                redirect_url = "http://%s.%s/%s" % (request.site.alias, settings.SERVER_NAME, 
                                        path_info)
                print redirect_url
                response = redirect(redirect_url)
        
            
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        local.application = self
        return ClosingIterator(self.dispatch(environ, start_response),
                                [local_manager.cleanup])
