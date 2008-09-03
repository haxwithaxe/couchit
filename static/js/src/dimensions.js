new function(_) {

    var Fx = new base2.Package(this, {
        name:    "Fx",
        version: "1.0",
        imports: "DOM",
        exports: "Style, Dimensions"
    })



    // evaluate the imported namespace
    eval(this.imports); 
    
    var Style = Base.extend({
        getStyle: function(styleProp) {
            var styles = document.defaultView.getComputedStyle(this);
            return styles.getPropertyValue(styleProp);
        },
        
        getSize: function(){
            //if (isBody(this)) return this.getWindow().getSize();
            return {x: this.offsetWidth, y: this.offsetHeight};
          },
    })
    HTMLElement.implement(Style);
    
    /// some functions imported from prototypes
    var Dimensions = Base.extend({
        
        getSize: function(){
           if (_isBody(this)) {
               DOM.bind(window);
               return window.getSize();
           }
           
           return {x: this.offsetWidth, y: this.offsetHeight};
         },
           
        getScroll: function() {
            position = {
                x: this.scrollLeft, 
                y: this.scrollTop
            };
            alert(styleNumber(this, "border-top-width"))
            return position;
        },

        scrollTo: function(x, y) {
            this.scrollLeft = x;
            this.scrollTop = y;
        },

        getScrollSize: function() {
            return {x: this.scrollWidth, y: this.scrollHeight};
        },
        
        getScrolls: function(){
            var element = this, position = {x: 0, y: 0};
            while (element && !_isBody(element)){
              position.x += element.scrollLeft;
              position.y += element.scrollTop;
              element = element.parentNode;
            }
            return position;
          },

        getOffsetParent: function(){
            var element = this;
            if (_isBody(element)) return null;
            if (!detect("trident")) return element.offsetParent;
            while ((element = element.parentNode) && !_isBody(element)){
              if (_styleString(element, 'position') != 'static') return element;
            }
            return null;
          },
          
        '@gecko': {
            getOffsets: function() {
                var element = this, position = {x: 0, y: 0};
                if (_isBody(this)) return position;
                while (element && !_isBody(element)){
                    position.x += element.offsetLeft;
                    position.y += element.offsetTop
                    if (!_borderBox(element)){
                        position.x += _leftBorder(element);
                        position.y += _topBorder(element);
                    }
                    var parent = element.parentNode;
                    if (parent && _styleString(parent, 'overflow') != 'visible'){
                        position.x += _leftBorder(parent);
                        position.y += _topBorder(parent);
                    }
                    element = element.offsetParent;
                }
                if (!_borderBox(this)) {
                    position.x -= _leftBorder(this);
                    position.y -= _topBorder(this);
                }
                
                return position;
            }
        },
        '@!gecko': {
            getOffsets: function() {
                var element = this, position = {x: 0, y: 0};
                if (_isBody(this)) return position;
                while (element && !_isBody(element)){
                    position.x += element.offsetLeft;
                    position.y += element.offsetTop;
                    if (element != this && (detect("trident") || detect("webkit"))){
                        position.x += _leftBorder(element);
                        position.y += _topBorder(element);
                    }
                    if (detect('trident')){
                            while (element && !element.currentStyle.hasLayout) element = element.offsetParent;
                    }
                    element = element.offsetParent;
                }

                return position;
            }
        },

        getPosition: function(relative){
            if (_isBody(this)) return {x: 0, y: 0};
            var offset = this.getOffsets(), scroll = this.getScrollSize();
            var position = {x: offset.x - scroll.x, y: offset.y - scroll.y};
            var relativePosition = relative.getPosition();
            return {x: position.x - relativePosition.x, y: position.y - relativePosition.y};
        },

        getCoordinates: function(element){
            var position = this.getPosition(element), size = this.getSize();
            var obj = {left: position.x, top: position.y, width: size.x, height: size.y};
            obj.right = obj.left + obj.width;
            obj.bottom = obj.top + obj.height;
            return obj;
        },
        
        computePosition: function(obj){
            return {left: obj.x - _styleNumber(this, 'margin-left'), top: obj.y - _styleNumber(this, 'margin-top')};
          },

        position: function(obj){
            var pos = this.computePosition(obj);
            this.style.left = pos.left;
            this.style.top = pos.top;
            return this
        },
        
       innerHeight: function() {
            return this.offsetHeight - _styleNumber(this, 'padding-top') - _styleNumber(this, 'padding-bottom');;
        },
        outerHeight: function() {
            return this.offsetHeight + _styleNumber(this, 'border-top-width') + _styleNumber(this, 'border-bottom-width');
        },
        
        innerWidth: function() {
            return this.offsetWidth - _styleNumber(this, 'padding-left') - _styleNumber(this, 'padding-right');;
        },
        
        outerWidth: function() {
            return this.offsetWidth + _styleNumber(this, 'border-left-width') + _styleNumber(this, 'border-right-width');
        }
    });
    
    HTMLElement.implement(Dimensions);

    function _styleString(element, style) {
        var styles = document.defaultView.getComputedStyle(element);
        return styles.getPropertyValue(style);
    }

    function _styleNumber(element, style){
        return parseInt(_styleString(element, style)) || 0;
    };

    function _borderBox(element){
        return _styleString(element, '-moz-box-sizing') == 'border-box';
    };

    function _topBorder(element){
        return _styleNumber(element, 'border-top-width');
    };

    function _leftBorder(element){
        return _styleNumber(element, 'border-left-width');
    };

    function _isBody(element){
        return (/^(?:body|html)$/i).test(element.tagName);
    };

    // evaluate the exported namespace (this initialises the Package)
    eval(this.exports);
}