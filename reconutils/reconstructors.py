#!/bin/env python
''' Reconstructors using recon tools '''
import os
from os.path import abspath

import numpy as N

from recon.operations import Operation, OperationManager

class FixPEOrder(Operation):
    ''' Fix for messed up MPFLASH fid file kindly provided by Mike T '''
    def run(self, image):
        pe_order = image.petable.tolist()
        pe_reorder = [pe_order.index(n) for n in xrange(image.n_pe)]
        image[:] = N.take(image[:], pe_reorder, axis=-2)

class Reconstructor(object):
    ''' Default reconstruction '''
    # Any operations (name, arg_dict) pairs) to run between read and write
    _op_defs = ()
    def __init__(self,
                 fid,
                 outpath=None,
                 prefix = 'recon', 
                 suffix=None,
                 filedim=3,
                 out_format='nifti-single'):
        self.fid = fid
        if outpath is None:
            outpath = fid.outpath
        if outpath is None:
            outpath = os.path.join(fid.path, fid.lhs)
        self.outpath = abspath(outpath)
        self._opmanager = OperationManager()
        reader_class = self._opmanager.getOperation('ReadImage')
        self._reader = reader_class(filename=abspath(fid.file),
                                    format = 'fid',
                                    vrange = ())
        writer_class = self._opmanager.getOperation('WriteImage')
        outspec = os.path.join(outpath, prefix)
        self._writer = writer_class(
            filename = outspec,
            suffix = suffix,
            filedim =  filedim,
            format = out_format,
            datatype = 'magnitude')

    def _extra_operations(self):
        ''' Operations between simple read and write '''
        ops = []
        for op_def in self._op_defs:
            op_name, op_args = op_def
            ops.append(self._opmanager.getOperation(op_name)(**op_args))
        return ops
    
    def run(self):
        if not os.path.exists(self.outpath):
            os.mkdir(self.outpath)
        image = self._reader.run()
        for operation in self._extra_operations():
            if operation.run(image) == -1:
                raise RuntimeError("critical operation failure")
        self._writer.run(image)
        
class EpiReconstructor(Reconstructor):
    ''' Default EPI reconstructor '''
    _op_defs = (
            ('ReorderSlices', {}),
            ('UnbalPhaseCorrection',{}),
            ('InverseFFT',{}),
            # ('FixTimeSkew', {'data_space': 'im-space'})
            )

    def __init__(self, 
                 fid,
                 outpath=None,
                 prefix = 'epi', 
                 suffix = None,
                 filedim=3,
                 out_format='nifti-single'):
        super(EpiReconstructor, self).__init__(
            fid, outpath, prefix, suffix, filedim, out_format)
        
class GemReconstructor(Reconstructor):
    ''' Default GEM reconstruction '''
    _op_defs = (
            ('ReorderSlices', {}),
            ('InverseFFT',{}))
    def __init__(self, 
                 fid,
                 outpath = None,
                 prefix = 'gem', 
                 suffix = None,
                 filedim=3,
                 out_format='nifti-single'):
        super(GemReconstructor, self).__init__(
            fid, outpath, prefix, suffix, filedim, out_format)

class MpflashReconstructor(Reconstructor):
    ''' Default MPFLASH reconstruction '''
    _op_defs = (
            ('InverseFFT',{}),)
    def __init__(self, 
                 fid,
                 outpath = None,
                 prefix = 'mpflash', 
                 suffix = None,
                 filedim=3,
                 out_format='nifti-single'):
        super(MpflashReconstructor, self).__init__(
            fid, outpath, prefix, suffix, filedim, out_format)

class ModMpflashReconstructor(MpflashReconstructor):
    ''' MPFLASH reconstruction for fiddled FID '''
    def __init__(self, 
                 fid,
                 outpath = None,
                 prefix = 'mpflash_ft', 
                 suffix = None,
                 filedim=3,
                 out_format='nifti-single'):
        super(ModMpflashReconstructor, self).__init__(
            fid, outpath, prefix, suffix, filedim, out_format)

    def _extra_operations(self):
        ''' Operations between simple read and write '''
        ops = [FixPEOrder()]
        return ops + super(MpflashReconstructor, self)._extra_operations()
