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
    'delete_page': views.delete_page,
    'history_page': views.history_page,
    'revision_page': views.revision_page,
    'diff_page': views.diff_page,
    'revisions_feed': views.revisions_feed,
    'site_changes': views.site_changes,
    'sitemap': views.sitemap,
    'site_design': views.site_design,
    'site_settings': views.site_settings,
    'site_claim': views.site_claim,
    'proxy': views.proxy,
    'site_login': views.site_login,
    'site_logout': views.site_logout,
    'forgot_password': views.site_forgot_password,
    'change_password': views.site_change_password,
    'site_address': views.site_address,
    'site_export': views.site_export,
    'site_delete': views.site_delete,
    'couchit_about': views.couchit_about,
    'couchit_find': views.couchit_find,
    'couchit_help': views.couchit_help
}



urls_map = Map([
    Rule('/', endpoint='show_page'),
    Rule('/proxy', endpoint='proxy'),
    Rule('/site/design', endpoint='site_design'),
    Rule('/site/claim', endpoint='site_claim'),
    Rule('/site/delete', endpoint='site_delete'),
    Rule('/site/forgot-password', endpoint='forgot_password'),
    Rule('/site/change-password', endpoint='change_password'),
    Rule('/site/change-site-address', endpoint='site_address'),
    Rule('/site/settings', endpoint='site_settings'),
    Rule('/site/sitemap.xml', endpoint='sitemap'),
    Rule('/sitemap.xml', endpoint='sitemap'),
    Rule('/site/changes', endpoint='site_changes'),
    Rule('/site/changes.<feedtype>', endpoint='site_changes'),
    Rule('/site/export.<feedtype>', endpoint='site_export'),
    Rule('/site/login', endpoint='site_login'),
    Rule('/site/logout', endpoint='site_logout'),
    Rule('/<path:pagename>/revisions.<feedtype>', endpoint='revisions_feed'),
    Rule('/<path:pagename>/revision/<nb_revision>', endpoint='revision_page'),
    Rule('/<path:pagename>/history', endpoint='history_page'),
    Rule('/<path:pagename>/edit', endpoint='edit_page'),
    Rule('/<path:pagename>/delete', endpoint='delete_page'),
    Rule('/<path:pagename>/diff', endpoint='diff_page'),
    Rule('/<path:pagename>/', endpoint='show_page', strict_slashes=False),
    Rule('/<path:pagename>', endpoint='show_page', strict_slashes=False)
    
   
])

