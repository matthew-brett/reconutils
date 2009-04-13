#!/bin/env python
''' Script to convert directories

e.g.

path_recon.py dir1 dir2

converts fid files in dir1 and dir2
'''

import os
import sys

from reconutils import fid

if __name__ == '__main__':
    inpaths = sys.argv[1:]
    for inpath in inpaths:
        inpath = os.path.abspath(inpath)
        dbuilder = fid.DirectoryBuilder(inpath)
        pipe = dbuilder.get_pipeline()
        pipe.run()
