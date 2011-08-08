# -*- coding: utf-8 -*-
# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#


import os
import copy
from zope.interface import implements
from node.base import OrderedNode
from node.utils import LocationIterator
from node.ext.python.goparser import GoParser
from node.ext.python.interfaces import (
        Incomplete,
        IPythonNode,
        IModule,
        IDocstring,
        IProtectedSection,
        IImport,
        IAttribute,
        IDecorator,
        IFunction,
        IClass,
        IBlock,
        )
from odict import odict
from plumber import plumber
from node.parts import (
    Reference,
    Order,
)

# -- Node implementations start heree --

class PythonNode(OrderedNode):
    """Python node. That is the base node."""

    __metaclass__ = plumber
    __plumbing__ = Reference, Order

    implements(IPythonNode)
        
    def __init__(self, 
            name, buffer=None, gometanode=None,  
            text=None, lines=None,
            bufstart=None, bufend=None, 
            startlineno=None, endlineno=None, 
            indent=None, nodelevel=None, postlf=None):
        OrderedNode.__init__(self, name)
        self._text = None
        self._lines = None
        self.buffer = None
        self._startlineno = None
        self._endlineno = None
        self.gometanode = gometanode
        if self.gometanode:
            self.astnode = gometanode.astnode
            # Start index of lines in buffer.
            self.bufstart = gometanode.startline + gometanode.offset
            # End index of lines in buffer.
            self.bufend = gometanode.endline + gometanode.offset
            # Start line number of python Node.
            startlineno = gometanode.startline
            # End line number of python Node.
            endlineno = gometanode.endline
            # Indent level of buffer[bufstart:bufend].
            self.indent = gometanode.indent
            buffer = gometanode.sourcelines
            lines = gometanode.get_sourcelines()
        # Number of Newlines to render after Node.
        self.buffer = buffer
        self.startlineno = startlineno
        self.endlineno = endlineno
        self.postlf = postlf
        self.text = text
        self.lines = lines
        
    # Text and lines work in sync here, if text is set lines are set and vice 
    # versa.
    def _get_lines(self):
        return self._lines
    
    def _set_lines(self, lines=None):
        if lines == None:
            return          # Don't change value if None is given
        self._lines = lines
        self._text = '\n'.join([i.rstrip('\n') for i in lines])

    def _get_text(self):
        return self._text
    
    def _set_text(self, text=None):
        if text == None:
            return          # Don't change value if None is given
        self._text = text
        self._lines = text.split('\n')
        
    def _get_startlineno(self):
        return self._startlineno
        
    def _set_startlineno(self, number):
        self._startlineno = number
        
    def _get_endlineno(self):
        return self._endlineno
        
    def _set_endlineno(self,number):
        self._endlineno = number
        
    text = property(_get_text, _set_text)
    lines = property(_get_lines, _set_lines)
    startlineno = property(_get_startlineno, _set_startlineno)
    endlineno = property(_get_endlineno, _set_endlineno)

    @property
    def nodelevel(self):
        level = -1
        for parent in LocationIterator(self):
            if IModule.providedBy(parent):
                break
            level += 1
        return level
    
    def getnodes(self, interface, name=None):
        items = [p for p in self.filtereditems(IProtectedSection)]
        if name is not None:
            items = [p for p in items if p.name == name]
        return items
    
    def docstrings(self):
        return self.getnodes(IDocstring)
    
    def blocks(self):
        return self.getnodes(IBlock)
    
    def imports(self):
        return self.getnodes(IImport)
    
    def protectedsections(self, name=None):
        return self.getnodes(IProtectedSection)
    
    def classes(self, name=None):
        return self.getnodes(IClass, name)
    
    def functions(self, name=None):
        return self.getnodes(IFunction, name)
    
    def attributes(self, name=None):
        return self.getnodes(IAttribute, name)

    def acquire(self, interface=None):
        if interface.providedBy(self):
            return self
        context = self.__parent__
        while context and not interface.providedBy(context):
            context = context.parent
        return context
                
    @property
    def noderepr(self):
        try:
            module = self.acquire(IModule)
            offset = module.bufoffset
            startlineno = self.startlineno
            if startlineno is not None:
                startlineno = str(startlineno + offset)
            else :
                startlineno = '?'
            endlineno = self.endlineno
            if endlineno is not None:
                endlineno = str(endlineno + offset)
            else :
                endlineno = '?'
            return str(self.__class__) + \
                   ': [%s:%s] - %s' % (str(self.startlineno),
                                       str(self.endlineno),
                                       str(self.nodelevel))
        except Exception, e:
            # happens if node was created manually
            import pdb;pdb.set_trace()
            return str(self.__class__) + ': [?:?] - %s' % str(self.nodelevel)    


class Module(PythonNode):
    implements(IModule)
    
    def __init__(self, 
            encoding=u'utf-8', 
            name=None, 
            lines=[], 
            startlineno=0, endlineno=None,
            bufoffset=0,
            ):
        PythonNode.__init__(self, name=name, lines=lines)
        self.encoding = encoding
        self.modulename = unicode(os.path.splitext(os.path.basename(name))[0])
        self.startlineno = startlineno
        self.endlineno = endlineno
        self.bufoffset = bufoffset
        
class Docstring(PythonNode):
    implements(IDocstring)
    
    def __init__(self, name=None, gometanode=None, lines=[], text='', buffer=[]):
        PythonNode.__init__(self, name=name, gometanode=gometanode, buffer=buffer, lines=lines)

class ProtectedSection(PythonNode):
    implements(IProtectedSection)

    def __init__(self, sectionname=None, buffer=[]):
        PythonNode.__init__(self, sectionname, None, buffer)
        self.sectionname = sectionname
        self.postlf = 1

