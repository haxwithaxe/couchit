
var _MSIE56 = base2.detect("MSIE[56]");


function within(v,a,z) { return((v>=a && v<=z)?true:false); }
function zero(v) { v=parseInt(v); return(!isNaN(v)?v:0); }

var maxValue={'H':360,'S':100,'V':100}, HSV={H:360, S:100, V:100};

var Color = base2.Base.extend({
    /*cords: function(W) {

    	var W2=W/2, rad=(hsv.H/360)*(Math.PI*2), hyp=(hsv.S+(100-hsv.V))/100*(W2/2);

    	$S('mCur').left=Math.round(Math.abs(Math.round(Math.sin(rad)*hyp)+W2+3))+'px';
    	$S('mCur').top=Math.round(Math.abs(Math.round(Math.cos(rad)*hyp)-W2-21))+'px';
    },*/

    HEX: function(o) {
        o=Math.round(Math.min(Math.max(0,o),255));

        return("0123456789ABCDEF".charAt((o-o%16)/16)+"0123456789ABCDEF".charAt(o%16));

    },

    RGB_HEX: function(o) { 
        var fu=this.HEX;
        return(fu(o.R)+fu(o.G)+fu(o.B)); 
    },

    HSV_RGB: function(o) {

        var R, G, A, B, C, S=o.S/100, V=o.V/100, H=o.H/360;

        if(S>0) { if(H>=1) H=0;

            H=6*H; F=H-Math.floor(H);
            A=Math.round(255*V*(1-S));
            B=Math.round(255*V*(1-(S*F)));
            C=Math.round(255*V*(1-(S*(1-F))));
            V=Math.round(255*V); 

            switch(Math.floor(H)) {

                case 0: R=V; G=C; B=A; break;
                case 1: R=B; G=V; B=A; break;
                case 2: R=A; G=V; B=C; break;
                case 3: R=A; G=B; B=V; break;
                case 4: R=C; G=A; B=V; break;
                case 5: R=V; G=A; B=B; break;

            }

            return({'R':R?R:0, 'G':G?G:0, 'B':B?B:0, 'A':1});

        }
        else return({'R':(V=Math.round(V*255)), 'G':V, 'B':V, 'A':1});

    },

    HSV_HEX: function(o) { 
        return(this.RGB_HEX(this.HSV_RGB(o))); 
    }
    
    
    
});

var ColorPicker = base2.Base.extend({
    colorSelector: null,
    
    constructor: function(el) {
        this.color = new Color();
        
        this.input = el;
        var div = document.createElement("div");
        div.classList.add("colorPickerDiv");
        this.colorSelector = this.rootLayers = div;
        document.body.appendChild(this.colorSelector);
        if (_MSIE56) {
            this.ieframe = document.createElement("iframe");
            this.ieframe.classList.add("selectbox_ieframe");
            this.ieframe.style["z-index"] = "99999";
            this.ieframe.style.display = "none";
            this.ieframe.appendChild(this.rootLayers);
            document.body.appendChild(this.ieframe);
        }

        this.build();
        this.init();
        this.hide();
    },
    
    build: function() {
        // slider
        var sv= document.createElement('div');
        sv.id = "SV";
        
        var svslide = document.createElement('div')
        svslide.id = "SVslide";
        svslide.style.top = -4 + "px";
        svslide.style.left = -4 + "px";
        sv.appendChild(svslide);

        this.colorSelector.appendChild(sv);
        this.svslide = svslide;
        this.sv = sv;

        var h = document.createElement('div');
        h.id = "H";
        
        var hslide = document.createElement('div');
        hslide.id = "Hslide";
        hslide.style.top = -7 + "px";
        hslide.style.left = -8 + "px";
        h.appendChild(hslide);
        this.hslide = hslide;
        
        var hmodel = document.createElement('div');
        hmodel.id = "Hmodel";
        
        for(var i=165; i>=0; i--) {
            var c = document.createElement('div');
            c.style.background = "#" + this.color.HSV_HEX({H:Math.round((360/165)*i), S:100, V:100});
            c.appendChild(document.createElement('br'));
            hmodel.appendChild(c);
        }
        h.appendChild(hmodel);
        this.colorSelector.appendChild(h);
        
        var self = this;
        self.input.addEventListener("click", function(e) {
            e.preventDefault();
            self.show();
            return false;
        }, false);
    },
    
    mkHSV: function(a,b,c) { 
        return(Math.min(a,Math.max(0,Math.ceil((parseInt(c)/b)*a))));
    },
    
    ckHSV: function(a,b) { 
        if (within(a,0,b))
            return(a); 
        else if(a>b) 
            return(b); 
        else if(a<0) 
            return('-'+oo);
    },

    init: function() {},

    hide: function() {
        this.colorSelector.classList.add("hidden");
        if (this.hideIfClickOutside) {
            document.body.removeEventListener("click", this.hideIfClickOutside, false);
            this.hideIfClickOutside = null;
        }
    },

    setPosition: function() {
        var offset = this.input.getOffsets();
        this.colorSelector.style.top = offset.y + this.input.outerHeight() + "px";
        this.colorSelector.style.left = offset.x + "px";
        if (this.ieframe) {
            this.ieframe.width = this.colorSelector.outerWidth();
            this.ieframe.height = this.colorSelector.outerHeight();
        }
    },

    insideSelector: function(event) {
        var offset = this.colorSelector.getOffsets();
        offset.right = offset.x + this.colorSelector.outerWidth();
        offset.bottom = offset.y + this.colorSelector.outerHeight();
        return event.pageY < offset.bottom &&
        event.pageY > offset.y &&
        event.pageX < offset.right &&
        event.pageX > offset.x;
    },
    
    drag:function(e) {
        pos = { x:0, y:0 };
        if (e.pageX || e.pageY) 	{
        	pos.x = e.pageX;
        	pos.y = e.pageY;
        } else if (e.clientX || e.clientY) 	{
        	pos.x = e.clientX + document.body.scrollLeft
        			+ document.documentElement.scrollLeft;
        	pos.y = e.clientY + document.body.scrollTop
        			+ document.documentElement.scrollTop;
        }
      
        
      if (e.target.id == "SV") {
          var offset = this.sv.getOffsets();
          this.svslide.style.top = (pos.y - offset.y) +  "px";
          this.svslide.style.left = (pos.x - offset.x) + "px";
      }
    },

    show: function() {
        this.colorSelector.classList.remove("hidden");
        this.setPosition();
    
        var self = this;
        self.hideIfClickOutside = function(event) {
            if (event.target != self.input && !self.insideSelector(event)) {
                self.hide();
            };
        };
        document.body.addEventListener("click", self.hideIfClickOutside, false);
        self.sv.addEventListener('mousedown', function(e) {
            self.drag(e);
        });
        
    },
})