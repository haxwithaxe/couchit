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
        'current_url': request.url,
        'host_url': request.host_url
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
        
