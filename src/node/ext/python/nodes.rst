Python Nodes
============

Test id Directory and Module etc build the correct node index::

    >>> from node.ext.directory import Directory
    >>> from node.ext.python import Module

    >>> directory = Directory('/tmp')
    >>> directory['foo.py'] = Module()
    >>> len(directory.index._index)
    2

Define print helper::

    >>> def print_source(source):
    ...     for line in source.split('\n'):
    ...         print line
    ...     print 'EOF'

Check ``CallableArguments``::

    >>> from node.ext.python.nodes import CallableArguments
    >>> ca = CallableArguments()
    >>> ca.extract_arguments()
    ([], odict())

    >>> ca.args = ['a', 'b']
    >>> ca.extract_arguments()
    (['a', 'b'], odict())

    >>> ca.kwargs = {'c': 1, 'd': 2}
    >>> ca.extract_arguments()
    (['a', 'b'], {'c': 1, 'd': 2})

    >>> ca.s_args = 'x, y'
    >>> ca.extract_arguments()
    (['x', 'y'], {'c': 1, 'd': 2})

    >>> ca.s_kwargs = 'z=dict(foo=bar)'
    >>> ca.extract_arguments()
    (['x', 'y'], odict([('z', 'dict(foo=bar)')]))

    >>> ca = CallableArguments()
    >>> ca.args = ['x', 'y']
    >>> ca.kwargs = {'z': 1}

    >>> ca2 = CallableArguments()
    >>> ca2.args = ['x', 'y']
    >>> ca2.kwargs = {'z': 1}

    >>> ca.arguments_equal(ca2)
    True

    >>> ca.args = ['a', 'y']
    >>> ca.arguments_equal(ca2)
    False

    >>> ca.args = ['x', 'y']
    >>> ca.kwargs = {'z': 2}
    >>> ca.arguments_equal(ca2)
    False

We use the module generated by the renderer tests for node tests::

    >>> import os
    >>> from node.ext.python import Module
    >>> path = os.path.join(datadir, 'rendered.py')
    >>> Module._do_parse = True # this was disabled by parser tests
    >>> module = Module(path)

Change Docstring contents::

    >>> doc = module.docstrings()[0]
    >>> print_source(doc())
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    <BLANKLINE>
    EOF

    >>> doc.text = u'I am the Changed Docstring'
    >>> print_source(doc())
    """I am the Changed Docstring
    """
    <BLANKLINE>
    EOF

Change protected section contents::

    >>> psec = module.protectedsections()[0]
    >>> print_source(psec())
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    <BLANKLINE>
    EOF

    >>> psec.text = u'import os\nimport sys'
    >>> print_source(psec())
    ##code-section section-1
    import os
    import sys
    ##/code-section section-1
    <BLANKLINE>
    <BLANKLINE>
    EOF

Change Block contents::

    >>> block = module.blocks()[0]
    >>> print_source(block())
    if foo is None:
        foo = 0
    <BLANKLINE>
    <BLANKLINE>
    EOF

    >>> text = u'try:\n    import ldap\n    print 1\n    a=1\n    print 2\n    print 3\nexcept ImportError, e:\n    pass'
    >>> block.text = text
    >>> print_source(block())
    try:
        import ldap
        print 1
        a=1
        print 2
        print 3
    except ImportError, e:
        pass
    <BLANKLINE>
    <BLANKLINE>
    EOF
    
    find lines containing some text
    >>> print block.findlines('print')
    [(2, u'    print 1'), (4, u'    print 2'), (5, u'    print 3')]
    
    Do some text manipulations
    insert 'foo()' call before first print statement
    
    >>> block.insertlinebefore('    foo()','print',0)
    >>> print_source(block())
    try:
        import ldap
        foo()
        print 1
        a=1
        print 2
        print 3
    except ImportError, e:
        pass
    <BLANKLINE>
    <BLANKLINE>
    EOF
    
    insert 'bar()' call after last print statement
    >>> block.insertlineafter('    bar()','print',-1)
    >>> print_source(block())
    try:
        import ldap
        foo()
        print 1
        a=1
        print 2
        print 3
        bar()
    except ImportError, e:
        pass
    <BLANKLINE>
    <BLANKLINE>
    EOF

    insert 'baz()' call after last blorf statement
    because there is no blorf line it should append it at the end of the block
    >>> block.insertlineafter('    baz()','blorf',-1)
    >>> print_source(block())
    try:
        import ldap
        foo()
        print 1
        a=1
        print 2
        print 3
        bar()
    except ImportError, e:
        pass
    <BLANKLINE>
    <BLANKLINE>
    baz()
    EOF

    shouldnt change anything, since newtext is already in the block
    >>> block.insertlineafter('    baz()','blorf',-1, ifnotpresent=True)
    >>> print_source(block())
    try:
        import ldap
        foo()
        print 1
        a=1
        print 2
        print 3
        bar()
    except ImportError, e:
        pass
    <BLANKLINE>
    <BLANKLINE>
    baz()
    EOF
    
    
    Reset block's test for further tests
    >>> block.text = u'try:\n    import ldap\nexcept ImportError, e:\n    pass'
    
