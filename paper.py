# Append to the paper doc from the command line. Useful for testing.
#
# Usage: DROPBOX_ACCESS_TOKEN='' python paper.py Question Answer
#

import sys
from lib.paper import append

title = sys.argv[1]
body = ' '.join(sys.argv[2:])
append(title, body)
