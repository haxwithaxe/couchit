# -*- coding: utf-8 -
# Copyright (c) 2002-2006, Mark Pilgrim, All rights reserved.
#
# from FeedParser <http://code.google.com/p/feedparser> 
# with some adaptation for couchit to remove or not javascript
#
import re
import sys
import sgmllib

_debug = 0

class _BaseHTMLProcessor(sgmllib.SGMLParser):
    elements_no_end_tag = ['area', 'base', 'basefont', 'br', 'col', 'frame', 'hr',
      'img', 'input', 'isindex', 'link', 'meta', 'param']
    
    def __init__(self, encoding):
        self.encoding = encoding
        if _debug: sys.stderr.write('entering BaseHTMLProcessor, encoding=%s\n' % self.encoding)
        sgmllib.SGMLParser.__init__(self)
        
    def reset(self):
        self.pieces = []
        sgmllib.SGMLParser.reset(self)

    def _shorttag_replace(self, match):
        tag = match.group(1)
        if tag in self.elements_no_end_tag:
            return '<' + tag + ' />'
        else:
            return '<' + tag + '></' + tag + '>'
        
    def feed(self, data):
        data = re.sub(r'<([^<\s]+?)\s*/>', self._shorttag_replace, data) 
        data = data.replace('&#39;', "'")
        data = data.replace('&#34;', '"')
        if self.encoding and type(data) == type(u''):
            data = data.encode(self.encoding)
        sgmllib.SGMLParser.feed(self, data)

    def normalize_attrs(self, attrs):
        # utility method to be called by descendants
        attrs = [(k.lower(), v) for k, v in attrs]
        attrs = [(k, k in ('rel', 'type') and v.lower() or v) for k, v in attrs]
        return attrs

    def unknown_starttag(self, tag, attrs):
        # called for each start tag
        # attrs is a list of (attr, value) tuples
        # e.g. for <pre class='screen'>, tag='pre', attrs=[('class', 'screen')]
        if _debug: sys.stderr.write('_BaseHTMLProcessor, unknown_starttag, tag=%s\n' % tag)
        uattrs = []
        # thanks to Kevin Marks for this breathtaking hack to deal with (valid) high-bit attribute values in UTF-8 feeds
        for key, value in attrs:
            if type(value) != type(u''):
                value = unicode(value, self.encoding)
            uattrs.append((unicode(key, self.encoding), value))
        strattrs = u''.join([u' %s="%s"' % (key, value) for key, value in uattrs]).encode(self.encoding)
        if tag in self.elements_no_end_tag:
            self.pieces.append('<%(tag)s%(strattrs)s />' % locals())
        else:
            self.pieces.append('<%(tag)s%(strattrs)s>' % locals())

    def unknown_endtag(self, tag):
        # called for each end tag, e.g. for </pre>, tag will be 'pre'
        # Reconstruct the original end tag.
        if tag not in self.elements_no_end_tag:
            self.pieces.append("</%(tag)s>" % locals())

    def handle_charref(self, ref):
        # called for each character reference, e.g. for '&#160;', ref will be '160'
        # Reconstruct the original character reference.
        self.pieces.append('&#%(ref)s;' % locals())
        
    def handle_entityref(self, ref):
        # called for each entity reference, e.g. for '&copy;', ref will be 'copy'
        # Reconstruct the original entity reference.
        self.pieces.append('&%(ref)s;' % locals())

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        # Store the original text verbatim.
        if _debug: sys.stderr.write('_BaseHTMLProcessor, handle_text, text=%s\n' % text)
        self.pieces.append(text)
        
    def handle_comment(self, text):
        # called for each HTML comment, e.g. <!-- insert Javascript code here -->
        # Reconstruct the original comment.
        self.pieces.append('<!--%(text)s-->' % locals())
        
    def handle_pi(self, text):
        # called for each processing instruction, e.g. <?instruction>
        # Reconstruct original processing instruction.
        self.pieces.append('<?%(text)s>' % locals())

    def handle_decl(self, text):
        # called for the DOCTYPE, if present, e.g.
        # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        #     "http://www.w3.org/TR/html4/loose.dtd">
        # Reconstruct original DOCTYPE
        self.pieces.append('<!%(text)s>' % locals())
        
    _new_declname_match = re.compile(r'[a-zA-Z][-_.a-zA-Z0-9:]*\s*').match
    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        if i == n:
            return None, -1
        m = self._new_declname_match(rawdata, i)
        if m:
            s = m.group()
            name = s.strip()
            if (i + len(s)) == n:
                return None, -1  # end of buffer
            return name.lower(), m.end()
        else:
            self.handle_data(rawdata)
