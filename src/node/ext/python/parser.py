import os
import _ast
import ast
import types
import copy
import exceptions
from odict import odict
from zope.component import provideHandler
from node.ext.directory.interfaces import IFileAddedEvent
from node.ext.python.interfaces import (
    CODESECTION_STARTTOKEN,
    CODESECTION_ENDTOKEN,
    Call,
    IModule,
    IFunction,
    IDocstring,
    IImport,
    IAttribute,
    IDecorator,
)
from node.ext.python.nodes import (
    Module,
    Docstring,
    ProtectedSection,
    Import,
    Attribute,
    Decorator,
    Function,
    Class,
    Block,
)


CODESECTION_STARTTOKEN = '##code-section '
CODESECTION_ENDTOKEN = '##/code-section '


POSITION_INSERT = 0
POSITION_AFTER = 1
POSITION_BEFORE = -1


class BaseParser(object):

    def __init__(self, model):
        self.model = model

    def __call__(self):
        raise NotImplemented(u'BaseParser does not implement ``__call__``')

    def _createastchild(self, astnode):
        if hasattr(astnode, 'lineno'):
            if astnode.lineno - 1 in self.model.readlines:
                return
        if isinstance(astnode, _ast.Import) \
          or isinstance(astnode, _ast.ImportFrom):
            import_ = Import(None, [], astnode, self.model.buffer)
            import_.readlines = self.model.readlines
            self.model[str(import_.uuid)] = import_
        elif isinstance(astnode, _ast.FunctionDef):
            function = Function(None, astnode, self.model.buffer)
            function.readlines = self.model.readlines
            self.model[str(function.uuid)] = function
            for childastnode in astnode.body:
                function.parser._createastchild(childastnode)
            function.initdecorators()
        elif isinstance(astnode, _ast.ClassDef):
            class_ = Class(None, astnode, self.model.buffer)
            class_.readlines = self.model.readlines
            self.model[str(class_.uuid)] = class_
            for childastnode in astnode.body:
                class_.parser._createastchild(childastnode)
            class_.initdecorators()
        elif isinstance(astnode, _ast.Expr) \
          and isinstance(astnode.value, _ast.Str):
            docstring = Docstring(None, astnode, self.model.buffer)
            docstring.readlines = self.model.readlines
            self.model[str(docstring.uuid)] = docstring
        elif isinstance(astnode, _ast.Assign):
            if not IFunction.providedBy(self.model):
                attribute = Attribute([], None, astnode, self.model.buffer)
                attribute.readlines = self.model.readlines
                self.model[str(attribute.uuid)] = attribute

    def _marklines(self, *args):
        for arg in args:
            if not arg in self.model.readlines:
                self.model.readlines.append(arg)

    def _findbodyend(self, node):
        if not hasattr(node, '_fields'):
            return
        for fieldname in node._fields:
            fields = getattr(node, fieldname)
            if type(fields) is not types.ListType:
                fields = [fields]
            for field in fields:
                if hasattr(field, 'lineno'):
                    if field.lineno > self.model.bufend:
                        self.model.bufend = field.lineno
                self._findbodyend(field)

    def _checkbodyendsmultilined(self):
        pointer = self.model.bufend
        buflen = len(self.model.buffer)
        source = ''
        while True:
            if buflen - 1 <= pointer:
                break
            line = self.model.buffer[pointer].strip()
            source = '%s\n%s' % (source, line)
            try:
                compile(source, '<string>', 'exec')
                break
            except SyntaxError, e:
                pointer += 1
        self.model.bufend = pointer

    def _checkbodyendsprotected(self):
        pointer = self.model.bufend
        if pointer < len(self.model.buffer) - 1:
            next = self.model.buffer[pointer].strip()
            if next.startswith(CODESECTION_ENDTOKEN):
                self.model.bufend += 1

    def _findnodeposition(self, startlineno, endlineno, indent):
        values = [v for v in self.model.values() \
                  if not IDecorator.providedBy(v)]
        if not values:
            return self.model, POSITION_INSERT
        last = None
        for child in values:
            # inrange case
            if child.startlineno <= startlineno \
               and child.endlineno >= endlineno:
                return child.parser._findnodeposition(startlineno,
                                                      endlineno,
                                                      indent)
            # before case
            if  endlineno < child.startlineno:
                return child, POSITION_BEFORE
            last = child
        # after case - indent check
        if last.indent == indent:
            return last, POSITION_AFTER
        return self.model, POSITION_AFTER

    def _findindent(self, lines):
        indent = None
        for line in lines:
            if not line.strip():
                continue
            curindent = 0
            for char in line:
                if char != u' ':
                    break
                curindent += 1
            if indent is None or curindent < indent:
                indent = curindent
        if indent is None:
            return None
        return indent / 4 # XXX improve

    def _cutline(self, line):
        return line[self.model.indent * 4:] # XXX improve

    def _resolvearg(self, arg):
        if isinstance(arg, _ast.Str):
            return repr(arg.s)
        elif isinstance(arg, _ast.Num):
            return arg.n
        elif isinstance(arg, _ast.Name):
            return arg.id
        elif isinstance(arg, _ast.Call):
            args = list()
            for a in arg.args:
                args.append(self._resolvearg(a))
            kwargs = odict()
            for keyword in arg.keywords:
                kwargs[keyword.arg] = self._resolvearg(keyword.value)
            try:
                return Call(name=arg.func.id, args=args, kwargs=kwargs)
            except AttributeError:
                return Call(name=arg.func.attr, args=args, kwargs=kwargs)
        elif isinstance(arg, _ast.Tuple) or isinstance(arg, _ast.List):
            ret = list()
            for a in arg.elts:
                ret.append(self._resolvearg(a))
            if isinstance(arg, _ast.Tuple):
                ret = tuple(ret)
            return ret
        elif isinstance(arg, _ast.Dict):
            ret = dict()
            pointer = 0
            for key in arg.keys:
                key = self._resolvearg(key)
                ret[key] = self._resolvearg(arg.values[pointer])
                pointer += 1
            return ret

    def parsedecorators(self, astnode):
        for dec in astnode.decorator_list:
            decorator = Decorator(None, dec)
            decorator.buffer = self.model.buffer
            decorator.readlines = self.model.readlines
            self.model._decorators.append(decorator)


