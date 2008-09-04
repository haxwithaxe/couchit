/* DHTML Color Picker : v1.0.4 : 2008/04/17 */
/* http://www.colorjack.com/software/dhtml+color+picker.html */

function $(v,o) { return((typeof(o)=='object'?o:document).getElementById(v)); }
function $S(o) { o=$(o); if(o) return(o.style); }
function abPos(o) { var o=(typeof(o)=='object'?o:$(o)), z={X:0,Y:0}; while(o!=null) { z.X+=o.offsetLeft; z.Y+=o.offsetTop; o=o.offsetParent; }; return(z); }
function agent(v) { return(Math.max(navigator.userAgent.toLowerCase().indexOf(v),0)); }
function toggle(v) { $S(v).display=($S(v).display=='none'?'block':'none'); }
function within(v,a,z) { return((v>=a && v<=z)?true:false); }
function XY(e,v) { var z=agent('msie')?[event.clientX+document.body.scrollLeft,event.clientY+document.body.scrollTop]:[e.pageX,e.pageY]; return(z[zero(v)]); }
function zero(v) { v=parseInt(v); return(!isNaN(v)?v:0); }


/* COLOR PICKER */

var maxValue={'H':360,'S':100,'V':100}, HSV={H:360, S:100, V:100};

var slideHSV={H:360, S:100, V:100}, zINDEX=15, stop=1;

function HSVslide(d,o,e) {

	function tXY(e) { tY=XY(e,1)-ab.Y; tX=XY(e)-ab.X; }
	function mkHSV(a,b,c) { return(Math.min(a,Math.max(0,Math.ceil((parseInt(c)/b)*a)))); }
	function ckHSV(a,b) { if(within(a,0,b)) return(a); else if(a>b) return(b); else if(a<0) return('-'+oo); }
	function drag(e) { if(!stop) { if(d!='drag') tXY(e);
	
		if(d=='SVslide') { ds.left=ckHSV(tX-oo,162)+'px'; ds.top=ckHSV(tY-oo,162)+'px';

			slideHSV.S=mkHSV(100,162,ds.left); slideHSV.V=100-mkHSV(100,162,ds.top); HSVupdate();

		}
		else if(d=='Hslide') { var ck=ckHSV(tY-oo,163), r='HSV', z={};
		
			ds.top=(ck-5)+'px'; slideHSV.H=mkHSV(360,163,ck);

			for(var i in r) { i=r.substr(i,1); z[i]=(i=='H')?maxValue[i]-mkHSV(maxValue[i],163,ck):HSV[i]; }

			HSVupdate(z); $S('SV').backgroundColor='#'+color.HSV_HEX({H:HSV.H, S:100, V:100});

		}
		else if(d=='drag') { ds.left=XY(e)+oX-eX+'px'; ds.top=XY(e,1)+oY-eY+'px'; }

	}}

	if(stop) { stop=''; var ds=$S(d!='drag'?d:o);

		if(d=='drag') { var oX=parseInt(ds.left), oY=parseInt(ds.top), eX=XY(e), eY=XY(e,1); $S(o).zIndex=zINDEX++; }

		else { var ab=abPos($(o)), tX, tY, oo=(d=='Hslide')?2:4; ab.X+=10; ab.Y+=22; if(d=='SVslide') slideHSV.H=HSV.H; }

		document.onmousemove=drag; document.onmouseup=function(){ stop=1; document.onmousemove=''; document.onmouseup=''; }; drag(e);

	}
};

function HSVupdate(v) { v=color.HSV_HEX(HSV=v?v:slideHSV);

	$('plugHEX').innerHTML=v;
	$S('plugCUR').background='#'+v;
	$S('plugID').background='#'+v;
	
	return(v);

};

function loadSV() { var z='';

	for(var i=165; i>=0; i--) { z+="<div style=\"BACKGROUND: #"+color.HSV_HEX({H:Math.round((360/165)*i), S:100, V:100})+";\"><br /><\/div>"; }

	$('Hmodel').innerHTML=z;
	
};


/* COLOR LIBRARY */

color={};

color.cords=function(W) {

	var W2=W/2, rad=(hsv.H/360)*(Math.PI*2), hyp=(hsv.S+(100-hsv.V))/100*(W2/2);

	$S('mCur').left=Math.round(Math.abs(Math.round(Math.sin(rad)*hyp)+W2+3))+'px';
	$S('mCur').top=Math.round(Math.abs(Math.round(Math.cos(rad)*hyp)-W2-21))+'px';

};

color.HEX=function(o) { o=Math.round(Math.min(Math.max(0,o),255));

    return("0123456789ABCDEF".charAt((o-o%16)/16)+"0123456789ABCDEF".charAt(o%16));

};

color.RGB_HEX=function(o) { var fu=color.HEX; return(fu(o.R)+fu(o.G)+fu(o.B)); };

color.HSV_RGB=function(o) {
    
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

};

color.HSV_HEX=function(o) { return(color.RGB_HEX(color.HSV_RGB(o))); };

/* LOAD */

loadSV();

HSVupdate({H:0, S:0, V:20});

$S('plugin').left=($('colorspy').offsetLeft+35)+'px';
$S('plugin').top=($('colorspy').offsetTop+35)+'px';			 
$S('plugin').display='block';

