/*
 Benoitc.js -- benoitc.org library.
 Copyright 2008 by Benoît Chesneau <benoitc@e-engura.com>

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

/*
  Contains portions of base2 - copyright 2007-2008, Dean Edwards
  http://code.google.com/p/base2/
  http://www.opensource.org/licenses/mit-license.php
  
  Contributors:
    Doeke Zanstra
*/
base2.DOM.bind(document);base2.JavaScript.bind(window);Object.extend=function(destination,source){for(var property in source)
destination[property]=source[property];return destination;};if(!document.createElementNS){document.createElement('article');document.createElement('aside');document.createElement('footer');document.createElement('header');document.createElement('nav');document.createElement('time');}
var userAgent=navigator.userAgent.toLowerCase();var Ajax=base2.Base.extend({lastModified:{},browser:{version:(userAgent.match(/.+(?:rv|it|ra|ie)[\/: ]([\d.]+)/)||[])[1],safari:/webkit/.test(userAgent),opera:/opera/.test(userAgent),msie:/msie/.test(userAgent)&&!/opera/.test(userAgent),mozilla:/mozilla/.test(userAgent)&&!/(compatible|webkit)/.test(userAgent)},constructor:function(options){this.options={url:location.href,method:'GET',timeout:0,async:true,contentType:'application/x-www-form-urlencoded',processData:true,data:null,username:null,password:null,accepts:{xml:"application/xml, text/xml",html:"text/html",script:"text/javascript, application/javascript",json:"application/json, text/javascript",text:"text/plain",_default:"*/*"}};Object.extend(this.options,options||{});},get:function(url,data,callback,type){if(typeof data=="function"){callback=data;data=null;}
return this.request({method:'GET',url:url,data:data,success:callback,dataType:type})},post:function(url,data,callback,type){if(typeof data=="function"){callback=data;data=null;}
return this.request({method:'POST',url:url,data:data,success:callback,dataType:type})},request:function(options){Object.extend(Ajax.options,options||{});Object.extend(options,Ajax.options);var status,data,method=options.method.toUpperCase()
if(options.data&&options.processData&&typeof options.data!="string")
options.data=Ajax.param(options.data);if(options.cache===false&&method=="GET"){var ts=now();var ret=options.url.replace(/(\?|&)_=.*?(&|$)/,"$1_="+ts+"$2");options.url=ret+((ret==options.url)?(options.url.match(/\?/)?"&":"?")+"_="+ts:"");}
if(options.data&&method=="GET"){options.url+=(options.url.match(/\?/)?"&":"?")+options.data;options.data=null;}
Ajax.active++;var remote=/^(?:\w+:)?\/\/([^\/?#]+)/;var requestDone=false;var xhr=window.ActiveXObject?new ActiveXObject("Microsoft.XMLHTTP"):new XMLHttpRequest();if(options.username)
xhr.open(method,options.url,options.async,options.username,options.password);else
xhr.open(method,options.url,options.async)
try{if(options.data)
xhr.setRequestHeader("Content-Type",options.contentType);if(options.ifModified)
xhr.setRequestHeader("If-Modified-Since",Ajax.lastModified[options.url]||"Thu, 01 Jan 1970 00:00:00 GMT");xhr.setRequestHeader("X-Requested-With","XMLHttpRequest");xhr.setRequestHeader("Accept",options.dataType&&options.accepts[options.dataType]?options.accepts[options.dataType]+", */*":options.accepts._default);}catch(e){}
if(options.beforeSend&&options.beforeSend(xhr,options)===false){Ajax.active--;xhr.abort()
return false;}
var onreadystatechange=function(isTimeout){if(!requestDone&&xhr&&(xhr.readyState==4||isTimeout=="timeout")){requestDone=true;if(ival){clearInterval(ival);ival=null;}
status=isTimeout=="timeout"&&"timeout"||!Ajax.httpSuccess(xhr)&&"error"||options.ifModified&&Ajax.httpNotModified(xhr,options.url)&&"notmodified"||"success";if(status=="success"){try{data=Ajax.httpData(xhr,options.dataType,options.dataFilter);}catch(e){status="parsererror";}}
if(status=="success"){var modRes;try{modRes=xhr.getResponseHeader("Last-Modified");}catch(e){}
if(options.ifModified&&modRes)
Ajax.lastModified[options.url]=modRes;success();}else
Ajax.handleError(options,xhr,status);complete();if(options.async)
xhr=null;}};if(options.async){var ival=setInterval(onreadystatechange,13);if(options.timeout>0)
setTimeout(function(){if(xhr){xhr.abort();if(!requestDone)
onreadystatechange("timeout");}},options.timeout);}
try{xhr.send(options.data);}catch(e){Ajax.handleError(options,xhr,null,e);}
if(!options.async)
onreadystatechange();function success(){if(options.success)
options.success(data,status);}
function complete(){if(options.complete)
options.complete(xhr,status);--Ajax.active;}
return xhr;},handleError:function(options,xhr,status,e){if(options.error)options.error(xhr,status,e);},active:0,httpSuccess:function(xhr){try{return!xhr.status&&location.protocol=="file:"||(xhr.status>=200&&xhr.status<300)||xhr.status==304||xhr.status==1223||Ajax.browser.safari&&xhr.status==undefined;}catch(e){}
return false;},httpNotModified:function(xhr,url){try{var xhrRes=xhr.getResponseHeader("Last-Modified");return xhr.status==304||xhrRes==this.lastModified[url]||Ajax.browser.safari&&xhr.status==undefined;}catch(e){}
return false;},httpData:function(xhr,type,filter){var ct=xhr.getResponseHeader("content-type"),xml=type=="xml"||!type&&ct&&ct.indexOf("xml")>=0,data=xml?xhr.responseXML:xhr.responseText;if(xml&&data.documentElement.tagName=="parsererror")
throw"parsererror";if(filter)
data=filter(data,type);if(type=="json")
data=JSON.parse(data);return data;},param:function(a){var s=[];if(a.constructor==Array)
a.forEach(function(element,index,array){s.push(encodeURIComponent(element.name)+"="+encodeURIComponent(element.value));});else
for(var j in a)
if(a[j]&&a[j].constructor==Array)
a[j].forEach(function(element,index,array){s.push(encodeURIComponent(j)+"="+encodeURIComponent(element));});else
s.push(encodeURIComponent(j)+"="+encodeURIComponent((typeof a[j]=="function"?a[j]():a[j])));return s.join("&").replace(/%20/g,"+");}});window.Ajax=new Ajax();Date.parseRFC3339=function(string){var date=new Date(0);var match=string.match(/(\d{4})-(\d\d)-(\d\d)\s*(?:[\sT]\s*(\d\d):(\d\d)(?::(\d\d))?(\.\d*)?\s*(Z|([-+])(\d\d):(\d\d))?)?/);if(!match)return;if(match[2])match[2]--;if(match[7])match[7]=(match[7]+'000').substring(1,4);var field=[null,'FullYear','Month','Date','Hours','Minutes','Seconds','Milliseconds'];for(var i=1;i<=7;i++)if(match[i])date['setUTC'+field[i]](match[i]);if(match[9])date.setTime(date.getTime()+
(match[9]=='-'?1:-1)*(match[10]*3600000+match[11]*60000));return date.getTime();}
function pretty_time(string){var now=new Date();var date=new Date(Date.parseRFC3339(string));day_diff=Math.floor((now-date)/1000);if(isNaN(day_diff)||day_diff<0||day_diff>=31)
return;}
function localizeDates(){var nodelist=document.getElementsByTagName('time');var lastdate='';var now=new Date();var times=new Array();for(var i=0;i<nodelist.length;i++)times[i]=nodelist[i];for(var i=0;i<times.length;i++){if(times[i].getAttribute('title')=="GMT"){var date=new Date(Date.parseRFC3339(times[i].getAttribute('datetime')));if(!date.getTime())return;diff=((now.getTime()-date.getTime())/1000),day_diff=Math.floor(diff/86400);if(isNaN(day_diff)||day_diff<0||day_diff>=31)
return;var text=date.toLocaleString();var title=date.toLocaleString();if(day_diff==0){text=(diff<60&&"Just Now"||diff<120&&"1 minute ago"||diff<3600&&Math.floor(diff/60)+" minutes ago"||diff<7200&&"1 hour ago"||diff<86400&&Math.floor(diff/3600)+" hours ago");title=date.toLocaleTimeString();}else{text=(day_diff=1&&"Yesterday"||day_diff<7&&day_diff+" days ago");title=date.toLocaleString();}
times[i].setAttribute('title',title);times[i].textContent="Posted "+text;var parent=times[i];while(parent&&parent.nodeName!='div')parent=parent.parentNode;if(parent&&parent.getAttribute('class')=='comment'){sibling=parent.previousSibling;while(sibling&&sibling.nodeType!=1){sibling=sibling.previousSibling;}
var header=date.toLocaleDateString();var datetime=times[i].getAttribute('datetime').substring(0,10);if(sibling&&sibling.nodeName.toLowerCase()=='h2'){if(lastdate==header){sibling.parentNode.removeChild(sibling);}else{sibling.childNodes[0].textContent=header;sibling.childNodes[0].setAttribute('datetime',datetime);}}else if(lastdate!=header){var h2=document.createElementNS(xhtml,'h2');var time=document.createElementNS(xhtml,'time');time.setAttribute('datetime',datetime);time.appendChild(document.createTextNode(header));h2.appendChild(time);parent.parentNode.insertBefore(h2,parent);}
lastdate=header;}}}}
if(document.addEventListener){document.addEventListener("DOMContentLoaded",localizeDates,false);}
if(!document.createElementNS){document.createElement('article');document.createElement('aside');document.createElement('footer');document.createElement('header');document.createElement('nav');document.createElement('time');}
var $A=function(iterable){if(!iterable)return[];if(iterable.toArray){return iterable.toArray();}else{var results=[];for(var i=0;i<iterable.length;i++)
results.push(iterable[i]);return results;}}
Function.prototype.ebind=function(){var __method=this,args=$A(arguments),object=args.shift();return function(){return __method.apply(object,args.concat($A(arguments)));}}
function AdminItem(slug){this.slug=slug;this.init();}
AdminItem.prototype.init=function(){var self=this;var editItem=document.querySelector(".editItem");editItem.addEventListener("click",function(e){e.preventDefault();self.edit();return false;},false);};AdminItem.prototype.publishUpdate=function(e){e.preventDefault();var self=this;url="/"+this.slug+"/edit";form=document.getElementById("feditItem");var els=form.getElementsByTagName('*');var form_data={};for(var i=0;i<els.length;i++){el=els[i];if(!el.name||el.disabled||(el.type=="reset")||(el.type=="button")&&(el.type=="checkbox"||el.type=="radio"&&!el.checked)||(el.type=='submit')||(el.type=='image')||(el.tagName.toLowerCase()=="select"&&el.selectedIndex==-1)){continue;}
if(el.tagName.toLowerCase()=="select"){var index=el.selectedIndex;if(index<0)continue;var a=[];for(var i=index;i<el.options.length;i++){op=el.options[i];var v=$j.browser.msie&&!(op.attributes['value'].specified)?op.text:op.value;a.push(v);}
form_data[el.name]=a}else{form_data[el.name]=el.value;}}
document.querySelectorAll("#feditItem li").forEach(function(el){el.removeClass("errors");});document.querySelectorAll("#feditItem li div.help_error").forEach(function(el){el.textContent="";el.addClass("hidden");})
Ajax.post(url,form_data,function(data){if(data['ok']){item=document.querySelector("#item");item.innerHTML=data['content'];edit=document.querySelector("#item-edit");edit.addClass("hidden");edit.innerHTML="";item.removeClass("hidden");var editItem=document.querySelector(".editItem");editItem.addEventListener('click',function(e){e.preventDefault();this.edit();return false;}.ebind(self),false);}else{errors=data['errors']
for(error in errors){var div=document.querySelector("#"+error+"Div");div.addClass("errors");var help=div.querySelector(".help_error");help.innerHTML=errors[error].join(",");help.removeClass("hidden");}}}.ebind(this),"json");return false;}
AdminItem.prototype.cancelEdit=function(){iedit=document.querySelector("#item-edit");iedit.addClass("hidden");iedit.innerHTML="";document.querySelector("#item").removeClass("hidden");}
AdminItem.prototype.getForm=function(){url="/"+this.slug+"/edit";var self=this;Ajax.get(url,function(data,status){form=document.querySelector("#item-edit");form.innerHTML=data;fcancel=document.querySelector("#item-edit .fcancel");fcancel.addEventListener("click",function(e){e.preventDefault();self.cancelEdit();this.removeEventListener('click',arguments.callee,false);return false;},false);form.querySelector("input.fpublish").addEventListener("click",self.publishUpdate.ebind(self),false);});};AdminItem.prototype.edit=function(){this.getForm();document.querySelector("#item").addClass("hidden");document.querySelector("#item-edit").removeClass("hidden");return false;}