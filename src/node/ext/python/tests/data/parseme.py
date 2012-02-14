# -*- coding: utf-8 -*-
# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

"""This file is used as test source for python nodes.

The code itself does nothing useful and is not executable.
"""

'''Another docstring.'''

import foo
import bar, baz
from pkg import Something
from pkg import A, B
from pkg.subpkg import C as D, E as F

# here we add a comment
# this line should be grouped with the one above

# this is a second comment

if 'foo' == 'whatever':
    print 'do something'

if 'bar' == 'whatever':
    for i in range(10):
        if i < 5:
            print 'a'
        elif i > 5:
            print 'b'
    if True:
        pass
    else:
        pass

for i in range(10):
    print i

try:
    a = [1] + 1
except Error, e:
    print e
except TypeError, e1:
    print e1

try:
    a = [1] + 1
finally:
    a = 0

try:
    a = [1] + 1
except Error, e:
    print e
finally:
    print 'done'

if True: pass

if a is None:
    """Docstring in block.
    """

if a is foo:
    # comment in block
    pass

if a is None:
    
    pass

if a is True \
  or b is True \
  or c is True:
    print d

while i < 10:
    i += 1

def somefunction(x, y, z):
    return x, y, z

assert(1 == 1)

param = 1

param_1 = """fubar"""

param_2 = """
   fubar
"""

param_3 = """
    %(hello)s %(world)s
""" % {
    'hello': 'hello',
    'world': 'world',
}

param_4 = {
    'key': 'value',
}

param_5 = {'key': value}

param_6 = object(1, bar='baz')

param_7 = u"somestring"

# add some doc here
# foo

@myfunctiondecorator(A, b='foo')
def somedecoratedfunction(param):
    return param

##code-section module
print 'something'
##/code-section module

def multilinefunctiondef(aa,
                         bb,
                         cc='hello'):
    print a, b, c

class SomeClass(object):
    """Some docstring.
    """
    
    attr = 0
    anotherattr = 1
    
    ##code-section class
    ##/code-section class
    
    def __init__(self, param):
        """Do something
        """
        self.param = param
    
    @param
    def myparam(self):
        return self.param

class OtherClass(A, B): # some comment
    """Some other docstring.
    """
    
    if True:
        a = 0
    else:
        a = 1
    
    # some doc
    
    def myfunction(self, *args, **kwargs):
        """Some function.
        """
        pass

class MultiLineClassDef(A, B,
                        C, D):
    """Multi line class def
    """

@decorator_1('a')
@decorator_2(object(1, foo=anothercall()))
@decorator_3(0)
def multidecoratedfunction():
    pass

@multilinedecorator(a=object,
                    b=object(),
                    c=None)
def multilinedecorated():
    pass

from foo import bar, \
                baz

from baz import (
    foo,
    bar,
)

import fooo

def functionwithdocstring(d={'foo': 1}, l=[1, 2, 3], t=(1, 2, 3), o=object()):
    """docstring
    """
    return a, \
           b, \
           c