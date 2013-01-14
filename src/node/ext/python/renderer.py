import os
from odict import odict
from zope.component.interfaces import ComponentLookupError
from agx.core import token
from interfaces import (
    CODESECTION_STARTTOKEN,
    CODESECTION_ENDTOKEN,
    Incomplete,
    Call,
    IDecorator,
    IClass,
    IDocstring,
    IFunction,
    IProtectedSection,
    IBlock,
)


class BaseRenderer(object):

    def __init__(self, model):
        self.model = model

    def __call__(self):
        raise NotImplemented(u'BaseRenderer does not implement ``__call__``')

    def _calcpostlf(self, values):
        valuecount = len(values)
        sametype = False
        for i in range(valuecount):
            value = values[i]
            if i + 1 == valuecount:
                value.postlf = 0
                continue
            if i + 1 < valuecount:
                sametype = value.__class__ is values[i + 1].__class__
            if not sametype:
                if IDocstring.providedBy(values[i + 1]):
                    value.postlf = 0
                    continue
                if IDocstring.providedBy(value):
                    if IFunction.providedBy(value.__parent__):
                        value.postlf = 0
                    else:
                        value.postlf = 1
                    continue
                value.postlf = 1
                continue
            if IClass.providedBy(value) \
              or IFunction.providedBy(value):
                value.postlf = 1
                continue
            value.postlf = 0


class ModuleRenderer(BaseRenderer):
    CODING = u'# -*- coding: %s -*-\n'
    _write_file = True

    def __call__(self):
        enc = self.CODING % self.model.encoding
        values = self.model.values()
        self._calcpostlf(values)
        valuecount = len(values)
        rendered = [enc]
        for i in range(valuecount):
            rendered.append(values[i]())
        rendered = u''.join(rendered).strip('\n')
        if not self._write_file:
            return rendered
        # XXX: we need to check here if module has IDirectory instance as
        #      parent
        with open(self.model.filepath, 'w') as out:
            out.write(rendered)


class DocstringRenderer(BaseRenderer):

    def __call__(self):
        line = ''
        lines = self.model.lines
        if len(lines) > 0:
            line = lines[0]
        level = self.model.nodelevel
        indent = level * 4 * u' '
        ret = [u'%s%s%s' % (indent, self.model.START_END, line)]
        if len(lines) > 1:
            for line in lines[1:]:
                ret.append(u'%s%s' % (indent, line))
        ret.append(u'%s%s\n' % (indent, self.model.START_END))
        ret += [u'' for i in range(self.model.postlf)]
        return u'\n'.join(ret)


class ProtectedSectionRenderer(BaseRenderer):

    def __call__(self):
        if self.model.sectionname is None:
            raise Incomplete, u"Incomplete protected section definition."
        if self.model.bufstart is not None and self.model.bufend is not None:
            secbegin = self.model.buffer[self.model.bufstart].strip()
            secend = self.model.buffer[self.model.bufend - 1].strip()
        else:
            secbegin = u'%s%s' % (CODESECTION_STARTTOKEN,
                                  self.model.sectionname)
            secend = u'%s%s' % (CODESECTION_ENDTOKEN,
                                self.model.sectionname)
        ret = list()
        indent = self.model.nodelevel * 4 * u' '
        lines = [secbegin] + self.model.lines + [secend]
        for line in lines:
            ret.append(indent + line)
        ret += [u'' for i in range(self.model.postlf + 1)]
        return u'\n'.join(ret)


class BlockRenderer(BaseRenderer):

    def __call__(self):
        indent = self.model.nodelevel * 4 * u' '
        lines = [u'%s%s' % (indent, l) for l in self.model.lines]
        if lines:
            lines += [u'' for i in range(self.model.postlf + 1)]
            return u'\n'.join(lines)
        return u''


class ImportRenderer(BaseRenderer):

    def __call__(self):
        if not self.model.names:
            raise Incomplete, u"Incomplete import definition."
        indent = self.model.nodelevel * 4 * u' '
        postlf = u''
        for i in range(self.model.postlf):
            postlf = '\n%s' % postlf
        if not self.model._changed:
            lines = self.model.buffer[self.model.bufstart:self.model.bufend]
            lines = [self.model.parser._cutline(l) for l in lines]
            lines = [u'%s%s' % (indent, l) for l in lines]
            return u'%s\n%s' % (u'\n'.join(lines), postlf)
        imports = list()
        for name in self.model.names:
            if not name[1]:
                imports.append(name[0])
            else:
                imports.append(u'%s as %s' % (name[0], name[1]))
        if self.model.fromimport:
            importline = u'from %s import ' % self.model.fromimport
        else:
            importline = u'import '
        if len(imports) == 1:
            return u'%s%s%s\n%s' % (indent, importline, imports[0], postlf)
        else:
            if self.model.fromimport:
                imports = [u'%s    %s,' % (indent, i) for i in imports]
                lines = ['%s(' % importline] + imports + [')\n%s' % postlf]
            else:
                indent = len(importline) * ' '
                imports = [u'%s%s, \\' % (indent, i) for i in imports]
                imports[0] = imports[0].strip()
                imports[-1] = imports[-1][:imports[-1].rfind(',')]
                line = '%s%s' % (importline, imports[0])
                lines = [line] + imports[1:] + ['%s' % postlf]
            return '\n'.join(lines)