def parse_module_handler(obj, event):
    """Called, if ``Module`` is created and added to ``Directory`` node.
    """
    obj.parser()


provideHandler(parse_module_handler, [IModule, IFileAddedEvent])


class ModuleParser(BaseParser):

    def __call__(self):
        path = self.model.filepath
        self.model._buffer = list()
        if not os.path.exists(path):
            return
        if self.model._do_parse:
            self._parse()

    def _parse(self):
        file = open(self.model.filepath, 'r')
        cont = file.read()
        # Leading and trailing blank lines cause problems in the builtin 
        # "compile" function, so we strip them. In order to provide correct 
        # line numbers we store the offset - we use in case of an Exception...
        before = len(cont.split(os.linesep))
        cont = cont.lstrip()
        after = len(cont.split(os.linesep))
        cont = cont.rstrip()
        self.model._buffer = cont.split(os.linesep)
        offset = before - after
        file.close()
        self.model.readlines = list()
        self._extractencoding()
        self.model.bufstart = 0
        self.model.bufend = len(self.model._buffer)
        self.model.bufoffset = offset
        try:
            self.model.astnode = ast.parse(
                os.linesep.join(self.model.buffer).strip(),
                self.model.filepath)
        except SyntaxError, e:
            # Since the python source files are being stripped we have to
            # add an offset to the line number we get thrown from compile()
            ex = exceptions.SyntaxError((e[0], \
                (e[1][0], e[1][1] + offset, e[1][2], e[1][3]))) 
                # <- don't read that
            raise ex
        except TypeError, e:
            # We don't have to modify TypeErrors since they don't contain
            # line numbers.
            raise e
        children = self._protectedsections()
        for node in children:
            self._marklines(*range(node.bufstart, node.bufend))
        # for i in xrange(len(self.model.astnode.body)):
        #     astnode = self.model.astnode.body
        for astnode in self.model.astnode.body:
            self._createastchild(astnode)
        self._markastrelated(self.model)
        children += self._parsecodeblocks()
        self._hookchildren(children)

    def _extractencoding(self):
        if len(self.model.buffer) == 0:
            return
        line = self.model.buffer[0].strip()
        if line.startswith(u'# -*- coding:') \
          and line.endswith(u'-*-'):
            encoding = line[14:len(line) - 3].strip()
            self.model.encoding = unicode(encoding)
            self.model.readlines.append(0)

    def _markastrelated(self, node):
        for child in node.values():
            if IDocstring.providedBy(child) \
              or IImport.providedBy(child) \
              or IAttribute.providedBy(child) \
              or IDecorator.providedBy(child):
                self._marklines(*range(child.bufstart, child.bufend))
            else:
                self._marklines(*range(child.bufstart, child.defendlineno))
            self._markastrelated(child)

    def _protectedsections(self):
        i = 0
        currentnode = None
        in_protected_section = False
        allnodes = list()
        for line in self.model.buffer:
            line_strip = line.strip()
            if line_strip.startswith('#'):
                if line_strip.startswith(CODESECTION_STARTTOKEN):
                    if in_protected_section:
                        print "WARNING: Nested protected sections"
                        continue
                    # Protected section is starting here
                    in_protected_section = True
                    name = line_strip[len(CODESECTION_STARTTOKEN):]
                    node = ProtectedSection(name, self.model.buffer)
                    node.sectionname = name
                    node.readlines = self.model.readlines
                    node.bufstart = i
                    currentnode = node
                elif line_strip.startswith(CODESECTION_ENDTOKEN):
                    if not in_protected_section:
                        raise RuntimeError, \
                              "ERROR: Protected section closed without open"
                    if line_strip != CODESECTION_ENDTOKEN + \
                                     currentnode.__name__:
                        # Protected section is continuing here
                        currentnode.lines.append(line)
                        continue
                    # Protected section is ending here
                    currentnode.bufend = i + 1
                    allnodes.append(currentnode)
                    in_protected_section = False
                    currentnode = None
            i += 1
        if in_protected_section:
            raise RuntimeError, \
                  "ERROR: Protected section did not close"
        return allnodes

    def _parsecodeblocks(self):
        blocks = list()
        start = end = 0
        curline = 0
        for line in self.model.buffer:
            if curline in self.model.readlines:
                if start != end:
                    blocks += self._createcodeblocks(start, end)
                    start = end + 1
                else:
                    start = curline + 1
            curline += 1
            end = curline
        blocks += self._createcodeblocks(start, end)
        return blocks

    def _createcodeblocks(self, start, end):
        lines = self.model.buffer[start:end]
        if not ''.join(lines).strip():
            return []
        previndent = None
        pointer = 0
        ret = []
        for line in lines:
            pointer += 1
            if not line.strip() or line.strip().startswith('#'):
                continue
            if previndent is None:
                previndent = self._findindent([self.model.buffer[start]])
            curindent = self._findindent([line])
            if curindent >= previndent:
                continue
            elif curindent < previndent:
                block = Block(None, self.model.buffer)
                block.readlines = self.model.readlines
                block.bufstart = start
                block.bufend = start + pointer - 1
                ret.append(block)
                start = start + pointer - 1
            previndent = curindent
        block = Block(None, self.model.buffer)
        block.readlines = self.model.readlines
        block.bufstart = start
        block.bufend = end
        ret.append(block)
        return ret

    def _hookchildren(self, children):
        for child in children:
            if not child.__name__:
                child.__name__ = str(child.uuid)
            child.__parent__ = self.model
            node, position = self._findnodeposition(child.startlineno,
                                                    child.endlineno,
                                                    child.indent)
            child.__parent__ = None
            if position == POSITION_INSERT:
                node[child.__name__] = child
            elif position == POSITION_BEFORE:
                node.__parent__.insertbefore(child, node)
            elif position == POSITION_AFTER:
                node.__parent__.insertafter(child, node)


