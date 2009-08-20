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
import os
import random
import re
from time import asctime, gmtime, time
import urllib2
import uuid
import zipfile
from StringIO import StringIO
import sys    

from jinja2.filters import do_truncate, do_striptags, escape
from werkzeug import redirect
from werkzeug.contrib.atom import AtomFeed
from werkzeug.routing import NotFound
from werkzeug.utils import url_unquote, generate_etag
from couchit import settings
from couchit.models import *
from couchit.api import *
from couchit.contrib import mimeparse
from couchit.http import BCResponse
from couchit.template import render_response, url_for, render_template, send_json, convert_markdown
from couchit.utils import local, make_hash, datetime_tojson, to_str, smart_str, force_unicode
from couchit.utils.mail import send_mail
from couchit.utils.sioc import SiocWiki, send_sioc

import simplejson as json

FORBIDDEN_PAGES = ['site', 'delete', 'edit', 'create', 'history', 'changes', 'sitemap.xml']

FORBIDDEN_CNAME = ['mail', 'www', 'blog', 'media', 'upload', 'files', 'store']

re_page = re.compile(r"^[&@()?!.,;_:\"'\-\/ \w]+$", re.U)
re_address = re.compile(r'^[-_\w]+$')

def not_logged(f):
    def decorated(request, **kwargs):
        authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
        if authenticated:
            redirect_url = local.site_url and local.site_url or "/"
            return redirect(redirect_url)
        return f(request, **kwargs)
    return decorated
    
def login_required(f):
    def decorated(request, **kwargs):
        authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
        if request.site.claimed and not authenticated:
            redirect_url = url_for('site_login')
            return redirect(redirect_url)
        return f(request, **kwargs)
    return decorated
    
def not_claimed(f):
    def decorated(request, **kwargs):
        if request.site.claimed:
            redirect_url = local.site_url and local.site_url or "/"
            return redirect(redirect_url)
        return f(request, **kwargs)
    return decorated
             
def can_edit(f):
    def decorated(request, **kwargs):
        if not request.can_edit:
            redirect_url = local.site_url and local.site_url or "/"
            return redirect(redirect_url)
        return f(request, **kwargs)
    return decorated
    
    
def valid_page(f):
    def decorated(request, **kwargs):
        if 'pagename' in kwargs:
            pagename = kwargs['pagename'] 
            if not re_page.match(pagename) and pagename is not None:
                print pagename 
                raise NotFound
            pagename = pagename.replace(" ", "_")
            kwargs['pagename'] = pagename
        return f(request, **kwargs)
    return decorated
        
    
def not_found(request):
    return render_response("not_found.html")


def home(request, cname=None, alias=None):
    def randomid():
        return str(uuid.uuid4()).replace('-','')
        
    def validate(request):
        createid = request.session.get('createid')
        spamid = request.session.get('spamid')
        spaminput = request.session.get('spaminput')
        
        if createid is None or spaminput is None or spamid is None:
            return False
            
        if request.form.get(spamid, False) or request.form.get(spaminput, False):
            return False
            
        if not request.form.get(createid, False):
            return False
            
        del request.session['createid']
        del request.session['spamid']
        del request.session['spaminput']
        return True
    
    if request.method == "POST" and validate(request):
        site = Site()
        if 'cname' in request.form:
            site.cname = request.form['cname']
        if 'alias' in request.form:
            site.alias = request.form['alias']
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
        if site.alias:
            redirect_url = 'http://%s.%s' % (site.alias, settings.SERVER_NAME)
        else:
            redirect_url = '/%s' % site.cname
        return redirect(redirect_url)

    # try to fight bots
    b1 = "c%s" % randomid()
    b2 = "c%s" % randomid()
    spamid = randomid()
    spaminput = randomid()
    createid = randomid()
    
    request.session['createid'] = createid
    request.session['spamid'] = spamid
    request.session['spaminput'] = spaminput

    return render_response('home.html', cname=cname, alias=alias,
                b1=b1, b2=b2, spamid=spamid, spaminput=spaminput, createid=createid)
  
  
