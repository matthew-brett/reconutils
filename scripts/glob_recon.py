#!/usr/bin/env python
''' Script to convert directories with glob

e.g.

glob_recon.py "CSR*"

(note quotes)

This converts all directories matching "CSR*"
'''

import os
import sys
import glob

from reconutils import fid

# Restrict reconstruction to ModMpflashes, when both are present
builder_classes = (fid.EpiFIDContainer, 
                   fid.GemFIDContainer,
                   fid.ModMpflashFIDContainer)


if __name__ == '__main__':
    try:
        globber = sys.argv[1]
    except IndexError:
        raise OSError, 'Need glob to find directories'
    for inpath in glob.glob(globber):
        print 'Reconstructing %s' % inpath
        fid.recon_directory(inpath, builder_classes=builder_classes)