#            self.updatepos(declstartpos, i)
            return None, -1

    def output(self):
        '''Return processed HTML as a single string'''
        return ''.join([str(p) for p in self.pieces])


class _HTMLSanitizer(_BaseHTMLProcessor):
    acceptable_elements = ['a', 'abbr', 'acronym', 'address', 'area', 'audio', 'b', 'big',
      'blockquote', 'br', 'button', 'caption', 'center', 'cite', 'code', 'col',
      'colgroup', 'dd', 'del', 'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset',
      'font', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input',
      'ins', 'kbd', 'label', 'legend', 'li', 'map', 'menu', 'object', 'ol', 'optgroup',
      'option', 'p', 'param', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike',
      'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th',
      'thead', 'tr', 'tt', 'u', 'ul', 'var','video']

    acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
      'action', 'align', 'alt', 'allowfullscreen', 'allowscriptaccess', 'axis', 'border', 'cellpadding', 'cellspacing',
      'char', 'charoff', 'charset', 'checked', 'cite', 'class', 'clear', 'cols',
      'colspan', 'color', 'compact', 'coords', 'datetime', 'dir', 'disabled',
      'enctype', 'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace',
      'id', 'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
      'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
      'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape', 'size',
      'span', 'src', 'start', 'summary', 'tabindex', 'target', 'title', 'type',
      'usemap', 'valign', 'value', 'vspace', 'width', 'style']

    unacceptable_elements_with_end_tag = ['script', 'applet']
    
    def __init__(self, encoding, javascript=False):
        _BaseHTMLProcessor.__init__(self, encoding)
        
        if javascript:
            self.unacceptable_elements_with_end_tag = ['applet']
            self.acceptable_elements.append('script')
	    self.acceptable_attributes += [ 'onblur'
		    , 'onchange'
		    , 'onclick'
		    , 'ondblclick'
		    , 'onfocus'
		    , 'onkeydown'
		    , 'onkeypress'
		    , 'onkeyup'
		    , 'onload'
		    , 'onmousedown'
		    , 'onmousemove'
		    , 'onmouseout'
		    , 'onmouseover'
		    , 'onmouseup'
		    , 'onreset'
		    , 'onselect'
		    , 'onsubmit'
		    , 'onunload']
        else: # reset
            unacceptable_elements_with_end_tag = ['script', 'applet']
            if 'script' in self.acceptable_elements:
                del self.acceptable_elements[self.acceptable_elements.index('script')]

    def reset(self):
        _BaseHTMLProcessor.reset(self)
        self.unacceptablestack = 0
        
    def unknown_starttag(self, tag, attrs):
        if not tag in self.acceptable_elements:
            if tag in self.unacceptable_elements_with_end_tag:
                self.unacceptablestack += 1
            return
        attrs = self.normalize_attrs(attrs)
        attrs = [(key, value) for key, value in attrs if key in self.acceptable_attributes]
        _BaseHTMLProcessor.unknown_starttag(self, tag, attrs)
        
    def unknown_endtag(self, tag):
        if not tag in self.acceptable_elements:
            if tag in self.unacceptable_elements_with_end_tag:
                self.unacceptablestack -= 1
            return
        _BaseHTMLProcessor.unknown_endtag(self, tag)

    def handle_pi(self, text):
        pass

    def handle_decl(self, text):
        pass

    def handle_data(self, text):
        if not self.unacceptablestack:
            _BaseHTMLProcessor.handle_data(self, text)

def sanitize_html(htmlSource, encoding='utf-8', javascript=False):
    p = _HTMLSanitizer(encoding=encoding, javascript=javascript)
    p.feed(htmlSource)
    data = p.output()
    
    data = data.strip().replace('\r\n', '\n')
    return data