class Import(PythonNode):
    implements(IImport)
    
    def __init__(self, fromimport=None, names=[], gometanode=None, buffer=[]):
        PythonNode.__init__(self, None, gometanode=gometanode, buffer=buffer)
        self.fromimport = fromimport
        self.names = names

class Attribute(PythonNode):
    implements(IAttribute)
    
    def __init__(self, targets=list(), value=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.targets = targets
        self.value = value

class Decorator(PythonNode):
    implements(IDecorator)
    
    def __init__(self, decoratorname=None, gometanode=None, buffer=[]):
        PythonNode.__init__(self, None, gometanode=gometanode, buffer=buffer)
        if decoratorname == None:
            decoratorname = astnode.func.id
        self.decoratorname = decoratorname
        self.args = copy.deepcopy(gometanode.astnode.args)
        self.kwargs = copy.deepcopy(gometanode.astnode.kwargs)

class Function(PythonNode):
    implements(IFunction)
    
    def __init__(self, functionname=None, gometanode=None, buffer=[]):
        PythonNode.__init__(self, name=functionname, gometanode=gometanode, buffer=buffer)
        self.args = list()
        self.kwargs = odict()
        self._decorators = list()
        self.functionname = functionname
        self._args_orgin = list()
        self._kwargs_orgin = odict()

class Class(PythonNode):
    implements(IClass)
    
    def __init__(self, classname=None, gometanode=None, buffer=[]):
        PythonNode.__init__(self, name=classname, gometanode=gometanode, buffer=buffer)
        self.bases = list()
        self._bases_orgin = list()
        self.classname = classname

class Block(PythonNode):
    implements(IBlock)
    
    def __init__(self, text=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.postlf = 1

# -- Node implementations end here --

class NodeMaker(object):

    def __init__(self):
        self.dispatch = {
                'Expr': DocstringNodeMaker,
            #    ProtectedSection,
                'Import' : ImportNodeMaker,
                'ImportFrom' : ImportNodeMaker,
                'Attribute' : AttributeNodeMaker,
                'Call' : DecoratorNodeMaker,
                'FunctionDef' : FunctionNodeMaker,
                'ClassDef' : ClassNodeMaker,
            #    Block,
            }

    def __call__(self, gometanode):
        raise NotImplemented(u'BaseParser does not implement ``__call__``')

    def makesubnode(self, node):
        maker = None
        try:
            maker = self.dispatch[node.astclassname]()
        except KeyError:
            maker = BlockNodeMaker()
            print "using default NodeMaker for %s because there is no node implementation." % (repr(node.astclassname),)
        pythonnode = maker(node)
        if not pythonnode:
            raise BaseException("Creation of %s failed, no python node returned."  % (repr(node.astclassname),))
        return pythonnode

class BlockNodeMaker(NodeMaker):

     def __call__(self, gometanode):
        name = str(gometanode)
        node = PythonNode(\
                name, 
                gometanode=gometanode, 
#                buffer=sourcelines,
                )
        return node

class ModuleNodeMaker(NodeMaker):
    
    def __call__(self, modulename, encoding, startlineno=0, endlineno=None, bufofset=0):
        node = Module(name=modulename, encoding=encoding, startlineno=startlineno, endlineno=endlineno, bufofset=bufofset)
        return node
        
class DocstringNodeMaker(NodeMaker):

    def __call__(self, gometanode=None):
        sourcelines = gometanode.codelines()
        node = Docstring( \
                name = str(gometanode), 
                gometanode = gometanode, 
                )
        return node
        
class ImportNodeMaker(NodeMaker):
    
    def __call__(self, gometanode=None):
        sourcelines = gometanode.codelines()
        names = [i.name for i in gometanode.astnode.names]
        
        if gometanode.astclassname == 'ImportFrom':
            fromimport = gometanode.astnode.module
        else:
            fromimport = None
        node = Import( \
                fromimport=fromimport, 
                names=names, 
                gometanode=gometanode, 
#                buffer=sourcelines,
                )
        return node
        
class AttributeNodeMaker(NodeMaker):            
    
    def __call__(self, gometanode):
        pass
        
class DecoratorNodeMaker(NodeMaker):
    
    def __call__(self, gometanode):
        node = Decorator(\
                decoratorname=gometanode.astnode.func.id,
                gometanode = gometanode)
        return node
        
class FunctionNodeMaker(NodeMaker):
    
    def __call__(self, gometanode):
        sourcelines = gometanode.codelines()
        node = Function(\
                functionname=gometanode.astnode.name, 
                gometanode=gometanode, 
                )
        for child in node.gometanode.children:
            subnode = self.makesubnode(child)
            node[subnode.uuid] = subnode
        return node
        
class ClassNodeMaker(NodeMaker):
    
    def __call__(self, gometanode):
        sourcelines = gometanode.codelines()
        node = Class(\
                classname=gometanode.astnode.name, 
                gometanode=gometanode, 
                )
        for child in gometanode.children:
            subnode = self.makesubnode(child)
            node[subnode.uuid] = subnode
        return node

class BaseParser(object):
    
    def __init__(self, model):
        self.model = model

    def __call__(self):
        sourcepath = self.model.filepath
        sourcefile = open(sourcepath,'r')
        sourcecode = sourcefile.read()
        sourcefile.close()
        
        P=GoParser(sourcecode, sourcepath)
        P()
        self.module = Module(\
                name = sourcepath, 
                encoding = P.encoding, 
                lines = P.lines, 
                startlineno = P.startline, 
                endlineno = P.endline,
                bufoffset = P.offset
                )
        B=NodeMaker()
        for node in P.nodes:
            pythonnode = B.makesubnode(node)
            assert(pythonnode)
            self.module[pythonnode.uuid] = pythonnode
        
