# -*- coding: utf-8 -*-
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#

import os
import re
import ast
import _ast
import sys
# import compiler


VERBOSE = True


class metanode(object):

    def __init__(self,
                 parent,
                 astnode,
                 sourcelines=None,
                 startline=None,
                 endline=None,
                 indent=None,
                 offset=None,
                 stuff=None,
                 do_correct=True,
                 parser=None,
                 ):
        """ Stores additional info about a ast node
        """
        self.parent = parent
        self.children = []
        self.astnode = astnode
        self.sourcelines = sourcelines
        self.startline = startline
        self.endline = endline
        self.indent = indent
        self.stuff = stuff
        self.offset = offset
        self.heuristictype = None
        self.parser = parser

        # print self.get_type()
        # if self.get_type() == 'NoneType':
        #     import pdb;pdb.set_trace()

        if parent != None:
            parent.children.append(self)
        else:
            parser.children.append(self)
        if do_correct:
            self.correct()

    def strip_comments(self, sourceline):
        """ Returns a line without comments, rstripped
        """
        stripped = re.sub('("""|\'\'\'|"|\'|)(.*?)\\1.*?#(.*)', '\\1\\2\\1', sourceline).rstrip()
        return stripped

    def is_empty(self, sourceline):
        """ Tests if a source line contains just whitespace.
        """
        if sourceline.strip() == '':
            return True
        return False

    def remove_trailing_blanklines(self):
        s = self.startline
        e = self.endline
        while e > s and self.is_empty(self.sourcelines[e]):
            e -= 1
        self.endline = e

    def handle_upside_down_ness(self):
        """ Would correct startlines that happen to be after endlines
        """
        if self.startline > self.endline:
            import pdb
            pdb.set_trace()
            self.startline, self.endline = self.endline, self.startline

    def correct_docstrings(self):
        """ Fixes endlines of docstrings
        """
        quotings = ['"""', "'''", "'", '"']
        found = None
        e = self.endline
        while self.is_empty(self.strip_comments(self.sourcelines[e])):
            e -= 1
        lastline = self.sourcelines[e]
        for quoting in quotings:
            if lastline.rfind(quoting) != -1:
                found = quoting
                break
        self.quoting = found
        s = self.startline
        e = self.endline
        block = '\n'.join(self.sourcelines[s:e + 1])
        while s >= 0 and len(re.findall(found, block)) <= 1:
            s -= 1
            block = '\n'.join(self.sourcelines[s:e + 1])
        self.startline = s
        self.heuristictype = "Docstring"

    def correct_decorators(self):
        """ Decorators should not include the function definition start,
            function definitions should not include the decorators.
        """
        for i in xrange(self.startline, self.endline + 1):
            if len(re.findall("^\s*def\s", self.sourcelines[i])) == 1:
                self.endline = i - 1
                self.parent.startline = i
                break
        self.heuristictype = "Decorator"

    def correct_comments(self):
        """ Looks if node contains comments at its end, because
            they have to be removed and placed in another (comment-) node.
        """
        s = self.startline
        e = self.endline
        while (e > s + 1):
            if re.findall('^\s*?#.*', self.sourcelines[e]) \
                    or self.is_empty(self.sourcelines[e]):
                e = e - 1
            else:
                break
        if e != self.endline:
            print self.dump()
            # generate comment type
            subnode = metanode(self.parent,
                               None,
                               self.sourcelines,
                               startline=e + 1,
                               endline=self.endline,
                               indent=self.indent,
                               offset=self.offset,
                               stuff=self.stuff,
                               do_correct=False,
                               parser=self.parser)
            subnode.heuristictype = 'Comment'
            self.endline = e
            if VERBOSE:
                print subnode.dump()

    def correct_col_offset(self):
        """ Fixes col_offset issues where it would be -1 for multiline strings
        """
        blanks = re.findall("^\s*", self.sourcelines[self.startline])[0]
        self.astnode.col_offset = len(blanks)

    def correct(self):
        """ Fixes ast issues
        """
        self.handle_upside_down_ness()
        self.remove_trailing_blanklines()
        self.correct_comments()

        # Deal with wrong start for Docstrings:
        if isinstance(self.astnode, _ast.Expr) and \
                isinstance(self.astnode.value, _ast.Str):
            self.correct_docstrings()

        # Deal with decorator line numbers:
        if (isinstance(self.astnode, _ast.Call) and
            isinstance(self.parent.astnode, _ast.FunctionDef)) \
            or (isinstance(self.astnode, _ast.Name) and
                isinstance(self.parent.astnode, _ast.FunctionDef)):
            self.correct_decorators()

        # Multiline expressions have wrong col_offset
        if isinstance(self.astnode, _ast.Expr) and \
                self.astnode.col_offset < 0:
            self.correct_col_offset()

    def get_codelines(self):
        """ Returns the lines of code assiciated with the node
        """
        return self.sourcelines[self.startline: self.endline + 1]

    def get_buffer(self):
        """ Returns the lines of code assiciated with the node
        """
        return self.sourcelines

    def get_type(self):
        """ Returns a string identifying the type of the ast node
        """
        if self.heuristictype:
            return self.heuristictype
        else:
            return self.astnode.__class__.__name__

    def get_astvalue(self, astnode):
        """ Returns the value of a ast object if that makes any sense
        """
        t = astnode.__class__.__name__
        if t == 'Name':
            return astnode.id
        if t == 'Str':
            return astnode.s
        if t == 'Num':
            return astnode.n
        return object()

    def __repr__(self):
        """ Returns a nodes representation
        """
        name = ''
        if hasattr(self.astnode, 'name'):
            name = " '%s'" % getattr(self.astnode, 'name')
        return "%s (%s-%s%s)" % (
            self.get_type(),
            self.startline + self.offset,
            self.endline + self.offset,
            name,
        )

    def dump(self):
        """ Nice for debugging
        """
        res = ""
        if getattr(self, 'astnode'):
            res = "--- %d (%d) %s (parent: %s)\n" % (
                self.indent,
                self.astnode.col_offset,
                repr(self),
                repr(self.parent),
            )