class ImportParser(BaseParser):

    def __call__(self):
        astnode = self.model.astnode
        if isinstance(astnode, _ast.ImportFrom):
            self.model.fromimport = unicode(astnode.module)
        for name in astnode.names:
            asname = name.asname is not None and unicode(name.asname) or None
            self.model.names.append([unicode(name.name), asname])
        self.model._fromimport_orgin = copy.deepcopy(self.model.fromimport)
        self.model._names_orgin = copy.deepcopy(self.model.names)

    def _definitionends(self, bufno):
        if len(self.model.buffer) < bufno:
            return True
        if len(self.model.buffer) <= bufno + 1:
            return True
        line = self.model.buffer[bufno + 1].strip()
        for term in [u'from ', u'import ', u'if ', u'for ', u'while ', u'try ',
                     u'with ', u'class ', u'def ', u'@', u'#', u'"""',
                     u'\'\'\'']:
            if line.startswith(term):
                return True
        if line == u'' or line.find(u'=') != -1:
            return True
        return False


class AttributeParser(BaseParser):

    def __call__(self):
        astnode = self.model.astnode
        for target in astnode.targets:
            if isinstance(target, _ast.Tuple):
                for name in target.elts:
                    self.model.targets.append(name.id)
            elif isinstance(target, _ast.Subscript):
                self.model.targets.append(target.value.attr)
            else:
                try:
                    self.model.targets.append(target.id)
                except AttributeError:
                    self.model.targets.append(target.value.id)
                    
        self.model._targets_orgin = copy.deepcopy(self.model.targets)
        self._findattributeend()
        self._extractvalue()
        self._parseastargs(astnode)
        self.model._args_orgin = copy.deepcopy(self.model.args)
        self.model._kwargs_orgin = copy.deepcopy(self.model.kwargs)

    def _findattributeend(self):
        pointer = self.model.bufstart
        buflen = len(self.model.buffer)
        source = ''
        while True:
            #if pointer + 1 == buflen:
            if pointer == buflen:
                break
            line = self.model.buffer[pointer].strip()
            source = '%s\n%s' % (source, line)
            try:
                compile(source, '<string>', 'exec')
                pointer += 1
                break
            except SyntaxError, e:
                pointer += 1
        self.model.bufend = pointer

    def _extractvalue(self):
        lines = self.model.buffer[self.model.bufstart:self.model.bufend]
        if not lines:
            lines.append(self.model.buffer[self.model.bufstart])
        lines[0] = lines[0][lines[0].find('=') + 1:].strip()
        for i in range(1, len(lines)):
            lines[i] = self._cutline(lines[i])
        self.model.value = '\n'.join(lines)
        self.model._value_orgin = '\n'.join(lines)

    def _parseastargs(self, astnode):
        if not hasattr(astnode.value, 'args'):
            return
        for arg in astnode.value.args:
            self.model.args.append(self._resolvearg(arg))
        for keyword in astnode.value.keywords:
            self.model.kwargs[keyword.arg] = self._resolvearg(keyword.value)