Change Attribute contents::

    >>> attr = module.attributes()[0]
    >>> print_source(attr())
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    <BLANKLINE>
    EOF

    >>> attr.value = u'False'
    >>> print_source(attr())
    foo, bar = False
    <BLANKLINE>
    EOF

    >>> attr.targets.remove(u'foo')
    >>> print_source(attr())
    bar = False
    <BLANKLINE>
    EOF

Change Import contents::

    >>> imp = module.imports()[0]
    >>> print_source(imp())
    import Bar, \
           Baz as XBaz
    EOF

    >>> imp.fromimport = u'fancymod'
    >>> print_source(imp())
    from fancymod import (
        Bar,
        Baz as XBaz,
    )
    <BLANKLINE>
    EOF

    >>> imp.names = [(u'FancyClass', None)]
    >>> print_source(imp())
    from fancymod import FancyClass
    <BLANKLINE>
    EOF

Change Class contents::

    >>> cla = module.classes()[0]
    >>> print_source(cla())
    class SomeClass(Foo, Bar):
    ...
    EOF

    >>> cla.bases = [
    ...     u'VeryVeryLongClassNameFromSomewhere',
    ...     u'VeryVeryLongClassNameFromSomewhereElse',
    ... ]
    >>> print_source(cla())
    class SomeClass(VeryVeryLongClassNameFromSomewhere,
                    VeryVeryLongClassNameFromSomewhereElse):
    ...
    EOF

Change Function contents::

    >>> func = cla.functions()[0]
    >>> print_source(func())
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            """Docstring of function.
            """
            return \
                foo, \
                bar
    <BLANKLINE>
    EOF

    >>> func.kwargs = {}
    >>> print_source(func())
        @somedecorator(a)
        def somefunction(self, foo, bar, *args):
            ...
    EOF

    >>> func.args = list()
    >>> print_source(func())
        @somedecorator(a)
        def somefunction(self):
    ...
    EOF


Change Decorator contents::

    >>> dec = func.decorators()[0]
    >>> print_source(dec())
        @somedecorator(a)
    <BLANKLINE>
    EOF

    since the decorator was parsed with args it has still the call brackets
    >>> dec.args = list()
    >>> print_source(dec())
        @somedecorator()
    <BLANKLINE>
    EOF

    now we make it non-callable
    >>> dec.is_callable=False
    >>> print_source(dec())
        @somedecorator
    <BLANKLINE>
    EOF
    
    
    >>> dec.kwargs = {'name': None}
    >>> print_source(dec())
        @somedecorator(name=None)
    <BLANKLINE>
    EOF

Check decorator comparison::

    >>> from node.ext.python import Decorator
    >>> dec = Decorator('decname')
    >>> dec.args = ['1', '2']
    >>> dec.kwargs = {'3': 'a'}

    >>> dec1 = Decorator('decname')
    >>> dec1.args = ['1', '2']
    >>> dec1.kwargs = {'3': 'a'}

    >>> dec1.equals(dec)
    True

    >>> dec.args = []
    >>> dec1.equals(dec)
    False

