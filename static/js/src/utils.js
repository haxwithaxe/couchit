function extend_object(destination, source) {
  for (var property in source)
    destination[property] = source[property];
  return destination;
};

function remove(){ for(var i=0, o; o=arguments[i]; i++) if(o && o.parentNode) o.parentNode.removeChild(o) }

function previousElement(o) {
    do o = o.previousSibling; while(o && o.nodeType != 1)
    return o
}

function nextElement(o) {
    do o = o.nextSibling; while(o && o.nodeType != 1)
    return o
}
// get form data from a form element
function get_formdata(form) {  
    var form_data = {};
    form.querySelectorAll("*").forEach(function(el) {
        if (!(!el.name || el.disabled || (el.type == "reset") ||
                (el.type == "button") && 
                (el.type == "checkbox" || el.type == "radio" && !el.checked) || 
                (el.type == 'submit') || (el.type == 'image') ||
                (el.tagName.toLowerCase() == "select" && el.selectedIndex == -1))) {
        
            if (el.tagName.toLowerCase() == "select") {
                var index = el.selectedIndex;
                if (index > 0) {
                    var  a = [];
                    for (var i=index; i< el.options.length; i++) {
                        op = el.options[i];
                        var v = $j.browser.msie && !(op.attributes['value'].specified) ? op.text : op.value;
                        a.push(v);
                    }
                    form_data[el.name] = a
                }
            
            } else {
                form_data[el.name] = el.value;
            }
        }
    });
    
    return form_data;
}

// From Prototype's array.js
var $A = function(iterable) {
  if (!iterable) return [];
  if (iterable.toArray) {
    return iterable.toArray();
  } else {
    var results = [];
    for (var i = 0; i < iterable.length; i++)
      results.push(iterable[i]);
    return results;
  }
}

Function.prototype.ebind = function() {
  var __method = this, args = $A(arguments), object = args.shift();
  return function() {
    return __method.apply(object, args.concat($A(arguments)));
  }
}