Python Parser
=============

::
    >>> import os
    >>> modulepath = os.path.join(datadir, 'parseme.py')
    >>> from node.ext.python.goparser import GoParser
    >>> fileinst = open(modulepath,'r')
    >>> source = fileinst.read()
    >>> fileinst.close()
    >>> myparser = GoParser(source, modulepath)
    >>> myparser.parsegen()
    --- 0 (0) Expr (5-8) (parent: None)
    005:"""This file is used as test source for python nodes.
    006:
    007:The code itself does nothing useful and is not executable.
    008:"""
    ...
    --- 1 (4) Return (192-194) (parent: FunctionDef (189-194))
    192:    return a, \\
    193:           b, \\
    194:           c

    >>> print repr(myparser.nodes)
    [Expr (5-8), Expr (10-10), Import (12-12), Import (13-13), 
    ImportFrom (14-14), ImportFrom (15-15), ImportFrom (16-21), 
    If (23-24), If (26-35), For (37-38), TryExcept (40-45), 
    TryFinally (47-50), TryFinally (52-57), If (59-59), If (61-63), 
    If (65-67), If (69-71), If (73-76), While (78-79), 
    FunctionDef (81-82), Assert (84-84), Assign (86-86), 
    Assign (88-88), Assign (90-92), Assign (94-99), Assign (101-103), 
    Assign (105-105), Assign (107-107), Assign (109-112), 
    FunctionDef (115-118), Print (119-120), FunctionDef (122-125), 
    ClassDef (127-144), ClassDef (146-160), ClassDef (162-165), 
    FunctionDef (170-171), FunctionDef (176-177), ImportFrom (179-180), 
    ImportFrom (182-185), Import (187-187), FunctionDef (189-194)]