Add some more stuff to ``OtherClass`` class of module for later checks::

    >>> cla1 = module.classes()[1]
    >>> from node.ext.python import Function
    >>> from node.ext.python import Docstring
    >>> from node.ext.python import ProtectedSection
    >>> from node.ext.python import Block
    >>> func1 = Function(u'addedfunc')
    >>> dec1 = Decorator(u'property')
    >>> block1 = Block()
    >>> block1.lines = [u'if True:', u'    return False']
    >>> doc1 = Docstring()
    >>> doc1.text = u'Added function doc'
    >>> func1['doc'] = doc1
    >>> func1['block'] = block1
    >>> cla1['funcadded'] = func1
    >>> psec1 = ProtectedSection(u'section-2')
    >>> psec1.lines = [u"print u'I am the protected section code'"]
    >>> cla['psec'] = psec1
    >>> path = os.path.join(datadir, 'changed.py')
    >>> module.__name__ = path
    >>> module()

Parse the already dumped file::

    >>> module = Module(path)
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.Docstring'>: [2:3] - 0
      <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 0
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [25:28] - 1
        <class 'node.ext.python.nodes.Function'>: [31:36] - 1
          <class 'node.ext.python.nodes.Docstring'>: [32:33] - 2
          <class 'node.ext.python.nodes.Block'>: [34:36] - 2
          <class 'node.ext.python.nodes.Decorator'>: [30:30] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 1
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Write the re-parsed file again unchanged and compare output files::

    >>> path = os.path.join(datadir, 'unchanged.py')
    >>> module.__name__ = path
    >>> module()

    >>> file = open(os.path.join(datadir, 'changed.py'))
    >>> changed = file.read()
    >>> file.close()
    >>> file = open(os.path.join(datadir, 'unchanged.py'))
    >>> unchanged = file.read()
    >>> file.close()
    >>> changed == unchanged
    True

Change path of module for node moving tests::

    >>> path = os.path.join(datadir, 'moved.py')
    >>> module.__name__ = path

Move module docstring to class function::

    >>> name = module.docstrings()[0].__name__
    >>> doc = module.detach(name)
    >>> func = module.classes(name=u'OtherClass')[0].functions()[0]
    >>> ref = func.blocks()[0]
    >>> func.insertbefore(doc, ref)
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 0
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [25:28] - 1
        <class 'node.ext.python.nodes.Function'>: [31:36] - 1
          <class 'node.ext.python.nodes.Docstring'>: [32:33] - 2
          <class 'node.ext.python.nodes.Block'>: [34:36] - 2
          <class 'node.ext.python.nodes.Decorator'>: [30:30] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 1
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Docstring'>: [2:3] - 2
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Move protected section to module::

    >>> cla = module.classes()[0]
    >>> name = cla.protectedsections()[0].__name__
    >>> psec = cla.detach(name)
    >>> module.insertafter(psec, cla)
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 0
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [25:28] - 1
        <class 'node.ext.python.nodes.Function'>: [31:36] - 1
          <class 'node.ext.python.nodes.Docstring'>: [32:33] - 2
          <class 'node.ext.python.nodes.Block'>: [34:36] - 2
          <class 'node.ext.python.nodes.Decorator'>: [30:30] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 0
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Docstring'>: [2:3] - 2
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Move protected section of module to class::

    >>> name = module.protectedsections()[0].__name__
    >>> psec = module.detach(name)
    >>> cla.insertafter(psec, cla.attributes()[1])
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [25:28] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 1
        <class 'node.ext.python.nodes.Function'>: [31:36] - 1
          <class 'node.ext.python.nodes.Docstring'>: [32:33] - 2
          <class 'node.ext.python.nodes.Block'>: [34:36] - 2
          <class 'node.ext.python.nodes.Decorator'>: [30:30] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 0
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Docstring'>: [2:3] - 2
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Move function from class to module::

    >>> name = cla.functions()[0].__name__
    >>> func = cla.detach(name)
    >>> func.args
    ['self']

    >>> func.args = [] # remove self from args

    >>> module.insertbefore(func, cla)
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Function'>: [31:36] - 0
        <class 'node.ext.python.nodes.Docstring'>: [32:33] - 1
        <class 'node.ext.python.nodes.Block'>: [34:36] - 1
        <class 'node.ext.python.nodes.Decorator'>: [30:30] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.Attribute'>: [25:28] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 0
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Docstring'>: [2:3] - 2
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Move attribute from class to module::

    >>> name = cla.attributes()[1].__name__
    >>> attr = cla.detach(name)
    >>> module.insertafter(attr, module.attributes()[0])
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:51] - -1
      <class 'node.ext.python.nodes.Block'>: [10:13] - 0
      <class 'node.ext.python.nodes.Attribute'>: [15:15] - 0
      <class 'node.ext.python.nodes.Attribute'>: [25:28] - 0
      <class 'node.ext.python.nodes.Import'>: [17:17] - 0
      <class 'node.ext.python.nodes.Function'>: [31:36] - 0
        <class 'node.ext.python.nodes.Docstring'>: [32:33] - 1
        <class 'node.ext.python.nodes.Block'>: [34:36] - 1
        <class 'node.ext.python.nodes.Decorator'>: [30:30] - 0
      <class 'node.ext.python.nodes.Class'>: [19:40] - 0
        <class 'node.ext.python.nodes.Docstring'>: [21:22] - 1
        <class 'node.ext.python.nodes.Attribute'>: [24:24] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [5:8] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [38:40] - 0
      <class 'node.ext.python.nodes.Class'>: [42:51] - 0
        <class 'node.ext.python.nodes.Function'>: [44:45] - 1
          <class 'node.ext.python.nodes.Docstring'>: [2:3] - 2
          <class 'node.ext.python.nodes.Block'>: [45:45] - 2
        <class 'node.ext.python.nodes.Function'>: [47:51] - 1
          <class 'node.ext.python.nodes.Docstring'>: [48:49] - 2
          <class 'node.ext.python.nodes.Block'>: [50:51] - 2

