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

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from pygments.styles import get_all_styles
import simplejson as json

from couchit import settings
from couchit.http import BCResponse, BCRequest
from couchit.contrib import markdown2
from couchit.utils import local, datetime_tojson, datetimestr_topython,force_unicode, smart_str
from couchit.utils.html import sanitize_html

template_env = Environment(loader=FileSystemLoader(settings.TEMPLATES_PATH))
template_env.charset = 'utf-8'
WIKI_CHANGES = {
    'mod': 'Changed',
    'add': 'Added',
    'del': 'Removed',
    'ins': 'Inserted'
}


_context_processors = []

def pretty_type(value):
    return WIKI_CHANGES.get(value, '')
template_env.filters['pretty_type'] = pretty_type

def url_for(endpoint, _external=False, **values):
    url = local.url_adapter.build(endpoint, values, force_external=_external)
    if getattr(local, 'cname', None) != None:
        url = "/%s%s" % (local.cname, url)
    return url

template_env.globals['url_for'] = url_for

template_env.globals['DEBUG'] = settings.DEBUG
template_env.filters['rfc3339'] = datetime_tojson
template_env.globals['ALL_COLORSHEME'] = list(get_all_styles())

re_script = re.compile("\"\'][\s]*javascript:(.*)[\"\']/g")


def convert_markdown(value, javascript=False):
    if local.site_url:
        base_url = local.site_url + '/'
    else:
        base_url = ''
    
    link_patterns = [
        (re.compile("\[\[\s*([^\]]+)\]\]", re.U), r'%s\1' % base_url, 1),
        (re.compile(r"(^| )(\b[A-Z][a-z]+[A-Z]\w+\b)", re.U), r"%s\1" % base_url, 0)
        
    ]
    
    md = markdown2.Markdown(extras=["link-patterns", "codehilite"],
                            link_patterns=link_patterns)
    
    _parsed_value = sanitize_html(md.convert(value), javascript=javascript)
    _parsed_value = force_unicode(_parsed_value)
    return _parsed_value
    
template_env.filters['markdown'] = convert_markdown


def format_datetime(value):
    value = datetimestr_topython(value)
    return value.strftime("%a %b %d %Y at %H:%M")
template_env.filters['formatdatetime'] = format_datetime

def date(value, arg=None):
    """Formats a date according to the given format."""
    if not value:
        return u''
    if arg is None:
        arg = "%a %b %d %Y at %H:%M"
    return value.strftime(arg)
template_env.filters["date"]=date

def tabular(value, r1, r2): 
    """
    display diff as block
    """
    rst ="""<tr class="tabularh"><th class="linenos">
    <a href="%(r1_url)s" title="revision %(r1_nb)s">%(r1_nb)s</a></th>
    <th class="linenos"><a href="%(r2_url)s" title="revision %(r2_nb)s">%(r2_nb)s</a></th>
    <td colspan="2"></td></tr>""" % {
        'r1_url': url_for('revision_page', cname=local.request.site.cname, pagename=r1.title.replace(" ", "_"), nb_revision=r1.nb_revision),
        'r1_nb':  r1.nb_revision,
        'r2_url': url_for('revision_page', cname=local.request.site.cname, pagename=r2.title.replace(" ", "_"), nb_revision=r2.nb_revision),
        'r2_nb': str(r2.nb_revision)
         
    }
    
    for row in value:
        for change in row:
            
            if change['type'] == 'unmod':
                l = change['base']['offset']
                for line in change['base']['lines']:
                    rst = rst + "<tr class=\"unmod\"><th class=\"linenos\">%s</th>\
                    <th class=\"linenos\">%s</th><td></td><td>%s</td></tr>" % (
                        l,
                        l,
                        line
                    )
                    l = l + 1
            else:
                class_ = "base btop"
                class_start="first" 
                
                nb_lines = len(change['base']['lines'])
                if change["type"] == "rem" and nb_lines == 1:
                    class_start = class_start +  " last"
                
                pos = 1
                for line in change['base']['lines']:       
                    rst = rst + '<tr class="%s"><th class=\"linenos\">%s</th>\
                    <th class=\"linenos\"></th><th class="diffm">-</th><td class="c wrap %s">%s</td></tr>' % (
                        class_,
                        change['base']['offset'],
                        class_start,
                        line
                    )
                    class_ = "base"
                    class_start = ""
                    pos = pos + 1
                    if pos == nb_lines and change["type"] == "rem":
                        class_start = "last"
                
                class_end = ""
                class_ = "changed"
                nb_lines = len(change['changed']['lines'])
                if change["type"] == "add":
                    if nb_lines == 1:
                        class_end = "first last"
                    else:
                        class_end = "first"
                if change["type"] == "mod" and nb_lines == 1:
                    class_end = "last"
                    
                pos = 1
                for line in change['changed']['lines']:
                    rst = rst + "<tr class=\"%s\"><th class=\"linenos\"></th><th class=\"linenos\">%s</th>\
                    <th class=\"diffp\">+</th><td class=\"c wrap %s\">%s</td></tr>" % (
                        class_,
                        change['base']['offset'],
                        class_end,
                        line
                    )
                    class_end = ""
                    pos = pos + 1
                    if pos == nb_lines:
                        class_end = "last"
            rst = rst + "<tr><th class=\"linenos\">...</th><td colspan=\"3\"></td></tr>"
    rst = "<table id=\"tableDiff\" class=\"difftabular\">%s</table>" % rst
    return rst
template_env.filters['tabular'] = tabular

def render_response(template_name, **kwargs):
    return BCResponse(render_template(template_name, **kwargs))

def render_template(template_name, _stream=False, **kwargs):
    tmpl = template_env.get_template(template_name)
    request = getattr(local, 'request', None)
    
    if  request is not None and isinstance(request, BCRequest):
        context = {}
        for processor in _context_processors:
            context.update(processor(request))
        context.update(kwargs)
    else:
        context = kwargs
    if _stream:
        return tmpl.stream(context)
    return tmpl.render(context)
    
def send_json(Body, etag=None):
    resp = BCResponse(json.dumps(Body))
    resp.add_etag()
    resp.headers['content-type'] = 'application/json'
    return resp
    
def register_contextprocessor(func):
    _context_processors.append(func)
    return func
