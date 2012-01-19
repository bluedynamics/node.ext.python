# -*- coding: utf-8 -*-
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#

from node.ext.python.goparser import GoParser
from node.ext.python.gonodes import (\
        Module, 
        Block, 
        Class, 
        Function,
        Docstring,
        Import,
        Decorator,
        )

typedefs = { \
        'ClassDef': 'Class',
        'FunctionDef': 'Function',
        'Docstring': 'Docstring',
        'ImportFrom': 'Import',
        'Decorator': 'Decorator',
        'Assign': 'Block',
        'If': 'Block',
        }

subdefs = { \
        'ClassDef': ['FunctionDef','ClassDef'],   
        'FunctionDef' : ['Decorator', 'Docstring'],
        'Block' : [],
        }


class Walker(object):
    
    gopnodes = None
    nodes = []
    
    def __init__(self, filename):
        self.filename = filename
        
    def createNodeByType(self, gopnode, force=None):
        if force:
            nodetype = force
        else:
            nodetype = typedefs.get(gopnode.get_type(), 'Block')
        
        call = str(nodetype)+\
                """(name=str(gopnode),
                gopnode=gopnode,
                buffer=gopnode.get_codelines(),
                bufstart=gopnode.startline,
                bufend=gopnode.endline,
                )"""
        newnode = eval(call)
        return newnode
        
    def createSubnode(self, gopnode, force=None):
        here = self.createNodeByType(gopnode, force)
        wanted_subtypes = subdefs.get(gopnode.get_type(), [])

        # Ignore Name child in ClassDef completely
        if here.get_type()=='Class' and \
           gopnode.children[0].get_type() == 'Name':
            gopnode.children = gopnode.children[1:]
        
        # lastsubsub = None
        for child in gopnode.children:
            subsub = None
            if child.get_type() not in wanted_subtypes or \
                    here.get_type() == 'Block':
                subsub = self.createSubnode(child, force="Block")
            else:
                subsub = self.createSubnode(child)

            if here.get_type() == 'Block':
                here.bufstart = min(here.bufstart, subsub.bufstart)
                here.bufend = max(here.bufend, subsub.bufend)
                here.buffer.append(subsub.buffer)
                lastsubsub = subsub
                subsub = None
                break

            # if lastsubsub and lastsubsub.get_type() == 'Block':
            #     lastsubsub.bufend = subsub.bufend
            #     lastsubsub.buffer.append(subsub.buffer)
            #     here[lastsubsub.uuid] = lastsubsub
            #     subsub = None
            #     print "combining with last block"
            #     break

            if subsub:
                here[subsub.uuid] = subsub
                lastsubsub = subsub
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
    #             node_a.gopnode, # @@@ other.gopnode is being discarded here...
    #             node_a.buffer+node_b.buffer,
    #             node_a.bufstart,
    #             node_b.bufend,
    #             )
    #     return [newnode]
    # 
    # def cleanup(self, node):
    #     numnodes = len(node.keys())
    #     if numnodes < 2:
    #         return node
    #     first_node = node.values()[0]
    #     newnodes = [self.cleanup(firstnode)]
    #     for i in xrange(numnodes-1):
    #         node_a = node.values()[i]
    #         node_b = node.values()[i+1]
    #         self.cleanup(node_a)
    #         newnodes.append(self.combine(node_a, node_b))
    #     node
    #     return newnodes

    def walk(self):
        """ Returns a filled Module node
        """
        fileinst = open(filename,'r')
        source = fileinst.read()
        fileinst.close()
        P = GoParser(source, filename)
        P.parsegen()

        root = Module(\
                filename = filename,
                buffer = P.get_codelines(),
                bufstart = P.startline,
                bufend = P.endline,
                encoding = P.get_coding(),
                )
        
        for gopnode in P.children:
            newnode = self.createSubnode(gopnode)
            print ".",
            if newnode != None:
                root[newnode.uuid] = newnode
        print
        
        # self.cleanup(root)
        return root

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


