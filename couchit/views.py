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

import os
import urllib2
import cgi
from werkzeug import redirect
from werkzeug.routing import NotFound
from werkzeug.utils import url_unquote
from couchit import settings
from couchit.models import Site, Page
from couchit.api import *
from couchit.http import BCResponse
from couchit.template import render_response, url_for
from couchit.utils import local, make_hash

def site_required(f):
    def decorated(request, **kwargs):
        site = None
        if not hasattr(request, 'site'):
            cname = kwargs.get('cname', None)
            if cname is None:
                return redirect('/')
            if not 'sites' in request.session:
                request.session['sites'] = {}
            
            if  request.session['sites']:
                site = request.session['sites'].get(cname, None)
            
            if site is None:
                site = get_site(local.db, cname)
                if site is None:
                    return redirect('/')
            request.session['sites'][site.cname] = site
            request.site = site  
        return f(request, **kwargs)
    return decorated

def not_found(request):
    return render_response("not_found.html")

def home(request):
    if request.method == "POST":
        site = Site()
        site.store(local.db)
        content = ''
        if 'content' in request.form:
            content = request.form['content']
        page = Page(
            title='Home',
            site=site.id,
            content=content
        )
        page.store(local.db)
        return redirect('/%s' % site.cname)
    return render_response('home.html')
  
@site_required  
def show_page(request, cname=None, pagename=None):
    if pagename is None:
        pagename ='home'
    page = get_page(local.db, request.site.id, pagename)
    if page is None:
        raise NotFound
    
    # get all pages
    pages = all_pages(local.db, request.site.id)
    
    return render_response('page/show.html', page=page, pages=pages, lexers=LEXERS_CHOICE)
    
@site_required
def edit_page(request, cname=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    
    page = get_page(local.db, request.site.id, pagename)
    if not page or page.id is None:
        page = Page(
            site=request.site.id,
            title=pagename.replace("_", " ")
        )
        
    if request.method == "POST":
        page.content = request.form.get('content', '')
        page.store(local.db)
        redirect_url = url_for('show_page', cname=cname, pagename=pagename)
        return redirect(redirect_url)
    
    return render_response('page/edit.html', page=page, site=request.site)
  
@site_required  
def history_page(request, cname=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not Page:
        return NotFound
    
    revisions = page.revisions(local.db)
    
    # get all pages
    pages = all_pages(local.db, request.site.id)
    return render_response('page/history.html', page=page, pages=pages, site=request.site, revisions=revisions)
    
@site_required
def revision_page(request, cname=None, pagename=None, nb_revision=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not Page:
        return NotFound
        
    if nb_revision is None:
        nb_revision = 0
    else:
        try:
            nb_revision = int(nb_revision)
        except ValueError:
            return NotFound
    
    # get all pages
    pages = all_pages(local.db, request.site.id)
        
    revision = page.revision(local.db, nb_revision)
    if revision is None:
        return render_response('page/revision_notfound.html', page=page, pages=pages, site=request.site)

    return render_response('page/show.html', page=revision, pages=pages, site=request.site)
 
@site_required   
def diff_page(request, cname=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not Page:
        return NotFound
    
    revisions = request.values.getlist('r')
    
    # get all pages
    pages = all_pages(local.db, request.site.id)
    
    diff = get_diff(local.db, page, revisions[0], revisions[1])
    
    return render_response('page/diff.html', page=page, pages=pages, site=request.site, diff=diff)
    
@site_required
def site_claim(request, cname):
    password=''
    if request.method == "POST" and "spassword" in request.form:
        password = request.form['password']
    elif request.method == "POST":
        site.password = make_hash(request.form['password'])
        site.email = request.form['email']
        site.privacy = request.form['privacy']
        site.claimed = True
        site.store(local.db)
        return redirect('/%s' % site.cname)
        
    return render_response('site/claim.html', site=request.site, password=password)
    
@site_required
def site_settings(request, cname):
    print request.site
    return render_response('site/settings.html', site=request.site)
    
@site_required
def site_design(request, cname):
    return render_response('site/design.html', site=request.site)
        
def proxy(request):
    """ simple proxy to manage remote connexion via ajax"""
    url = request.values.get('url', None)
    host = host = url.split("/")[2]
    if host not in settings.ALLOWED_HOSTS:
        return send_json({'error': "host isn't allowed"})
    
    if request.method == "POST" or request.method == "PUT":
        length = request.environ['CONTENT_LENGTH']
        headers = {
            "Content-Type": os.environ["CONTENT_TYPE"],
            "Accept": os.environ["ACCEPT"]
        }
        print headers
        body = input_stream.read()
        r = urllib2.Request(url, body, headers)
        y = urllib2.urlopen(r)
    else:
        headers = {
            "Content-Type": request.environ["CONTENT_TYPE"],
            "Accept": request.environ["HTTP_ACCEPT"]
        }
        print request.environ
        r = urllib2.Request(url, headers=headers)
        y = urllib2.urlopen(r)
        
    i = y.info()
    if i.has_key("Content-Type"):
        content_type = i["Content-Type"]
    else:
        content_type = 'text/plain'
    print
    
    resp = y.read()
    
    response = BCResponse(resp)
    response.content_type = content_type
    return response
            
        
