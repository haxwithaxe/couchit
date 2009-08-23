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

import restclient

class Akismet(restclient.Resource):
    URI = "rest.akismet.com/1.1"
    USER_AGENT = "couchit/1.1"
    
    def __init__(self, site_url, key):
        self.default_headers = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        self.key = key
        self.site_url = site_url
        self.API_KEY_URI = "http://%s.%s" % (key, self.URI)
        super(Akismet, self).__init__(self.API_KEY_URI)
        
    def _make_params(self, user_ip, user_agent, content, extras=None):
        extras = extras or {}
        params = {
            "blog": self.site_url,
            "user_ip": user_ip,
            "user_agent": user_agent,
            "comment_content": content
        }
        
        params.update(extras)
        return params
        
    def comment_check(self, user_ip, user_agent, content, extras=None):
        params = self._make_params(user_ip, user_agent, content, extras=extras)
        res = self.post("/comment-check", params, headers=self.default_headers)
        if res == "true":
            return True
        return False
        
    def submit_spam(self, user_ip, user_agent, content, extras=None):
        params = self._make_params(user_ip, user_agent, content, extras=extras)
        self.post("/submit-spam", params, headers=self.default_headers)
        
    def submit_ham(self, user_ip, user_agent, content, extras=None):
        params = self._make_params(user_ip, user_agent, content, extras=extras)
        self.post("/submit-ham", params, headers=self.default_headers)
        
    def verify_key(self):
        res = restclient.RestClient()
        resp = res.post("http://%s" % self.URI, "/verify-key", body={"blog": self.site_url, "key": self.key},
                    headers=self.default_headers)
        if resp != "valid":
            return False
        return True 
        