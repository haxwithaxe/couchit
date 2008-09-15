# -*- coding: utf-8 -
#
# Copyright 2008 by Benoît Chesneau <benoitc@e-engura.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from couchit.template import register_contextprocessor
from couchit.utils import local

@register_contextprocessor
def site(request):
    site = getattr(request, 'site', '')
    return { 'site': site }

@register_contextprocessor
def site_url(request):
    if hasattr(local, 'site_url'):
        site_url = local.site_url
    else:
        site_url = ''
    return {
        'site_url': site_url,
        'current_url': request.url
    }

@register_contextprocessor
def authenticated(request):
    authenticated = False
    can_edit = True
    if hasattr(request, 'site'):
        authenticated = request.session.get('%s_authenticated' % request.site.cname, False)
        if request.site.privacy == "public" and not authenticated:
            can_edit = False
            
    return { 
        'authenticated': authenticated,
        'can_edit': can_edit
     }
        
