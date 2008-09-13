import os
import sys

sys.path.append("../tools")
from merge_css import MergeCSS
from merge_js import MergeJS

if  __name__ == "__main__":
    merge_css = MergeCSS('couchit.yml')
    merge_css.run()
    
    merge_js = MergeJS('couchit.yml')
    merge_js.run()