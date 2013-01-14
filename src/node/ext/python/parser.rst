Python Parser
=============

Setup
-----

Set up a test environment. Create a temporary directory and copy 
``parseme.py`` file into it::

    >>> import os
    >>> modulepath = os.path.join(datadir, 'parseme.py')


Test parsing
------------

Create a ``Module``. ``name`` is the abspath of the destination Python file, if
it already exists, read and parse it::

    >>> from node.ext.python import Module

Disable auto parsing::

    >>> Module._do_parse = False

Factor ``Module``::

    >>> module = Module(modulepath)
    >>> module
    <Module object '.../parseme.py' at ...>

Now simulate the contents of ``Module._parse()`` and check the results. Read
the existing file and write to ``Module._buffer``::

    >>> file = open(module.filepath, 'r')
    >>> module._buffer = file.readlines()
    >>> file.close()
    >>> module.buffer
    ['# -*- coding: utf-8 -*-\n', 
    ...]

Extract the module name::

    >>> module.readlines = list()
    >>> module.modulename
    u'parseme'

Extract file encoding::

    >>> module.parser._extractencoding()
    >>> module.encoding
    u'utf-8'

Set pointer Attributes on module::

    >>> module.bufstart = 0
    >>> module.bufend = len(module._buffer)

Parse the abstract syntax tree::
  
    >>> import ast
    >>> module.astnode = ast.parse(''.join(module.buffer))

Convert ``Module._buffer`` to ``unicode`` and strip new lines::

    >>> module._buffer = [unicode(l.strip('\n')) \
    ...                   for l in module._buffer]

Parse ``ProtectedSection`` objects from ``PythonNode.buffer``::

    >>> sections = module.parser._protectedsections()
    >>> for node in sections:
    ...     module.parser._marklines(*range(node.bufstart, node.bufend))

Hook ast children::

    >>> for astnode in module.astnode.body:
    ...     module.parser._createastchild(astnode)
    >>> module.parser._markastrelated(module)
  
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:194] - -1
      <class 'node.ext.python.nodes.Docstring'>: [5:8] - 0
      <class 'node.ext.python.nodes.Docstring'>: [10:10] - 0
      <class 'node.ext.python.nodes.Import'>: [12:12] - 0
      <class 'node.ext.python.nodes.Import'>: [13:13] - 0
      <class 'node.ext.python.nodes.Import'>: [14:14] - 0
      <class 'node.ext.python.nodes.Import'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [16:16] - 0
      <class 'node.ext.python.nodes.Function'>: [81:82] - 0
      <class 'node.ext.python.nodes.Attribute'>: [86:86] - 0
      <class 'node.ext.python.nodes.Attribute'>: [88:88] - 0
      <class 'node.ext.python.nodes.Attribute'>: [90:92] - 0
      <class 'node.ext.python.nodes.Attribute'>: [94:99] - 0
      <class 'node.ext.python.nodes.Attribute'>: [101:103] - 0
      <class 'node.ext.python.nodes.Attribute'>: [105:105] - 0
      <class 'node.ext.python.nodes.Attribute'>: [107:107] - 0
      <class 'node.ext.python.nodes.Attribute'>: [109:109] - 0
      <class 'node.ext.python.nodes.Function'>: [115:116] - 0
        <class 'node.ext.python.nodes.Decorator'>: [114:114] - 0
      <class 'node.ext.python.nodes.Function'>: [122:125] - 0
      <class 'node.ext.python.nodes.Class'>: [127:144] - 0
        <class 'node.ext.python.nodes.Docstring'>: [128:129] - 1
        <class 'node.ext.python.nodes.Attribute'>: [131:131] - 1
        <class 'node.ext.python.nodes.Attribute'>: [132:132] - 1
        <class 'node.ext.python.nodes.Function'>: [137:140] - 1
          <class 'node.ext.python.nodes.Docstring'>: [138:139] - 2
        <class 'node.ext.python.nodes.Function'>: [143:144] - 1
          <class 'node.ext.python.nodes.Decorator'>: [142:142] - 1
      <class 'node.ext.python.nodes.Class'>: [146:160] - 0
        <class 'node.ext.python.nodes.Docstring'>: [147:148] - 1
        <class 'node.ext.python.nodes.Function'>: [157:160] - 1
          <class 'node.ext.python.nodes.Docstring'>: [158:159] - 2
      <class 'node.ext.python.nodes.Class'>: [162:165] - 0
        <class 'node.ext.python.nodes.Docstring'>: [164:165] - 1
      <class 'node.ext.python.nodes.Function'>: [170:171] - 0
        <class 'node.ext.python.nodes.Decorator'>: [167:167] - 0
        <class 'node.ext.python.nodes.Decorator'>: [168:168] - 0
        <class 'node.ext.python.nodes.Decorator'>: [169:169] - 0
      <class 'node.ext.python.nodes.Function'>: [176:177] - 0
        <class 'node.ext.python.nodes.Decorator'>: [173:175] - 0
      <class 'node.ext.python.nodes.Import'>: [179:180] - 0
      <class 'node.ext.python.nodes.Import'>: [182:185] - 0
      <class 'node.ext.python.nodes.Import'>: [187:187] - 0
      <class 'node.ext.python.nodes.Function'>: [189:194] - 0
        <class 'node.ext.python.nodes.Docstring'>: [190:191] - 1

