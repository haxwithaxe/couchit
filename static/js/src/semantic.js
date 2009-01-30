var Feed = new Class.create({
    initialize: function() {
        var self = this;
        $(document.body).select('a[rel=feed]').each(function(el) {
            el.addClassName('feed');
        });
    }
});