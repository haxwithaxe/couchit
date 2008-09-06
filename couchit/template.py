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
import simplejson as json

from couchit import settings
from couchit.http import BCResponse, BCRequest
from couchit.contrib.markdown2 import Markdown
from couchit.utils import local, datetime_tojson, datetimestr_topython

template_env = Environment(loader=FileSystemLoader(settings.TEMPLATES_PATH))
template_env.charset = 'utf-8'
_markdown = Markdown(safe_mode=True, extras=['code-color'])
WIKI_CHANGES = {
    'mod': 'Changed',
    'add': 'Added',
    'del': 'Removed',
    'ins': 'Inserted'
}

def pretty_type(value):
    return WIKI_CHANGES.get(value, '')
template_env.filters['pretty_type'] = pretty_type

def url_for(endpoint, _external=False, **values):
    return local.url_adapter.build(endpoint, values, force_external=_external)
template_env.globals['url_for'] = url_for

template_env.globals['DEBUG'] = settings.DEBUG
template_env.filters['rfc3339'] = datetime_tojson

def convert_markdown(value):
    return _markdown.convert(value)
template_env.filters['markdown'] = convert_markdown

def format_datetime(value):
    value = datetimestr_topython(value)
    return value.strftime("%a %b %d %Y at %H:%M")
template_env.filters['formatdatetime'] = format_datetime

def tabular(value): 
    """
    display diff as block
    """
    rst ='<tr class="tabularh"><th class="linenos">a</th><th class="linenos">b</th><td colspan="2"></td></tr>'
    for row in value:
        for change in row:
            
            if change['type'] == 'unmod':
                l = change['base']['offset']
                for line in change['base']['lines']:
                    rst = rst + "<tr class=\"unmod\"><th class=\"linenos\">%s</th>\
                    <th class=\"linenos\">%s</th><td></td><td>%s</td>" % (
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
                    <th class=\"linenos\"></th><th class="diffm">-</th><td class="c wrap %s">%s</td>' % (
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
                    <th class=\"diffp\">+</th><td class=\"c wrap %s\">%s</td>" % (
                        class_,
                        change['base']['offset'],
                        class_end,
                        line
                    )
                    class_end = ""
                    pos = pos + 1
                    if pos == nb_lines:
                        class_end = "last"
            rst = rst + "<tr><th class=\"linenos\">...<th><td colspan=\"3\"></td></tr>"
    rst = "<table class=\"difftabular\">%s</table>" % rst
    return rst
template_env.filters['tabular'] = tabular

def render_response(template_name, **kwargs):
    return BCResponse(render_template(template_name, **kwargs))

def render_template(template_name, _stream=False, **kwargs):
    tmpl = template_env.get_template(template_name)
    if _stream:
        return tmpl.stream(kwargs)
    return tmpl.render(kwargs)
    
def send_json(Body, etag=None):
    resp = BCResponse(json.dumps(Body))
    resp.add_etag()
    resp.headers['content-type'] = 'application/json'
    return resp