Parse Code Blocks and hook children::

    >>> children = sections + module.parser._parsecodeblocks()
    >>> module.parser._hookchildren(children)

Check pointers of ``ProtectedSection``. Case filled::

    >>> sec = sections[0]
    >>> sec.buffer[sec.bufstart:sec.bufend]
    [u'##code-section module', 
    u"print 'something'", 
    u'##/code-section module']
    >>> sec.bufstart, sec.bufend, sec.startlineno, sec.endlineno, sec.indent
    (117, 120, 118, 120, 0)

Check pointers of ``ProtectedSection``. Case empty::

    >>> sec = sections[1]
    >>> sec.buffer[sec.bufstart:sec.bufend]
    [u'    ##code-section class', 
    u'    ##/code-section class']
    >>> sec.bufstart, sec.bufend, sec.startlineno, sec.endlineno, sec.indent
    (133, 135, 134, 135, 1)

Check ``Import.parser._definitionends`` method::

    >>> from node.ext.python import Import
    >>> import_ = Import(buffer=module.buffer)
    >>> import_.buffer[11:12]
    [u'import foo']
    >>> import_.parser._definitionends(11)
    True

    >>> import_.buffer[178:185]
    [u'from foo import bar, \\', 
    u'                baz', 
    u'', 
    u'from baz import (', 
    u'    foo,', 
    u'    bar,', 
    u')']
    >>> import_.parser._definitionends(178)
    False
    >>> import_.parser._definitionends(179)
    True
    >>> import_.parser._definitionends(181)
    False
    >>> import_.parser._definitionends(182)
    False
    >>> import_.parser._definitionends(183)
    False
    >>> import_.parser._definitionends(184)
    True

Check ``Decorator.parser._definitionends`` method::

    >>> from node.ext.python import Decorator
    >>> decorator = Decorator(buffer=module.buffer)
    >>> decorator.buffer[166:169]
    [u"@decorator_1('a')", 
    u'@decorator_2(object(1, foo=anothercall()))', 
    u'@decorator_3(0)']
    >>> decorator.parser._definitionends(166)
    True
    >>> decorator.parser._definitionends(167)
    True
    >>> decorator.parser._definitionends(168)
    True

    >>> decorator.buffer[172:175]
    [u'@multilinedecorator(a=object,', 
    u'                    b=object(),', 
    u'                    c=None)']
    >>> decorator.parser._definitionends(172)
    False
    >>> decorator.parser._definitionends(173)
    False
    >>> decorator.parser._definitionends(174)
    True

Check ``Function.parser._definitionends`` method::

    >>> from node.ext.python import Function
    >>> func = Function(buffer=module.buffer)
    >>> func.buffer[114:115]
    [u'def somedecoratedfunction(param):']
    >>> func.parser._definitionends(114)
    True

    >>> func.buffer[121:125]
    [u'def multilinefunctiondef(aa,', 
    u'                         bb,', 
    u"                         cc='hello'):", 
    u'    print a, b, c']

    >>> func.parser._definitionends(121)
    False
    >>> func.parser._definitionends(122)
    False
    >>> func.parser._definitionends(123)
    True

Check ``Class.parser._definitionends`` method::

    >>> from node.ext.python import Class
    >>> class_ = Class(buffer=module.buffer)
    >>> class_.buffer[126:127]
    [u'class SomeClass(object):']
    >>> class_.parser._definitionends(126)
    True

    >>> class_.buffer[145:146]
    [u'class OtherClass(A, B): # some comment']
    >>> class_.parser._definitionends(145)
    True

    >>> class_.buffer[161:163]
    [u'class MultiLineClassDef(A, B,', 
    u'                        C, D):']
    >>> class_.parser._definitionends(161)
    False
    >>> class_.parser._definitionends(162)
    True