@valid_page
def show_page(request=None, pagename=None):
    mimetypes = request.accept_mimetypes
    
    if pagename is None:
        pagename ='home'
        
    #pagename = pagename.replace(" ", "_")

    redirect_from = request.values.get('redirect_from', '')
        
    page = get_page(local.db, request.site.id, pagename)
    if not page or page.id is None:
        alias = AliasPage.get_alias(local.db, request.site.id, pagename)
        if alias is not None:
            page = Page.load(local.db, alias.page)
            return redirect(url_for('show_page', 
            pagename=page.title.replace(' ', '_'),
            redirect_from=pagename))
            
   
    if not page or page.id is None:
        if pagename.lower() in FORBIDDEN_PAGES:
            redirect_url = "%s?error=%s" % (
                url_for('show_page', pagename='home'),
                u"Page name invalid."
            )
            return redirect(redirect_url)
        page = Page(
            site=request.site.id,
            title=pagename.replace("_", " ")
        )
    
    if mimeparse.best_match(['application/rdf+xml', 'text/xml', 'text/html'], 
    request.headers['ACCEPT']) == "application/rdf+xml":
        site_title = request.site.title and request.site.title or request.site.cname
        site_url = request.host_url
        if not local.site_url:
            site_url += local.site_url
        
        sioc = SiocWiki(site_url, site_title, datetime_tojson(request.site.created))
        sioc.add_page(page.content, page.title, request.url, datetime_tojson(page.updated))
        return send_sioc(sioc.to_str())

    # get all pages
    pages = all_pages(local.db, request.site.id)
    
    response = render_response('page/show.html', page=page, pages=pages, 
        lexers=LEXERS_CHOICE, redirect_from=redirect_from)
        
    return response

@can_edit
@valid_page
def edit_page(request, pagename=None):
    if pagename is None:
        pagename ='Home'
    
    page = get_page(local.db, request.site.id, pagename)
    if not page or page.id is None:
        page = Page(
            site=request.site.id,
            title=pagename.replace("_", " ")
        )
        
    if request.is_xhr and request.method=="POST":
        error = ""
        data = json.loads(request.data)
        new_title = data.get('new_title')
        if new_title and new_title is not None:
            try:
                page.rename(local.db, new_title)
                redirect_url = url_for('show_page', pagename=new_title.replace(' ', '_'))
                return send_json({"ok": True, "redirect_url": redirect_url})
            except PageExist:
                error = "A page already exist with this name"
            else:
                error = "An unexpected error happened, please contact administrator."
                
            
        else:
            error = u"New title is empty"
        return send_json({
            "ok": False,
            "error": error
        })
            
    if request.method == "POST":
        if 'new_title' in request.form:
            new_title = request.form['new_title']
            try:
                page.rename(local.db, new_title)
                redirect_url = url_for('show_page', pagename=new_title.replace(' ', '_'))
                return redirect(redirect_url)
            except PageExist:
                error = "A page already exist with this name"
            else:
                error = "An unexpected error happened, please contact administrator."
        else:
            page.content = request.form.get('content', '')
            page.store(local.db)
            redirect_url = url_for('show_page', pagename=pagename)
            return redirect(redirect_url)
    
    return redirect(url_for('show_page', pagename=pagename))

@can_edit
@login_required
@valid_page
def delete_page(request, pagename):
    if pagename == 'Home': #security reason
        return redirect(url_for('show_page', pagename='Home'))
    
    page = get_page(local.db, request.site.id, pagename)
    if not page or page.id is None:
        raise NotFound
    
    del local.db[page.id]
    
    if local.site_url:
        redirect_url = local.site_url
    else:
        redirect_url = '/'
    return redirect(redirect_url)
    