class ArgumentRenderer(object):
    LIMIT = 80

    def __init__(self, model=None):
        self.model = model
        self._startlen_exeeds = False
        self._arglines = None
        self._startlen = None
        self._defaultlen = None

    def render_arg(self, arg):
        if isinstance(arg, Call):
            return self.resolve_call(arg)
        return unicode(arg) # XXX encoding

    def render_kwarg(self, kw, arg):
        if isinstance(arg, Call):
            return u'%s=%s' % (kw, self.resolve_call(arg))
        if kw.startswith('**'):
            return unicode(kw)
        return u'%s=%s' % (kw, unicode(arg)) # XXX encoding

    def resolve_call(self, call):
        ret = '%s(' % call['name']
        args = [self.render_arg(a) for a in call['args']]
        kwargs = [self.render_kwarg(kw, a) for kw, a in call['kwargs'].items()]
        return '%s%s)' % (ret, ', '.join(args + kwargs))

    def render_arguments(self, indent, baselen, args=[], kwargs=odict()):
        self._arglines = list()
        arguments = list()
        for arg in args:
            arguments.append(self.render_arg(arg))
        for kw, arg in kwargs.items():
            arguments.append(self.render_kwarg(kw, arg))
        limit = self.LIMIT - indent * 4
        self._startlen = limit - baselen
        self._defaultlen = limit - 10
        if self._startlen > self._defaultlen:
            self._defaultlen = self._startlen
        if self._startlen < 0:
            self._startlen = 0
        if self._defaultlen < 0:
            self._defaultlen = 30
        self._startlen_exeeds = False
        for arg in arguments:
            if len(arg) >= self._startlen:
                self._startlen_exeeds = True
                break
        self._resolve_arglines(arguments, indent)
        if not self._arglines:
            return u''
        return u',\n'.join(self._arglines)

    def _resolve_arglines(self, arguments, indent, from_inner=False):
        if not from_inner:
            reflen = self._startlen
        elif self._startlen_exeeds:
            reflen = self._defaultlen
        else:
            reflen = self._startlen
        limit = self.LIMIT - indent * 4
        indentstr = (limit - reflen) * ' '
        line = u''
        for i in range(len(arguments)):
            if not from_inner:
                # case first line, first arg
                if i == 0 and len(arguments[i]) > self._startlen:
                    self._arglines.append(u'\n')
                    self._resolve_arglines(arguments, indent, True)
                    return
            else:
                # case continuation line, first arg
                if i == 0 and len(arguments[i]) > reflen:
                    self._arglines.append('%s%s' % (indentstr, arguments[i]))
                    self._resolve_arglines(arguments[1:], indent, True)
                    return
            if line:
                newline = u'%s, %s' % (line, arguments[i])
            else:
                newline = arguments[i]
            if len(newline) > reflen:
                if from_inner:
                    line = u'%s%s' % (indentstr, line)
                self._arglines.append(line)
                self._resolve_arglines(arguments[i:], indent, True)
                return
            line = newline
        if line:
            if from_inner:
                line = u'%s%s' % (indentstr, line)
            self._arglines.append(line)


class AttributeRenderer(BaseRenderer, ArgumentRenderer):

    def __init__(self, model):
        ArgumentRenderer.__init__(self, model)

    def __call__(self):
        if not self.model.targets or self.model.value is None:
            raise Incomplete, u"Incomplete attribute definition."
        level = self.model.nodelevel
        indent = level * 4 * u' '
        if not self.model._changed:
            lines = self.model.buffer[self.model.bufstart:self.model.bufend]
            lines = [self.model.parser._cutline(l) for l in lines]
            lines = [u'%s%s' % (indent, l) for l in lines]
            lines += [u'' for i in range(self.model.postlf + 1)]
            return '\n'.join(lines)
        d_args, d_kwargs = self.model.extract_arguments()
        if not d_args and not d_kwargs:
            lines = self.model.value.split(u'\n')
            lines[0] = u'%s%s = %s' % (indent, ', '.join(self.model.targets),
                                       lines[0])
            if len(lines) > 1:
                for i in range(len(lines[1:])):
                    lines[i + 1] = u'%s%s' % (indent, lines[i + 1])
            lines += [u'' for i in range(self.model.postlf + 1)]
            return '\n'.join(lines)
        targets = ', '.join(self.model.targets)
        value = self.model.value
        baselen = len(targets) + len(value) + 8
        rendered_args = self.render_arguments(level, baselen, d_args, d_kwargs)
        post = '\n' * self.model.postlf
        ret = u'%s%s = %s(%s)\n%s' % (
            indent, targets, value, rendered_args, post)
        return ret