Check pointers of ``Import``. Case one-liner::

    >>> from node.ext.python.interfaces import IImport
    >>> imports = [i for i in module.filtereditems(IImport)]
    >>> len(imports)
    8

    >>> imp = imports[0]
    >>> imp.buffer[imp.bufstart:imp.bufend]
    [u'import foo']
    >>> imp.bufstart, imp.bufend, imp.startlineno, imp.endlineno, imp.indent
    (11, 12, 12, 12, 0)

Check pointers of ``Import``. Case multi-liner::

    >>> imp = imports[6]
    >>> imp.buffer[imp.bufstart:imp.bufend]
    [u'from baz import (', 
    u'    foo,', 
    u'    bar,', 
    u')']
    >>> imp.bufstart, imp.bufend, imp.startlineno, imp.endlineno, imp.indent
    (181, 185, 182, 185, 0)

Check pointers of ``Function``. Case function def one-liner::

    >>> func = module.functions(name='somefunction')[0]
    >>> func.buffer[func.bufstart:func.bufend]
    [u'def somefunction(x, y, z):', 
    u'    return x, y, z']
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.defendlineno, func.indent
    (80, 82, 81, 82, 81, 0)

Check pointers of ``Function``. Case function def multi-liner::

    >>> func = module.functions(name=u'multilinefunctiondef')[0]
    >>> func.buffer[func.bufstart:func.bufend]
    [u'def multilinefunctiondef(aa,', 
    u'                         bb,', 
    u"                         cc='hello'):", 
    u'    print a, b, c']
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.defendlineno, func.indent
    (121, 125, 122, 125, 124, 0)

Check pointers of ``Function``. Case function end multi-liner::

    >>> func = module.functions(name=u'functionwithdocstring')[0]
    >>> func.buffer[func.bufstart:func.bufend]
    [u"def functionwithdocstring(d={'foo': 1}, l=[1, 2, 3], t=(1, 2, 3), o=object()):", 
    u'    """docstring', 
    u'    """', 
    u'    return a, \\', 
    u'           b, \\', 
    u'           c']
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.defendlineno, func.indent
    (188, 194, 189, 194, 189, 0)

Check pointers of ``Function``. Case function as child::

    >>> func = module.classes(name=u'SomeClass')[0].functions(name=u'__init__')[0]
    >>> func.buffer[func.bufstart:func.bufend]
    [u'    def __init__(self, param):', 
    u'        """Do something', 
    u'        """', 
    u'        self.param = param']
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.defendlineno, func.indent
    (136, 140, 137, 140, 137, 1) 

Check pointers of ``Function``. Case decorated function::

    >>> func = module.functions(name=u'somedecoratedfunction')[0]
    >>> func.buffer[func.bufstart:func.bufend]
    [u'def somedecoratedfunction(param):', 
    u'    return param']
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.defendlineno, func.indent
    (114, 116, 115, 116, 115, 0)

Check pointers of ``Attribute``::

    >>> attr = module.attributes(name=u'param')[0]
    >>> attr.buffer[attr.bufstart:attr.bufend]
    [u'param = 1']
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, attr.indent
    (85, 86, 86, 86, 0)

    >>> attr = module.attributes(name=u'param_3')[0]
    >>> attr.buffer[attr.bufstart:attr.bufend]
    [u'param_3 = """', 
    u'    %(hello)s %(world)s', 
    u'""" % {', 
    u"    'hello': 'hello',", 
    u"    'world': 'world',", 
    u'}']
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, attr.indent
    (93, 99, 94, 99, 0)

    >>> attr = module.classes('SomeClass')[0].attributes('anotherattr')[0]
    >>> attr.buffer[attr.bufstart:attr.bufend]
    [u'    anotherattr = 1']
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, attr.indent
    (131, 132, 132, 132, 1)

Check pointers of ``Decorator``. Single line decorator::

    >>> func = module.functions(name='somedecoratedfunction')[0]
    >>> deco = func.decorators()[0]
    >>> deco.buffer[deco.bufstart:deco.bufend]
    [u"@myfunctiondecorator(A, b='foo')"]
    >>> deco.bufstart, deco.bufend, deco.startlineno, deco.endlineno, deco.indent
    (113, 114, 114, 114, 0)

Check pointers of ``Decorator``. Multiple decorators, single line decorators::

    >>> func = module.functions(name='multidecoratedfunction')[0]
    >>> len(func.decorators())
    3

    >>> deco = func.decorators(name='decorator_1')[0]
    >>> deco.buffer[deco.bufstart:deco.bufend]
    [u"@decorator_1('a')"]
    >>> deco.bufstart, deco.bufend, deco.startlineno, deco.endlineno, deco.indent
    (166, 167, 167, 167, 0)

    >>> deco = func.decorators(name='decorator_2')[0]
    >>> deco.buffer[deco.bufstart:deco.bufend]
    [u'@decorator_2(object(1, foo=anothercall()))']
    >>> deco.bufstart, deco.bufend, deco.startlineno, deco.endlineno, deco.indent
    (167, 168, 168, 168, 0)

    >>> deco = func.decorators(name='decorator_3')[0]
    >>> deco.buffer[deco.bufstart:deco.bufend]
    [u'@decorator_3(0)']
    >>> deco.bufstart, deco.bufend, deco.startlineno, deco.endlineno, deco.indent
    (168, 169, 169, 169, 0)

