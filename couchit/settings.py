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

DEBUG = True

SERVER_NAME = 'couch.it:5000'

# database
SERVER_URI ='http://127.0.0.1:5984'
DATABASE_NAME ='couchit'

# paths
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.join(PROJECT_PATH, '../static')
TEMPLATES_PATH = os.path.join(PROJECT_PATH, '../templates')

SECRET_KEY = "%k5h7xdg+&gi)bar$&gr^5$vaxvvk&z3vq@iizo@s$h3a-___$"

############
# SESSIONS #
############
SESSION_COOKIE_NAME = 'COUCHIT_SID'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = False


ALLOWED_HOSTS = ['www.friendpaste.com', 'friendpaste.com', 
'pypaste.com', 'www.pypaste.com']