import os
import nose
from nose.tools import raises, assert_raises

from pipeline import Pipeline

class NullJob(object):
    def run(self):
        pass

class NotAJob(object):
    pass

ajob = NullJob()
notjob = NotAJob()
p10 = Pipeline([ajob] * 10)

def test_pipeline():
    p = Pipeline()
    assert(len(p) == 0)
    p = Pipeline([ajob])
    assert(len(p) == 1)
    assert_raises(ValueError, Pipeline, [notjob])
    p.append(ajob)
    assert(len(p) == 2)

def test_iteration():
    new_p = Pipeline()
    for j in p10:
        new_p.append(j)
    assert(new_p == p10)

def test_run():
    results = p10.run()
    assert(results == [None] * 10)
    
def test_operators():
    p = Pipeline()
    p2 = Pipeline()
    p3 = p + p2
    assert(isinstance(p3, Pipeline))
    p4 = p * 4
    assert(isinstance(p4, Pipeline))
    p5 = p4[:2]
    assert(isinstance(p5, Pipeline))
    assert(len(p5)==2)
    p2 += [NullJob()]
    assert(isinstance(p2, Pipeline))
    
@raises(ValueError)
def test_insert():
    notjob = NotAJob()
    ajob = NullJob()
    p = Pipeline([ajob])
    p[0] = notjob
    p+= [notjob]

if __name__ == '__main__':
    nose.main()
