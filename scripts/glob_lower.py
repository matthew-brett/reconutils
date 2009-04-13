#!/usr/bin/env python
''' Convert all directories and contents to lower case

e.g.

glob_lower.py "*.FID"

(note quotes)

This converts all directory names matching *.FID to lower case
as well as file names in that directory
'''

import os
import sys
import glob

def lower_file(pth):
    p, fname = os.path.split(pth)
    if fname == fname.upper():
        os.rename(pth, os.path.join(p, fname.lower()))
    
def lower_path(path):
    for pth in glob.glob(os.path.join(path, '*')):
        lower_file(pth)
    lower_file(path)
            
if __name__ == '__main__':
    try:
        globber = sys.argv[1]
    except IndexError:
        raise OSError, 'Need glob to find directories'
    for inpath in glob.glob(globber):
        lower_path(inpath)
    
