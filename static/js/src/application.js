// allow IE to recognize HTMl5 elements
if (!document.createElementNS) {
    document.createElement('section');
    document.createElement('audio');
    document.createElement('video');
    document.createElement('article');
    document.createElement('aside');
    document.createElement('footer');
    document.createElement('header');
    document.createElement('nav');
    document.createElement('time');
}

Date.parseRFC3339 = function (string) {
    var date=new Date(0);
    var match = string.match(/(\d{4})-(\d\d)-(\d\d)\s*(?:[\sT]\s*(\d\d):(\d\d)(?::(\d\d))?(\.\d*)?\s*(Z|([-+])(\d\d):(\d\d))?)?/);
    if (!match) return;
    if (match[2]) match[2]--;
    if (match[7]) match[7] = (match[7]+'000').substring(1,4);
    var field = [null,'FullYear','Month','Date','Hours','Minutes','Seconds','Milliseconds'];
    for (var i=1; i<=7; i++) if (match[i]) date['setUTC'+field[i]](match[i]);
    if (match[9]) date.setTime(date.getTime()+(match[9]=='-'?1:-1)*(match[10]*3600000+match[11]*60000) );
    return date.getTime();
}


// Localize the display of <time> elements
function localizeDates() {
    var lastdate = '';
    var now = new Date();

    $$('time').each(function(el, index) {
        if (el.getAttribute('title') == "GMT") {
            var date = new Date(Date.parseRFC3339(el.getAttribute('datetime')));
            if (!date.getTime())
                return;
            diff = ((now.getTime() - date.getTime()) / 1000),
            day_diff = Math.floor(diff / 86400);
            if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
                return;
            var text = date.toLocaleString();
            var title = date.toLocaleString();
            
            if (day_diff == 0) {
                text = (diff < 60 && "Just Now" ||
                diff < 120 && "1 minute ago" ||
                diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
                diff < 7200 && "1 hour ago" ||
                diff < 86400 && Math.floor( diff / 3600 ) + " hours ago");
                title = date.toLocaleTimeString();
            } else {
                hours = date.getHours();
                minutes = date.getMinutes();
                hours = (hours < 10) && "0" + hours || hours;
                minutes = (minutes < 10) && "0" + minutes || minutes;
                text = (day_diff == 1 && "Yesterday at " +  hours + ":" + minutes ||
                el.textContent);
                title = date.toLocaleString();
            }
            el.setAttribute('title', title);
            el.textContent = "posted " + text;
        }
    });

}

var Page = {};
var Site = {
    url: "",
    name: ""
};

var FORBIDDEN_PAGES = ['site', 'delete', 'edit', 'create', 'history', 'changes', 'archives']

