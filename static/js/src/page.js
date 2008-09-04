var Page = {};
var Site = {
    url: "",
    name: ""
};

var Create = base2.Base.extend({
    constructor: function() {
        var self = this;
        this.form = document.querySelector("#fnewpage");
        this.doCreate = document.querySelector("a.doCreate");
        this.form.classList.add("hidden");
        this.doCreate.addEventListener("click", function(e) {
            e.preventDefault();
            self.show();
            return false;
        }, false);
        
        document.querySelector("a.cancel").addEventListener("click", function(e) {
            e.preventDefault();
            self.cancel();
            return false;
        }, false);

        document.querySelector("#screate").addEventListener("click", function(e) {
            e.preventDefault();
            self.submit();
            return false;
        }, false);
    },
    
    show: function() {
        this.doCreate.classList.add("hidden");
        this.form.classList.remove("hidden");
    },
    
    cancel: function() {
        this.form.classList.add("hidden");
        this.doCreate.classList.remove("hidden");
    },
    
    submit: function() { 
        var title = document.querySelector("#title");
        var slug = title.value.replace(/ /g, "_");
        document.location.href = Site.url + "/" + slug + "/edit";
    },
});

var Compare = base2.Base.extend({
    nb_selected: 0,
    selected: false,
    
    constructor: function() {
        var self = this;
        
        this.Form = document.querySelector('#fhistory');
        document.querySelectorAll('input.c').forEach(function(el) {
            el.addEventListener("click", function(e) {
                self.check(this);
            }, false);
        });
    },
    check: function(el) {
        row = el.parentNode.parentNode;
        base2.DOM.bind(row);
        row.classList.toggle('rselected')
        if (!el.checked) {
            this.nb_selected -=1;
            el.classList.remove("selected");
        
        } else {
            this.nb_selected +=1;
            el.classList.add("selected");
            
        }
        
        if (this.nb_selected == 2) {
            this.Form.querySelectorAll('input.c').forEach(function(el) {
                if (! el.classList.has('selected'))
                    el.disabled = "disabled";
            });
            this.selected = true;
        } else {
            if (this.selected) {
                this.Form.querySelectorAll('input.c').forEach(function(el) {
                    if (! el.classList.has('selected'))
                        el.disabled = null;
                });
                this.selected = false;
            }
        }
    }
});