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

import re
import urllib2
from jinja2.filters import do_truncate, do_striptags
from werkzeug import redirect
from werkzeug.contrib.atom import AtomFeed
from werkzeug.routing import NotFound
from werkzeug.utils import url_unquote
from couchit import settings
from couchit.models import Site, Page, PasswordToken
from couchit.api import *
from couchit.http import BCResponse
from couchit.template import render_response, url_for, render_template, send_json
from couchit.utils import local, make_hash, datetime_tojson
from couchit.utils.mail import send_mail

FORBIDDEN_PAGES = ['site', 'delete', 'edit', 'create', 'history', 'changes']

re_page = re.compile(r'^[- \w]+$', re.U)

def not_logged(f):
    def decorated(request, **kwargs):
        authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
        if authenticated:
            redirect_url = local.site_url and local.site_url or "/"
            return redirect(redirect_url)
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
  
  
def show_page(request=None, pagename=None):
    if pagename is None:
        pagename ='home'
        
    page = get_page(local.db, request.site.id, pagename)
    if not page or page.id is None or not re_page.match(pagename):
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
    
    # get all pages
    pages = all_pages(local.db, request.site.id)
    
    return render_response('page/show.html', page=page, pages=pages, lexers=LEXERS_CHOICE)
    

def edit_page(request=None, pagename=None):
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
        redirect_url = url_for('show_page', pagename=pagename)
        return redirect(redirect_url)
    
    return render_response('page/edit.html', page=page)
  
  
def history_page(request=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    
    if not page:
        return NotFound
    
    revisions = page.revisions(local.db)
    
    # get all pages
    pages = all_pages(local.db, request.site.id)

    return render_response('page/history.html', page=page, pages=pages, revisions=revisions)
    

def revision_page(request=None, pagename=None, nb_revision=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        return NotFound
        
    if nb_revision is None:
        nb_revision = 0
    else:
        try:
            nb_revision = int(nb_revision)
        except ValueError:
            return NotFound

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
 
   
def diff_page(request=None, pagename=None):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        if request.is_xhr:
            return send_json({'ok': False, 'reason': 'not found'})
        return NotFound
    
    revisions = request.values.getlist('r')
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

    
  
def revisions_feed(request=None, pagename=None, feedtype="atom"):
    if pagename is None:
        pagename ='Home'
    page = get_page(local.db, request.site.id, pagename)
    if not page:
        return NotFound
    all_revisions = [page] + page.revisions(local.db)
    if feedtype == "atom":
        feed = AtomFeed(
                    title="%s: Latest revisions of %s" % (request.site.cname, page.title),
                    subtitle=request.site.subtitle,
                    updated = page.updated,
                    id = page.title.replace(" ", "_")
        )
        for rev in all_revisions:
            for change in rev.changes:
                if change['type'] != "unmod":
                    title = "\n".join(change['changed']['lines'])
                    title = do_truncate(do_striptags(title), 60)
            title = title and title or "Edited."
            feed.add(title, rev.content, 
                updated=rev.updated,
                url=url_for("revision_page", 
                    cname=request.site.cname, pagename=pagename, 
                    nb_revision=rev.nb_revision
                ),
                id=str(rev.nb_revision)
            )
        return feed.get_response()
    else:
        json = {
            'title': "%s: Latest revisions of %s" % (request.site.cname, page.title),
            'subtitle': request.site.subtitle,
            'updated':datetime_tojson(page.updated),
            'revisions': []
        }
        for rev in all_revisions:
            title = ''
            for change in rev.changes:
                if change['type'] != "unmod":
                    title = "\n".join(change['changed']['lines'])
                    title = do_truncate(do_striptags(title), 60)
                    
            title = title and title or "Edited."
            url = url_for("revision_page", 
                        cname=request.site.cname, pagename=pagename, 
                        nb_revision=rev.nb_revision
            )
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
                    id = request.site.cname
        )
        for rev in changes:
            feed.add(rev.title, rev.content, 
                updated=rev.updated,
                url=url_for("show_page", 
                    cname=request.site.cname, pagename=rev.title.replace(' ', '_')
                ),
                id=rev.title.replace(' ', '_')
            )
        return feed.get_response()
    elif feedtype == 'json':
        json = {
                'title': "%s: Latest changes" % request.site.title and request.site.title or request.site.cname,
                'subtitle': request.site.subtitle,
                'updated':datetime_tojson(changes[0].updated),
                'pages': []
            }
        for rev in changes:
            url = url_for("show_page", 
                        cname=request.site.cname, pagename=rev.title.replace(' ', '_')
            )
            json['pages'].append({
                'title': rev.title,
                'content': rev.content,
                'url':  url,
                'updated':datetime_tojson(rev.updated),
                'id':rev.title.replace(' ', '_')
            })
        return send_json(json)

    return render_response('site/changes.html', changes=changes, pages=pages)
        
    

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
    

def site_settings(request):
    # get all pages
    pages = all_pages(local.db, request.site.id)
    return render_response('site/settings.html', pages=pages)

@not_logged    
def site_login(request):
    back=request.values.get('back', '')
    error = None
    notify = request.session.get('notify', '')
    if notify:
        del request.session['notify']
    if request.method == "POST":
        if validate_password(local.db, request.site.id, request.form['password']):
            request.session['%s_authenticated' % request.site.cname] = True
            if request.form['remember']:
                request.session['permanent'] = True
            back = request.form['back']
            redirect_url = back and back or '/'
            return redirect(redirect_url)
        else:
            error = u'Password is invalid.'
    return render_response('site/login.html', back=back, error=error, notify=notify)
    

def site_logout(request):
    request.session['%s_authenticated' % request.site.cname] = False
    if local.site_url:
        redirect_url = local.site_url
    else:
        redirect_url = '/'
    return redirect(redirect_url)

@not_logged
def site_change_password(request):
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

@not_logged    
def site_forgot_password(request):
    back=request.values.get('back', '')
    if request.method == 'POST':
        back = request.form['back']
        
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
        redirect_url = url_for('login', back=back)
        return redirect(redirect_url)
        
    return render_response('site/forgot_password.html', back=back)

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
                menu_inactive_color = request.form.get('menu_inactive_color', '666666')
            )
        site.store(local.db)
        request.site = site 
     
    pages = all_pages(local.db, request.site.id)       
    return render_response('site/design.html', pages=pages)
    
        
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
