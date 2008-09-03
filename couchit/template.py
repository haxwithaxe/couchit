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

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import simplejson as json

from couchit import settings
from couchit.http import BCResponse, BCRequest
from couchit.contrib.markdown import Markdown
from couchit.utils import local, datetime_tojson, datetimestr_topython

template_env = Environment(loader=FileSystemLoader(settings.TEMPLATES_PATH))
template_env.charset = 'utf-8'
_markdown = Markdown()

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