Check pointers of ``Decorator``. Multi line decorator::

    >>> func = module.functions(name='multilinedecorated')[0]
    >>> len(func.decorators())
    1

    >>> deco = func.decorators()[0]
    >>> deco.buffer[deco.bufstart:deco.bufend]
    [u'@multilinedecorator(a=object,', 
    u'                    b=object(),', 
    u'                    c=None)']
    >>> deco.bufstart, deco.bufend, deco.startlineno, deco.endlineno, deco.indent
    (172, 175, 173, 175, 0)

Check pointers of ``Class``. Single line class def::

    >>> class_ = module.classes(name='SomeClass')[0]
    >>> class_.buffer[class_.bufstart:class_.bufend][:3]
    [u'class SomeClass(object):', 
    u'    """Some docstring.', 
    u'    """']
    >>> class_.bufstart, class_.bufend, class_.startlineno, class_.endlineno, \
    ...     class_.defendlineno, class_.indent
    (126, 144, 127, 144, 127, 0)

Check pointers of ``Class``. Multi line class def::

    >>> class_ = module.classes(name='MultiLineClassDef')[0]
    >>> class_.buffer[class_.bufstart:class_.bufend][:4]
    [u'class MultiLineClassDef(A, B,', 
    u'                        C, D):', 
    u'    """Multi line class def', 
    u'    """']
    >>> class_.bufstart, class_.bufend, class_.startlineno, class_.endlineno, \
    ...     class_.defendlineno, class_.indent
    (161, 165, 162, 165, 163, 0)

Check pointers of ``Class``. Case comment after class def::

    >>> class_ = module.classes(name='OtherClass')[0]
    >>> class_.buffer[class_.bufstart:class_.bufend][:3]
    [u'class OtherClass(A, B): # some comment', 
    u'    """Some other docstring.', 
    u'    """']
    >>> class_.bufstart, class_.bufend, class_.startlineno, class_.endlineno, \
    ...     class_.defendlineno, class_.indent
    (145, 160, 146, 160, 146, 0)

Check pointers of ``Docstring``. Case multi line::

    >>> from node.ext.python.interfaces import IDocstring
    >>> docstrings = [d for d in module.filtereditems(IDocstring)]
    >>> len(docstrings)
    2

    >>> doc = docstrings[0]
    >>> doc.buffer[doc.bufstart:doc.bufend]
    [u'"""This file is used as test source for python nodes.', 
    u'', 
    u'The code itself does nothing useful and is not executable.', 
    u'"""']
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (4, 8, 5, 8, 0)

Check pointers of ``Docstring``. Case single line::

    >>> doc = docstrings[1]
    >>> doc.buffer[doc.bufstart:doc.bufend]
    [u"'''Another docstring.'''"]
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (9, 10, 10, 10, 0)

Check pointers of ``Docstring``. Case docstring as child::

    >>> docstrings = [d for d in module.classes()[0].filtereditems(IDocstring)]
    >>> len(docstrings)
    1

    >>> doc = docstrings[0]
    >>> doc.buffer[doc.bufstart:doc.bufend]
    [u'    """Some docstring.', 
    u'    """']
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (127, 129, 128, 129, 1)

Check the ``Module.parser._createcodeblocks`` method. Case no split::

    >>> blocks = module.parser._createcodeblocks(72, 77)
    >>> len(blocks)
    1

    >>> block = blocks[0]
    >>> block.buffer[block.bufstart:block.bufend]
    [u'if a is True \\', 
    u'  or b is True \\', 
    u'  or c is True:', 
    u'    print d', 
    u'']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (72, 77, 73, 76, 0)

Check the ``Module.parser._createcodeblocks`` method. Case split::

    >>> module.buffer[81:86]
    [u'    return x, y, z', 
    u'', 
    u'assert(1 == 1)', 
    u'', 
    u'param = 1']

    >>> blocks = module.parser._createcodeblocks(81, 86)
    >>> len(blocks)
    2

    >>> block = blocks[0]
    >>> block.buffer[block.bufstart:block.bufend]
    [u'    return x, y, z', 
    u'']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (81, 83, 82, 82, 1)

    >>> block = blocks[1]
    >>> block.buffer[block.bufstart:block.bufend]
    [u'assert(1 == 1)', 
    u'', 
    u'param = 1']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (83, 86, 84, 86, 0)

