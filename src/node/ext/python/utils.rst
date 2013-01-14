node.ext.python.utils
=====================

Define print helper::

    >>> def print_source(source):
    ...     for line in source.split('\n'):
    ...         print line
    ...     print 'EOF'

The Imports helper class.

Its context must be an IModule implemenation::

    >>> from node.ext.python.utils import Imports
    >>> imp = Imports(object())
    Traceback (most recent call last):
      ...
    ValueError: Given context is not an IModule implementation

    >>> from node.ext.python import Module
    >>> module = Module('somemodule.py')
    >>> module.rendererfactory._write_file = False
    >>> imp = Imports(module)
    >>> imp
    <node.ext.python.utils.Imports object at ...>

Add some imports::

    >>> imp.set()
    Traceback (most recent call last):
      ...
    ValueError: No definitions given.

    >>> imp.set(fromimport='foo', names=[['bar', None]])
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    EOF

    >>> imp.set(fromimport='bar', names=[['baz', None]])
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    from bar import baz
    EOF

Add another import for fromimport::

    >>> imp.set(fromimport='bar', names=[['abc', None]])
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    from bar import (
        baz,
        abc,
    )
    EOF

Update an import::

    >>> imp.set(fromimport='bar', names=[['abc', 'lalala']])
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    from bar import (
        baz,
        abc as lalala,
    )
    EOF

Add a Class to module and chack if new imports are added to top of module::

    >>> from node.ext.python import Class
    >>> class_ = Class('SomeClass')
    >>> module['someclass'] = class_
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    from bar import (
        baz,
        abc as lalala,
    )
    <BLANKLINE>
    class SomeClass(object):
        pass
    EOF

    >>> imp.set(fromimport='insert', names=[['MyClass', None]])
    >>> print_source(module())
    # -*- coding: utf-8 -*-
    from foo import bar
    from bar import (
        baz,
        abc as lalala,
    )
    from insert import MyClass
    <BLANKLINE>
    class SomeClass(object):
        pass
    EOF
