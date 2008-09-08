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
                text = (day_diff = 1 && "Yesterday" ||
                day_diff < 7 && day_diff + " days ago");
                title = date.toLocaleString();
            }
            el.setAttribute('title', title);
            el.textContent = "Posted " + text;
        }
    });

}

var Page = {};
var Site = {
    url: "",
    name: ""
};



var Create = Class.create({
    initialize: function() {
        var self = this;
        
     
        
        this.Form = $("fnewpage");
        this.doCreate = $$("a.doCreate")[0];
       
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
        var slug = title.value.replace(/ /g, "_");
        document.location.href = Site.url + "/" + slug + "/edit";
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


var claim = Class.create({
    email: false,
    password: false,
    
    initialize: function() {
        var email = $('email');
    }
})


document.observe("dom:loaded", function() {
    localizeDates();
});