# Copyright BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2

import os
from odict import odict
from zodict.node import Node
from zope.interface import implements
from zope.location import LocationIterator
from node.ext.directory.interfaces import IDirectory
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

class PythonNode(Node):
    
    implements(IPythonNode)
    
    parserfactory = None
    rendererfactory = None
    
    def __init__(self, name, astnode=None, buffer=[]):
        Node.__init__(self, name)
        self.astnode = astnode
        self.buffer = buffer
        self.bufstart = None
        self.bufend = None
        self.readlines = None
        self.postlf = 0
        if astnode is not None and hasattr(self.astnode, 'lineno'):
            self.bufstart = self.astnode.lineno - 1
            self.bufend = self.astnode.lineno
    
    def __call__(self):
        return self.rendererfactory(self)()
    
    @property
    def startlineno(self):
        if self.bufstart is None:
            return None
        return self.bufstart + 1
    
    @property
    def endlineno(self):
        return self.bufend
    
    @property
    def indent(self):
        if hasattr(self, 'defendlineno'):
            end = self.defendlineno
        else:
            end = self.endlineno
        return self.parser._findindent(self.buffer[self.bufstart:end])
    
    @property
    def nodelevel(self):
        level = -1
        for parent in LocationIterator(self):
            if IModule.providedBy(parent):
                break
            level += 1
        return level
    
    def docstrings(self):
        return [d for d in self.filtereditems(IDocstring)]
    
    def blocks(self):
        return [b for b in self.filtereditems(IBlock)]
    
    def imports(self):
        return [i for i in self.filtereditems(IImport)]
    
    def protectedsections(self, name=None):
        psecs = [p for p in self.filtereditems(IProtectedSection)]
        if name is not None:
            psecs = [p for p in psecs if p.sectionname == name]
        return psecs
    
    def classes(self, name=None):
        classes = [c for c in self.filtereditems(IClass)]
        if name is not None:
            classes = [c for c in classes if c.classname == name]
        return classes
    
    def functions(self, name=None):
        functions = [f for f in self.filtereditems(IFunction)]
        if name is not None:
            functions = [f for f in functions if f.functionname == name]
        return functions
    
    def attributes(self, name=None):
        attrs = [a for a in self.filtereditems(IAttribute)]
        if name is not None:
            attrs = [a for a in attrs if name in a.targets]
        return attrs
    
    @property
    def noderepr(self):
        try:
            startlineno = self.startlineno
            startlineno = startlineno is not None and startlineno or '?'
            endlineno = self.endlineno
            endlineno = endlineno is not None and endlineno or '?'
            return str(self.__class__) + \
                   ': [%s:%s] - %s' % (str(startlineno),
                                       str(endlineno),
                                       str(self.nodelevel))
        except Exception, e:
            # happens if node was created manually
            return str(self.__class__) + ': [?:?] - %s' % str(self.nodelevel)
    
class Module(PythonNode):
    
    implements(IModule)
    
    # flag to turn off parsing on __init__. Needed by test.
    _do_parse = True
    
    def __init__(self, name=None):
        Node.__init__(self, name)
        self.encoding = u'utf-8'
        self.astnode = None
        self.bufstart = None
        self.bufend = None
        self.readlines = None
        self.parser = self.parserfactory(self)
        try:
            self.filepath
            self.parser()
        except Incomplete, e:
            pass
    
    @property
    def modulename(self):
        if self.__name__ is None:
            return None
        return unicode(os.path.splitext(os.path.basename(self.__name__))[0])
    
    @property
    def filepath(self):
        path = self.__name__
        if path is None:
            raise Incomplete, u"Could not verify file path."
        if path.find(os.path.sep) != -1:
            return path
        if self.__parent__ is None \
          or not IDirectory.providedBy(self.__parent__):
            raise Incomplete, u"Could not verify file path."
        return os.path.join(*self.path)
    
    @property
    def buffer(self):
        return self._buffer
    
    @property
    def indent(self):
        return 0

class _TextMixin(object):
    
    def __init__(self):
        self.LINES_CHANGED = 0
        self.TEXT_CHANGED = 1
        self.LAST_CHANGE = None
    
    def _set_lines(self, lines):
        self._lines = lines
        self.LAST_CHANGE = self.LINES_CHANGED
    
    def _get_text(self):
        if self._text is not False:
            if self.LAST_CHANGE == self.TEXT_CHANGED:
                return self._text
        self.text = u'\n'.join(self.lines)
        return self._text
    
    def _set_text(self, text):
        self._text = text.strip('\n')
        self.LAST_CHANGE = self.TEXT_CHANGED
    
    text = property(_get_text, _set_text)

