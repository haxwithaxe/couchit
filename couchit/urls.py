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

from werkzeug.routing import Map, Rule, Subdomain, RequestRedirect,Submount

from couchit import views

all_views = {
    'home': views.home,
    'show_page': views.show_page,
    'edit_page': views.edit_page,
    'history_page': views.history_page,
    'revision_page': views.revision_page,
    'diff_page': views.diff_page,
    'revisions_feed': views.revisions_feed,
    'site_changes': views.site_changes,
    'site_design': views.site_design,
    'site_settings': views.site_settings,
    'site_claim': views.site_claim,
    'proxy': views.proxy,
    'login': views.site_login,
    'logout': views.site_logout
}



urls_map = Map([
    Rule('/proxy', endpoint='proxy', ),
    Rule('/site/design', endpoint='site_design', ),
    Rule('/site/claim', endpoint='site_claim', ),
    Rule('/site/settings', endpoint='site_settings', ),
    Rule('/site/changes', endpoint='site_changes', ),
    Rule('/site/changes.<feedtype>', endpoint='site_changes', ),
    Rule('/login', endpoint='login', ),
    Rule('/logout', endpoint='logout', ),
    Rule('/<pagename>/revisions.<feedtype>', endpoint='revisions_feed', ),
    Rule('/<pagename>/revision/<nb_revision>', endpoint='revision_page', ),
    Rule('/<pagename>/history', endpoint='history_page', ),
    Rule('/<pagename>/edit', endpoint='edit_page', ),
    Rule('/<pagename>/diff', endpoint='diff_page', ),
    Rule('/', defaults={'pagename': 'home' }, endpoint='show_page', ),
    Rule('/<pagename>', endpoint='show_page', )
])