Check the ``Module.parser._createcodeblocks`` method. Case block as child::

    >>> blocks = module.parser._createcodeblocks(148, 156)
    >>> len(blocks)
    1

    >>> block = blocks[0]
    >>> block.buffer[block.bufstart:block.bufend]
    [u'    ', 
    u'    if True:', 
    u'        a = 0', 
    u'    else:', 
    u'        a = 1', 
    u'    ', 
    u'    # some doc', 
    u'    ']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (148, 156, 150, 155, 1)

Check the ``Module.parser._createcodeblocks`` method. Case empty block::

    >>> module.buffer[196:198]
    []

    >>> blocks = module.parser._createcodeblocks(196, 198)
    >>> len(blocks)
    0

Check the ``Module.parser._parsecodeblocks`` method::

    >>> blocks = module.parser._parsecodeblocks()
    >>> len(blocks)
    14

    >>> def blockbystartlineno(lineno):
    ...     for block in blocks:
    ...         if block.startlineno == lineno:
    ...             return block

    >>> block = blockbystartlineno(125)
    >>> block.buffer[block.bufstart:block.bufend]
    [u'    print a, b, c', 
    u'']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (124, 126, 125, 125, 1)

    >>> block = blockbystartlineno(140)
    >>> block.buffer[block.bufstart:block.bufend]
    [u'        self.param = param', 
    u'    ']
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (139, 141, 140, 140, 2)
  
Check the ``PythonNode.parser._findnodeposition`` method::

    X[1..15]
      Y[1..4]      
      Z[7..10]

    >>> from node.ext.python.nodes import PythonNode
    >>> from node.ext.python.parser import BaseParser
    >>> class TestNode(PythonNode):
    ...     def __init__(self, name):
    ...         PythonNode.__init__(self, name)
    ...         self.parser = BaseParser(self)
    ...     @property
    ...     def indent(self):
    ...         return self._testindent
    ...     def _get_startlineno(self): return self._teststartlineno
    ...     def _set_startlineno(self, n): self._teststartlineno = n
    ...     startlineno = property(_get_startlineno, _set_startlineno)
    ...     def _get_endlineno(self): return self._testendlineno
    ...     def _set_endlineno(self, n): self._testendlineno = n
    ...     endlineno = property(_get_endlineno, _set_endlineno)
    >>> node = TestNode('x')
    >>> node.startlineno = 1
    >>> node.endlineno = 15
    >>> node._testindent = 0
    >>> node['y'] = TestNode('y')
    >>> node['y'].startlineno = 1
    >>> node['y'].endlineno = 4
    >>> node['y']._testindent = 1
    >>> node['z'] = TestNode('z')
    >>> node['z'].startlineno = 7
    >>> node['z'].endlineno = 10
    >>> node['z']._testindent = 1

Case insert before 'z'::

    >>> node.parser._findnodeposition(5, 6, 1)
    (<TestNode object 'z' at ...>, -1)

Case insert after 'z'::

    >>> node.parser._findnodeposition(11, 15, 1)
    (<TestNode object 'z' at ...>, 1)

Case insert after 'x'::

    >>> node.parser._findnodeposition(11, 15, 0)
    (<TestNode object 'x' at ...>, 1)

Case insert into 'x'::

    X[1..2]      

    >>> node = TestNode('x')
    >>> node.startlineno = 1
    >>> node.endlineno = 2
    >>> node._testindent = 0
    >>> node.parser._findnodeposition(2, 2, 0)
    (<TestNode object 'x' at ...>, 0)

Case insert into 'y'::

    X[1..5]
      y[2..3]      

    >>> node = TestNode('x')
    >>> node.startlineno = 1
    >>> node.endlineno = 5
    >>> node._testindent = 0
    >>> node['y'] = TestNode('y')
    >>> node['y'].startlineno = 2
    >>> node['y'].endlineno = 3
    >>> node['y']._testindent = 1
    >>> node.parser._findnodeposition(3, 3, 2)
    (<TestNode object 'y' at ...>, 0)

