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

from werkzeug import redirect
from werkzeug.routing import NotFound
from werkzeug.utils import url_unquote
from couchit.models import Site, Page
from couchit.api import *
from couchit.template import render_response, url_for
from couchit.utils import local

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
    
def show_page(request, cname=None, pagename=None):
    if cname is None:
        return redirect('/')
        
    site = get_site(local.db, cname)
    if site is None:
        return NotFound

    if pagename is None:
        pagename ='home'
    page = get_page(local.db, site.id, pagename)
    if page is None:
        raise NotFound
    
    # get all pages
    pages = all_pages(local.db, site.id)
    
    return render_response('page/show.html', page=page, pages=pages, site=site)
    
def edit_page(request, cname=None, pagename=None):
    if cname is None:
        return redirect('/')
        
    site = get_site(local.db, cname)
    if site is None:
        return redirect('/')
        
    if pagename is None:
        pagename ='Home'
    
    page = get_page(local.db, site.id, pagename)
    if not page or page.id is None:
        page = Page(
            site=site.id,
            title=pagename.replace("_", " ")
        )
        
    if request.method == "POST":
        page.content = request.form.get('content', '')
        page.store(local.db)
        redirect_url = url_for('show_page', cname=cname, pagename=pagename)
        return redirect(redirect_url)
    
    return render_response('page/edit.html', page=page, site=site)
    
def history_page(request, cname=None, pagename=None):
    if cname is None:
        return redirect('/')

    site = get_site(local.db, cname)
    if site is None:
        return redirect('/')
    
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, site.id, pagename)
    if not Page:
        return NotFound
    
    revisions = page.revisions(local.db)
    
    # get all pages
    pages = all_pages(local.db, site.id)
    return render_response('page/history.html', page=page, pages=pages, site=site, revisions=revisions)
    
def revision_page(request, cname=None, pagename=None, nb_revision=None):
    if cname is None:
        return redirect('/')

    site = get_site(local.db, cname)
    if site is None:
        return redirect('/')
    
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, site.id, pagename)
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
    pages = all_pages(local.db, site.id)
        
    revision = page.revision(local.db, nb_revision)
    if revision is None:
        return render_response('page/revision_notfound.html', page=page, pages=pages, site=site)

    return render_response('page/show.html', page=revision, pages=pages, site=site)
    
def diff_page(request, cname=None, pagename=None):
    if cname is None:
        return redirect('/')
        
    site = get_site(local.db, cname)
    if site is None:
        return redirect('/')
        
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, site.id, pagename)
    if not Page:
        return NotFound
    
    revisions = request.values.getlist('r')
    
    # get all pages
    pages = all_pages(local.db, site.id)
    
    diff = get_diff(local.db, page, revisions[0], revisions[1])
    
    return render_response('page/diff.html', page=page, pages=pages, site=site, diff=diff)
    
    
def site_design(request, cname):
    if cname is None:
        return redirect('/')
        
    site = get_site(local.db, cname)
    if site is None:
        return redirect('/')
    return render_response('site/design.html', site=site)