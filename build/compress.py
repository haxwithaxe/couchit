import os
import sys

from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

sys.path.append("../tools")
from merge_css import MergeCSS
from merge_js import MergeJS

if  __name__ == "__main__":
    # merge css and compact it
    merge_css = MergeCSS('couchit.yml')
    merge_css.run()
    
    # merge js and minify
    merge_js = MergeJS('couchit.yml')
    merge_js.run()
    
    # generate pygments styles
    
    for style in get_all_styles():
        highlight_css =  os.path.join("../static/css", "%s.css" % style)
        print "generate %s" % highlight_css
        css = HtmlFormatter(style=style).get_style_defs('.codehilite')
        f = open(highlight_css, 'w')
        f.write(css)
        f.close()
        
        