Now the protected sections and blocks are added::

    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:194] - -1
      <class 'node.ext.python.nodes.Block'>: [2:3] - 0
      <class 'node.ext.python.nodes.Docstring'>: [5:8] - 0
      <class 'node.ext.python.nodes.Docstring'>: [10:10] - 0
      <class 'node.ext.python.nodes.Import'>: [12:12] - 0
      <class 'node.ext.python.nodes.Import'>: [13:13] - 0
      <class 'node.ext.python.nodes.Import'>: [14:14] - 0
      <class 'node.ext.python.nodes.Import'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [16:16] - 0
      <class 'node.ext.python.nodes.Block'>: [18:79] - 0
      <class 'node.ext.python.nodes.Function'>: [81:82] - 0
        <class 'node.ext.python.nodes.Block'>: [82:82] - 1
      <class 'node.ext.python.nodes.Block'>: [84:84] - 0
      <class 'node.ext.python.nodes.Attribute'>: [86:86] - 0
      <class 'node.ext.python.nodes.Attribute'>: [88:88] - 0
      <class 'node.ext.python.nodes.Attribute'>: [90:92] - 0
      <class 'node.ext.python.nodes.Attribute'>: [94:99] - 0
      <class 'node.ext.python.nodes.Attribute'>: [101:103] - 0
      <class 'node.ext.python.nodes.Attribute'>: [105:105] - 0
      <class 'node.ext.python.nodes.Attribute'>: [107:107] - 0
      <class 'node.ext.python.nodes.Attribute'>: [109:109] - 0
      <class 'node.ext.python.nodes.Block'>: [111:112] - 0
      <class 'node.ext.python.nodes.Function'>: [115:116] - 0
        <class 'node.ext.python.nodes.Decorator'>: [114:114] - 0
        <class 'node.ext.python.nodes.Block'>: [116:116] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [118:120] - 0
      <class 'node.ext.python.nodes.Function'>: [122:125] - 0
        <class 'node.ext.python.nodes.Block'>: [125:125] - 1
      <class 'node.ext.python.nodes.Class'>: [127:144] - 0
        <class 'node.ext.python.nodes.Docstring'>: [128:129] - 1
        <class 'node.ext.python.nodes.Attribute'>: [131:131] - 1
        <class 'node.ext.python.nodes.Attribute'>: [132:132] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [134:135] - 1
        <class 'node.ext.python.nodes.Function'>: [137:140] - 1
          <class 'node.ext.python.nodes.Docstring'>: [138:139] - 2
          <class 'node.ext.python.nodes.Block'>: [140:140] - 2
        <class 'node.ext.python.nodes.Function'>: [143:144] - 1
          <class 'node.ext.python.nodes.Decorator'>: [142:142] - 1
          <class 'node.ext.python.nodes.Block'>: [144:144] - 2
      <class 'node.ext.python.nodes.Class'>: [146:160] - 0
        <class 'node.ext.python.nodes.Docstring'>: [147:148] - 1
        <class 'node.ext.python.nodes.Block'>: [150:155] - 1
        <class 'node.ext.python.nodes.Function'>: [157:160] - 1
          <class 'node.ext.python.nodes.Docstring'>: [158:159] - 2
          <class 'node.ext.python.nodes.Block'>: [160:160] - 2
      <class 'node.ext.python.nodes.Class'>: [162:165] - 0
        <class 'node.ext.python.nodes.Docstring'>: [164:165] - 1
      <class 'node.ext.python.nodes.Function'>: [170:171] - 0
        <class 'node.ext.python.nodes.Decorator'>: [167:167] - 0
        <class 'node.ext.python.nodes.Decorator'>: [168:168] - 0
        <class 'node.ext.python.nodes.Decorator'>: [169:169] - 0
        <class 'node.ext.python.nodes.Block'>: [171:171] - 1
      <class 'node.ext.python.nodes.Function'>: [176:177] - 0
        <class 'node.ext.python.nodes.Decorator'>: [173:175] - 0
        <class 'node.ext.python.nodes.Block'>: [177:177] - 1
      <class 'node.ext.python.nodes.Import'>: [179:180] - 0
      <class 'node.ext.python.nodes.Import'>: [182:185] - 0
      <class 'node.ext.python.nodes.Import'>: [187:187] - 0
      <class 'node.ext.python.nodes.Function'>: [189:194] - 0
        <class 'node.ext.python.nodes.Docstring'>: [190:191] - 1
        <class 'node.ext.python.nodes.Block'>: [192:194] - 1

Check some ``Block`` contents::

    >>> from node.ext.python.interfaces import IBlock
    >>> blocks = [b for b in module.filtereditems(IBlock)]
    >>> block = blocks[0]
    >>> block.nodelevel
    0
    >>> block.lines
    [u'# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com', 
    u'# GNU General Public License Version 2']

    >>> block = blocks[1]
    >>> block.nodelevel
    0
    >>> block.lines[0]
    u'# here we add a comment'
    >>> block.lines[-1]
    u'    i += 1'

    >>> block = blocks[2]
    >>> block.lines[0]
    u'assert(1 == 1)'

