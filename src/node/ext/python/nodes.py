import os
import ast
from odict import odict
from plumber import plumber
from node.behaviors import (
    Reference,
    Order,
)
from node.utils import LocationIterator
from node.base import OrderedNode
from zope.interface import implementer
from node.ext.directory.interfaces import IDirectory
from node.ext.python.interfaces import (
    Incomplete,
    IPythonNode,
    IModule,
    IDocstring,
    IProtectedSection,
    IImport,
    IAttribute,
    ICallableArguments,
    IDecorator,
    IFunction,
    IClass,
    IBlock,
    IDecorable,
)


@implementer(IPythonNode)
class PythonNode(OrderedNode):
    """A Node for Python code.
    """
    __metaclass__ = plumber
    __plumbing__ = Reference, Order

    parserfactory = None
    rendererfactory = None

    def __init__(self, name, astnode=None, buffer=[]):
        OrderedNode.__init__(self, name)
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
            else:
                startlineno = '?'
            endlineno = self.endlineno
            if endlineno is not None:
                endlineno = str(endlineno + offset)
            else:
                endlineno = '?'
#           startlineno = startlineno is not None and startlineno+offset or '?'
#            endlineno = endlineno is not None and endlineno+offset or '?'
            return str(self.__class__) + \
                ': [%s:%s] - %s' % (str(startlineno),
                                    str(endlineno),
                                    str(self.nodelevel))
        except Exception, e:
            # happens if node was created manually
            return str(self.__class__) + ': [?:?] - %s' % str(self.nodelevel)


@implementer(IModule)
class Module(PythonNode):
    """A Python Module Node: abstract representation of a python module.
    """
    # flag to turn off parsing on __init__. Needed by test.
    _do_parse = True

    def __init__(self, name=None):
        PythonNode.__init__(self, name)
        self.encoding = u'utf-8'
        self.astnode = None
        self.bufstart = None
        self.bufend = None
        self.bufoffset = 0
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

    def _get_buffer(self):
        return self._buffer

    def _set_buffer(self, val):
        # set by parser directly. XXX
        pass

    buffer = property(_get_buffer, _set_buffer)

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


@implementer(IDocstring)
class Docstring(PythonNode, _TextMixin):
    """A Node for a docstring.
    """

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
                and \
           (buf[n].strip().endswith(u'"""') or
                buf[n].strip().endswith(u"'''")) \
                and not len(buf[n].strip()) == 3:
            return n + 1
        while n > 0:
            n -= 1
            if buf[n].find(u'"""') != -1 or buf[n].find(u"'''") != -1:
                return n + 1

    def _get_bufstart(self):
        return self.startlineno - 1

    def _set_bufstart(self, lineno):
        pass

    bufstart = property(_get_bufstart, _set_bufstart)


@implementer(IProtectedSection)
class ProtectedSection(PythonNode, _TextMixin):
    """A Node for a protected section:
    Some code that will not be overwritten.
    """

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


@implementer(IBlock)
class Block(PythonNode, _TextMixin):
    """A Node for a block of code.
    """

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


@implementer(IImport)
class Import(PythonNode):
    """A Node for an import statement.
    """

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

    def _set_bufend(self, lineno):
        pass

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