#         print "--- %d (%d)/%03d-%03d/ %s (parent: %s)" % (
#                 self.indent,
#                 self.astnode.col_offset,
#                 self.startline+self.offset,
#                 self.endline+self.offset,
# #                self.astnode.__class__.__name__,
#                 repr(self),
#                 repr(self.parent),
#                 )
#         # import pdb;pdb.set_trace()
#         print "--- %d (%d) %s" % (
#                 self.indent,
#                 self.astnode.col_offset,
# #                self.astnode.__class__.__name__,
#                 repr(self.astnode),
#                 ),
        # for field in self.astnode._fields:
        #     print "%s:%s " % (field, repr(getattr(self.astnode, field, '-')),),
        # print "Parent:", repr(self.parent)
        for l in xrange(self.startline, self.endline + 1):
            res += "%03d:%s\n" % (l + self.offset, repr(self.sourcelines[l])[1:-1])
        return res


class GoParser(object):

    def __init__(self, source, filename):
        """ Creates a parser object
        """
        self.source = source
        self.filename = filename
        self.removeblanks()
        self.children = []

    def walk(self, parent, nodes, start, end, ind):
        """ Iterates nodes of the abstract syntax tree
        """
        # lastnode = None
        nodecount = len(nodes)

        for i in xrange(nodecount):
            current = nodes[i]

            if i < (nodecount - 1):
                if nodes[i + 1].lineno != current.lineno:
                    nend = nodes[i + 1].lineno - 1
                else:
                    nend = nodes[i + 1].lineno
            else:
                nend = end
            start = current.lineno

            mnode = metanode(
                parent=parent,
                astnode=current,
                sourcelines=self.lines,
                startline=start,
                endline=nend,
                indent=ind,
                offset=self.offset,
                stuff=None,
                do_correct=True,
                parser=self,
            )

            if VERBOSE:
                print mnode.dump()

