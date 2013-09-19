# -*- coding: utf-8 -*-
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#

import re
import sys
from zope.component import provideHandler
from node.ext.python.interfaces import IModule
from node.ext.directory.interfaces import IFileAddedEvent
from node.ext.python.goparser import GoParser
from node.ext.python.gonodes import (
    Module,
    Block,
    Class,
    Function,
    Docstring,
    Import,
    Decorator,
    ProtectedSection,
    Attribute,
    #Expression,
)

typedefs = {
    'ClassDef': 'Class',
    'FunctionDef': 'Function',
    'Docstring': 'Docstring',
    'ImportFrom': 'Import',
    'Decorator': 'Decorator',
    'Assign': 'Attribute',  # value oder args und kwargs
    ##'Expr': 'Expression',  # @@@ Gogo. needs impl ;-)
}

subdefs = {
    'ClassDef': ['FunctionDef', 'ClassDef', 'Assign', 'Expr', 'Docstring'],
    'FunctionDef': ['Decorator', 'Docstring'],
    'Block': [],
}


class Walker(object):
    """
    XXX missing docstring
    """
    gopnodes = None
    nodes = []
    protected_lines = []

    def __init__(self, filename):
        """
        XXX missing docstring
        """
        self.filename = filename

    def createNodeByType(self, gopnode, force=None):
        """
        XXX missing docstring
        """
        if force:
            nodetype = force
        else:
            nodetype = typedefs.get(gopnode.get_type(), 'Block')

        call = str(nodetype) +\
            """(name=str(gopnode),
                gopnode=gopnode,
                buffer=gopnode.get_buffer(),
                bufstart=gopnode.startline,
                bufend=gopnode.endline,
                )"""
        print "-" * 40
        print call
        print "-" * 40
        import pdb
        pdb.set_trace()  # keule!
        newnode = eval(call)
        return newnode

    def createSubnode(self, gopnode, force=None):
        """
        XXX missing docstring
        """
        wanted_subtypes = subdefs.get(gopnode.get_type(), [])
        if gopnode.startline in self.protected_lines:
            # import pdb;pdb.set_trace()
            here = self.createNodeByType(gopnode, force="ProtectedSection")
        else:
            here = self.createNodeByType(gopnode, force)

        # Ignore Name child in ClassDef completely
        if here.get_type() == 'Class' and \
                gopnode.children[0].get_type() == 'Name':
            gopnode.children = gopnode.children[1:]

        # lastsubsub = None
        for child in gopnode.children:
            subsub = None

            if child.get_type() not in wanted_subtypes or \
                    here.get_type() == 'Block':
                subsub = self.createSubnode(child, force="Block")
                if here.get_type() == 'Block':
                    here.bufstart = min(here.bufstart, subsub.bufstart)
                    here.bufend = max(here.bufend, subsub.bufend)
                    # lastsubsub = subsub
                    subsub = None
                    continue
            else:
                subsub = self.createSubnode(child)

            if subsub:
                here[str(subsub.uuid)] = subsub
                # lastsubsub = subsub
        return here

    # def combine(self, node_a, node_b):
    #     """ Combines two blocks if possible
    #     """
    #     both = [node_a, node_b]
    #     if node_a.gopnode.indent != node_b.gopnode.indent:
    #         return both
    #     if node_a.get_type() != node_b.get_type():
    #         return both
    #     if node_a.bufstart > node_b.bufstart:
    #         node_a, node_b = node_b, node_a
    #     if node_a.bufend != node_b.bufstart-1:
    #         return both
    #     newnode = Block(node_a.nodename+"+"+node_b.nodename,\
    #             node_a.gopnode, # @@@ other.gopnode is being discarded here..
    #             node_a.buffer+node_b.buffer,
    #             node_a.bufstart,
    #             node_b.bufend,
    #             )
    #     return [newnode]

    def clean_pair(self, node_a, node_b):
        """
        XXX missing docstring
        """
        if node_a.get_type() == node_b.get_type() == 'ProtectedSection':
            print "About to delete %s" % (node_a,)
            node_b.bufstart = min(node_a.bufstart, node_b.bufstart)
            node_b.bufend = max(node_a.bufend, node_b.bufend)
#            if node_a.parent.node(node_a.uuid):
            if node_b.parent == node_a:
#                import pdb;pdb.set_trace()
                node_a.parent[str(node_b.uuid)] = node_b
            del node_a.parent[str(node_a.uuid)]
        node_b.gopnode.startline = node_b.bufstart
        node_b.gopnode.endline = node_b.bufend

    def serialized_tree(self, nodes):
        """
        XXX missing docstring
        """
        sernodes = []
        for node in nodes:
            sernodes.append(node)
            sernodes += self.serialized_tree(node.values())
        return sernodes

    def cleanup(self, node):
        """
        XXX missing docstring
        """
        sertree = self.serialized_tree(node.values())
#        newnodes = []
        i = 0
        while i < len(sertree) - 1:
            node_a = sertree[i]
            node_b = sertree[i + 1]
            self.clean_pair(node_a, node_b)
            i = i + 1
        return node

    def walk(self):
        """ Returns a filled Module node
        """
        fileinst = open(filename, 'r')
        source = fileinst.read()
        fileinst.close()
        P = GoParser(source, filename)
        P.parsegen()

        sourcecode = P.get_codelines()

        root = Module(
            filename=filename,
            buffer=sourcecode,
            bufstart=P.startline,
            bufend=P.endline,
            encoding=P.get_coding(),
        )

        # Prepare protected sections
#        protectedsections = re.findall('(?ms)##code\-section (\\w*).*?##/code\-section \\1', '\n'.join(sourcecode))
#        import pdb;pdb.set_trace()
        section_id = None
        for line_number in xrange(len(sourcecode)):
            line = sourcecode[line_number]
            new_section_id = re.findall('##code\-section (\\w*)', line)
            if new_section_id and section_id:
                raise "Fuck Shit Bitches! Don't nest "
            if new_section_id:
                section_id = new_section_id
            if section_id:
                self.protected_lines.append(line_number)
                if re.findall('##/code\-section (\\w*)', line):
                    section_id = None

        print "Protected Lines are:", self.protected_lines

        for gopnode in P.children:
            newnode = self.createSubnode(gopnode)
            print ".",
            if newnode != None:
                # try:
                    root[str(newnode.uuid)] = newnode
                # except Exception, e:
                #     import pdb
                #     pdb.set_trace()

        print

        self.cleanup(root)
        return root


def parse_module_handler(obj, event):
    """Called, if ``Module`` is created and added to ``Directory`` node.
    """
    import pdb;pdb.set_trace()  # keule!
    obj.parser()

provideHandler(parse_module_handler, [IModule, IFileAddedEvent])


def main(filename):
    """ The module can be called with a filename of a python file for testing
    """
    W = Walker(filename)
    root = W.walk()
    print "TREE:"
    root.printtree()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        filename = __file__
    else:
        filename = sys.argv[1]
    main(filename)
