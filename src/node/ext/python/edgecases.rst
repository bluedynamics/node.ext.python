Here we deal with some more cryptic stuff and edge cases::

    >>> import os
    >>> modulepath = os.path.join(datadir, 'edgecases.py')    
    >>> from node.ext.python import Module
    >>> module = Module(modulepath)
    >>> module
    <Module object '.../edgecases.py' at ...>

    # >>> module.printtree()
    # <class 'node.ext.python.nodes.Module'>: [4:41] - -1
    #   <class 'node.ext.python.nodes.Import'>: [4:4] - 0
    #   <class 'node.ext.python.nodes.Function'>: [9:10] - 0
    #     <class 'node.ext.python.nodes.Block'>: [10:10] - 1
    #   <class 'node.ext.python.nodes.Function'>: [24:27] - 0
    #     <class 'node.ext.python.nodes.Block'>: [25:27] - 1
    #   <class 'node.ext.python.nodes.Function'>: [30:33] - 0
    #     <class 'node.ext.python.nodes.Block'>: [31:33] - 1
    #   <class 'node.ext.python.nodes.Block'>: [32:33] - 0
    #   <class 'node.ext.python.nodes.Class'>: [35:39] - 0
    #     <class 'node.ext.python.nodes.Function'>: [36:36] - 1
    #       <class 'node.ext.python.nodes.Block'>: [37:37] - 2
    #     <class 'node.ext.python.nodes.Function'>: [38:38] - 1
    #       <class 'node.ext.python.nodes.Block'>: [39:39] - 2
    #   <class 'node.ext.python.nodes.Function'>: [41:41] - 0
    # 

    >>> modulepath = os.path.join(datadir, 'nullbyte.py')    
    >>> from node.ext.python import Module
    >>> module = Module(modulepath)
    Traceback (most recent call last):
      ...
    TypeError: compile() expected string without null bytes

