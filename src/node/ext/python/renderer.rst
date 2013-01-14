Python Renderers
================


Setup
-----

Set up a test environment::

    >>> import os
    >>> path = os.path.join(datadir, 'rendered.py')

Remove the generated file created by previous test run::

    >>> try:
    ...     os.remove(path)
    ... except Exception: pass

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

Check Module::
  
    >>> module = Module(path)
    >>> module.rendererfactory._write_file = False
    >>> module()
    u'# -*- coding: utf-8 -*-'

Check Docstring::

    >>> docstring = Docstring()
    >>> print_source(docstring())
    """
    """
    <BLANKLINE>
    EOF

    >>> docstring.lines
    []

    >>> docstring.text
    u''

    >>> docstring.text = u'\n\n\na\nb\n\n\n\n'
    >>> docstring.text
    u'a\nb'

    >>> docstring.lines = [u'a', u'b', u'c']
    >>> docstring.lines
    [u'a', u'b', u'c']

    >>> docstring.text
    u'a\nb\nc'

    >>> docstring.text = u'I am a docstring.\n\nSome Documentation.'
    >>> docstring.text
    u'I am a docstring.\n\nSome Documentation.'

    >>> docstring.lines
    [u'I am a docstring.', u'', u'Some Documentation.']

    >>> print_source(docstring())
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    <BLANKLINE>
    EOF

Add docstring to module and render::

    >>> module['docstring-1'] = docstring
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    EOF

Check ProtectedSection::

    >>> ProtectedSection()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete protected section definition.

    >>> sec = ProtectedSection('section-1')
    >>> print_source(sec())
    ##code-section section-1
    ##/code-section section-1
    <BLANKLINE>
    <BLANKLINE>
    EOF

    >>> sec.lines
    []

    >>> sec.text
    u''

    >>> sec.lines = [u'a', u'b', u'c']
    >>> sec.lines
    [u'a', u'b', u'c']

    >>> sec.text
    u'a\nb\nc'

    >>> sec.text = u'from foo import bar'
    >>> sec.text
    u'from foo import bar'

    >>> sec.lines
    [u'from foo import bar']

    >>> print_source(sec())
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    <BLANKLINE>
    EOF

Add protected section to module and render::

    >>> module['section-1'] = sec
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    EOF

Check Block::

    >>> block = Block()
    >>> block()
    u''

    >>> block.lines
    []

    >>> block.text
    u''

    >>> block.lines = [u'a', u'b', u'c']
    >>> block.lines
    [u'a', u'b', u'c']

    >>> block.text
    u'a\nb\nc'

    >>> block.text = u'if foo is None:\n    foo = 0'
    >>> block.text
    u'if foo is None:\n    foo = 0'

    >>> block.lines
    [u'if foo is None:', u'    foo = 0']

    >>> print_source(block())
    if foo is None:
        foo = 0
    <BLANKLINE>
    <BLANKLINE>
    EOF

Add block to module and render::

    >>> module['block-1'] = block
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    if foo is None:
        foo = 0
    EOF

Check Attribute::

    >>> Attribute()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete attribute definition.

    >>> attribute = Attribute(['foo', 'bar'],
    ...                       u'{\n    \'x\': 1,\n    \'y\': 2,\n}')
    >>> print_source(attribute())
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    <BLANKLINE>
    EOF

Add attribute to module and render::

    >>> module['attribute-1'] = attribute
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    if foo is None:
        foo = 0
    <BLANKLINE>
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    EOF

Check Import::

    >>> Import()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete import definition.

    >>> import_ = Import(u'foo')
    >>> import_()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete import definition.

    >>> import_.names = [('Bar', None)]
    >>> print_source(import_())
    from foo import Bar
    <BLANKLINE>
    EOF

    >>> import_.names = [
    ... ('Bar', None),
    ... ('Bat', None),
    ... ('Baz', None),
    ... ]
    >>> print_source(import_())
    from foo import (
        Bar,
        Bat,
        Baz,
    )
    <BLANKLINE>
    EOF

    >>> import_.names = [
    ... ('Bar', 'XBar'),
    ... ('Bat', 'XBat'),
    ... ('Baz', 'XBaz'),
    ... ]
    >>> print_source(import_())
    from foo import (
        Bar as XBar,
        Bat as XBat,
        Baz as XBaz,
    )
    <BLANKLINE>
    EOF

    >>> import_.fromimport = None
    >>> import_.names = [
    ... ('Bar', None),
    ... ('Baz', 'XBaz'),
    ... ]
    >>> print_source(import_())
    import Bar, \
           Baz as XBaz
    <BLANKLINE>
    EOF

