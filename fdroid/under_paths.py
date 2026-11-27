#!/usr/bin/env python3
"""Print the paths in <list> that are under one of <roots> (build.sh dry run).

Usage: under_paths.py <list> <roots>
"""

import os
import sys

roots = [l.strip() for l in open(sys.argv[2]) if l.strip()]
for line in open(sys.argv[1]):
    p = os.path.normpath(line.strip())
    while p.startswith('../'):
        p = p[3:]
    if any(p == r or p.startswith(r + '/') for r in roots):
        print('  ' + p)
