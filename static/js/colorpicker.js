var YAHOO=function(){return{util:{}}}();YAHOO.util.Color=new function(){this.hsv2rgb=function(C,K,H){var B,D,G;if(K==0){B=H*255;D=H*255;G=H*255}else{var F=C*6;if(F==6){F=0}var E=Math.floor(F);var A=H*(1-K);var J=H*(1-K*(F-E));var I=H*(1-K*(1-(F-E)));if(E==0){var_r=H;var_g=I;var_b=A}else{if(E==1){var_r=J;var_g=H;var_b=A}else{if(E==2){var_r=A;var_g=H;var_b=I}else{if(E==3){var_r=A;var_g=J;var_b=H}else{if(E==4){var_r=I;var_g=A;var_b=H}else{var_r=H;var_g=A;var_b=J}}}}}B=var_r*255;D=var_g*255;G=var_b*255}return[Math.round(B),Math.round(D),Math.round(G)]};this.rgb2hsv=function(A,F,G){var A=(A/255);var F=(F/255);var G=(G/255);var D=Math.min(A,F,G);var H=Math.max(A,F,G);deltaMax=H-D;var I=H;var K,E;var J,B,C;if(deltaMax==0){E=0;K=0}else{K=deltaMax/H;J=(((H-A)/6)+(deltaMax/2))/deltaMax;B=(((H-F)/6)+(deltaMax/2))/deltaMax;C=(((H-G)/6)+(deltaMax/2))/deltaMax;if(A==H){E=C-B}else{if(F==H){E=(1/3)+J-C}else{if(G==H){E=(2/3)+B-J}}}if(E<0){E+=1}if(E>1){E-=1}}return[E,K,I]};this.rgb2hex=function(C,B,A){return this.toHex(C)+this.toHex(B)+this.toHex(A)};this.hexchars="0123456789ABCDEF";this.toHex=function(A){A=A||0;A=parseInt(A,10);if(isNaN(A)){A=0}A=Math.round(Math.min(Math.max(0,A),255));return this.hexchars.charAt((A-A%16)/16)+this.hexchars.charAt(A%16)};this.toDec=function(A){return this.hexchars.indexOf(A.toUpperCase())};this.hex2rgb=function(B){var A=[];A[0]=(this.toDec(B.substr(0,1))*16)+this.toDec(B.substr(1,1));A[1]=(this.toDec(B.substr(2,1))*16)+this.toDec(B.substr(3,1));A[2]=(this.toDec(B.substr(4,1))*16)+this.toDec(B.substr(5,1));return A};this.isValidRGB=function(A){if((!A[0]&&A[0]!=0)||isNaN(A[0])||A[0]<0||A[0]>255){return false}if((!A[1]&&A[1]!=0)||isNaN(A[1])||A[1]<0||A[1]>255){return false}if((!A[2]&&A[2]!=0)||isNaN(A[2])||A[2]<0||A[2]>255){return false}return true}};if(!Control){var Control={}}Control.colorPickers=[];Control.ColorPicker=Class.create();Control.ColorPicker.activeColorPicker;Control.ColorPicker.CONTROL;Control.ColorPicker.prototype={initialize:function(D,B){var A=this;Control.colorPickers.push(A);this.field=$(D);this.fieldName=this.field.name||this.field.id;this.options=Object.extend({IMAGE_BASE:"/static/img/"},B||{});this.swatch=$(this.options.swatch)||this.field;this.rgb={};this.hsv={};this.isOpen=false;if(!Control.ColorPicker.CONTROL){Control.ColorPicker.CONTROL={};if(!$("colorpicker")){var C=Builder.node("div",{id:"colorpicker"});C.innerHTML='<div id="colorpicker-div">'+((/MSIE ((6)|(5\.5))/gi.test(navigator.userAgent)&&/windows/i.test(navigator.userAgent)&&!/opera/i.test(navigator.userAgent))?'<img id="colorpicker-bg" src="'+this.options.IMAGE_BASE+'blank.gif" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src=\''+this.options.IMAGE_BASE+"pickerbg.png', sizingMethod='scale')\" alt=\"\">":'<img id="colorpicker-bg" src="'+this.options.IMAGE_BASE+'pickerbg.png" alt="">')+'<div id="colorpicker-bg-overlay" style="z-index: 1002;"></div><div id="colorpicker-selector"><img src="'+this.options.IMAGE_BASE+'select.gif" width="11" height="11" alt="" /></div></div><div id="colorpicker-hue-container"><img src="'+this.options.IMAGE_BASE+'hue.png" id="colorpicker-hue-bg-img"><div id="colorpicker-hue-slider"><div id="colorpicker-hue-thumb"><img src="'+this.options.IMAGE_BASE+'hline.png"></div></div></div><div id="colorpicker-footer"><span id="colorpicker-value">#<input type="text" onclick="this.select()" id="colorpicker-value-input" name="colorpicker-value" value=""></input></span><button id="colorpicker-okbutton">OK</button></div>';document.body.appendChild(C)}Control.ColorPicker.CONTROL={popUp:$("colorpicker"),pickerArea:$("colorpicker-div"),selector:$("colorpicker-selector"),okButton:$("colorpicker-okbutton"),value:$("colorpicker-value"),input:$("colorpicker-value-input"),picker:new Draggable($("colorpicker-selector"),{snap:function(E,F){return[Math.min(Math.max(E,0),Control.ColorPicker.activeColorPicker.control.pickerArea.offsetWidth),Math.min(Math.max(F,0),Control.ColorPicker.activeColorPicker.control.pickerArea.offsetHeight)]},zindex:1009,change:function(E){var F=E.currentDelta();Control.ColorPicker.activeColorPicker.update(F[0],F[1])}}),hueSlider:new Control.Slider("colorpicker-hue-thumb","colorpicker-hue-slider",{axis:"vertical",onChange:function(E){Control.ColorPicker.activeColorPicker.updateHue(E)}})};Element.hide($("colorpicker"))}this.control=Control.ColorPicker.CONTROL;this.toggleOnClickListener=this.toggle.bindAsEventListener(this);this.updateOnChangeListener=this.updateFromFieldValue.bindAsEventListener(this);this.closeOnClickOkListener=this.close.bindAsEventListener(this);this.updateOnClickPickerListener=this.updateSelector.bindAsEventListener(this);Event.observe(this.swatch,"click",this.toggleOnClickListener);Event.observe(this.field,"change",this.updateOnChangeListener);Event.observe(this.control.input,"change",this.updateOnChangeListener);this.updateSwatch()},toggle:function(A){this[(this.isOpen)?"close":"open"](A);Event.stop(A)},open:function(A){Control.colorPickers.each(function(C){C.close()});Control.ColorPicker.activeColorPicker=this;this.isOpen=true;Element.show(this.control.popUp);if(this.options.getPopUpPosition){var B=this.options.getPopUpPosition.bind(this)(A)}else{var B=Position.cumulativeOffset(this.swatch||this.field);B[0]=(B[0]+(this.swatch||this.field).offsetWidth+10)}this.control.popUp.style.left=(B[0])+"px";this.control.popUp.style.top=(B[1])+"px";this.updateFromFieldValue();Event.observe(this.control.okButton,"click",this.closeOnClickOkListener);Event.observe(this.control.pickerArea,"mousedown",this.updateOnClickPickerListener);if(this.options.onOpen){this.options.onOpen.bind(this)(A)}},close:function(A){if(Control.ColorPicker.activeColorPicker==this){Control.ColorPicker.activeColorPicker=null}this.isOpen=false;Element.hide(this.control.popUp);Event.stopObserving(this.control.okButton,"click",this.closeOnClickOkListener);Event.stopObserving(this.control.pickerArea,"mousedown",this.updateOnClickPickerListener);if(this.options.onClose){this.options.onClose.bind(this)()}},updateHue:function(A){var C=(this.control.pickerArea.offsetHeight-A*100)/this.control.pickerArea.offsetHeight;if(C==1){C=0}var B=YAHOO.util.Color.hsv2rgb(C,1,1);if(!YAHOO.util.Color.isValidRGB(B)){return }this.control.pickerArea.style.backgroundColor="rgb("+B[0]+", "+B[1]+", "+B[2]+")";this.update()},updateFromFieldValue:function(C){if(!this.isOpen){return }var D=(C&&Event.findElement(C,"input"))||this.field;var B=YAHOO.util.Color.hex2rgb(D.value);if(!YAHOO.util.Color.isValidRGB(B)){return }var A=YAHOO.util.Color.rgb2hsv(B[0],B[1],B[2]);this.control.selector.style.left=Math.round(A[1]*this.control.pickerArea.offsetWidth)+"px";this.control.selector.style.top=Math.round((1-A[2])*this.control.pickerArea.offsetWidth)+"px";this.control.hueSlider.setValue((1-A[0]))},updateSelector:function(B){var C=Event.pointerX(B);var A=Event.pointerY(B);var D=Position.cumulativeOffset($("colorpicker-bg"));this.control.selector.style.left=(C-D[0]-6)+"px";this.control.selector.style.top=(A-D[1]-6)+"px";this.update((C-D[0]),(A-D[1]));this.control.picker.initDrag(B)},updateSwatch:function(){var B=YAHOO.util.Color.hex2rgb(this.field.value);if(!YAHOO.util.Color.isValidRGB(B)){return }this.swatch.style.backgroundColor="rgb("+B[0]+", "+B[1]+", "+B[2]+")";var A=YAHOO.util.Color.rgb2hsv(B[0],B[1],B[2]);this.swatch.style.color=(A[2]>0.65)?"#000000":"#FFFFFF"},update:function(A,D){if(!A){A=this.control.picker.currentDelta()[0]}if(!D){D=this.control.picker.currentDelta()[1]}var C=(this.control.pickerArea.offsetHeight-this.control.hueSlider.value*100)/this.control.pickerArea.offsetHeight;if(C==1){C=0}this.hsv={hue:1-this.control.hueSlider.value,saturation:A/this.control.pickerArea.offsetWidth,brightness:(this.control.pickerArea.offsetHeight-D)/this.control.pickerArea.offsetHeight};var B=YAHOO.util.Color.hsv2rgb(this.hsv.hue,this.hsv.saturation,this.hsv.brightness);this.rgb={red:B[0],green:B[1],blue:B[2]};this.field.value=YAHOO.util.Color.rgb2hex(B[0],B[1],B[2]);this.control.input.value=this.field.value;this.updateSwatch();if(this.options.onUpdate){this.options.onUpdate.bind(this)(this.field.value)}}};