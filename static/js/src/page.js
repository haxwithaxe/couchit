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
})