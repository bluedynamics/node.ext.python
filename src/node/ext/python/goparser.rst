Python Parser
=============


Define print helper::

    >>> def print_source(source):
    ...     for line in source.split('\n'):
    ...         print line
    ...     print 'EOF'

Required imports::

    >>> from node.ext.python import (
    ...     Module,
    ...     Docstring,
    ...     ProtectedSection,
    ...     Import,
    ...     Attribute,
    ...     Decorator,
    ...     Function,
    ...     Class,
    ...     Block,
    ... )

Test attribute::

    >>> attribute = Attribute(['foo', 'bar'],
    ...                       u'{\n    \'x\': 1,\n    \'y\': 2,\n}')
    >>> print_source(attribute())
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    <BLANKLINE>
    EOF


::
    >>> import os
    >>> modulepath = os.path.join(datadir, 'parseme.py')
    >>> from node.ext.python.goparser import GoParser
    >>> fileinst = open(modulepath,'r')
    >>> source = fileinst.read()
    >>> fileinst.close()
    >>> myparser = GoParser(source, modulepath)
    >>> myparser.parsegen()
    --- 0 (0) Docstring (5-8) (parent: None)
    005:"""This file is used as test source for python nodes.
    006:
    007:The code itself does nothing useful and is not executable.
    008:"""
    <BLANKLINE>
    --- 0 (0) Docstring (10-10) (parent: None)
    010:'''Another docstring.'''
    <BLANKLINE>
    --- 0 (0) Import (12-12) (parent: None)
    012:import foo
    <BLANKLINE>
    --- 0 (0) Import (13-13) (parent: None)
    013:import bar, baz
    <BLANKLINE>
    --- 0 (0) ImportFrom (14-14) (parent: None)
    014:from pkg import Something
    <BLANKLINE>
    --- 0 (0) ImportFrom (15-15) (parent: None)
    015:from pkg import A, B
    <BLANKLINE>
    --- 0 (0) ImportFrom (16-21) (parent: None)
    016:from pkg.subpkg import C as D, E as F
    017:
    018:# here we add a comment
    019:# this line should be grouped with the one above
    020:
    021:# this is a second comment
    <BLANKLINE>
    018:# here we add a comment
    019:# this line should be grouped with the one above
    020:
    021:# this is a second comment
    <BLANKLINE>
    --- 0 (0) ImportFrom (16-17) (parent: None)
    016:from pkg.subpkg import C as D, E as F
    017:
    <BLANKLINE>
    --- 0 (0) If (23-24) (parent: None)
    023:if 'foo' == 'whatever':
    024:    print 'do something'
    <BLANKLINE>
    --- 1 (4) Print (24-24) (parent: If (23-24))
    024:    print 'do something'
    <BLANKLINE>
    --- 2 (10) Str (24-24) (parent: Print (24-24))
    024:    print 'do something'
    <BLANKLINE>
    --- 0 (0) If (26-35) (parent: None)
    026:if 'bar' == 'whatever':
    027:    for i in range(10):
    028:        if i < 5:
    029:            print 'a'
    030:        elif i > 5:
    031:            print 'b'
    032:    if True:
    033:        pass
    034:    else:
    035:        pass
    <BLANKLINE>
    --- 1 (4) For (27-31) (parent: If (26-35))
    027:    for i in range(10):
    028:        if i < 5:
    029:            print 'a'
    030:        elif i > 5:
    031:            print 'b'
    <BLANKLINE>
    --- 2 (8) If (28-31) (parent: For (27-31))
    028:        if i < 5:
    029:            print 'a'
    030:        elif i > 5:
    031:            print 'b'
    <BLANKLINE>
    --- 3 (12) Print (29-29) (parent: If (28-31))
    029:            print 'a'
    <BLANKLINE>
    --- 4 (18) Str (29-29) (parent: Print (29-29))
    029:            print 'a'
    <BLANKLINE>
    --- 3 (13) If (30-31) (parent: If (28-31))
    030:        elif i > 5:
    031:            print 'b'
    <BLANKLINE>
    --- 4 (12) Print (31-31) (parent: If (30-31))
    031:            print 'b'
    <BLANKLINE>
    --- 5 (18) Str (31-31) (parent: Print (31-31))
    031:            print 'b'
    <BLANKLINE>
    --- 1 (4) If (32-35) (parent: If (26-35))
    032:    if True:
    033:        pass
    034:    else:
    035:        pass
    <BLANKLINE>
    --- 2 (8) Pass (33-34) (parent: If (32-35))
    033:        pass
    034:    else:
    <BLANKLINE>
    --- 2 (8) Pass (35-35) (parent: If (32-35))
    035:        pass
    <BLANKLINE>
    --- 0 (0) For (37-38) (parent: None)
    037:for i in range(10):
    038:    print i
    <BLANKLINE>
    --- 1 (4) Print (38-38) (parent: For (37-38))
    038:    print i
    <BLANKLINE>
    --- 2 (10) Name (38-38) (parent: Print (38-38))
    038:    print i
    <BLANKLINE>
    --- 0 (0) TryExcept (40-45) (parent: None)
    040:try:
    041:    a = [1] + 1
    042:except Error, e:
    043:    print e
    044:except TypeError, e1:
    045:    print e1
    <BLANKLINE>
    --- 1 (4) Assign (41-41) (parent: TryExcept (40-45))
    041:    a = [1] + 1
    <BLANKLINE>
    --- 2 (4) Name (41-41) (parent: Assign (41-41))
    041:    a = [1] + 1
    <BLANKLINE>
    --- 1 (0) ExceptHandler (42-43 '<_ast.Name object at 0x101c70bd0>') (parent: TryExcept (40-45))
    042:except Error, e:
    043:    print e
    <BLANKLINE>
    --- 2 (4) Print (43-43) (parent: ExceptHandler (42-43 '<_ast.Name object at 0x101c70bd0>'))
    043:    print e
    <BLANKLINE>
    --- 3 (10) Name (43-43) (parent: Print (43-43))
    043:    print e
    <BLANKLINE>
    --- 1 (0) ExceptHandler (44-45 '<_ast.Name object at 0x101c70d10>') (parent: TryExcept (40-45))
    044:except TypeError, e1:
    045:    print e1
    <BLANKLINE>
    --- 2 (4) Print (45-45) (parent: ExceptHandler (44-45 '<_ast.Name object at 0x101c70d10>'))
    045:    print e1
    <BLANKLINE>
    --- 3 (10) Name (45-45) (parent: Print (45-45))
    045:    print e1
    <BLANKLINE>
    --- 0 (0) TryFinally (47-50) (parent: None)
    047:try:
    048:    a = [1] + 1
    049:finally:
    050:    a = 0
    <BLANKLINE>
    --- 1 (4) Assign (48-49) (parent: TryFinally (47-50))
    048:    a = [1] + 1
    049:finally:
    <BLANKLINE>
    --- 2 (4) Name (48-49) (parent: Assign (48-49))
    048:    a = [1] + 1
    049:finally:
    <BLANKLINE>
    --- 1 (4) Assign (50-50) (parent: TryFinally (47-50))
    050:    a = 0
    <BLANKLINE>
    --- 2 (4) Name (50-50) (parent: Assign (50-50))
    050:    a = 0
    <BLANKLINE>
    --- 0 (0) TryFinally (52-57) (parent: None)
    052:try:
    053:    a = [1] + 1
    054:except Error, e:
    055:    print e
    056:finally:
    057:    print 'done'
    <BLANKLINE>
    --- 1 (0) TryExcept (52-56) (parent: TryFinally (52-57))
    052:try:
    053:    a = [1] + 1
    054:except Error, e:
    055:    print e
    056:finally:
    <BLANKLINE>
    --- 2 (4) Assign (53-53) (parent: TryExcept (52-56))
    053:    a = [1] + 1
    <BLANKLINE>
    --- 3 (4) Name (53-53) (parent: Assign (53-53))
    053:    a = [1] + 1
    <BLANKLINE>
    --- 2 (0) ExceptHandler (54-56 '<_ast.Name object at 0x101c82310>') (parent: TryExcept (52-56))
    054:except Error, e:
    055:    print e
    056:finally:
    <BLANKLINE>
    --- 3 (4) Print (55-56) (parent: ExceptHandler (54-56 '<_ast.Name object at 0x101c82310>'))
    055:    print e
    056:finally:
    <BLANKLINE>
    --- 4 (10) Name (55-56) (parent: Print (55-56))
    055:    print e
    056:finally:
    <BLANKLINE>
    --- 1 (4) Print (57-57) (parent: TryFinally (52-57))
    057:    print 'done'
    <BLANKLINE>
    --- 2 (10) Str (57-57) (parent: Print (57-57))
    057:    print 'done'
    <BLANKLINE>
    --- 0 (0) If (59-59) (parent: None)
    059:if True: pass
    <BLANKLINE>
    --- 1 (9) Pass (59-59) (parent: If (59-59))
    059:if True: pass
    <BLANKLINE>
    --- 0 (0) If (61-63) (parent: None)
    061:if a is None:
    062:    """Docstring in block.
    063:    """
    <BLANKLINE>
    --- 1 (4) Docstring (62-63) (parent: If (61-63))
    062:    """Docstring in block.
    063:    """
    <BLANKLINE>
    --- 0 (0) If (65-67) (parent: None)
    065:if a is foo:
    066:    # comment in block
    067:    pass
    <BLANKLINE>
    --- 1 (4) Pass (67-67) (parent: If (65-67))
    067:    pass
    <BLANKLINE>
    --- 0 (0) If (69-71) (parent: None)
    069:if a is None:
    070:
    071:    pass
    <BLANKLINE>
    --- 1 (4) Pass (71-71) (parent: If (69-71))
    071:    pass
    <BLANKLINE>
    --- 0 (0) If (73-76) (parent: None)
    073:if a is True \\
    074:  or b is True \\
    075:  or c is True:
    076:    print d
    <BLANKLINE>
    --- 1 (4) Print (76-76) (parent: If (73-76))
    076:    print d
    <BLANKLINE>
    --- 2 (10) Name (76-76) (parent: Print (76-76))
    076:    print d
    <BLANKLINE>
    --- 0 (0) While (78-79) (parent: None)
    078:while i < 10:
    079:    i += 1
    <BLANKLINE>
    --- 1 (4) AugAssign (79-79) (parent: While (78-79))
    079:    i += 1
    <BLANKLINE>
    --- 0 (0) FunctionDef (81-82 'somefunction') (parent: None)
    081:def somefunction(x, y, z):
    082:    return x, y, z
    <BLANKLINE>
    --- 1 (4) Return (82-82) (parent: FunctionDef (81-82 'somefunction'))
    082:    return x, y, z
    <BLANKLINE>
    --- 0 (0) Assert (84-84) (parent: None)
    084:assert(1 == 1)
    <BLANKLINE>
    --- 0 (0) Assign (86-86) (parent: None)
    086:param = 1
    <BLANKLINE>
    --- 1 (0) Name (86-86) (parent: Assign (86-86))
    086:param = 1
    <BLANKLINE>
    --- 0 (0) Assign (88-88) (parent: None)
    088:param_1 = """fubar"""
    <BLANKLINE>
    --- 1 (0) Name (88-88) (parent: Assign (88-88))
    088:param_1 = """fubar"""
    <BLANKLINE>
    --- 0 (0) Assign (90-92) (parent: None)
    090:param_2 = """
    091:   fubar
    092:"""
    <BLANKLINE>
    --- 1 (0) Name (90-92) (parent: Assign (90-92))
    090:param_2 = """
    091:   fubar
    092:"""
    <BLANKLINE>
    --- 0 (0) Assign (94-99) (parent: None)
    094:param_3 = """
    095:    %(hello)s %(world)s
    096:""" % {
    097:    'hello': 'hello',
    098:    'world': 'world',
    099:}
    <BLANKLINE>
    --- 1 (0) Name (94-99) (parent: Assign (94-99))
    094:param_3 = """
    095:    %(hello)s %(world)s
    096:""" % {
    097:    'hello': 'hello',
    098:    'world': 'world',
    099:}
    <BLANKLINE>
    --- 0 (0) Assign (101-103) (parent: None)
    101:param_4 = {
    102:    'key': 'value',
    103:}
    <BLANKLINE>
    --- 1 (0) Name (101-103) (parent: Assign (101-103))
    101:param_4 = {
    102:    'key': 'value',
    103:}
    <BLANKLINE>
    --- 0 (0) Assign (105-105) (parent: None)
    105:param_5 = {'key': value}
    <BLANKLINE>
    --- 1 (0) Name (105-105) (parent: Assign (105-105))
    105:param_5 = {'key': value}
    <BLANKLINE>
    --- 0 (0) Assign (107-107) (parent: None)
    107:param_6 = object(1, bar='baz')
    <BLANKLINE>
    --- 1 (0) Name (107-107) (parent: Assign (107-107))
    107:param_6 = object(1, bar='baz')
    <BLANKLINE>
    --- 0 (0) Assign (109-112) (parent: None)
    109:param_7 = u"somestring"
    110:
    111:# add some doc here
    112:# foo
    <BLANKLINE>
    111:# add some doc here
    112:# foo
    <BLANKLINE>
    --- 0 (0) Assign (109-110) (parent: None)
    109:param_7 = u"somestring"
    110:
    <BLANKLINE>
    --- 1 (0) Name (109-112) (parent: Assign (109-110))
    109:param_7 = u"somestring"
    110:
    111:# add some doc here
    112:# foo
    <BLANKLINE>
    111:# add some doc here
    112:# foo
    <BLANKLINE>
    --- 1 (0) Name (109-110) (parent: Assign (109-110))
    109:param_7 = u"somestring"
    110:
    <BLANKLINE>
    --- 0 (0) FunctionDef (114-118 'somedecoratedfunction') (parent: None)
    114:@myfunctiondecorator(A, b='foo')
    115:def somedecoratedfunction(param):
    116:    return param
    117:
    118:##code-section module
    <BLANKLINE>
    117:
    118:##code-section module
    <BLANKLINE>
    --- 0 (0) FunctionDef (114-116 'somedecoratedfunction') (parent: None)
    114:@myfunctiondecorator(A, b='foo')
    115:def somedecoratedfunction(param):
    116:    return param
    <BLANKLINE>
    --- 1 (1) Decorator (114-114) (parent: FunctionDef (115-116 'somedecoratedfunction'))
    114:@myfunctiondecorator(A, b='foo')
    <BLANKLINE>
    --- 2 (21) Name (114-115) (parent: Decorator (114-114))
    114:@myfunctiondecorator(A, b='foo')
    115:def somedecoratedfunction(param):
    <BLANKLINE>
    --- 1 (4) Return (116-118) (parent: FunctionDef (115-116 'somedecoratedfunction'))
    116:    return param
    117:
    118:##code-section module
    <BLANKLINE>
    118:##code-section module
    <BLANKLINE>
    --- 1 (4) Return (116-117) (parent: FunctionDef (115-116 'somedecoratedfunction'))
    116:    return param
    117:
    <BLANKLINE>
    --- 0 (0) Print (119-120) (parent: None)
    119:print 'something'
    120:##/code-section module
    <BLANKLINE>
    --- 1 (6) Str (119-120) (parent: Print (119-120))
    119:print 'something'
    120:##/code-section module
    <BLANKLINE>
    --- 0 (0) FunctionDef (122-125 'multilinefunctiondef') (parent: None)
    122:def multilinefunctiondef(aa,
    123:                         bb,
    124:                         cc='hello'):
    125:    print a, b, c
    <BLANKLINE>
    --- 1 (4) Print (125-125) (parent: FunctionDef (122-125 'multilinefunctiondef'))
    125:    print a, b, c
    <BLANKLINE>
    --- 2 (10) Name (125-125) (parent: Print (125-125))
    125:    print a, b, c
    <BLANKLINE>
    --- 2 (13) Name (125-125) (parent: Print (125-125))
    125:    print a, b, c
    <BLANKLINE>
    --- 2 (16) Name (125-125) (parent: Print (125-125))
    125:    print a, b, c
    <BLANKLINE>
    --- 0 (0) ClassDef (127-144 'SomeClass') (parent: None)
    127:class SomeClass(object):
    128:    """Some docstring.
    129:    """
    130:
    131:    attr = 0
    132:    anotherattr = 1
    133:
    134:    ##code-section class
    135:    ##/code-section class
    136:
    137:    def __init__(self, param):
    138:        """Do something
    139:        """
    140:        self.param = param
    141:
    142:    @param
    143:    def myparam(self):
    144:        return self.param
    <BLANKLINE>
    --- 1 (16) Name (127-128) (parent: ClassDef (127-144 'SomeClass'))
    127:class SomeClass(object):
    128:    """Some docstring.
    <BLANKLINE>
    --- 1 (4) Docstring (128-129) (parent: ClassDef (127-144 'SomeClass'))
    128:    """Some docstring.
    129:    """
    <BLANKLINE>
    --- 1 (4) Assign (131-131) (parent: ClassDef (127-144 'SomeClass'))
    131:    attr = 0
    <BLANKLINE>
    --- 2 (4) Name (131-131) (parent: Assign (131-131))
    131:    attr = 0
    <BLANKLINE>
    --- 1 (4) Assign (132-135) (parent: ClassDef (127-144 'SomeClass'))
    132:    anotherattr = 1
    133:
    134:    ##code-section class
    135:    ##/code-section class
    <BLANKLINE>
    134:    ##code-section class
    135:    ##/code-section class
    <BLANKLINE>
    --- 1 (4) Assign (132-133) (parent: ClassDef (127-144 'SomeClass'))
    132:    anotherattr = 1
    133:
    <BLANKLINE>
    --- 2 (4) Name (132-135) (parent: Assign (132-133))
    132:    anotherattr = 1
    133:
    134:    ##code-section class
    135:    ##/code-section class
    <BLANKLINE>
    134:    ##code-section class
    135:    ##/code-section class
    <BLANKLINE>
    --- 2 (4) Name (132-133) (parent: Assign (132-133))
    132:    anotherattr = 1
    133:
    <BLANKLINE>
    --- 1 (4) FunctionDef (137-140 '__init__') (parent: ClassDef (127-144 'SomeClass'))
    137:    def __init__(self, param):
    138:        """Do something
    139:        """
    140:        self.param = param
    <BLANKLINE>
    --- 2 (8) Docstring (138-139) (parent: FunctionDef (137-140 '__init__'))
    138:        """Do something
    139:        """
    <BLANKLINE>
    --- 2 (8) Assign (140-140) (parent: FunctionDef (137-140 '__init__'))
    140:        self.param = param
    <BLANKLINE>
    --- 3 (8) Attribute (140-140) (parent: Assign (140-140))
    140:        self.param = param
    <BLANKLINE>
    --- 1 (4) FunctionDef (142-144 'myparam') (parent: ClassDef (127-144 'SomeClass'))
    142:    @param
    143:    def myparam(self):
    144:        return self.param
    <BLANKLINE>
    --- 2 (5) Decorator (142-142) (parent: FunctionDef (143-144 'myparam'))
    142:    @param
    <BLANKLINE>
    --- 2 (8) Return (144-144) (parent: FunctionDef (143-144 'myparam'))
    144:        return self.param
    <BLANKLINE>
    --- 0 (0) ClassDef (146-160 'OtherClass') (parent: None)
    146:class OtherClass(A, B): # some comment
    147:    """Some other docstring.
    148:    """
    149:
    150:    if True:
    151:        a = 0
    152:    else:
    153:        a = 1
    154:
    155:    # some doc
    156:
    157:    def myfunction(self, *args, **kwargs):
    158:        """Some function.
    159:        """
    160:        pass
    <BLANKLINE>
    --- 1 (17) Name (146-146) (parent: ClassDef (146-160 'OtherClass'))
    146:class OtherClass(A, B): # some comment
    <BLANKLINE>
    --- 1 (20) Name (146-147) (parent: ClassDef (146-160 'OtherClass'))
    146:class OtherClass(A, B): # some comment
    147:    """Some other docstring.
    <BLANKLINE>
    --- 1 (4) Docstring (147-148) (parent: ClassDef (146-160 'OtherClass'))
    147:    """Some other docstring.
    148:    """
    <BLANKLINE>
    --- 1 (4) If (150-155) (parent: ClassDef (146-160 'OtherClass'))
    150:    if True:
    151:        a = 0
    152:    else:
    153:        a = 1
    154:
    155:    # some doc
    <BLANKLINE>
    154:
    155:    # some doc
    <BLANKLINE>
    --- 1 (4) If (150-153) (parent: ClassDef (146-160 'OtherClass'))
    150:    if True:
    151:        a = 0
    152:    else:
    153:        a = 1
    <BLANKLINE>
    --- 2 (8) Assign (151-152) (parent: If (150-153))
    151:        a = 0
    152:    else:
    <BLANKLINE>
    --- 3 (8) Name (151-152) (parent: Assign (151-152))
    151:        a = 0
    152:    else:
    <BLANKLINE>
    --- 2 (8) Assign (153-155) (parent: If (150-153))
    153:        a = 1
    154:
    155:    # some doc
    <BLANKLINE>
    155:    # some doc
    <BLANKLINE>
    --- 2 (8) Assign (153-154) (parent: If (150-153))
    153:        a = 1
    154:
    <BLANKLINE>
    --- 3 (8) Name (153-155) (parent: Assign (153-154))
    153:        a = 1
    154:
    155:    # some doc
    <BLANKLINE>
    155:    # some doc
    <BLANKLINE>
    --- 3 (8) Name (153-154) (parent: Assign (153-154))
    153:        a = 1
    154:
    <BLANKLINE>
    --- 1 (4) FunctionDef (157-160 'myfunction') (parent: ClassDef (146-160 'OtherClass'))
    157:    def myfunction(self, *args, **kwargs):
    158:        """Some function.
    159:        """
    160:        pass
    <BLANKLINE>
    --- 2 (8) Docstring (158-159) (parent: FunctionDef (157-160 'myfunction'))
    158:        """Some function.
    159:        """
    <BLANKLINE>
    --- 2 (8) Pass (160-160) (parent: FunctionDef (157-160 'myfunction'))
    160:        pass
    <BLANKLINE>
    --- 0 (0) ClassDef (162-165 'MultiLineClassDef') (parent: None)
    162:class MultiLineClassDef(A, B,
    163:                        C, D):
    164:    """Multi line class def
    165:    """
    <BLANKLINE>
    --- 1 (24) Name (162-162) (parent: ClassDef (162-165 'MultiLineClassDef'))
    162:class MultiLineClassDef(A, B,
    <BLANKLINE>
    --- 1 (27) Name (162-162) (parent: ClassDef (162-165 'MultiLineClassDef'))
    162:class MultiLineClassDef(A, B,
    <BLANKLINE>
    --- 1 (24) Name (163-163) (parent: ClassDef (162-165 'MultiLineClassDef'))
    163:                        C, D):
    <BLANKLINE>
    --- 1 (27) Name (163-164) (parent: ClassDef (162-165 'MultiLineClassDef'))
    163:                        C, D):
    164:    """Multi line class def
    <BLANKLINE>
    --- 1 (4) Docstring (164-165) (parent: ClassDef (162-165 'MultiLineClassDef'))
    164:    """Multi line class def
    165:    """
    <BLANKLINE>
    --- 0 (0) FunctionDef (167-171 'multidecoratedfunction') (parent: None)
    167:@decorator_1('a')
    168:@decorator_2(object(1, foo=anothercall()))
    169:@decorator_3(0)
    170:def multidecoratedfunction():
    171:    pass
    <BLANKLINE>
    --- 1 (1) Decorator (167-167) (parent: FunctionDef (167-171 'multidecoratedfunction'))
    167:@decorator_1('a')
    <BLANKLINE>
    --- 2 (13) Str (167-167) (parent: Decorator (167-167))
    167:@decorator_1('a')
    <BLANKLINE>
    --- 1 (1) Decorator (168-168) (parent: FunctionDef (167-171 'multidecoratedfunction'))
    168:@decorator_2(object(1, foo=anothercall()))
    <BLANKLINE>
    --- 2 (13) Call (168-168) (parent: Decorator (168-168))
    168:@decorator_2(object(1, foo=anothercall()))
    <BLANKLINE>
    --- 3 (20) Num (168-168) (parent: Call (168-168))
    168:@decorator_2(object(1, foo=anothercall()))
    <BLANKLINE>
    --- 1 (1) Decorator (169-169) (parent: FunctionDef (170-171 'multidecoratedfunction'))
    169:@decorator_3(0)
    <BLANKLINE>
    --- 2 (13) Num (169-170) (parent: Decorator (169-169))
    169:@decorator_3(0)
    170:def multidecoratedfunction():
    <BLANKLINE>
    --- 1 (4) Pass (171-171) (parent: FunctionDef (170-171 'multidecoratedfunction'))
    171:    pass
    <BLANKLINE>
    --- 0 (0) FunctionDef (173-177 'multilinedecorated') (parent: None)
    173:@multilinedecorator(a=object,
    174:                    b=object(),
    175:                    c=None)
    176:def multilinedecorated():
    177:    pass
    <BLANKLINE>
    --- 1 (1) Decorator (173-175) (parent: FunctionDef (176-177 'multilinedecorated'))
    173:@multilinedecorator(a=object,
    174:                    b=object(),
    175:                    c=None)
    <BLANKLINE>
    --- 1 (4) Pass (177-177) (parent: FunctionDef (176-177 'multilinedecorated'))
    177:    pass
    <BLANKLINE>
    --- 0 (0) ImportFrom (179-180) (parent: None)
    179:from foo import bar, \\
    180:                baz
    <BLANKLINE>
    --- 0 (0) ImportFrom (182-185) (parent: None)
    182:from baz import (
    183:    foo,
    184:    bar,
    185:)
    <BLANKLINE>
    --- 0 (0) Import (187-187) (parent: None)
    187:import fooo
    <BLANKLINE>
    --- 0 (0) FunctionDef (189-194 'functionwithdocstring') (parent: None)
    189:def functionwithdocstring(d={'foo': 1}, l=[1, 2, 3], t=(1, 2, 3), o=object()):
    190:    """docstring
    191:    """
    192:    return a, \\
    193:           b, \\
    194:           c
    <BLANKLINE>
    --- 1 (4) Docstring (190-191) (parent: FunctionDef (189-194 'functionwithdocstring'))
    190:    """docstring
    191:    """
    <BLANKLINE>
    --- 1 (4) Return (192-194) (parent: FunctionDef (189-194 'functionwithdocstring'))
    192:    return a, \\
    193:           b, \\
    194:           c
    <BLANKLINE>
    >>> print repr(myparser.children)
        [Docstring (5-8), Docstring (10-10), Import (12-12), Import (13-13), ImportFrom (14-14), ImportFrom (15-15), ImportFrom (16-17), Comment (18-21), If (23-24), If (26-35), For (37-38), TryExcept (40-45), TryFinally (47-50), TryFinally (52-57), If (59-59), If (61-63), If (65-67), If (69-71), If (73-76), While (78-79), FunctionDef (81-82 'somefunction'), Assert (84-84), Assign (86-86), Assign (88-88), Assign (90-92), Assign (94-99), Assign (101-103), Assign (105-105), Assign (107-107), Assign (109-110), Comment (111-112), FunctionDef (115-116 'somedecoratedfunction'), Comment (117-118), Print (119-120), FunctionDef (122-125 'multilinefunctiondef'), ClassDef (127-144 'SomeClass'), ClassDef (146-160 'OtherClass'), ClassDef (162-165 'MultiLineClassDef'), FunctionDef (170-171 'multidecoratedfunction'), FunctionDef (176-177 'multilinedecorated'), ImportFrom (179-180), ImportFrom (182-185), Import (187-187), FunctionDef (189-194 'functionwithdocstring')]