class DecoratorParser(BaseParser):

    def __call__(self):
        astnode = self.model.astnode
        if isinstance(astnode, _ast.Name) or isinstance(astnode, _ast.Attribute):
            if not getattr(astnode, 'id', None):
                # XXX: added by phil because sometimes astnode.id is None
                astnode.id = astnode.attr
            self.model.decoratorname = astnode.id
            self.model._decoratorname_orgin = astnode.id
            return

        if not getattr(astnode.func, 'id', None):
            # XXX: added by phil because sometimes astnode.func.id is None
            astnode.func.id = astnode.func.attr
        self.model.decoratorname = astnode.func.id
        self.model._decoratorname_orgin = astnode.func.id
        self._parseastargs(astnode)
        self.model._args_orgin = copy.deepcopy(self.model.args)
        self.model._kwargs_orgin = copy.deepcopy(self.model.kwargs)

    def _parseastargs(self, astnode):
        for arg in astnode.args:
            self.model.args.append(self._resolvearg(arg))
        for keyword in astnode.keywords:
            self.model.kwargs[keyword.arg] = self._resolvearg(keyword.value)

    def _definitionends(self, bufno):
        if len(self.model.buffer) <= bufno:
            return True
        line = self.model.buffer[bufno + 1].strip()
        for term in [u'class ', u'def ', u'@']:
            if line.startswith(term):
                return True
        return False


class FunctionParser(BaseParser):

    def __call__(self):
        astnode = self.model.astnode
        self.model.functionname = astnode.name
        self._findbodyend(astnode)
        self._checkbodyendsmultilined()
        self._checkbodyendsprotected()
        self._parseastargs(astnode)
        self.model._args_orgin = copy.deepcopy(self.model.args)
        self.model._kwargs_orgin = copy.deepcopy(self.model.kwargs)
        self.parsedecorators(astnode)

    def _parseastargs(self, astnode):
        all = list()
        for arg in astnode.args.args:
            all.append(self._resolvearg(arg))
        args = all[:len(all) - len(astnode.args.defaults)]
        kwargs = all[len(all) - len(astnode.args.defaults):]
        for arg in astnode.args.args:
            resolved = self._resolvearg(arg)
            if resolved in args:
                self.model.args.append(resolved)
        pointer = 0
        for kwarg in astnode.args.defaults:
            self.model.kwargs[kwargs[pointer]] = self._resolvearg(kwarg)
            pointer += 1
        if astnode.args.vararg:
            self.model.args.append('*%s' % astnode.args.vararg)
        if astnode.args.kwarg:
            self.model.kwargs['**%s' % astnode.args.kwarg] = None

    def _definitionends(self, bufno):
        if len(self.model.buffer) <= bufno:
            return True
        line = self.model.buffer[bufno].strip()
        if line.find(u'#') > 0:
            line = line[0:line.find(u'#')].strip()
        if line.endswith(u'\\') \
          or line.endswith(u','):
            return False
        if line.endswith(u':'):
            return True
        return False


class ClassParser(BaseParser):

    def __call__(self):
        astnode = self.model.astnode
        self.model.classname = astnode.name
        self._findbodyend(astnode)
        self._checkbodyendsmultilined()
        self._checkbodyendsprotected()
        def base_name(astnode):
            name = list()
            while True:
                if isinstance(astnode, _ast.Attribute):
                    name.append(astnode.attr)
                    astnode = astnode.value
                else:
                    name.append(astnode.id)
                    break
            name.reverse()
            return '.'.join(name)
        self.model.bases = [base_name(base) for base in astnode.bases]
        self.model._bases_orgin = copy.deepcopy(self.model.bases)
        self.parsedecorators(astnode)

    def _definitionends(self, bufno):
        if len(self.model.buffer) <= bufno:
            return True
        line = self.model.buffer[bufno].strip()
        if line.find(u'#') > 0:
            line = line[0:line.find(u'#')].strip()
        if line.endswith(u'\\') \
          or line.endswith(u','):
            return False
        if line.endswith(u':'):
            return True
        return False