Check some ``ProtectedSection`` contents::

    >>> from node.ext.python.interfaces import IProtectedSection
    >>> sec = [s for s in module.filtereditems(IProtectedSection)][0]
    >>> sec.nodelevel
    0
    >>> sec.lines
    [u"print 'something'"]

    >>> sec = [s for s in \
    ...        module.classes()[0].filtereditems(IProtectedSection)][0]
    >>> sec.nodelevel
    1
    >>> sec.lines
    []

Check some ``Docstring`` contents::

    >>> from node.ext.python.interfaces import IDocstring
    >>> docstrings = [d for d in module.filtereditems(IDocstring)]
    >>> doc = docstrings[0]
    >>> doc.nodelevel
    0
    >>> doc.lines
    [u'This file is used as test source for python nodes.', 
    u'', 
    u'The code itself does nothing useful and is not executable.']

    >>> doc = [d for d in module.classes()[0].filtereditems(IDocstring)][0]
    >>> doc.nodelevel
    1
    >>> doc.lines
    [u'Some docstring.']

Check some ``Import`` attributes::

    >>> from node.ext.python.interfaces import IImport
    >>> imports = [i for i in module.filtereditems(IImport)]
    >>> imp = imports[0]
    >>> imp.nodelevel
    0
    >>> imp.fromimport
    >>> imp.names
    [[u'foo', None]]

    >>> imp = imports[1]
    >>> imp.nodelevel
    0
    >>> imp.fromimport
    >>> imp.names
    [[u'bar', None], [u'baz', None]]

    >>> imp = imports[2]
    >>> imp.nodelevel
    0
    >>> imp.fromimport
    u'pkg'
    >>> imp.names
    [[u'Something', None]]

    >>> imp = imports[3]
    >>> imp.nodelevel
    0
    >>> imp.fromimport
    u'pkg'
    >>> imp.names
    [[u'A', None], [u'B', None]]

    >>> imp = imports[4]
    >>> imp.nodelevel
    0
    >>> imp.fromimport
    u'pkg.subpkg'
    >>> imp.names
    [[u'C', u'D'], [u'E', u'F']]

Check some ``Decorator`` contents::

    >>> dec = module.functions(name=u'somedecoratedfunction')[0].decorators()[0]
    >>> dec.args
    ['A']
    >>> dec.kwargs
    odict([('b', "'foo'")])

    >>> dec = module.functions(name='multilinedecorated')[0].decorators()[0]
    >>> dec.args
    []
    >>> dec.kwargs
    odict([('a', 'object'), 
    ('b', {'args': [], 'name': 'object', 'kwargs': odict()}), 
    ('c', 'None')])

    >>> dec = module.functions(\
    ...           name=u'multidecoratedfunction')[0].decorators()[0]
    >>> dec.args
    ["'a'"]
    >>> dec.kwargs
    odict()

    >>> dec = module.functions(\
    ...           name=u'multidecoratedfunction')[0].decorators()[1]
    >>> dec.args
    [{'args': [1], 'name': 'object', 
    'kwargs': odict([('foo', {'args': [], 'name': 'anothercall', 
    'kwargs': odict()})])}]

    >>> dec.kwargs
    odict()

Check some ``Function`` contents::

    >>> from node.ext.python.interfaces import IFunction
    >>> functions = [f for f in module.filtereditems(IFunction)]
    >>> func = functions[0]
    >>> func.functionname
    'somefunction'

    >>> func.args
    ['x', 'y', 'z']

    >>> func.kwargs
    odict()

    >>> func = functions[2]
    >>> func.functionname
    'multilinefunctiondef'

    >>> func.args
    ['aa', 'bb']

    >>> func.kwargs
    odict([('cc', "'hello'")])

    >>> func = module.functions(name=u'functionwithdocstring')[0]
    >>> func.args
    []

    >>> func.kwargs
    odict([('d', {"'foo'": 1}), 
    ('l', [1, 2, 3]), 
    ('t', (1, 2, 3)), 
    ('o', {'args': [], 'name': 'object', 'kwargs': odict()})])

Check some ``Class`` contents::

    >>> from node.ext.python.interfaces import IClass
    >>> classes = [c for c in module.filtereditems(IClass)]
    >>> class_ = classes[0]
    >>> class_.classname
    'SomeClass'

    >>> class_.bases
    ['object']

