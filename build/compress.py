import os
import sys

sys.path.append("../tools")
from merge_css import MergeCSS


if  __name__ == "__main__":
    merge = MergeCSS('couchit.yml')
    merge.run()