Add import to module and render::

    >>> module['import-1'] = import_
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    if foo is None:
        foo = 0
    <BLANKLINE>
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    import Bar, \
           Baz as XBaz
    EOF

Check ArgumentRenderer Mixin class.

The ``render_arg`` and ``render_kwarg`` functions::

    >>> from node.ext.python.renderer import ArgumentRenderer
    >>> ar = ArgumentRenderer()
    >>> ar.render_arg('a')
    u'a'
    >>> ar.render_arg('"a"')
    u'"a"'
    >>> ar.render_arg('object()')
    u'object()'
    >>> ar.render_arg(1)
    u'1'
    >>> ar.render_arg([])
    u'[]'
    >>> ar.render_arg({})
    u'{}'
    >>> ar.render_arg(True)
    u'True'
    >>> ar.render_arg(None)
    u'None'
    >>> ar.render_kwarg('name', None)
    u'name=None'

    >>> from node.ext.python import Call
    >>> call = Call(name='SomeObj', args=[1, 2, 3], kwargs=dict(foo='"bar"'))
    >>> ar.render_arg(call)
    u'SomeObj(1, 2, 3, foo="bar")'

Check if internal ``_startlen_exeeds``, ``_startlen``, and ``_defaultlen``
attributes are calculated properly:: 

    >>> dummy = ar.render_arguments(0, 78, ['a'])
    >>> ar._startlen_exeeds
    False
    >>> ar._startlen
    2
    >>> ar._defaultlen
    70

    >>> dummy = ar.render_arguments(0, 50, [30 * 'a'])
    >>> ar._startlen_exeeds
    True
    >>> ar._startlen
    30
    >>> ar._defaultlen
    70

    >>> dummy = ar.render_arguments(3, 50, [19 * 'a'])
    >>> ar._startlen_exeeds
    True
    >>> ar._startlen
    18
    >>> ar._defaultlen
    58

    >>> dummy = ar.render_arguments(3, 50, [17 * 'a'])
    >>> ar._startlen_exeeds
    False
    >>> ar._startlen
    18
    >>> ar._defaultlen
    58

    >>> dummy = ar.render_arguments(3, 50, [18 * 'a'])
    >>> ar._startlen_exeeds
    True
    >>> ar._startlen
    18
    >>> ar._defaultlen
    58

    >>> dummy = ar.render_arguments(0, 2)
    >>> ar._startlen
    78
    >>> ar._defaultlen
    78

    >>> dummy = ar.render_arguments(20, 10)
    >>> ar._startlen
    0
    >>> ar._defaultlen
    30

    >>> dummy = ar.render_arguments(18, 4)
    >>> ar._arglines = list()
    >>> ar._resolve_arglines(['a'], 18)
    >>> ar._arglines
    ['a']

Some tests on internal ``_resolve_arglines`` function::

    >>> dummy = ar.render_arguments(18, 1)
    >>> ar._arglines = list()
    >>> ar._resolve_arglines([8 * 'a'], 18)
    >>> ar._startlen
    7
    >>> ar._defaultlen
    7
    >>> ar._arglines
    [u'\n', ' aaaaaaaa']

    >>> dummy = ar.render_arguments(10, 20)
    >>> ar._arglines = list()
    >>> args = [8 * str(i) for i in range (10)]
    >>> ar._resolve_arglines(args, 10)
    >>> ar._startlen
    20
    >>> ar._defaultlen
    30
    >>> ar._arglines
    [u'00000000, 11111111', 
    u'                    22222222, 33333333', 
    u'                    44444444, 55555555', 
    u'                    66666666, 77777777', 
    u'                    88888888, 99999999']

Tests ``render_arguments`` function::

    >>> kwargs = {
    ... 'foo': 'callsomelongnamefunction()',
    ... 'bar': [1, 2, 3, 4, 5],
    ... 'call': call,
    ... }
    >>> ar.render_arguments(1, 30, args, kwargs).split('\n')
    [u'00000000, 11111111, 22222222, 33333333,', 
    u'                              44444444, 55555555, 66666666, 77777777,', 
    u'                              88888888, 99999999,', 
    u'                              call=SomeObj(1, 2, 3, foo="bar"),', 
    u'                              foo=callsomelongnamefunction(),', 
    u'                              bar=[1, 2, 3, 4, 5]']

