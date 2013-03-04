import unittest
"""
tests for classes in node.ext.python.nodes.py
"""


class TestPythonNode(unittest.TestCase):
    """
    tests for node.ext.python.nodes.py:PythonNode
    """

    # def test__init__(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.__init__
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )
    #     self.assertTrue(pn)
    #     # XXX TODO: test the case when "astnode is not None and ..."

    # def test__call__(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.__call__
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )
    #     #result = pn()
    #     #print result
    #     #self.assertTrue(pn)
    #     # XXX TODO: make this test make some sense
    #     pass

    def test_startlineno_is_None(self):
        """
        test node.ext.python.nodes.py:PythonNode.startlineno
        in case startlineno is None
        """
        from node.ext.python.nodes import PythonNode
        pn = PythonNode(
            'some_name'  # give it some name
        )
        result = pn.startlineno
        self.assertTrue(result is None)

    def test_startlineno_is_not_None(self):
        """
        test node.ext.python.nodes.py:PythonNode.startlineno
        in case startlineno is NOT None
        """
        from node.ext.python.nodes import PythonNode
        pn = PythonNode(
            'some_name'  # give it some name
        )
        # XXX do something to make startlineno not None, e.g. insert content
        result = pn.startlineno
        self.assertTrue(result is not None)

    def test_endlineno_is_None(self):
        """
        test node.ext.python.nodes.py:PythonNode.endlineno
        """
        from node.ext.python.nodes import PythonNode
        pn = PythonNode(
            'some_name'  # give it some name
        )
        result = pn.endlineno
        self.assertTrue(result is None)

    # def test_indent(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.indent
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     from node.ext.python.parser import BaseParser
    #     prsr = BaseParser(
    #         "foomodel"  # a model
    #     )
    #     pn = PythonNode(
    #         'some_name',  # give it some name
    #         parser=prsr  # a parser
    #     )
    #     result = pn.indent
    #     self.assertTrue(result is None)

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )

    # def test_(self):
    #     """
    #     test node.ext.python.nodes.py:PythonNode.
    #     """
    #     from node.ext.python.nodes import PythonNode
    #     pn = PythonNode(
    #         'some_name'  # give it some name
    #     )


class TestModule(unittest.TestCase):
    """
    tests for node.ext.python.nodes.py:Module
    """

    # def test__init__(self):
    #     """
    #     test node.ext.python.nodes.py:Module.__init__
    #     """
    #     from node.ext.python.nodes import Module
    #     pm = Module('fooparser')
    #     pm.rendererfactory._write_file = False
    #     print pm()
    #     self.assertTrue(pm)

    # def test_modulename(self):
    #     """
    #     test node.ext.python.nodes.py:Module.modulename
    #     """
    #     from node.ext.python.nodes import Module
    #     pm = Module('fooparser')
    #     pm.modulename()


class TestDocstring(unittest.TestCase):
    """
    tests for node.ext.python.nodes.py:Docstring
    """

    _my_docstring = """this is a sample docstring
    """

    def test__init__(self):
        """
        test node.ext.python.nodes.py:Docstring.__init__
        """
        from node.ext.python import Docstring
        ds = Docstring()
        #print ds()
        self.assertEqual(
            ds(),
            u'"""\n"""\n'
        )

    def test_get_lines(self):
        """
        test node.ext.python.nodes.py:Docstring._get_lines
        """
        from node.ext.python import Docstring
        ds = Docstring('fooparser')
        result = ds._get_lines()
        self.assertEqual(result, [])

    def test_startlineno(self):
        from node.ext.python import Docstring
        ds = Docstring()
        result = ds.startlineno
        #print result
        self.assertTrue(result is None)

    # def test_get_bufstart(self):
    #     from node.ext.python import Docstring
    #     ds = Docstring()
    #     result = ds._get_bufstart()
    #     print result
    def test_bufstart(self):
        from node.ext.python import Docstring
        ds = Docstring()
        result = ds.bufstart
        #print result
        self.assertTrue(result is None)

    def test_get_text_empty(self):
        """
        test node.ext.python.nodes.py:Docstring is empty by default
        """
        from node.ext.python import Docstring
        ds = Docstring()
        self.assertEqual(ds.text, u'')

    def test_set_text(self):
        """
        test node.ext.python.nodes.py:Docstring can be set to some text
        """
        from node.ext.python import Docstring
        ds = Docstring()
        ds.text = u'\n\n\na\nb\n\n\n\n'
        self.assertEqual(ds.text, u'a\nb')

    def test_set_lines(self):
        """
        test node.ext.python.nodes.py:Docstring can take some lines
        """
        from node.ext.python import Docstring
        ds = Docstring()
        ds.lines = [u'a', u'b', u'c']
        self.assertEqual(ds.lines, [u'a', u'b', u'c'])
        self.assertEqual(ds.text, u'a\nb\nc')
        ds.text = u'I am a docstring.\n\nSome Documentation.'
        self.assertEqual(ds.text, u'I am a docstring.\n\nSome Documentation.')
        self.assertEqual(
            ds.lines,
            [u'I am a docstring.', u'', u'Some Documentation.']
        )


class TestBlock(unittest.TestCase):
    """
    test node.ext.python.nodes.py:Block
    """

    def test_block(self):
        from node.ext.python import Block
        bl = Block()
        self.assertEqual(bl(), u'')
        self.assertEqual(bl.text, u'')
        self.assertEqual(bl.lines, [])
        # set some values
        bl.lines = [u'a', u'b', u'c']
        self.assertEqual(bl.text, u'a\nb\nc')
        self.assertEqual(bl.lines, [u'a', u'b', u'c'])
        # set some other text
        bl.text = u'if foo is None:\n    foo = 0'
        self.assertEqual(bl.text, u'if foo is None:\n    foo = 0')
        self.assertEqual(
            bl.lines,
            [
                u'if foo is None:',
                u'    foo = 0'
            ]
        )


class TestProtectedSection(unittest.TestCase):
    """
    test node.ext.python.nodes.py:ProtectedSection
    """

#    def test_init_incomplete(self):
#        from node.ext.python import ProtectedSection
#
#        with self.assertRaises(Incomplete, ps):
#            ps = ProtectedSection()()
# XXX
# http://docs.python.org/2/library/unittest.html#unittest.TestCase.assertRaises

    def test_init(self):
        from node.ext.python import ProtectedSection
        ps = ProtectedSection('section-1')
        result = ps()
        self.assertEqual(  # check auto-generated comment for protected code
            result,
            u'##code-section section-1\n##/code-section section-1\n'
        )
        result_lines = ps.lines
        self.assertEqual(  # check default: empty set of lines
            result_lines,
            []
        )

        result_text = ps.text
        self.assertEqual(  # check default: empty text
            result_text,
            u''
        )

        ps.lines = [u'a', u'b', u'c']  # set some lines
        self.assertEqual(
            ps.lines,
            [u'a', u'b', u'c']
        )
        self.assertEqual(
            ps.text,
            u'a\nb\nc'
        )

        ps.text = u'from foo import bar'
        self.assertEqual(
            ps.lines,
            [u'from foo import bar']
        )
        self.assertEqual(
            ps.text,
            u'from foo import bar'
        )



#    def test_init2(self):
#        # import class directly; somehow fails all needed imports? XXX
#        from node.ext.python.nodes import ProtectedSection
#        sec = ProtectedSection('section-1')
#        result = sec()
#        self.assertEqual(
#            result,
#            u'##code-section section-1\n##/code-section section-1\n'
#        )


if __name__ == '__main__':
    unittest.main()
