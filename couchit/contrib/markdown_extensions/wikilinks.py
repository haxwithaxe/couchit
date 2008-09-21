# -*- coding: utf-8 -*-
'''
WikiLinks Extension for Python-Markdown
======================================

Converts [[WikiLinks]] to relative links.  Requires Python-Markdown 2.0+

Basic usage:

    >>> import markdown
    >>> text = "Some text with a [[WikiLink]]."
    >>> html = markdown.markdown(text, ['wikilinks'])
    >>> html
    u'<p>Some text with a <a href="/WikiLink/" class="wikilink">WikiLink</a>.</p>'

Whitespace behavior:

    >>> markdown.markdown('[[ foo bar_baz ]]', ['wikilinks'])
    u'<p><a class="wikilink" href="/foo_bar_baz/">foo bar_baz</a></p>'
    >>> markdown.markdown('foo [[ ]] bar', ['wikilinks'])
    u'<p>foo  bar</p>'

To define custom settings the simple way:

    >>> markdown.markdown(text, 
    ...     ['wikilinks(base_url=/wiki/,end_url=.html,html_class=foo)']
    ... )
    u'<p>Some text with a <a href="/wiki/WikiLink.html" class="foo">WikiLink</a>.</p>'
    
Custom settings the complex way:

    >>> md = markdown.Markdown(
    ...     extensions = ['wikilinks'], 
    ...     extension_configs = {'wikilinks': [
    ...                                 ('base_url', 'http://example.com/'), 
    ...                                 ('end_url', '.html'),
    ...                                 ('html_class', '') ]},
    ...     safe_mode = True)
    >>> md.convert(text)
    u'<p>Some text with a <a href="http://example.com/WikiLink.html">WikiLink</a>.</p>'

Use MetaData with mdx_meta.py (Note the blank html_class in MetaData):

    >>> text = """wiki_base_url: http://example.com/
    ... wiki_end_url:   .html
    ... wiki_html_class:
    ...
    ... Some text with a WikiLink."""
    >>> md = markdown.Markdown(extensions=['meta', 'wikilinks'])
    >>> md.convert(text)
    u'<p>Some text with a <a href="http://example.com/WikiLink.html">WikiLink</a>.</p>'

MetaData should not carry over to next document:

    >>> md.convert("No [[MetaData]] here.")
    u'<p>No <a href="/MetaData/" class="wikilink">MetaData</a> here.</p>'

From the command line:

    python markdown.py -x wikilinks(base_url=http://example.com/,end_url=.html,html_class=foo) src.txt

By [Waylan Limberg](http://achinghead.com/).

License: [BSD](http://www.opensource.org/licenses/bsd-license.php) 

Dependencies:
* [Python 2.3+](http://python.org)
* [Markdown 2.0+](http://www.freewisdom.org/projects/python-markdown/)
'''

import codecs
import re
from werkzeug.utils import url_quote
from couchit.contrib import markdown
from couchit.utils import CouchitUnicodeDecodeError, force_unicode, smart_str, utf8

re_page = re.compile(r'[^\w^\s^-]', re.U)

class WikiLinkExtension (markdown.Extension) :
    def __init__(self, configs):
        # set extension defaults
        self.config = {
                        'base_url' : ['/', 'String to append to beginning or URL.'],
                        'end_url' : ['/', 'String to append to end of URL.'],
                        'html_class' : ['wikilink', 'CSS hook. Leave blank for none.']
        }
        
        # Override defaults with user settings
        for key, value in configs :
            self.setConfig(key, value)
        
    def extendMarkdown(self, md, md_globals):
        self.md = md
    
        # append to end of inline patterns
        WIKILINK_RE = r'\[\[([^\]]+)\]\]'
        #r'''(?P<escape>\\|\b)(?P<camelcase>([A-Z]+[a-z-_]+){2,})\b'''
        WIKILINK_PATTERN = WikiLinks(WIKILINK_RE, self.config)
        WIKILINK_PATTERN.md = md
        md.inlinePatterns.append(WIKILINK_PATTERN)  
        

class WikiLinks (markdown.BasePattern) :
    def __init__(self, pattern, config):
        markdown.BasePattern.__init__(self, pattern)
        self.config = config
  
    def handleMatch(self, m):
        if m.group(2).strip():
            base_url, end_url, html_class = self._getMeta()
            label = m.group(2).strip()
            label = re_page.sub("", label)
            url = '%s%s%s'% (base_url, label, end_url)
            a = markdown.etree.Element('a')
            a.text = markdown.AtomicString(label)
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        
        return a

    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url'][0]
        end_url = self.config['end_url'][0]
        html_class = self.config['html_class'][0]
        if hasattr(self.md, 'Meta'):
            if self.md.Meta.has_key('wiki_base_url'):
                base_url = self.md.Meta['wiki_base_url'][0]
            if self.md.Meta.has_key('wiki_end_url'):
                end_url = self.md.Meta['wiki_end_url'][0]
            if self.md.Meta.has_key('wiki_html_class'):
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class
    

def makeExtension(configs=None) :
    return WikiLinkExtension(configs=configs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