Check Decorator::

    >>> Decorator()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete decorator definition.

    >>> dec = Decorator(u'somedecorator')
    >>> print_source(dec())
    @somedecorator
    <BLANKLINE>
    EOF

    >>> dec.args = ['a']
    >>> print_source(dec())
    @somedecorator(a)
    <BLANKLINE>
    EOF

    >>> dec.args = ['"a"']
    >>> print_source(dec())
    @somedecorator("a")
    <BLANKLINE>
    EOF

    >>> dec.args = ['object()']
    >>> print_source(dec())
    @somedecorator(object())
    <BLANKLINE>
    EOF

    >>> dec.args = [1, [], {}, True]
    >>> print_source(dec())
    @somedecorator(1, [], {}, True)
    <BLANKLINE>
    EOF

    >>> call = Call(name='SomeObj', args=[1, 2, 3], kwargs=dict(foo='"bar"'))
    >>> dec.args = [call]
    >>> print_source(dec())
    @somedecorator(SomeObj(1, 2, 3, foo="bar"))
    <BLANKLINE>
    EOF

    >>> dec.args = ['a']
    >>> dec.kwargs = {'name': None}
    >>> print_source(dec())
    @somedecorator(a, name=None)
    <BLANKLINE>
    EOF

    >>> dec.args = args
    >>> dec.kwargs = kwargs
    >>> dec.nodelevel
    0
    >>> print_source(dec())
    @somedecorator(00000000, 11111111, 22222222, 33333333, 44444444, 55555555,
                   66666666, 77777777, 88888888, 99999999,
                   call=SomeObj(1, 2, 3, foo="bar"), foo=callsomelongnamefunction(),
                   bar=[1, 2, 3, 4, 5])
    <BLANKLINE>
    EOF

Check Function::

    >>> Function()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete function definition.

    >>> func = Function(u'somefunction')
    >>> print_source(func())
    def somefunction():
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

    >>> func.args = ['foo', 'bar']
    >>> func.kwargs = {'baz': False}
    >>> print_source(func())
    def somefunction(foo, bar, baz=False):
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

    >>> func.args = ['"%s"' % (str(i) * 8) for i in range(10)]
    >>> print_source(func())
    def somefunction("00000000", "11111111", "22222222", "33333333", "44444444",
                     "55555555", "66666666", "77777777", "88888888", "99999999",
                     baz=False):
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

    >>> func.args = ['foo', 'bar', '*args']
    >>> func.kwargs = {'**kwargs': None}
    >>> print_source(func())
    def somefunction(foo, bar, *args, **kwargs):
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

Add decorator to function::

    >>> dec.args = []
    >>> dec.kwargs = {}
    >>> func['decorator-1'] = dec
    >>> print_source(func())
    @somedecorator
    def somefunction(foo, bar, *args, **kwargs):
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

    >>> dec.args = ['a']
    >>> print_source(func())
    @somedecorator(a)
    def somefunction(foo, bar, *args, **kwargs):
        raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

Check Class::

    >>> Class()()
    Traceback (most recent call last):
      ...
    Incomplete: Incomplete class definition.
    
    >>> class_ = Class(u'SomeClass')
    >>> print_source(class_())
    class SomeClass(object):
        pass
    <BLANKLINE>
    EOF

    >>> class_.bases = ['Foo', 'Bar']
    >>> print_source(class_())
    class SomeClass(Foo, Bar):
        pass
    <BLANKLINE>
    EOF

    >>> class_.bases = [
    ...     'Aaaaaaaa',
    ...     'Bbbbbbbb',
    ...     'Cccccccc',
    ...     'Dddddddd',
    ...     'Eeeeeeee',
    ...     'Ffffffff',
    ...     'Gggggggg',
    ...     'Hhhhhhhh',
    ... ]
    >>> print_source(class_())
    class SomeClass(Aaaaaaaa, Bbbbbbbb, Cccccccc, Dddddddd, Eeeeeeee, Ffffffff,
                    Gggggggg, Hhhhhhhh):
        pass
    <BLANKLINE>
    EOF

    >>> class_.bases = ['Foo', 'Bar']

Add function to class. Take a look at the function output, ``self`` is added to
arguments transparently::

    >>> class_['function-1'] = func
    >>> print_source(class_())
    class SomeClass(Foo, Bar):
    <BLANKLINE>
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

Insert docstring before function. Newline behaves different::

    >>> doc = Docstring()
    >>> doc.__name__ = 'docstring-1'
    >>> doc.text = u'Docstring of ``SomeClass``.'
    >>> class_.insertbefore(doc, func)
    >>> print_source(class_())
    class SomeClass(Foo, Bar):
        """Docstring of ``SomeClass``.
        """
    <BLANKLINE>
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

