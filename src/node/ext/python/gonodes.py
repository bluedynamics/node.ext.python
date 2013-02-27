# -*- coding: utf-8 -*-
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#

import os
from zope.interface import implements
from plumber import plumber
from odict import odict
from node.base import OrderedNode
from node.parts import (
    Reference,
    Order,
)
from node.utils import LocationIterator
from node.ext.python.interfaces import (
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
    # IAssignment,
    # IExpression,
    #    Incomplete,
)


class PythonNode(OrderedNode):
    __metaclass__ = plumber
    __plumbing__ = Reference, Order

    implements(IPythonNode)

    parserfactory= None
    rendererfactory = None

    def __init__(self,
                 name=None,
                 gopnode=None,
                 buffer=None,
                 bufstart=None,
                 bufend=None,
                 ):
        OrderedNode.__init__(self, name)
        self.gopnode = gopnode
        self.buffer = buffer
        self.bufstart = bufstart
        self.bufend = bufend
        self.bufoff = 0
        self.readlines = None
        self.postlf = 0
        # self.lines = []
        self.nodename = str(gopnode)

    @property
    def startlineno(self):
        return self.bufstart

    @property
    def endlineno(self):
        return self.bufend

    @property
    def indent(self):
        return self.gopnode.indent

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

    def acquire(self, interface=None):
        # @@@ Gogo. maybe remove exists on base node impl
        if interface.providedBy(self):
            return self
        context = self.__parent__
        while context and not interface.providedBy(context):
            context = context.parent
        return context

    def get_type(self):
        return self.__class__.__name__

    # @property
    # def noderepr(self):
    #     try:
    #         # module = self.acquire(IModule)
    #         # offset = module.bufoff
    #         return "<" + self.__class__.__name__ + ' ' + self.nodename + \
    #                ': [%s:%s] - %s>' % (str(self.bufstart + self.bufoff),
    #                                     str(self.bufend + self.bufoff),
    #                                     str(self.indent))
    #     except Exception, e:
    #         # happens if node was created manually
    #         print e
    #         return "<" + self.__class__.__name__ + ' ' + self.nodename + ': [?:?] - %s>' % str(self.indent)

    def __str__(self):
        return "%s<%s [%s:%s]>" % (self.get('indent', 'No indent'),
                                   self.__class__.__name__,
                                   self.get('bufstart', 'No bufstart'),
                                   self.get('bufend', 'No bufend'),)

    def __call__(self):
        return self.rendererfactory(self)()


class _TextMixin(object):

    def __init__(self):
        self.LINES_CHANGED = 0
        self.TEXT_CHANGED = 1
        self.LAST_CHANGE = None
        self._lines = list()
        self._text = list()

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


    text = property(_get_text, _set_text)
    lines = property(_get_lines, _set_lines)


class Block(PythonNode, _TextMixin):
    implements(IBlock)

    def __init__(self, *args, **kwargs):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, *args, **kwargs)

    @property
    def noderepr(self):
        try:
            module = self.acquire(IModule)
            # offset = module.bufoff
            return "<" + self.__class__.__name__ + "(%s)" % self.nodename + \
                   ': [%s:%s] - %s>' % (str(self.bufstart + self.bufoff),
                                        str(self.bufend + self.bufoff),
                                        str(self.indent))
        except Exception, e:
            # happens if node was created manually
            print e
            return "<" + self.__class__.__name__ + ' ' + self.nodename + ': [?:?] - %s>' % str(self.indent)


class Class(PythonNode):
    implements(IClass)

    def __init__(self, *args, **kwargs):
        PythonNode.__init__(self, *args, **kwargs)


class Decorator(PythonNode):
    implements(IDecorator)

    def __init__(self, *args, **kwargs):
        PythonNode.__init__(self, *args, **kwargs)


class ProtectedSection(PythonNode, _TextMixin):
    implements(IProtectedSection)

    def __init__(self, *args, **kwargs):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, *args, **kwargs)
        if args:
            self.sectionname = args[0]