var Create = Class.create({
    initialize: function() {
        var self = this;
        
     
        
        this.Form = $("fnewpage");
        this.doCreate = $("doCreate");
       
        this.Form.addClassName("hidden");
        Event.observe(this.doCreate, "click", function(e) {
            Event.stop(e);
            self.show();
            return false;
        }, false);
        
        Event.observe($$("a.cancelCreate")[0], "click", function(e) {
            Event.stop(e);
            self.cancel();
            return false;
        }, false);

        $("screate").observe("click", function(e) {
            Event.stop(e);
            self.submit();
            return false;
        }, false);
    },
    
    show: function() {
        this.doCreate.addClassName("hidden");
        this.Form.removeClassName("hidden");
    },
    
    cancel: function() {
        this.Form.addClassName("hidden");
        this.doCreate.removeClassName("hidden");
    },
    
    submit: function() { 
        var title = $("title");
        if (!title.value.match(/^['\-\"\/ \w\u00A1-\uFFFF]+$/i) || FORBIDDEN_PAGES.indexOf(title.value) >= 0) {
            alert("Page title invalid");
            return false;
        }
        
        var slug = title.value.replace(/ /g, "_");
        url = Site.url + "/" +  slug + "#pedit";
        
        window.location.href = url;
        this.Form.addClassName("hidden");
        this.doCreate.removeClassName("hidden");
    },
});

var Compare = Class.create({
    nb_selected: 0,
    selected: false,
    
    initialize: function() {
        var self = this;
        
        this.Form = $('fhistory');
        $$('input.c').each(function(el) {
            el.observe("click", function(e) {
                self.check(this);
            }, false);
        });
    },
    check: function(el) {
        row = el.parentNode.parentNode;
        row.toggleClassName('rselected')
        if (!el.checked) {
            this.nb_selected -=1;
            el.removeClassName("selected");
        
        } else {
            this.nb_selected +=1;
            el.addClassName("selected");
            
        }
        
        if (this.nb_selected == 2) {
            $$('input.c').each(function(el) {
                if (! el.hasClassName('selected'))
                    el.disabled = "disabled";
            });
            this.selected = true;
        } else {
            if (this.selected) {
                $$('input.c').each(function(el) {
                    if (! el.hasClassName('selected'))
                        el.disabled = null;
                });
                this.selected = false;
            }
        }
    }
});

var Diff = Class.create({
    initialize: function() {
        var self = this;
        this.rev_from = $('rev_from');
        this.rev_to = $('rev_to');
        
        $('scompare').observe('click', function(e) {
            Event.stop(e);
            self.get_diff();
            return false;
        })
    },
    
    get_diff: function() {
        var from = this.rev_from.getValue();
        var to = this.rev_to.getValue();
        if (from == to) {
            alert("Why would you want compare same version ...");
            return
        }
        url = $('fdiff').action + "?r="+from+"&r="+to;
        new Ajax.Request(url, {
          method: 'get',
          contentType: 'application/json', 
          requestHeaders: {Accept: 'application/json'},
          onSuccess: function(response) {   
             data = response.responseText.evalJSON(true);
             if (data['ok']) {
                Element.remove($('tableDiff'));
                $('pdiff').insert(data['diff'])
             }
         }
        });
    }
});

var Settings = Class.create({
   initialize: function() {
       var self = this;
       this.observer = null;
       this.title = $('site_header').select("h1 a")[0];
       this.subtitle = $('site_header').select("h2")[0];
       $$('input').each(function(el) {
          new Form.Element.Observer(
              el,
              0.2, 
              function(el, value) {
                  if (el.id == "site_title") {
                      self.title.update(value);
                      document.title = value + " - settings";
                  }
                    
                  if (el.id == "site_subtitle")
                    self.subtitle.update(value);
                    
                   if(self.observer) clearTimeout(self.observer);
                   self.observer = setTimeout(self.save.bind(self), 400);
              }
         );
       });
   },
   
   save: function() {
       var data = {}
       try {
           data = {
               'title': $('site_title').getValue(),
               'subtitle': $('site_subtitle').getValue(),
               'email': $('email').getValue(),
               'privacy': $$('input:checked[type="radio"][name="privacy"]').pluck('value')[0],
               'allow_javascript': $('allow_javascript').getValue()
           }
       } catch(e) {
           data = {
                'title': $('site_title').getValue(),
                'subtitle': $('site_subtitle').getValue()
            }
       }
       
       
       url = $('fsettings').action;
       new Ajax.Request(url, {
         method: 'post',
         postBody: Object.toJSON(data),
         contentType: 'application/json', 
         requestHeaders: {Accept: 'application/json'},
         onSuccess: function(response) {   
            data = response.responseText.evalJSON(true);
            
        }
       });
   }
});


var SiteAddress = Class.create({
    initialize: function() {
        var self = this;
        if (!$('error').innerHTML)
            $('error').hide();
            
        new Form.Element.Observer(
              "alias",
              0.2, 
              function(el, value) {
                  if (value.length > 3 && !value.match(/^(\w+)$/)) {
                       $('error').update("<strong>Error:</strong> "+ 
                       $('alias').value + " is invalid, "+ 
                       "only use letters and numbers.");
                       $('error').show();
                  } else {
                      $('error').hide()
                  }
              }
         );

         $('faddress').observe('submit', function(e) {
            Event.stop(e);
            var error = null;
            var value = $('alias').getValue();
            
            if (value.length <= 3) {
                error = "length < 3";
            } else if (!value.match(/^(\w+)$/)) {
                error = value + " is invalid, only use letters and numbers."
            } 
            if (error) {
                $('error').update("<strong>Error:</strong> "+error);
                $('error').show();
                return false;
            } else {
                self.valid_name();
            }

         }, false)
        
    },
    
    valid_name: function() {
        url = $('faddress').action;
        new Ajax.Request(url, {
          method: 'get',
          contentType: 'application/json',
          parameters: {
              'alias': $('alias').getValue()
          }, 
          requestHeaders: {Accept: 'application/json'},
          onSuccess: function(response) {   
             data = response.responseText.evalJSON(true);
             if (data['ok']) {
                 $('faddress').submit();
             } else {
                 $('error').update("<strong>Error:</strong> "+data['error']);
                 $('error').show();
             }
         }
        });
    }
    
    
})

var Claim = Class.create({
    initialize: function() {
        var self = this;
        this.email = $('email');
        this.password = $('password')
        $('fclaim').observe('submit', function(e) {
            Event.stop(e);
            if (self.validate()) {
                this.submit();
            }
        }, false);
    },
    
    validate: function() {
        $$('.help_error').each(function(el) {
            el.remove();
        });
        $$('.errors').each(function(el) {
            el.removeClassName('errors');
        });
        nb_errors = 0;
        if (!this.email.value.match(/(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$/i)) {
            var div = new Element('div', {'class': 'help_error'}).update('Invalid email address.');
            this.email.parentNode.insert(div);
            $('row_email').addClassName('errors');
            nb_errors += 1;
        } 
                
        if (this.password.value.length <= 0) {
            var div = new Element('div', {'class': 'help_error'}).update('You should set a password.');
            this.password.parentNode.insert(div);
            $('row_password').addClassName('errors');
            nb_errors += 1;
        }
        
        if (nb_errors > 0)
            return false;
        return true;
        
    }
});


document.observe("dom:loaded", function() {
    localizeDates();
});