Insert Attributes before function::

    >>> attr = Attribute()
    >>> attr.__name__ = u'attr-1'
    >>> attr.targets = ['someattribute']
    >>> attr.value = "u'somevalue'"
    >>> class_.insertbefore(attr, func)
    >>> print_source(attr())
         someattribute = u'somevalue'
    <BLANKLINE>
    EOF

    >>> attr = Attribute()
    >>> attr.__name__ = u'attr-2'
    >>> attr.targets = ['otherattribute']
    >>> attr.value = u"{\n" + \
    ... u"    'key-1': 1,\n" + \
    ... u"    'key-2': 2,\n" + \
    ... u"}"
    >>> print_source(attr())
    otherattribute = {
        'key-1': 1,
        'key-2': 2,
    }
    <BLANKLINE>
    EOF

    >>> class_.insertbefore(attr, func)
    >>> print_source(class_())
    class SomeClass(Foo, Bar):
        """Docstring of ``SomeClass``.
        """
    <BLANKLINE>
        someattribute = u'somevalue'
        otherattribute = {
            'key-1': 1,
            'key-2': 2,
        }
    <BLANKLINE>
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            raise NotImplementedError("stub generated by AGX.")
    <BLANKLINE>
    EOF

    >>> attr = Attribute()
    >>> attr.__name__ = u'attr-3'
    >>> attr.targets = ['attribute_with_callable']
    >>> attr.value = 'SomeFactory'
    >>> attr.args.append('foo')
    >>> attr.kwargs['bar'] = 'baz'
    >>> print_source(attr())
    attribute_with_callable = SomeFactory(foo, bar=baz)
    <BLANKLINE>
    EOF

Add Block to function::

    >>> block = Block()
    >>> block.lines = [
    ...     u'return \\',
    ...     u'    foo, \\',
    ...     u'    bar',
    ... ]
    >>> print_source(block())
    return \
        foo, \
        bar
    <BLANKLINE>
    <BLANKLINE>
    EOF

    >>> func['block-1'] = block
    >>> print_source(func())
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            return \
                foo, \
                bar
    <BLANKLINE>
    EOF

Add Docstring to function::

    >>> doc = Docstring()
    >>> doc.__name__ = 'doc-1'
    >>> doc.text = u'Docstring of function.'
    >>> func.insertbefore(doc, block)
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

Add class to module and render::

    >>> module['class-1'] = class_
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    if foo is None:
        foo = 0
    <BLANKLINE>
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    import Bar, \
           Baz as XBaz
    <BLANKLINE>
    class SomeClass(Foo, Bar):
        """Docstring of ``SomeClass``.
        """
    <BLANKLINE>
        someattribute = u'somevalue'
        otherattribute = {
            'key-1': 1,
            'key-2': 2,
        }
    <BLANKLINE>
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            """Docstring of function.
            """
            return \
                foo, \
                bar
    EOF

Add another class::

    >>> class_ = Class()
    >>> class_.classname = u'OtherClass'
    >>> func = Function()
    >>> func.functionname = u'otherfunction'
    >>> class_['func-1'] = func
    >>> module['class-2'] = class_
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    """I am a docstring.
    <BLANKLINE>
    Some Documentation.
    """
    ##code-section section-1
    from foo import bar
    ##/code-section section-1
    <BLANKLINE>
    if foo is None:
        foo = 0
    <BLANKLINE>
    foo, bar = {
        'x': 1,
        'y': 2,
    }
    import Bar, \
           Baz as XBaz
    <BLANKLINE>
    class SomeClass(Foo, Bar):
        """Docstring of ``SomeClass``.
        """
    <BLANKLINE>
        someattribute = u'somevalue'
        otherattribute = {
            'key-1': 1,
            'key-2': 2,
        }
    <BLANKLINE>
        @somedecorator(a)
        def somefunction(self, foo, bar, *args, **kwargs):
            """Docstring of function.
            """
            return \
                foo, \
                bar
    <BLANKLINE>
    class OtherClass(object):
    <BLANKLINE>
        def otherfunction(self):
            raise NotImplementedError("stub generated by AGX.")
    EOF

Write file to datadir::

    >>> module.rendererfactory._write_file = True
    >>> module.__name__ = path
    >>> module()

Add common namespace package ``__init__.py``. We use a corrupted filename to
avoid the data dir to be a real python package::

    >>> try:
    ...     os.remove('%s/__init_.py' % datadir)
    ... except Exception: pass
    
    >>> init = Module('%s/__init_.py' % datadir)
    >>> sn_dec = Block()
    >>> sn_dec.text = u"__import__('pkg_resources').declare_namespace(" + \
    ...               u"__name__)"
    >>> init['ns_dec'] = sn_dec
    >>> init()
