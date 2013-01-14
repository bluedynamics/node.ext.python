from node.ext.python.interfaces import (
    IModule,
    IImport,
    IDocstring,
    IBlock,
)
from node.ext.python import Import


class Imports(object):
    """Adapter like object for managing imports on modules.
    """

    def __init__(self, context):
        if not IModule.providedBy(context):
            raise ValueError(u"Given context is not an IModule implementation")
        self.context = context

    def set(self, fromimport=None, names=None):
        if fromimport is None and names is None:
            raise ValueError(u"No definitions given.")
        imports = self.context.imports()
        if len(imports) == 0:
            import_ = Import(fromimport, names)
            import_.__name__ = str(import_.uuid)
            self._add(import_)
            return
        existent = False
        for imp in imports:
            if imp.fromimport == fromimport:
                existent = True
        if not existent:
            import_ = Import(fromimport, names)
            import_.__name__ = str(import_.uuid)
            self._add(import_)
            return
        for imp in imports:
            if imp.fromimport == fromimport:
                for name in names:
                    update = False
                    for iname, asname in imp.names:
                        if iname == name[0]:
                            update = True
                if update:
                    for i in range(len(imp.names)):
                        if imp.names[i][0] == name[0]:
                            imp.names[i] = name
                else:
                    imp.names.append(name)

    def _add(self, import_):
        values = self.context.values()
        for value in values:
            if IBlock.providedBy(value):
                comment = True
                for line in value.lines:
                    if not line.startswith('#'):
                        comment = False
                        break
                if comment:
                    self.context.insertafter(import_, value)
                    return
            if not IImport.providedBy(value) \
              and not IDocstring.providedBy(value):
                self.context.insertbefore(import_, value)
                return
        self.context[import_.uuid] = import_
