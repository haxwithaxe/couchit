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

import platform
import os

DEBUG = False

SERVER_NAME = 'couch.it'

NODE_DEV = "enki.local"
if platform.node() == NODE_DEV:
    SERVER_NAME = "couchit.local:5000"
    
# database
SERVER_URI ='http://127.0.0.1:5984'
DATABASE_NAME ='couchit'

# paths
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.join(PROJECT_PATH, '../static')
TEMPLATES_PATH = os.path.join(PROJECT_PATH, '../templates')

DESIGN_PATH = (
    os.path.join(PROJECT_PATH, '../_design'),
)

SECRET_KEY = "%k5h7xdg+&gi)bar$&gr^5$vaxvvk&z3vq@iizo@s$h3a-___$"

############
# SESSIONS #
############
SESSION_COOKIE_NAME = 'COUCHIT_SID'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = False

###########
# EMAIL   #
###########
# Host for sending e-mail.
EMAIL_HOST = 'localhost'

# Port for sending e-mail.
EMAIL_PORT = 25

# Optional SMTP authentication information for EMAIL_HOST.
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_USE_TLS = False


# for ajax proxy
ALLOWED_HOSTS = ['www.friendpaste.com', 'friendpaste.com', 
'pypaste.com', 'www.pypaste.com']
