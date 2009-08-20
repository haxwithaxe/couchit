#!/usr/local/bin/python -v
# -*- coding: utf-8 -*-
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
import os
import sys

sys.path.append('/var/www/vhosts/couchit-v1.1')
os.environ['PYTHON_EGG_CACHE'] = '/var/cache/.python-eggs'


def make_couchit():
    from couchit.application import CouchitApp
    return CouchitApp()

application = make_couchit()