class DecoratorRenderer(BaseRenderer, ArgumentRenderer):

    def __init__(self, model):
        ArgumentRenderer.__init__(self, model)

    def __call__(self):
        if self.model.decoratorname is None:
            raise Incomplete, u"Incomplete decorator definition."
        indent = self.model.nodelevel * 4 * u' '
        if not self.model._changed:
            lines = self.model.buffer[self.model.bufstart:self.model.bufend]
            lines = [self.model.parser._cutline(l) for l in lines]
            lines = [u'%s%s' % (indent, l) for l in lines]
            return u'%s\n' % u'\n'.join(lines)
        name = self.model.decoratorname
        level = self.model.nodelevel
        d_args, d_kwargs = self.model.extract_arguments()
        if d_args or d_kwargs.keys():
            rendered_args = self.render_arguments(level, len(name) + 2,
                                                  d_args, d_kwargs)
            return u'%s@%s(%s)\n' % (indent, name, rendered_args)
        return u'%s@%s\n' % (indent, name)


class FunctionRenderer(BaseRenderer, ArgumentRenderer):

    def __init__(self, model):
        ArgumentRenderer.__init__(self, model)

    def __call__(self):
        if self.model.functionname is None:
            raise Incomplete(u"Incomplete function definition.")
        showNotImplemented = True
        ret = list()
        for decorator in self.model.filtereditems(IDecorator):
            ret.append(decorator())
        name = self.model.functionname
        level = self.model.nodelevel
        args, kwargs = self.model.extract_arguments()
        indent = level * 4 * u' '
        base_str = u'def %s(' % name
        rfunc = u'%s%s' % (indent, base_str)
        parent = self.model.__parent__
        # XXX: to be tested, if the deactivation of the next 2 lines doesnt
        # break ->
        # if not IClass.providedBy(parent) and u'self' in args:
        #     args = args[1:]
        if IClass.providedBy(parent):
            # add self to methods, but only if the class is not an interface
            try:
                isInterface = token(str(parent.uuid),
                                    False, isInterface=False).isInterface
            except ComponentLookupError:
                isInterface = False
            if not isInterface  and not u'self' in args:
                args = [u'self'] + args
            else:
                # interface methods are empty on purpose
                showNotImplemented = False
        rargs = self.render_arguments(level, len(name) + 5, args, kwargs)
        rfunc = u'%s%s):\n' % (rfunc, rargs)
        ret.append(rfunc)
        values = [val for val in self.model.values() \
                  if not IDecorator.providedBy(val)]
        for child in values:
            child.postlf = 0
            ret.append(child())
        if not values:
            if showNotImplemented:
                ret.append(u'%s    raise NotImplementedError("stub generated by AGX.")\n' % indent)
            else:
                ret.append(u'%s    pass\n' % indent)
        ret += [u'\n' for i in range(self.model.postlf)]
        return u''.join(ret)


class ClassRenderer(BaseRenderer, ArgumentRenderer):

    def __call__(self):
        if self.model.classname is None:
            raise Incomplete(u"Incomplete class definition.")
        ret = list()
        for decorator in self.model.filtereditems(IDecorator):
            ret.append(decorator())
        name = self.model.classname
        level = self.model.nodelevel
        bases = self.model.bases
        indent = level * 4 * u' '
        base_str = u'class %s(' % name
        rclass = u'%s%s' % (indent, base_str)
        if not bases:
            bases = ['object']
        if len(bases) > 1 and 'object' in bases:
            bases.remove('object')
        rargs = self.render_arguments(level, len(name) + 7, bases)
        rclass = u'%s%s):\n' % (rclass, rargs)
        ret.append(rclass)
        values = [val for val in self.model.values() \
                  if not IDecorator.providedBy(val)]
        # case ``pass`` was parsed for class body
        if len(values) == 1 \
          and IBlock.providedBy(values[0]) \
          and values[0].text == u'pass':
            values = list()
        self._calcpostlf(values)
        if not values:
            ret.append(u'%s    pass\n' % indent)
        valuecount = len(values)
        for i in range(valuecount):
            if i == 0 and not IDocstring.providedBy(values[i]):
                ret.append('\n')
            ret.append(values[i]())
        ret += [u'\n' for i in range(self.model.postlf)]
        return u''.join(ret)