class Function(PythonNode):
    implements(IFunction)

    def __init__(self, *args, **kwargs):
        PythonNode.__init__(self, *args, **kwargs)
        self.functionname = self.gopnode.astnode.name
        # Extract arguments
        self.args = list()
        self.kwargs = odict()
        argslen = len(self.gopnode.astnode.args.args)
        defaultslen = len(self.gopnode.astnode.args.defaults)
        offset = argslen - defaultslen
        for i in xrange(argslen):
            if i < offset:
                # we have a regular argument
                self.args.append(self.gopnode.astnode.args.args[i].id)
            else:
                # we have a default value
                self.kwargs[self.gopnode.astnode.args.args[i].id] = \
                    self.gopnode.get_astvalue(self.gopnode.astnode.args.defaults[i - offset])

    def decorators(self, name=None):
        decorators = [d for d in self.filtereditems(IDecorator)]
        if name is not None:
            decorators = [d for d in decorators if d.decoratorname == name]
        return decorators

    def __str__(self):
        sargs = ''
        sargs += ','.join(self.args)
        kargs = ''
        kargs += ','.join([k + '=' + str(v) for k, v in self.kwargs.items()])
        if sargs and kargs:
            arguments = sargs + ',' + kargs
        else:
            arguments = sargs + kargs
        decs = self.decorators()
        if decs:
            decorators = ' ' + ','.join(['@' + i.decoratorname for i in decs])
        else:
            decorators = ''
        return "<Function %s(%s)%s>" % (self.functionname, arguments, decorators)


class Docstring(PythonNode, _TextMixin):
    implements(IDocstring)

    def __init__(self, text=None, astnode=None, buffer=[]):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, None, astnode, buffer)
    #     self._lines = False
    #     self._text = False
    #     if text is not None:
    #         self.text = text
        self.START_END = u'"""'
    #     if self.get('lines', False) == False:
    #         self.lines = list()
    #     #self.parser = self.parserfactory(self)

    # def _get_lines(self):
    #     if self._lines is not False or self._text is not False:
    #         if self.LAST_CHANGE == self.TEXT_CHANGED:
    #             lines = self.text.split(u'\n')
    #             if len(lines) == 1 and not lines[0]:
    #                 lines = []
    #             self.lines = lines
    #         return self._lines
    #     try:
    #         lines = self.buffer[self.bufstart:self.bufend]
    #     except TypeError, e:
    #         self.lines = list()
    #         return self._lines
    #     if lines[0].find(u"'''") != -1:
    #         self.START_END = u"'''"
    #     lines = [line.strip().strip(u'"""').strip(u"'''") for line in lines]
    #     if len(lines) > 1 and not lines[-1]:
    #         lines = lines[:len(lines) - 1]
    #     return lines


class Import(PythonNode):
    implements(IImport)

    def __init__(self, *args, **kwargs):
        PythonNode.__init__(self, *args, **kwargs)


class Attribute(PythonNode, _TextMixin):
    implements(IAttribute)

    def __init__(self, *args, **kwargs):
        _TextMixin.__init__(self)
        PythonNode.__init__(self, *args, **kwargs)
        if args:
            self.targets = args[0]
            self.value = args[1]

 # class Assignment(PythonNode):
 #     implements(IAssignment)

 #     def __init__(self, *args, **kwargs):
 #         PythonNode.__init__(self, *args, **kwargs)


# class Expression(PythonNode):
#     implements(IExpression)

#     def __init__(self, *args, **kwargs):
#         PythonNode.__init__(self, *args, **kwargs)


class Module(PythonNode):
    implements(IModule)

#    # flag to turn off parsing on __init__. Needed by test.
#    _do_parse = True

    def __init__(self,
                 filepath=None,
                 buffer=None,
                 bufstart=None,
                 bufend=None,
                 encoding=u'utf-8'
                 ):
        PythonNode.__init__(self, filepath, None, buffer=buffer, bufstart=bufstart, bufend=bufend)
        self.filepath = filepath
        self.encoding = encoding
        self.modulename = self.getModuleNameFromFilename()
        self.nodename = self.modulename

        self.readlines = None
        self.postlf = 0
        self.gopnode = None

        self.buffer = buffer
        self.bufstart = bufstart
        self.bufend = bufend

    @property
    def indent(self):
        return 0

    def getModuleNameFromFilename(self):
        return ''.join(os.path.basename(self.filepath).split('.')[:-1])