Check pointers of the code generated by renderer tests::

    >>> path = os.path.join(datadir, 'rendered.py')
    >>> Module._do_parse = True
    >>> module = Module(path)
    >>> module.bufstart, module.bufend, module.startlineno, module.endlineno, \
    ...     module.indent
    (0, 43, 1, 43, 0)

    >>> doc = module.docstrings()[0]
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (1, 5, 2, 5, 0)

    >>> psec = module.protectedsections()[0]
    >>> psec.bufstart, psec.bufend, psec.startlineno, psec.endlineno, \
    ...     psec.indent
    (6, 9, 7, 9, 0)

    >>> block = module.blocks()[0]
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (9, 13, 11, 12, 0)

    >>> attr = module.attributes()[0]
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, \
    ...     attr.indent
    (13, 17, 14, 17, 0)

    >>> imp = module.imports()[0]
    >>> imp.bufstart, imp.bufend, imp.startlineno, imp.endlineno, imp.indent
    (18, 20, 19, 20, 0)

    >>> cla = module.classes()[0]
    >>> cla.bufstart, cla.bufend, cla.startlineno, cla.endlineno, cla.indent
    (21, 38, 22, 38, 0)

    >>> doc = cla.docstrings()[0]
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (22, 24, 23, 24, 1)

    >>> attr = cla.attributes()[0]
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, \
    ...     attr.indent
    (25, 26, 26, 26, 1)

    >>> attr = cla.attributes()[1]
    >>> attr.bufstart, attr.bufend, attr.startlineno, attr.endlineno, \
    ...     attr.indent
    (26, 30, 27, 30, 1)

    >>> func = cla.functions()[0]
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.indent
    (32, 38, 33, 38, 1)

    >>> dec = func.decorators()[0]
    >>> dec.bufstart, dec.bufend, dec.startlineno, dec.endlineno, dec.indent
    (31, 32, 32, 32, 1)

    >>> doc = func.docstrings()[0]
    >>> doc.bufstart, doc.bufend, doc.startlineno, doc.endlineno, doc.indent
    (33, 35, 34, 35, 2)

    >>> block = func.blocks()[0]
    >>> block.bufstart, block.bufend, block.startlineno, block.endlineno, \
    ...     block.indent
    (35, 39, 36, 38, 2)

    >>> cla = module.classes()[1]
    >>> cla.bufstart, cla.bufend, cla.startlineno, cla.endlineno, cla.indent
    (39, 43, 40, 43, 0)

    >>> func = cla.functions()[0]
    >>> func.bufstart, func.bufend, func.startlineno, func.endlineno, \
    ...     func.indent
    (41, 43, 42, 43, 1)

Check Namespace package ``__init__.py`` parsing::

    >>> init = Module('%s/__init_.py' % datadir)
    >>> init.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:2] - -1
      <class 'node.ext.python.nodes.Block'>: [2:2] - 0

Create ``node.ext.directory.Directory`` instance and test the parsing handler::

    >>> from node.ext.directory import Directory
    >>> directory = Directory(datadir)
    >>> module = Module()
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [?:?] - -1

    >>> directory['rendered.py'] = module
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:43] - -1
      <class 'node.ext.python.nodes.Docstring'>: [2:5] - 0
      <class 'node.ext.python.nodes.ProtectedSection'>: [7:9] - 0
      <class 'node.ext.python.nodes.Block'>: [11:12] - 0
      <class 'node.ext.python.nodes.Attribute'>: [14:17] - 0
      <class 'node.ext.python.nodes.Import'>: [19:20] - 0
      <class 'node.ext.python.nodes.Class'>: [22:38] - 0
        <class 'node.ext.python.nodes.Docstring'>: [23:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [26:26] - 1
        <class 'node.ext.python.nodes.Attribute'>: [27:30] - 1
        <class 'node.ext.python.nodes.Function'>: [33:38] - 1
          <class 'node.ext.python.nodes.Docstring'>: [34:35] - 2
          <class 'node.ext.python.nodes.Block'>: [36:38] - 2
          <class 'node.ext.python.nodes.Decorator'>: [32:32] - 1
      <class 'node.ext.python.nodes.Class'>: [40:43] - 0
        <class 'node.ext.python.nodes.Function'>: [42:43] - 1
          <class 'node.ext.python.nodes.Block'>: [43:43] - 2

Check class only containing attributes, no follow ups::

    >>> modulepath = os.path.join(datadir, 'class_wo_functions.py')
    >>> module = Module(modulepath)

    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:7] - -1
      <class 'node.ext.python.nodes.Class'>: [3:7] - 0
        <class 'node.ext.python.nodes.Attribute'>: [5:5] - 1
        <class 'node.ext.python.nodes.Attribute'>: [6:6] - 1
        <class 'node.ext.python.nodes.Attribute'>: [7:7] - 1

    >>> module.classes()[0].attributes()[-1].startlineno
    7

    >>> module.classes()[0].attributes()[-1].bufstart
    6

    >>> module.classes()[0].attributes()[-1].endlineno
    7

    >>> module.classes()[0].attributes()[-1].bufend
    7
