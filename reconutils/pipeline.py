#!/bin/env python
''' Builders for reconstruction pipelines from directories '''

import os
import sys
from types import MethodType

class Pipeline(list):
    ''' Pipeline container for reconstruction jobs '''
    def __init__(self, sequence=None):
        if sequence is None:
            sequence = []
        for e in sequence:
            self.append(e)

    def __add__(self, y):
        ''' Add needs to make a new object of own type '''
        for e in y:
            self.append(e)
        return type(self)(res)

    def __mul__(self, n):
        return type(self)(
            super(Pipeline, self).__mul__(n))

    def __getslice__(self, i, j):
        ''' getslice needs to make a new object of own type '''        
        return type(self)(
            super(Pipeline, self).__getslice__(i, j))

    def _checked_item(self, item):
        try:
            f = item.run
        except AttributeError:
            raise ValueError, 'item must have run attribute'
        if not isinstance(f, MethodType):
            raise ValueError, 'item must have run method'
        return item
    
    def append(self, item):
        super(Pipeline, self).append(self._checked_item(item))
        
    def __setitem__(self, index, item):
        super(Pipeline, self).__setitem__(
            index, self._checked_item(item))
        
    def run(self):
        results = []
        for job in self:
            results.append(job.run())
        return results