class Docstring(PythonNode, _TextMixin):
    
    implements(IDocstring)
    
    def __init__(self, text=None, astnode=None, buffer=[]):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, None, astnode, buffer)
        self._lines = False
        self._text = False
        if text is not None:
            self.text = text
        self.START_END = u'"""'
        self.parser = self.parserfactory(self)
        
    def _get_lines(self):
        if self._lines is not False or self._text is not False:
            if self.LAST_CHANGE == self.TEXT_CHANGED:
                lines = self.text.split(u'\n')
                if len(lines) == 1 and not lines[0]:
                    lines = []
                self.lines = lines
            return self._lines
        try:
            lines = self.buffer[self.bufstart:self.bufend]
        except TypeError, e:
            self.lines = list()
            return self._lines
        if lines[0].find(u"'''") != -1:
            self.START_END = u"'''"
        lines = [line.strip().strip(u'"""').strip(u"'''") for line in lines]
        if len(lines) > 1 and not lines[-1]:
            lines = lines[:len(lines) - 1]
        return lines
    
    lines = property(_get_lines, _TextMixin._set_lines)
    
    @property
    def startlineno(self):
        end = self.bufend
        if end is None:
            return
        buf = self.buffer
        n = end - 1
        if (buf[n].find(u'"""') != -1 or buf[n].find(u"'''") != -1) \
          and (buf[n].strip().endswith(u'"""') \
          or buf[n].strip().endswith(u"'''")) \
          and not len(buf[n].strip()) == 3:
            return n + 1
        while n > 0:
            n -= 1
            if buf[n].find(u'"""') != -1 \
              or buf[n].find(u"'''") != -1:
                return n + 1
    
    def _get_bufstart(self):
        return self.startlineno - 1
    
    def _set_bufstart(self, lineno): pass
    
    bufstart = property(_get_bufstart, _set_bufstart)
        
class ProtectedSection(PythonNode, _TextMixin):
    
    implements(IProtectedSection)

    def __init__(self, sectionname=None, buffer=[]):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, sectionname, None, buffer)
        self.sectionname = sectionname
        self.postlf = 1
        self._lines = False
        self._text = False
        self.parser = self.parserfactory(self)
    
    def _get_lines(self):
        if self._lines is not False or self._text is not False:
            if self.LAST_CHANGE == self.TEXT_CHANGED:
                lines = self.text.split(u'\n')
                if len(lines) == 1 and not lines[0]:
                    lines = []
                self.lines = lines
            return self._lines
        try:
            lines = self.buffer[self.bufstart:self.bufend]
            if self.bufstart + 1 >= self.bufend - 1:
                self.lines = list()
                return self._lines
        except TypeError, e:
            self.lines = list()
            return self._lines
        lines = self.buffer[self.bufstart + 1:self.bufend - 1]
        self.lines = [self.parser._cutline(line) for line in lines]
        return self._lines
    
    lines = property(_get_lines, _TextMixin._set_lines)

class Block(PythonNode, _TextMixin):
    
    implements(IBlock)
    
    def __init__(self, text=None, buffer=[]):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, None, None, buffer)
        self.postlf = 1
        self._lines = False
        self._text = False
        if text is not None:
            self.text = text
        self.parser = self.parserfactory(self)
    
    def _get_lines(self):
        if self._lines is not False or self._text is not False:
            if self.LAST_CHANGE == self.TEXT_CHANGED:
                lines = self.text.split(u'\n')
                if len(lines) == 1 and not lines[0]:
                    lines = []
                self.lines = lines
            return self._lines
        start = self.bufstart
        end = self.bufend
        try:
            while not self.buffer[start].strip():
                start += 1
            while not self.buffer[end - 1].strip():
                end -= 1
            lines = self.buffer[start:end]
            self.lines = [self.parser._cutline(l) for l in lines]
        except TypeError, e:
            self.lines = list()
        return self._lines
    
    lines = property(_get_lines, _TextMixin._set_lines)
    
    @property
    def startlineno(self):
        start = self.bufstart
        while not self.buffer[start].strip():
            start += 1
        return start + 1
    
    @property
    def endlineno(self):
        end = self.bufend
        while not self.buffer[end - 1].strip():
            end -= 1
        return end

