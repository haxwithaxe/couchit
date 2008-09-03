var userAgent = navigator.userAgent.toLowerCase();

// ajax object based on jquery one. Rewrote with base
var Ajax = base2.Base.extend({
    lastModified: {},
    browser: {
       	version: (userAgent.match( /.+(?:rv|it|ra|ie)[\/: ]([\d.]+)/ ) || [])[1],
       	safari: /webkit/.test( userAgent ),
       	opera: /opera/.test( userAgent ),
       	msie: /msie/.test( userAgent ) && !/opera/.test( userAgent ),
       	mozilla: /mozilla/.test( userAgent ) && !/(compatible|webkit)/.test( userAgent )
       },
       
    constructor: function(options) {
        this.options = {
            url: location.href,
            method: 'GET',
            timeout: 0,
            async: true,
            contentType: 'application/x-www-form-urlencoded',
            processData: true,
            data: null,
            username: null,
            password: null,
            accepts: {
                xml: "application/xml, text/xml",
                html: "text/html",
                script: "text/javascript, application/javascript",
                json: "application/json, text/javascript",
                text: "text/plain",
                _default: "*/*"
            }

        };
        extend_object(this.options, options || {});
    },

   
    
    get: function(url, data, callback, type) {
        if (typeof data == "function") {
            callback = data;
            data = null;
        }
        return this.request({
            method: 'GET',
            url: url,
            data: data,
            success: callback,
            dataType: type
        })
    },

    post: function(url, data, callback, type) {
        if (typeof data == "function") {
            callback = data;
            data = null;
        }
        return this.request({
            method: 'POST',
            url: url,
            data: data,
            success: callback,
            dataType: type
        })
    },

    request: function(options) {
        
        extend_object(Ajax.options, options || {});
        extend_object(options, Ajax.options);
        
        var status, data, method = options.method.toUpperCase()
        
        if (options.data && options.processData && typeof options.data != "string")
            options.data = Ajax.param(options.data);
            
        
        if ( options.cache === false && method == "GET" ) {
			var ts = now();
			// try replacing _= if it is there
			var ret = options.url.replace(/(\?|&)_=.*?(&|$)/, "$1_=" + ts + "$2");
			// if nothing was replaced, add timestamp to the end
			options.url = ret + ((ret == options.url) ? (options.url.match(/\?/) ? "&" : "?") + "_=" + ts : "");
		}
        

        // If data is available, append data to url for get requests
        if (options.data && method == "GET") {
            options.url += (options.url.match(/\?/) ? "&": "?") + options.data;

            // IE likes to send both get and post data, prevent this
            options.data = null;
        }
        
        Ajax.active++;
        // Matches an absolute URL, and saves the domain
        var remote = /^(?:\w+:)?\/\/([^\/?#]+)/;
        
        var requestDone = false;

        // Create the request object; Microsoft failed to properly
        // implement the XMLHttpRequest in IE7, so we use the ActiveXObject when it is available
        var xhr = window.ActiveXObject ? new ActiveXObject("Microsoft.XMLHTTP") : new XMLHttpRequest();

        // Open the socket
        // Passing null username, generates a login popup on Opera (#2865)
        if (options.username)
            xhr.open(method, options.url, options.async, options.username, options.password);
        else
            xhr.open(method, options.url, options.async)

        // Need an extra try/catch for cross domain requests in Firefox 3
        try {
            // Set the correct header, if data is being sent
            if (options.data)
                xhr.setRequestHeader("Content-Type", options.contentType);

            // Set the If-Modified-Since header, if ifModified mode.
            if (options.ifModified)
                xhr.setRequestHeader("If-Modified-Since",
                    Ajax.lastModified[options.url] || "Thu, 01 Jan 1970 00:00:00 GMT");

            // Set header so the called script knows that it's an XMLHttpRequest
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

            // Set the Accepts header for the server, depending on the dataType
            xhr.setRequestHeader("Accept", options.dataType && options.accepts[options.dataType] ?
                options.accepts[options.dataType] + ", */*":
                options.accepts._default);
        } catch(e) {}
        
        if ( options.beforeSend && options.beforeSend(xhr, options) === false ) {
            Ajax.active--;
            xhr.abort()
            return false;
        }
        
        var onreadystatechange = function(isTimeout) {
            if ( !requestDone && xhr && (xhr.readyState == 4 || isTimeout == "timeout") ) {
				requestDone = true;
				
		        // clear poll interval
				if (ival) {
					clearInterval(ival);
					ival = null;
				}

				status = isTimeout == "timeout" && "timeout" ||
					!Ajax.httpSuccess( xhr ) && "error" ||
					options.ifModified && Ajax.httpNotModified( xhr, options.url ) && "notmodified" ||
					"success";

				if ( status == "success" ) {
					// Watch for, and catch, XML document parse errors
					try {
						// process the data (runs the xml through httpData regardless of callback)
						data = Ajax.httpData( xhr, options.dataType, options.dataFilter );
					} catch(e) {
						status = "parsererror";
					}
				}

				// Make sure that the request was successful or notmodified
				if ( status == "success" ) {
					// Cache Last-Modified header, if ifModified mode.
					var modRes;
					try {
						modRes = xhr.getResponseHeader("Last-Modified");
					} catch(e) {} // swallow exception thrown by FF if header is not available

					if ( options.ifModified && modRes )
						Ajax.lastModified[options.url] = modRes;
					
					success();

				} else
					Ajax.handleError(options, xhr, status);

				// Fire the complete handlers
				complete();

				// Stop memory leaks
				if ( options.async )
					xhr = null;
			}
		};
		
		if ( options.async ) {
			// don't attach the handler to the request, just poll it instead
			var ival = setInterval(onreadystatechange, 13);

			// Timeout checker
			if ( options.timeout > 0 )
				setTimeout(function(){
					// Check to see if the request is still happening
					if ( xhr ) {
						// Cancel the request
						xhr.abort();

						if( !requestDone )
							onreadystatechange( "timeout" );
					}
				}, options.timeout);
		}

		// Send the data
		try {
			xhr.send(options.data);
		} catch(e) {
			Ajax.handleError(options, xhr, null, e);
		}

		// firefox 1.5 doesn't fire statechange for sync requests
		if ( !options.async )
			onreadystatechange();

		function success(){
			// If a local callback was specified, fire it and pass it the data
			if ( options.success )
				options.success( data, status );

		}

		function complete(){
			// Process result
			if ( options.complete )
				options.complete(xhr, status);

            --Ajax.active;
		}

		// return XMLHttpRequest to allow aborting the request etc.
		return xhr;
		
            
    },
    

    handleError: function( options, xhr, status, e ) {
		// If a local callback was specified, fire it
		if ( options.error ) options.error( xhr, status, e );
	},

	// Counter for holding the number of active queries
	active: 0,

	// Determines if an XMLHttpRequest was successful or not
	httpSuccess: function( xhr ) {
		try {
			// IE error sometimes returns 1223 when it should be 204 so treat it as success, see #1450
			return !xhr.status && location.protocol == "file:" ||
				( xhr.status >= 200 && xhr.status < 300 ) || xhr.status == 304 || xhr.status == 1223 ||
				Ajax.browser.safari && xhr.status == undefined;
		} catch(e){}
		return false;
	},

	// Determines if an XMLHttpRequest returns NotModified
	httpNotModified: function( xhr, url ) {
		try {
			var xhrRes = xhr.getResponseHeader("Last-Modified");

			// Firefox always returns 200. check Last-Modified date
			return xhr.status == 304 || xhrRes == this.lastModified[url] ||
				Ajax.browser.safari && xhr.status == undefined;
		} catch(e){}
		return false;
	},

	httpData: function( xhr, type, filter ) {
		var ct = xhr.getResponseHeader("content-type"),
			xml = type == "xml" || !type && ct && ct.indexOf("xml") >= 0,
			data = xml ? xhr.responseXML : xhr.responseText;

		if ( xml && data.documentElement.tagName == "parsererror" )
			throw "parsererror";
			
		// Allow a pre-filtering function to sanitize the response
		if( filter )
			data = filter( data, type );


		// Get the JavaScript object, if JSON is used.
		if ( type == "json" )
			data = JSON.parse(data);

		return data;
	},
	
    // serialize an array
    param: function(a) {
        var s = [];
        // If an array was passed in, assume that it is an array
        // of form elements
        if (a.constructor == Array)
            a.forEach(function(element, index, array) {
                s.push(encodeURIComponent(element.name) + "=" + encodeURIComponent(element.value));
            });
        else
            // Otherwise, assume that it's an object of key/value pairs
            for (var j in a)
                if (a[j] && a[j].constructor == Array)
                    a[j].forEach(function(element, index, array) {
                        s.push(encodeURIComponent(j) + "=" + encodeURIComponent(element));
                    });
                else
                    s.push(encodeURIComponent(j) + "=" + encodeURIComponent((typeof a[j] == "function" ? a[j]() : a[j])));
        return s.join("&").replace(/%20/g, "+");
    }

});


window.Ajax = new Ajax();