from zope.interface import (
    Interface,
    Attribute,
)
from node.interfaces import (
    INode,
    ICallable,
)
from node.ext.directory.interfaces import IFile


CODESECTION_STARTTOKEN = '##code-section '
CODESECTION_ENDTOKEN = '##/code-section '


class Call(dict):
    pass


class Incomplete(Exception):
    pass


class IPythonNode(INode, ICallable):
    """Python node.
    """

    buffer = Attribute(u"The existing file line buffer als list. Read-only.")
    astnode = Attribute(u"The python node refering ast node.")
    startlineno = Attribute(u"Start line number of python Node. Read-only.")
    endlineno = Attribute(u"End line number of python Node. Read-only.")
    bufstart = Attribute(u"Start index of lines in buffer. Read-only.")
    bufend = Attribute(u"End index of lines in buffer. Read-only.")
    indent = Attribute(u"Indent level of buffer[bufstart:bufend].")
    postlf = Attribute(u"Number of Newlines to render on __call__ after Node.")
    # XXX propably move ``nodelevel`` to Node under name level
    nodelevel = Attribute(u"The current node level.")

    def docstrings():
        """Return docstrings.
        """

    def blocks():
        """Return blocks.
        """

    def imports():
        """Return blocks.
        """

    def protectedsections(name=None):
        """Return protected sections. If name is not None, filter by name.
        """

    def classes(name=None):
        """Return classes. If name is not None, filter by name.
        """

    def functions(name=None):
        """Return functions. If name is not None, filter by name.
        """

    def attributes(name=None):
        """Return attributes. If name is not None, filter by name.
        """


class IModule(IFile, IPythonNode):
    """Python module.
    """
    modulename = Attribute(u"The name of the module.")
    encoding = Attribute(u"The file encoding. Defaults to utf-8")
    bufoffset = Attribute(u"Number of lines stripped at the top of a "
                          u"module file")


class IBlock(IPythonNode):
    """Python code block.
    """
    lines = Attribute(u"List of code lines.")
    text = Attribute(u"block contents as text.")


class IProtectedSection(IPythonNode):
    """Protected section.
    """
    lines = Attribute(u"List of code lines.")
    text = Attribute(u"block contents as text.")


class IDocstring(IPythonNode):
    """Docstring.
    """
    lines = Attribute(u"The doc string contents.")
    text = Attribute(u"block contents as text.")


class IImport(IPythonNode):
    """Import line.
    """
    fromimport = Attribute("The module name from import or None")
    names = Attribute(u"List of tuples containing (importname, asname)")


class IAttribute(IPythonNode):
    """Attribute.
    """
    targets = Attribute(u"The targets of the attribute.")
    value = Attribute(u"The attribute value.")


class ICallableArguments(Interface):
    """Arguments of a callable, usually a decorator or a function.
    """
    args = Attribute(u"The callable arguments")
    kwargs = Attribute(u"The callable kwarguments")
    s_args = Attribute(u"The callable arguments as string")
    s_kwargs = Attribute(u"The callable kwarguments as string")

    def extract_arguments():
        """Return 2-tuple with args and kwargs.

        The arguments are computed by looking up the string value for s_args
        and s_kwargs, as fallback args and kwargs are used.
        """

    def arguments_equal(other):
        """Check whether other callable arguments are equal to self.
        """


class IDecorator(IPythonNode, ICallableArguments):
    """Decorator.
    """
    decoratorname = Attribute(u"The name of the decorator.")

    def equals(other):
        """Check whether other decorator is equal to self.
        """


class IDecorable(Interface):
    """Decorable nodes (currently Function, Class).
    """


class IFunction(IPythonNode, ICallableArguments):
    """Python function.
    """
    functionname = Attribute(u"Name of the function")
    defendlineno = Attribute(u"End line number of function def. Read-only.")

    def decorators(name=None):
        """Return decorators. If name is not None, filter by name.
        """


class IClass(IPythonNode):
    """Python class.
    """
    classname = Attribute(u"Name of the class.")
    bases = Attribute(u"List of base classes for this class")
    defendlineno = Attribute(u"End line number of class def. Read-only.")

    def decorators(name=None):
        """Return decorators. If name is not None, filter by name.
        """