class Import(PythonNode):
    
    implements(IImport)
    
    def __init__(self, fromimport=None, names=[], astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.fromimport = fromimport
        self.names = names
        self._fromimport_orgin = None
        self._names_orgin = list()
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()
    
    def _get_bufend(self):
        bufno = self.bufstart
        while not self.parser._definitionends(bufno):
            bufno += 1
        return bufno + 1
    
    def _set_bufend(self, lineno): pass
    
    bufend = property(_get_bufend, _set_bufend)
    
    @property
    def endlineno(self):
        return self.bufend
    
    @property
    def _changed(self):
        if self.astnode is None:
            return True
        if self.names != self._names_orgin \
          or self.fromimport != self._fromimport_orgin:
            return True
        return False

class Attribute(PythonNode):
    
    implements(IAttribute)
    
    def __init__(self, targets=list(), value=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.targets = targets
        self.value = value
        self.postlf = 0
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()
    
    @property
    def endlineno(self):
        return self.bufend
    
    @property
    def _changed(self):
        if self.targets != self._targets_orgin:
            return True
        return False

class Decorator(PythonNode):
    
    implements(IDecorator)
    
    def __init__(self, decoratorname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.args = list()
        self.kwargs = odict()
        self.s_args = None
        self.s_kwargs = None
        self.decoratorname = decoratorname
        self._args_orgin = list()
        self._kwargs_orgin = odict()
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()
    
    @property
    def nodelevel(self):
        level = -1
        for parent in LocationIterator(self):
            if IModule.providedBy(parent):
                break
            level += 1
        if level == 0:
            return 0
        return level - 1
    
    def _get_bufend(self):
        bufno = self.bufstart
        while not self.parser._definitionends(bufno):
            bufno += 1
        return bufno + 1
    
    def _set_bufend(self, lineno): pass
    
    bufend = property(_get_bufend, _set_bufend)
    
    @property
    def endlineno(self):
        return self.bufend
    
    @property
    def _changed(self):
        if self.astnode is None:
            return True
        if self.s_args or self.s_kwargs:
            return True
        if self.args != self._args_orgin \
          or self.kwargs != self._kwargs_orgin:
            return True
        return False

class Function(PythonNode):
    
    implements(IFunction)
    
    def __init__(self, functionname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.args = list()
        self.kwargs = odict()
        self._decorators = list()
        self.functionname = functionname
        self._args_orgin = list()
        self._kwargs_orgin = odict()
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()
    
    def decorators(self, name=None):
        decorators = [d for d in self.filtereditems(IDecorator)]
        if name is not None:
            decorators = [d for d in decorators if d.decoratorname == name]
        return decorators
    
    def initdecorators(self):
        for decorator in self._decorators:
            self[decorator.uuid] = decorator
    
    def _get_bufstart(self):
        p = self._bufstart
        while True:
            if p >= len(self.buffer):
                raise RuntimeError, u"Could not find function start lineno."
            if self.buffer[p].strip().startswith('def '):
                return p
            p += 1
    
    def _set_bufstart(self, val):
        self._bufstart = val
    
    bufstart = property(_get_bufstart, _set_bufstart)
    
    @property
    def defendlineno(self):
        bufno = self.bufstart
        while not self.parser._definitionends(bufno):
            bufno += 1
        return bufno + 1
    
    @property
    def _changed(self):
        if self.args != self._args_orgin \
          or self.kwargs != self._kwargs_orgin:
            return True
        return False

class Class(PythonNode):
    
    implements(IClass)
    
    def __init__(self, classname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        self.bases = list()
        self._bases_orgin = list()
        self.classname = classname
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()
    
    @property
    def defendlineno(self):
        bufno = self.bufstart
        while not self.parser._definitionends(bufno):
            bufno += 1
        return bufno + 1
    
    def decorators(self, name=None):
        decorators = [d for d in self.filtereditems(IDecorator)]
        if name is not None:
            decorators = [d for d in decorators if d.decoratorname == name]
        return decorators
    
    @property
    def _changed(self):
        if self.bases != self._bases_orgin:
            return True
        return False