@implementer(ICallableArguments)
class CallableArguments(object):
    """A Node for callable arguments.
    """

    UNSET = object()

    def __init__(self):
        self.args = list()
        self.kwargs = odict()
        self.s_args = None
        self.s_kwargs = None

    def extract_arguments(self):
        if self.s_args:
            _args = self.s_args.split(',')
            _args = [_arg.strip() for _arg in _args]
        else:
            _args = self.args
        if self.s_kwargs:
            # use ast to parse the kwarg definition since
            # a def like arge=[1,2,3],args=33 would break with just splitting
            # by ','
            # make call out of it because then ast gives the comma the
            # smallest prio

            fcalls = 'dummy(%s)' % self.s_kwargs.strip()
            call = ast.parse(fcalls).body[0].value
            keywords = call.keywords
            _kwargs = odict()

            for i, kw in zip(range(len(keywords)), keywords):
                key = kw.arg
                offset = kw.value.col_offset
                # not the last rec
                if i < len(keywords) - 1:
                    nextoffset = keywords[i + 1].value.col_offset
                    val = fcalls[offset:nextoffset]
                    # step back to the last comma
                    val = val[:val.rfind(',')]
                # for the last one we chop off the trailing ')'
                else:
                    val = fcalls[offset: - 1]
                _kwargs[key] = val
        else:
            _kwargs = self.kwargs
        return _args, _kwargs

    def arguments_equal(self, other):
        a_args, a_kwargs = self.extract_arguments()
        b_args, b_kwargs = other.extract_arguments()
        if len(a_args) != len(b_args) or len(a_kwargs) != len(b_kwargs):
            return False
        for arg in a_args:
            if not arg in b_args:
                return False
        for key, value in a_kwargs.items():
            b_val = b_kwargs.get(key, self.UNSET)
            if b_val is self.UNSET or b_val != value:
                return False
        return True


@implementer(IDecorable)
class Decorable:
    """mixin for decorables (Function,Attribute,Class.
    """

    def __init__(self):
        self._decorators = list()

    def decorators(self, name=None):
        decorators = [d for d in self.filtereditems(IDecorator)]
        if name is not None:
            decorators = [d for d in decorators if d.decoratorname == name]
        return decorators

    def initdecorators(self):
        for decorator in self._decorators:
            self[decorator.uuid] = decorator


@implementer(IAttribute)
class Attribute(PythonNode, CallableArguments):
    """A Node for attributes.
    """

    def __init__(self, targets=list(), value=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        CallableArguments.__init__(self)
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
        if self.astnode is None:
            return True
        if self.value != self._value_orgin:
            return True
        if self.targets != self._targets_orgin:
            return True
        if self.s_args or self.s_kwargs:
            return True
        if self.args != self._args_orgin \
                or self.kwargs != self._kwargs_orgin:
            return True
        return False

    def __repr__(self):
        return '<Attribute object %s at %s>' % (self.targets, self.name)


@implementer(IDecorator)
class Decorator(PythonNode, CallableArguments):
    """A Node for a decorator.
    """

    def __init__(self, decoratorname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        CallableArguments.__init__(self)
        self.decoratorname = decoratorname
        self._args_orgin = list()
        self._kwargs_orgin = odict()
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()

    def equals(self, other):
        if self.decoratorname == other.decoratorname \
                and self.arguments_equal(other):
            return True
        return False

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

    def _set_bufend(self, lineno):
        pass

    bufend = property(_get_bufend, _set_bufend)

    @property
    def endlineno(self):
        return self.bufend

    @property
    def _changed(self):
        if self.astnode is None:
            return True
        if self.decoratorname != self._decoratorname_orgin:
            return True
        if self.s_args or self.s_kwargs:
            return True
        if self.args != self._args_orgin \
                or self.kwargs != self._kwargs_orgin:
            return True
        return False


@implementer(IFunction)
class Function(PythonNode, CallableArguments, Decorable):
    """A Node for a function.
    """

    def __init__(self, functionname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        CallableArguments.__init__(self)
        Decorable.__init__(self)
        self.functionname = functionname
        self._args_orgin = list()
        self._kwargs_orgin = odict()
        self.parser = self.parserfactory(self)
        if astnode is not None:
            self.parser()

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
        if self.astnode is None:
            return True
        if self.s_args or self.s_kwargs:
            return True
        if self.args != self._args_orgin \
                or self.kwargs != self._kwargs_orgin:
            return True
        return False


@implementer(IClass)
class Class(PythonNode, Decorable):
    """A Node for a python class.
    """

    def __init__(self, classname=None, astnode=None, buffer=[]):
        PythonNode.__init__(self, None, astnode, buffer)
        Decorable.__init__(self)
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

    def __repr__(self):
        return '<Class object %s>' % self.classname