@valid_page
def history_page(request=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    
    if not page:
        raise NotFound
    
    revisions = page.revisions(local.db)
    
    # get all pages
    pages = all_pages(local.db, request.site.id)

    return render_response('page/history.html', page=page, pages=pages, revisions=revisions)
    
@valid_page
def revision_page(request=None, pagename=None, nb_revision=None):
    if pagename is None:
        pagename ='Home'
        
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        raise NotFound
        
    if nb_revision is None:
        nb_revision = 0
    else:
        try:
            nb_revision = int(nb_revision)
        except ValueError:
            raise NotFound

    revision = page.revision(local.db, nb_revision)
    if revision is None:
        return render_response('page/revision_notfound.html', page=page, pages=pages, site=request.site)
        
    # revert page
    if request.method == "POST" and "srevert" in request.form:
        page.content = revision.content
        page.store(local.db)
        return redirect(url_for("show_page", pagename=pagename))
        
    # get all pages
    pages = all_pages(local.db, request.site.id)
    
    return render_response('page/show.html', page=revision, pages=pages)

@valid_page  
def diff_page(request=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        if request.is_xhr:
            return send_json({'ok': False, 'reason': 'not found'})
        raise NotFound
    
    diff = ''
    rev1 = rev2 = page
    revisions = request.values.getlist('r')
    if revisions and len(revisions) >=2:
        diff, rev1, rev2 = get_diff(local.db, page, revisions[0], revisions[1])
    
    if request.is_xhr:
         return send_json({
            'ok': True,
            'diff': render_template('page/diff_inc.html', diff=diff, rev1=rev1, rev2=rev2)
         })
     
    all_revisions = [page] + page.revisions(local.db)

    # get all pages
    pages = all_pages(local.db, request.site.id)

    return render_response('page/diff.html', page=page, pages=pages, diff=diff, rev1=rev1, 
    rev2=rev2, revisions=all_revisions)

    
@valid_page  
def revisions_feed(request=None, pagename=None, feedtype="atom"):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        raise NotFound
    all_revisions = [page] + page.revisions(local.db)
    if feedtype == "atom":
        feed = AtomFeed(
                    title="%s: Latest revisions of %s" % (request.site.cname, page.title),
                    subtitle=request.site.subtitle,
                    updated = page.updated,
                    feed_url = request.url
        )
        for rev in all_revisions:
            title = ''
            _url="%s%s" % (request.host_url, url_for("revision_page", 
                pagename=pagename, 
                nb_revision=rev.nb_revision
            ))
            for change in rev.changes:
                if change['type'] != "unmod":
                    title = "\n".join(change['changed']['lines'])
                    title = do_truncate(do_striptags(title), 60)
            title = title and title or "Edited."
            feed.add(title, convert_markdown(rev.content), 
                updated=rev.updated,
                url=_url,
                id=_url,
                author=rev.title.replace(' ', '_')
            )
        return feed.get_response()
    else:
        json = {
            'title': "%s: Latest revisions of %s" % (request.site.cname, page.title),
            'subtitle': request.site.subtitle,
            'updated':datetime_tojson(page.updated),
            'feed_url': request.url,
            'revisions': []
        }
        for rev in all_revisions:
            title = ''
            for change in rev.changes:
                if change['type'] != "unmod":
                    title = "\n".join(change['changed']['lines'])
                    title = do_truncate(do_striptags(title), 60)
                    
            title = title and title or "Edited."
            url = "%s%s" % (request.host_url, url_for("revision_page", 
                        cname=request.site.cname, pagename=pagename, 
                        nb_revision=rev.nb_revision
            ))
            json['revisions'].append({
                'title': title,
                'content': rev.content,
                'url':  url,
                'updated':datetime_tojson(rev.updated),
                'id':rev.nb_revision
            })
        return send_json(json)

def site_changes(request, feedtype=None):
    pages = all_pages(local.db, request.site.id)
    changes = get_changes(local.db, request.site.id)

    if feedtype == "atom":
        
        feed = AtomFeed(
                    title="%s: Latest changes" % request.site.title and request.site.title or request.site.cname,
                    subtitle=request.site.subtitle,
                    updated = changes[0].updated,
                    feed_url = request.url
        )
        for rev in changes:
            _url = "%s%s" % (request.host_url, url_for("show_page", pagename=rev.title.replace(' ', '_')))
            feed.add(rev.title, convert_markdown(rev.content), 
                updated=rev.updated,
                url=_url,
                id=_url,
                author=rev.title.replace(' ', '_')
            )
        return feed.get_response()
    elif feedtype == 'json':
        json = {
                'title': "%s: Latest changes" % request.site.title and request.site.title or request.site.cname,
                'subtitle': request.site.subtitle,
                'updated':datetime_tojson(changes[0].updated),
                'feed_url': request.url,
                'pages': []
            }
        for rev in changes:
            url = "%s%s" % (request.host_url, url_for("show_page", pagename=rev.title.replace(' ', '_')))
            json['pages'].append({
                'title': rev.title,
                'content': rev.content,
                'url':  url,
                'updated':datetime_tojson(rev.updated),
                'id':rev.title.replace(' ', '_')
            })
        return send_json(json)
    elif feedtype == 'rdf':
        site_title = request.site.title and request.site.title or request.site.cname
        site_url = request.host_url
        if not local.site_url:
            site_url += local.site_url
        
        sioc = SiocWiki(site_url, site_title, datetime_tojson(request.site.created))
        for rev in changes:
            _url = "%s%s" % (request.host_url, url_for("show_page", pagename=rev.title.replace(' ', '_')))
            sioc.add_page(rev.content, rev.title, _url, datetime_tojson(rev.updated))
        return send_sioc(sioc.to_str())

    return render_response('site/changes.html', changes=changes, pages=pages)

@can_edit
@login_required
def site_export(request, feedtype="atom"):
    def _zinfo(fname, date_time):
        zinfo = zipfile.ZipInfo()
        zinfo.filename = fname
        zinfo.compress_type = zipfile.ZIP_DEFLATED
        zinfo.date_time = date_time
        return zinfo
    
    pages = all_pages(local.db, request.site.id)
    if pages:
        pages.sort(lambda a,b: cmp(a.updated, b.updated))
    if feedtype == "atom":
        feed = AtomFeed(
            title="%s: Latest changes" % request.site.title and request.site.title or request.site.cname,
            subtitle=request.site.subtitle,
            updated = pages[0].updated,
            feed_url = request.url
        )
        for page in pages:
            _url = "%s%s" % (request.host_url, url_for("show_page", pagename=page.title.replace(' ', '_')))
            feed.add(page.title, escape(page.content),
            updated=page.updated, 
            url=_url,
            id=_url,
            author=page.title.replace(' ', '_')
        )
        return feed.get_response()
    elif feedtype == "json":
        json = {
            'title': "%s: Latest changes" % request.site.title and request.site.title or request.site.cname,
            'subtitle': request.site.subtitle,
            'updated':datetime_tojson(pages[0].updated),
            'pages': []
        }
        for page in pages:
            url = url_for("show_page", 
                        pagename=page.title.replace(' ', '_')
            )
            json['pages'].append({
                'title': page.title,
                'content': page.content,
                'url':  url,
                'updated':datetime_tojson(page.updated),
                'id':page.title.replace(' ', '_')
            })
        return send_json(json)
    elif feedtype == "zip":
        pages = all_pages(local.db, request.site.id)
        zip_content = StringIO()
        zfile = zipfile.ZipFile(zip_content, "w", zipfile.ZIP_DEFLATED)
        import time, codecs
        for page in pages:
             zinfo = _zinfo("markdown/%s" % smart_str(page.title.replace(" ", "_")) + ".txt", 
                        time.localtime()[:6])
             zfile.writestr(zinfo, codecs.BOM_UTF8 + page.content.encode('utf-8'))
             zinfo = _zinfo("%s" % smart_str(page.title.replace(" ", "_")) + ".html", 
                         time.localtime()[:6])
             zfile.writestr(zinfo, codecs.BOM_UTF8 + render_template("page/export.html", 
                        page=page, request=request, pages=pages).encode( "utf-8" ))
                        
        zinfo = _zinfo("index.html", time.localtime()[:6])
        zfile.writestr(zinfo,  codecs.BOM_UTF8 + render_template("page/export_index.html",
            pages=pages, request=request).encode( "utf-8" ))
         
        zfile.close()
        response = BCResponse(zip_content.getvalue())
        response.headers['content-type'] = "application/x-zip-compressed"
        return response

@can_edit    
@login_required
def site_delete(request):
    if request.method == "POST":
        authkey = '%s_authenticated' % request.site.cname
        if authkey in request.session:
            del request.session[authkey]
        del local.db[request.site.id]
        redirect_url = "http://%s" % settings.SERVER_NAME
        return redirect(redirect_url)
    return render_response('site/delete.html')

@can_edit 
@not_claimed
def site_claim(request):
    if request.method == "POST":
        site = get_site(local.db, request.site.cname)
        site.password = make_hash(request.form['password'])
        site.email = request.form['email']
        site.privacy = request.form['privacy']
        site.claimed = True
        site.store(local.db)
        request.site = site
        
        if site.alias:
            site_url = "http://%s.%s" % (site.alias, settings.SERVER_NAME)
        else:
            site_url = "http://%s/%s" % (settings.SERVER_NAME, site.cname)
        
        mail_subject = u"You claimed %s" % site_url
        mail_content = render_template("site/email_claimed.txt", url=site_url)
        send_mail(mail_subject, mail_content, "CouchIt <feedback@couch.it>", 
            [site.email], fail_silently=True)
            
        if local.site_url:
            redirect_url = local.site_url
        else:
            redirect_url = '/'
        
        request.session['%s_authenticated' % site.cname] = True;
        return redirect(redirect_url)
        
    return render_response('site/claim.html')

@can_edit    
@login_required
def site_settings(request):
    if request.is_xhr and request.method == "POST":
        data = json.loads(request.data)
        allow_javascript = data.get('allow_javascript', False) and True or False
        site = get_site(local.db, request.site.cname)
        site.title = data.get('title', site.title)
        site.subtitle = data.get('subtitle', site.subtitle)
        site.email = data.get('email', site.email)
        site.privacy = data.get('privacy', site.privacy)
        site.allow_javascript = allow_javascript
        site.store(local.db)
        request.site = site
        return send_json({ 'ok': True })
        
    
    site_address = None
    if request.site.alias is not None and request.site.alias:
        site_address = "http://%s.%s" % (request.site.alias, settings.SERVER_NAME)
        
    # get all pages
    pages = all_pages(local.db, request.site.id)
    return render_response('site/settings.html', pages=pages, site_address=site_address)

@can_edit
@login_required
def site_address(request):
    error = None
    if request.is_xhr:
        alias = request.values.get('alias')
        if alias is None:
            return send_json({
                'ok': False,
                'error': u"alias is empty or length < 3"
            })
        elif get_site(local.db, alias, True) and request.site.alias != alias or alias in FORBIDDEN_CNAME:
            return send_json({
                'ok': False,
                'error':  u"A site with this name has already been registered in couch.it"
            })
        return send_json({ 'ok': True })
    
    if request.method == "POST":
        alias = request.form.get('alias')
        if not alias or len(alias) <= 3:
            error = u"alias is empty or length < 3"
        elif not re_address.match(alias):
            error = u"Address name is invalid. It should only contain string and _ or -."
        elif get_site(local.db, alias, True) and request.site.alias != alias:
            error = u"A site with this name has already been registered in couch.it"
        else:
            site = get_site(local.db, request.site.cname)
            site.alias = alias
            site.store(local.db)
            request.site = site
            redirect_url = "http://%s.%s" % (site.alias, settings.SERVER_NAME)
            return redirect(redirect_url)
            
    return render_response('site/site_address.html', error=error)

@not_logged    
def site_login(request):
    error = None
    notify = None
    back = ''
    if request.method == "GET":
        back=request.values.get('back', '')
        notify = request.session.get('notify', '')
        if notify:
            del request.session['notify']
    
    if request.method == "POST":
        error = u'Password is invalid.'
        if validate_password(local.db, request.site.id, request.form['password']):
            print "here"
            request.session['%s_authenticated' % request.site.cname] = True
            if 'remember' in request.form:
                request.session['permanent'] = True
            elif 'permanent' in request.session:
                del request.session['permanent']
            back = request.form.get('back', '')
            if back:
                redirect_url = back
            else:
                if local.site_url:
                    redirect_url = local.site_url
                else:
                    redirect_url = '/'
            return redirect(redirect_url)
            

    return render_response('site/login.html', back=back, error=error, notify=notify)
    

def site_logout(request):
    request.session['%s_authenticated' % request.site.cname] = False
    if local.site_url:
        redirect_url = local.site_url
    else:
        redirect_url = '/'
    return redirect(redirect_url)

def site_change_password(request):
    authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
    if authenticated:
        return change_password_authenticated(request)
    
    error = None
    token = request.values.get('t', None)
    invalid_token = False
    if request.method == 'GET':
        if token is None or not validate_token(local.db, request.site.id, token):
            error = u"Invalid token. Please verify url in your mail."
            invalid_token = True
    if request.method == 'POST':
        token = request.form.get('token', '')
        password = request.form.get('password')
        if not validate_token(local.db, request.site.id, token):
            error = u"Invalid token. Please verify url in your mail."
            invalid_token = True
        else:
            if password:
                site = get_site(local.db, request.site.cname)
                site.password = make_hash(request.form['password'])
                site.store(local.db)
            
                # delete token
                del local.db[token]
            
                request.session['%s_authenticated' % request.site.cname] = True
                request.site = site
                if local.site_url:
                    redirect_url = local.site_url
                else:
                    redirect_url = '/'
            
                return redirect(redirect_url)
            else:
                error=u'Password is empty.'
    return render_response('site/change_password.html', token=token, 
                error=error, invalid_token=invalid_token)
    
@can_edit                
def change_password_authenticated(request):
    error = None
    if request.method == 'POST':
        site = get_site(local.db, request.site.cname)
        p1 = request.form.get('password', '')
        p2 = request.form.get('old_password', '')
        
        if not p1:
            error = u"New password can't be empty"
        elif not p2:
            error = u"Old password can't be empty"
        elif make_hash(p2) != site.password:
            error = u"Old password is invalid."
        else:
            h = make_hash(p1)
            if (h != site.password):
                site.password = h
                site.store(local.db)
            request.site = site
            return redirect(url_for('site_settings'))
        
    return render_response('site/change_password_authenticated.html', error=error)

def site_forgot_password(request):
    back=request.values.get('back', '')
    if request.method == 'POST':
        back = request.form.get('back', '')
        
        # create token
        otoken = PasswordToken(site=request.site.id)
        otoken.store(local.db)
        
        if request.site.alias:
            site_url = "http://%s.%s" % (request.site.alias, settings.SERVER_NAME)
        else:
            site_url = "http://%s/%s" % (settings.SERVER_NAME, request.site.cname)
        
        # send email
        mail_subject = u"Password to your couchit site"
        mail_content = render_template('site/forgot_password.txt', url=site_url, token=otoken.id)
        send_mail(mail_subject, mail_content, "CouchIt <feedback@couch.it>", 
            [request.site.email], fail_silently=True)
            
        request.session['notify'] = u"We've sent out the secret link. Go check your email!"
        redirect_url = url_for('site_login', back=back)
        return redirect(redirect_url)
        
    return render_response('site/forgot_password.html', back=back)

@can_edit
@login_required
def site_design(request):
    DEFAULT_COLORS = dict(
        background_color = 'E7E7E7',
        text_color = '000000',
        link_color = '14456E',
        border_color = 'D4D4D4',
        page_fill_color = 'FFFFFF',
        page_text_color = '000000',
        page_link_color = '14456E',
        menu_inactive_color = '666666',
        syntax_style = 'default'
    )
    
    if not request.site.theme or request.site.theme is None:
        request.site.theme = DEFAULT_COLORS
        
    if request.method == 'POST':
        site = get_site(local.db, request.site.cname)
        style = request.form.get('style', 'default')
        if style == 'default':
            site.default_theme = True
            site.theme = DEFAULT_COLORS
        else:
            site.default_theme = False
            site.theme = dict(
                background_color = request.form.get('background_color', 'E7E7E7'),
                text_color = request.form.get('text_color', '000000'),
                link_color = request.form.get('link_color', '14456E'),
                border_color = request.form.get('border_color', 'D4D4D4'),
                page_fill_color = request.form.get('page_fill_color', 'FFFFFF'),
                page_text_color = request.form.get('page_text_color', '000000'),
                page_link_color = request.form.get('page_link_color', '14456E'),
                menu_inactive_color = request.form.get('menu_inactive_color', '666666'),
                syntax_style = request.form.get('syntax_style', 'default')
            )
        site.store(local.db)
        request.site = site 
     
    pages = all_pages(local.db, request.site.id)       
    return render_response('site/design.html', pages=pages)
    

    
def sitemap(request):
    pages = all_pages(local.db, request.site.id)
    return render_response("site/sitemap.xml", pages=pages)
         
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
        body = input_stream.read()
        r = urllib2.Request(url, body, headers)
        y = urllib2.urlopen(r)
    else:
        headers = {
            "Content-Type": request.environ["CONTENT_TYPE"],
            "Accept": request.environ["HTTP_ACCEPT"]
        }
        r = urllib2.Request(url, headers=headers)
        y = urllib2.urlopen(r)
        
    i = y.info()
    if i.has_key("Content-Type"):
        content_type = i["Content-Type"]
    else:
        content_type = 'text/plain'
    
    resp = y.read()
    
    response = BCResponse(resp)
    response.content_type = content_type
    return response 


def couchit_about(request):
    return render_response('about.html')
    

def couchit_help(request):
    return render_response('help.html')

def couchit_find(request):
    return render_response('find.html')
