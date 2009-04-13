''' Containers for fid files '''

import os
from os.path import join as opj
import re
from glob import glob as glob

from reconstructors import EpiReconstructor, GemReconstructor, \
     MpflashReconstructor, ModMpflashReconstructor, Reconstructor

from pipeline import Pipeline


class DirectoryBuilder(object):
    ''' Take directory and return reconstruction pipeline '''
    def __init__(self, inroot,
                 fidder=None,
                 outroot=None,
                 builder_classes=None):
        self.inroot = inroot
        if outroot is None:
            outroot = inroot
        self.outroot = outroot
        fids = glob_fids(inroot, fidder)
        if builder_classes is None:
            builder_classes = (EpiFIDContainer, 
                               GemFIDContainer,
                               MpflashFIDContainer,
                               ModMpflashFIDContainer)
        self.builders = [klass(fids, outroot)
                         for klass in builder_classes]

    def get_pipeline(self):
        pipeline = Pipeline()
        for builder in self.builders:
            pipeline += builder.get_pipeline()
        return pipeline


class FID(object):
    ''' Class to contain fid (file) information
    FID interface - attributes only
    file - filename
    path - path from filename
    fname - filename component of file
    outpath - output path
    lhs - part of filename left of .
    rhs - part of filename right of . - usually 'fid'
    root - interesting part of rhs identifying fid type somewhat
    digit - number identifying acquisition in filename if present
    suffix - something after the digit - usually cruft
    type - string identifying type of FID, epi, gem, etc
    '''
    _digit_splitter = re.compile('(.*?)(\d+)(.*)')
    def __init__(self, fidfile, outpath=None):
        self.file = fidfile
        self.outpath = outpath
        path, fname = os.path.split(fidfile)
        self.path = path
        self.fname = fname
        lhs, rhs = os.path.splitext(fname)
        self.lhs = lhs
        self.rhs = rhs[1:]
        self.type = None
        self._parse_lhs()
        self._guess_type()
        
    def _parse_lhs(self):
        ''' Sets root, digit and suffix if available '''
        m = self._digit_splitter.match(self.lhs)
        if m is None:
            self.root = self.lhs
            self.digit = 0
            self.suffix = ''
            return
        self.root, digit, self.suffix = m.groups()
        try:
            digit = int(digit)
        except ValueError:
            digit = 0
        self.digit = digit

    def _guess_type(self):
        ident = self.root.lower()
        if ident.startswith('epi'):
            self.type = 'epi'
        elif ident.startswith('gem') or ident.startswith('coplanar'):
            self.type = 'gem'
        elif ident.startswith('mpflash_ft'):
            self.type = 'mod mpflash'
        elif ident.startswith('mpflash'):
            self.type = 'mpflash'
        
def test_fid_init():
    cwd = os.getcwd()
    fid_path = opj(cwd, 'epi1.fid')
    f = FID(fid_path)
    assert f.file == fid_path
    assert f.lhs == 'epi1'
    assert f.rhs == 'fid'
    assert f.root == 'epi'
    assert f.digit == 1


class FIDContainer(object):
    reconstructor = Reconstructor
    fid_type = 'unknown'
    def __init__(self, fids, outroot=None):
        self.fids = fids
        self.outroot = outroot
        self.filter()
        self.sort()
        self.set_outpaths()

    @staticmethod
    def _cmp(x, y):
        ''' Compare fids for sort '''
        res = cmp(x.root, y.root)
        if res == 0:
            res = cmp(x.digit, y.digit)
        return res

    def sort(self):
        ''' Sort in place '''
        self.fids.sort(self._cmp)

    def filter(self):
        self.fids = [fid for fid in self.fids if self.accepter(fid)]

    def set_outpaths(self):
        ''' Override this method to set outpaths '''
        pass

    def accepter(self, fid):
        return fid.type == self.fid_type

    def get_pipeline(self):
        pipeline = Pipeline()
        for fid in self:
            pipeline.append(self.reconstructor(fid))
        return pipeline

    def __iter__(self):
        return self.fids.__iter__()


class OneFIDContainer(FIDContainer):
    def __init__(self, fids, outroot=None):
        super(OneFIDContainer, self).__init__(fids, outroot)
        if len(self.fids) > 1:
            raise ValueError, 'Found more than one FID:\n%s' % \
                  '\n'.join([fid.file for fid in self])

    def set_outpaths(self):
        for fid in self:
            fid.outpath = self.outroot
        

class GemFIDContainer(OneFIDContainer):
    reconstructor = GemReconstructor
    fid_type = 'gem'


class MpflashFIDContainer(OneFIDContainer):
    reconstructor = MpflashReconstructor
    fid_type = 'mpflash'


class ModMpflashFIDContainer(OneFIDContainer):
    reconstructor = ModMpflashReconstructor
    fid_type = 'mod mpflash'


class EpiFIDContainer(FIDContainer):
    reconstructor = EpiReconstructor
    fid_type = 'epi'
    
    def set_outpaths(self):
        for fid in self:
            sub_dir = '%s%02d' % (fid.root, fid.digit)
            fid.outpath = os.path.join(self.outroot, sub_dir)


def test_fid_container():
    fid_paths = []
    fid_paths.append(opj(
        os.getcwd(), 'epi2.fid'))
    fid_paths.append(opj(
        os.getcwd(), 'epi1.fid'))
    fid_cont = FIDContainer(fid_paths)
    for i, fid in enumerate(fid_cont):
        assert i+1 == fid.digit

def glob_fids(path, fidder=None):
    if fidder is None:
        fidder = FID
    fid_list = glob(opj(path, '*.fid')) + glob(opj(path, '*.FID'))
    fids = [fidder(fidfile)
                for fidfile in fid_list if os.path.isdir(fidfile)]
    return fids

def recon_directory(inpath, fidder=None, builder_classes=None):
    inpath = os.path.abspath(inpath)
    dbuilder = DirectoryBuilder(inpath,
                                fidder = fidder,
                                builder_classes = builder_classes)
    pipe = dbuilder.get_pipeline()
    pipe.run()

if __name__ == '__main__':
    import nose
    nose.main()
