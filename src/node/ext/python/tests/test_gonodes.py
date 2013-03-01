import unittest


class TestPythonNode(unittest.TestCase):
    """
    tests gonodes.py:PythonNode
    """
    def test__init__(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertTrue(pn)

    def test_startlineno(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertIsNone(pn.startlineno)

    def test_endlineno(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertIsNone(pn.endlineno)

    def test_indent_is_None(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertIsNone(pn.indent)

    def test_nodelevel(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.nodelevel, 0)

    def test_docstrings(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.docstrings(), [])

    def test_blocks(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.blocks(), [])

    def test_imports(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.imports(), [])

    def test_protectedsections(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode(name='foo')
        self.assertEquals(pn.protectedsections(), [])

    def test_classes(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.classes(), [])

    def test_functions(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.functions(), [])

    def test_attributes(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.attributes(), [])

    def test_acquire(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.acquire(), [])

    def test_get_type(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.get_type(), 'PythonNode')

    def test__str__(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(
            pn.__str__(),
            'No indent<PythonNode [No bufstart:No bufend]>'
        )

    def test__call__(self):
        from node.ext.python.gonodes import PythonNode
        pn = PythonNode()
        self.assertEquals(pn.__call__(), [])


class Test_TextMixin(unittest.TestCase):
    """
    tests for gonodes.py:_TextMixin
    """
    def test_set_lines(self):
        pass


class Test_Block(unittest.TestCase):
    """
    tests for gonodes.py:Block
    """
    #def test__init__(self):
    #    pass

    def test_noderepr(self):
        from node.ext.python.gonodes import Block
        bl = Block()  # XXX: set up a proper Block for this test
        #self.assertEqual(bl.noderepr, "foo")
        bl


class Test_Class(unittest.TestCase):
    """
    tests for gonodes.py:Class
    """
    def test__init__(self):
        from node.ext.python.gonodes import Class
        cl = Class()  # XXX: set up a proper Class for this test
        #self.assertEqual(bl.noderepr, "bar")
        cl


class Test_Decorator(unittest.TestCase):
    """
    tests for gonodes.py:Decorator
    """
    def test__init__(self):
        from node.ext.python.gonodes import Decorator
        de = Decorator()  # XXX: set up a proper Class for this test
        #self.assertEqual(de, "bar")  # XXX: test something
        de


class Test_ProtectedSection(unittest.TestCase):
    """
    tests for gonodes.py:ProtectedSection
    """
    def test__init__(self):
        from node.ext.python.gonodes import ProtectedSection
        ps = ProtectedSection()  # XXX: set up a ProtectedSection for this test
        ps

    def test__init__with_args(self):
        from node.ext.python.gonodes import ProtectedSection
        ps = ProtectedSection(foo='bar')  # XXX:
        # set up a ProtectedSection for this test
        # and choose some usefull args
        ps


class Test_Function(unittest.TestCase):
    """
    tests for gonodes.py:_TextMixin
    """
    def test__init__(self):
        from node.ext.python.gonodes import Function
        #ds = Function()  # XXX

    def test_decorators(self):
        from node.ext.python.gonodes import Function
        #ds = Function()  # XXX
        #self.assertTrue(ds.decorators())

    def test__str__(self):
        from node.ext.python.gonodes import Function
        #ds = Function()  # XXX
        #self.assertTrue(ds.__str__())


class Test_Docstring(unittest.TestCase):
    """
    tests for gonodes.py:_TextMixin
    """
    def test_it(self):
        from node.ext.python.gonodes import Docstring
        ds = Docstring()
