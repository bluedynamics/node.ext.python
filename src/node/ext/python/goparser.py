# -*- coding: utf-8 -*-
# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2
# Georg Gogo. BERNHARD gogo@bluedynamics.com
#
import os
import re
import ast
import _ast
import sys
import compiler


class metanode(object):

    def __init__(
            self,
            parent,
            astnode,
            sourcelines = None,
            startline = None, 
            endline = None,
            indent = None,
            offset = None,
            stuff = None,
            ):
        """Stores additional info about a ast node.
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
        if parent != None:
            parent.children.append(self)
        self.correct()

    def get_sourcelines(self):
        """Returns the lines of code assiciated with the node.
        """
        return self.sourcelines[self.startline, self.endline+1]

    def strip_comments(self, sourceline):
        """Returns a line without comments, rstripped.
        """
        stripped = re.sub('("""|\'\'\'|"|\'|)(.*?)\\1.*?#(.*)', '\\1\\2\\1',
                          sourceline).rstrip()
        return stripped

    def is_empty(self, sourceline):
        """Tests if a source line contains just whitespace.
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
    	"""Would correct startlines that happen to be after endlines.
    	"""
        if self.startline > self.endline:
            self.startline, self.endline = self.endline, self.startline

    def correct_docstrings(self):
    	"""Fixes endlines of docstrings.
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

    def correct_decorators(self):
        """Decorators should not include the function definition start,
        function definitions should not include the decorators.
        """
        for i in xrange(self.startline, self.endline+1):
            if len(re.findall("^\s*def\s", self.sourcelines[i])) == 1:
                self.endline = i - 1
                self.parent.startline = i
                break

    def correct_col_offset(self):
        """Fixes col_offset issues where it would be -1 for multiline strings.
        """
        blanks = re.findall("^\s*", self.sourcelines[self.startline])[0]
        self.astnode.col_offset = len(blanks)

    def correct(self):
        """ ixes ast issues.
        """
        self.handle_upside_down_ness()
        self.remove_trailing_blanklines()
        # Deal with wrong start for Docstrings:
        if isinstance(self.astnode, _ast.Expr) and \
           isinstance(self.astnode.value, _ast.Str):
            self.correct_docstrings()
        # Deal with decorator line numbers:
        if (isinstance(self.astnode, _ast.Call) and \
           isinstance(self.parent.astnode, _ast.FunctionDef)) \
        or (isinstance(self.astnode, _ast.Name) and \
           isinstance(self.parent.astnode, _ast.FunctionDef)):
            self.correct_decorators()
        # Multiline expressions have wrong col_offset
        if isinstance(self.astnode, _ast.Expr) and \
           self.astnode.col_offset < 0:
            self.correct_col_offset()

    def codelines(self):
        """Returns the lines of code that are associated with the node.
        """
        return self.sourcelines[self.startline:self.endline+1]

    def __repr__(self):
        """Returns a nodes representation.
        """
        return "%s (%s-%s)" % ( \
                self.astnode.__class__.__name__, 
                self.startline+self.offset,
                self.endline+self.offset, 
                )

    def dump(self):
        """Nice for debugging.
        """
        print "--- %d (%d) %s (parent: %s)" % (
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
        for l in xrange(self.startline, self.endline+1):
            print "%03d:%s" % (l + self.offset, repr(self.sourcelines[l])[1:-1])


class GoParser(object):

    def __init__(self, source, filename):
        """Creates a parser object.
        """
        self.source = source
        self.filename = filename
        self.removeblanks()
        self.nodes = []

    def walk(self, parent, nodes, start, end, ind):
        """ Iterates nodes of the abstract syntax tree
        """
#         try:
        nodecount = len(nodes)
#         except TypeError:
# #            print "avoiding %s - no lineno - break!" % repr(nodes)
#             return

        for i in xrange(nodecount):
            current = nodes[i]

            if not hasattr(current, 'lineno'):
 #               print "avoiding %s - no lineno - break!" % repr(current)
                continue

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
                    )
            mnode.dump()
            if parent == None:
                self.nodes.append(mnode)

            next_set = []
            for field in current._fields:
                next_item = getattr(current, field, None)
                if type(next_item) == type([]):
                    for item in getattr(current, field, []):
                        if hasattr(item, 'lineno'):
                            next_set.append([item.lineno, item])
            next_set.sort()
            next_set = [i[1] for i in next_set]
            self.walk(mnode, next_set, start, nend, ind + 1)

            # if hasattr(current, 'body'):
            #     self.walk(current.body, start, nend, ind + 1)
            # # if hasattr(current, 'handlers'):
            # #     self.walk(current.handlers, start, nend, ind + 1)

    def removeblanks(self):
        """Removes trailing blank lines and rstrips source code. This
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

    def parsegen(self):
        """Reads the input file, parses it and calls a generator method on
        each node.
        """
        astt = ast.parse(self.source, self.filename)
        self.lines = [''] + self.lines
        self.walk(None, astt.body, 1, self.endline, 0)


def main(filename):
    """The module can be called with a filename of a python file for testing.
    """
    fileinst = open(filename,'r')
    source = fileinst.read()
    fileinst.close()

    P = GoParser(source, filename)
    P.parsegen()

    print repr(P.nodes)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        filename = __file__
    else:
        filename = sys.argv[1]
    main(filename)