#            if parent == None:
#                self.children.append(mnode)

            next_set = []
            for field in current._fields:
                next_item = getattr(current, field, None)
                if isinstance(next_item, type([])):
                    for item in getattr(current, field, []):
                        if hasattr(item, 'lineno'):
                            next_set.append([item.lineno, item])
            next_set.sort()
            next_set = [i[1] for i in next_set]
            self.walk(mnode, next_set, start, nend, ind + 1)

    # def cleanuptree(self, nodes, lastnode=None):
    #     """ Performs some corrections on pairs of nodes
    #     """
    #     if not nodes:
    #         return
    #     if lastnode and nodes:
    #         newA, newB = self.cleanup_pair(lastnode, nodes[0])
    #     nodeA = None
    #     nodeB = None
    #     for i in xrange(1, len(nodes)):
    #         nodeA = nodes[i-1]
    #         nodeB = nodes[i]
    #         self.cleanuptree(nodeA.children, nodeA)
    #         newA, newB = self.cleanup_pair(nodeA, nodeB)
    #         nodes[i-1] = newA
    #         nodes[i] = newB
    #     if nodeB:
    #         self.cleanuptree(nodeB.children)

    def removeblanks(self):
        """ Removes trailing blank lines and rstrips source code. This
            function sets the offset to use to correct the indexing.
        """
        # Strip trailing blanks in lines
        self.lines = [i.rstrip() for i in self.source.split(os.linesep)]
        self.source = os.linesep.join(self.lines)
        # Count number of lines before removing heading blanks
        before = len(self.lines)
        # Remove heading blanks
        self.source = self.source.lstrip()
        # Count number of lines after removing heading blanks
        self.lines = self.source.split(os.linesep)
        after = len(self.lines)
        # Remove trailing blanks lines
        self.source = self.source.rstrip()
        self.lines = self.source.split(os.linesep)
        self.startline = 0
        self.offset = (before - after)
        self.endline = len(self.lines)

    def cleanup_fragmented_comments(self, nodeA, nodeB, allitems):
        """
        """
        if (nodeA.get_type() == nodeB.get_type() == 'Comment'):
            nodeA.startline = min(nodeA.startline, nodeB.startline)
            nodeA.endline = max(nodeA.endline, nodeB.endline)
            allitems.remove(nodeB)

    def cleanup_last_statement_and_docstring(self, nodeA, nodeB, allitems):
        """ There's an issu where a docstring appears in the
            buffer of the last statement of the previous codeblock
        """
        if (nodeB.get_type() == 'Docstring'):
            index = allitems.index(nodeB) - 1
            while nodeA.endline == nodeB.startline:
                nodeA.endline = nodeB.startline - 1
                # print "Really corrected a doctsring flaw in %s and %s" % \
                #    (nodeA, nodeB,)
                index = index - 1
                nodeA = allitems[index]

    def walk_pairs(self, itemlist, method):
        itemcount = len(itemlist)
        if itemcount < 2:
            return
        i = 1
        while i < len(itemlist):
            A = itemlist[i - 1]
            B = itemlist[i]
            method(A, B, itemlist)
            i = i + 1

    def serialized_tree(self, nodes):
        sernodes = []
        for node in nodes:
            sernodes.append(node)
            sernodes += self.serialized_tree(node.children)
        return sernodes

    def clean_walk_siblings(self, nodes):
        if not nodes:
            return
#        print "walking siblings", nodes
        self.walk_pairs(nodes, self.clean_pair)
        for node in nodes:
            self.clean_walk_siblings(node.children)

    def clean_pair(self, nodeA, nodeB, allitems=[]):
#        print "Cleaning %s vs. %s" % (nodeA, nodeB)
        self.cleanup_last_statement_and_docstring(nodeA, nodeB, allitems)
        self.cleanup_fragmented_comments(nodeA, nodeB, allitems)

    def parsegen(self):
        """ Reads the input file, parses it and
            calls a generator method on each node.
            This function also cleans up all nodes
            in a second step.
        """
        astt = ast.parse(self.source, self.filename)
        self.lines = [''] + self.lines
        self.walk(None, astt.body, 1, self.endline, 0)

        serializedtree = self.serialized_tree(self.children)
#        print "--------------walikng serialized:", serializedtree
        self.walk_pairs(serializedtree, self.clean_pair)
#        print "--------------walikng siblings:"
        self.clean_walk_siblings(self.children)

    def get_codelines(self):
        """ Returns an array of source lines
        """
        return self.lines[1:]

    def get_coding(self):
        """ Returns the files coding and defaults to ASCII (PEP: 0263)
        """
        try:
            return unicode([i for i in re.compile("(?:#\s\-\*\-\scoding\:\s(.*?)\s\-\*\-)|coding[:=]\s*([-\w.]+)").findall('\n'.join(self.source.split('\n')[:2]))[0] if i][0])
        except:
            return u'ASCII'


def main(filename):
    """ The module can be called with a filename of a python file for testing
    """
    fileinst = open(filename, 'r')
    source = fileinst.read()
    fileinst.close()

    P = GoParser(source, filename)
    P.parsegen()

    print repr(P.children)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        filename = __file__
    else:
        filename = sys.argv[1]
    VERBOSE = True
    main(filename)
