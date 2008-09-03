#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 by Benoît Chesneau <couchit@e-engura.com>
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

from werkzeug import script

def make_couchit():
    from couchit.application import CouchitApp
    return CouchitApp()

def shell_init_func():
    from couchit import settings
    couchit = make_couchit()
    return locals()

def setup():
    from couchit.utils import install, load_views
    couchit = make_couchit()
    install()
    load_views()

action_runserver = script.make_runserver(make_couchit, use_reloader=True)
action_shell = script.make_shell(shell_init_func)
action_setup = setup

if __name__ == '__main__':
    script.run()