Dump file and check output file::

    >>> module()
    >>> file = open(module.filepath)
    >>> content = file.read()
    >>> file.close()
    >>> print_source(content)
    # -*- coding: utf-8 -*-
    try:
        import ldap
    except ImportError, e:
        pass
    <BLANKLINE>
    bar = False
    otherattribute = {
        'key-1': 1,
        'key-2': 2,
    }
    <BLANKLINE>
    from fancymod import FancyClass
    <BLANKLINE>
    @somedecorator(name=None)
    def somefunction():
        """Docstring of function.
        """
        return \
            foo, \
            bar
    <BLANKLINE>
    class SomeClass(VeryVeryLongClassNameFromSomewhere,
                    VeryVeryLongClassNameFromSomewhereElse):
        """Docstring of ``SomeClass``.
        """
    <BLANKLINE>
        someattribute = u'somevalue'
    <BLANKLINE>
        ##code-section section-1
        import os
        import sys
        ##/code-section section-1
    <BLANKLINE>
    ##code-section section-2
    print u'I am the protected section code'
    ##/code-section section-2
    <BLANKLINE>
    class OtherClass(object):
    <BLANKLINE>
        def otherfunction(self):
            """I am the Changed Docstring
            """
            raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
        def addedfunc(self):
            """Added function doc
            """
            if True:
                return False
    EOF

Check if this output re-parses valid::

    >>> module = Module(module.filepath)
    >>> module.printtree()
    <class 'node.ext.python.nodes.Module'>: [1:50] - -1
      <class 'node.ext.python.nodes.Block'>: [2:5] - 0
      <class 'node.ext.python.nodes.Attribute'>: [7:7] - 0
      <class 'node.ext.python.nodes.Attribute'>: [8:11] - 0
      <class 'node.ext.python.nodes.Import'>: [13:13] - 0
      <class 'node.ext.python.nodes.Function'>: [16:21] - 0
        <class 'node.ext.python.nodes.Docstring'>: [17:18] - 1
        <class 'node.ext.python.nodes.Block'>: [19:21] - 1
        <class 'node.ext.python.nodes.Decorator'>: [15:15] - 0
      <class 'node.ext.python.nodes.Class'>: [23:33] - 0
        <class 'node.ext.python.nodes.Docstring'>: [25:26] - 1
        <class 'node.ext.python.nodes.Attribute'>: [28:28] - 1
        <class 'node.ext.python.nodes.ProtectedSection'>: [30:33] - 1
      <class 'node.ext.python.nodes.ProtectedSection'>: [35:37] - 0
      <class 'node.ext.python.nodes.Class'>: [39:50] - 0
        <class 'node.ext.python.nodes.Function'>: [41:44] - 1
          <class 'node.ext.python.nodes.Docstring'>: [42:43] - 2
          <class 'node.ext.python.nodes.Block'>: [44:44] - 2
        <class 'node.ext.python.nodes.Function'>: [46:50] - 1
          <class 'node.ext.python.nodes.Docstring'>: [47:48] - 2
          <class 'node.ext.python.nodes.Block'>: [49:50] - 2
