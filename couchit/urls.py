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

from werkzeug.routing import Map, Rule, RequestRedirect,Submount

from couchit import views

all_views = {
    'home': views.home,
    'show_page': views.show_page,
    'edit_page': views.edit_page,
    'history_page': views.history_page,
    'revision_page': views.revision_page,
    'diff_page': views.diff_page,
    'site_design': views.site_design,
    'site_settings': views.site_settings,
    'site_claim': views.site_claim
}



urls_map = Map([
    Rule('/', endpoint='home'),
    
    Rule('/<cname>/site/design', endpoint='site_design'),
    Rule('/<cname>/site/claim', endpoint='site_claim'),
    Rule('/<cname>/site/settings', endpoint='site_settings'),
    Rule('/<cname>/<pagename>/revision/<nb_revision>', endpoint='revision_page'),
    Rule('/<cname>/<pagename>/history', endpoint='history_page'),
    Rule('/<cname>/<pagename>/edit', endpoint='edit_page'),
    Rule('/<cname>/<pagename>/diff', endpoint='diff_page'),
    Rule('/<cname>', defaults={'pagename': 'home' }, endpoint='show_page'),
    Rule('/<cname>/<pagename>', endpoint='show_page'),
    
])