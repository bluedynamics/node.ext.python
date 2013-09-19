import unittest


class TestBaseParser(unittest.TestCase):
    """
    tests for node.ext.python.parser.py:BaseParser
    """

    def test_init(self):
        """
        testing the BaseParsers init function
        """
        from node.ext.python.parser import BaseParser
        bp = BaseParser(
            'parsermodel'  # parameter 'model'
        )
        self.assertTrue(bp)

    def test_call(self):
        """
        testing the BaseParsers call function:
        not ment to be called!
        """
        from node.ext.python.parser import BaseParser
        bp = BaseParser(
            'parsermodel'  # parameter 'model'
        )
        self.assertTrue(bp)
        #self.assertRaises(NotImplemented, bp)
        #with self.assertRaises(NotImplemented) as context:
        #    bp()
        #self.assertEqual(
        #    context.exception.message,
        #    'BaseParser does not implement ``__call__``'
        #)
        # XXX make this work
        # is NotImplemented a real exception???
        pass

    def test_createastchild(self):
        from node.ext.python.parser import BaseParser
        bp = BaseParser(
            'parsemodel'  # param 'model'
        )
        # XXX how to test this?
        self.assertTrue(bp)


class Test_ImportParser(unittest.TestCase):
    """
    tests for node.ext.python.parser.py:ImportParser
    """
    def test_call(self):
        """ test the ImportParser
        """
        pass

    def test_definitionends(self):
        """test the _definitionends function in ImportParser
        """
        from node.ext.python.parser import ImportParser
        ip = ImportParser(
            model="foo"
        )
        self.assertTrue(ip)
        # XXX test for something  specific to ImportParser


class Test_AttributeParser(unittest.TestCase):
    """
    tests for node.ext.python.parser.py:AttributeParser
    """
    def test_call(self):
        """ test the AttributeParser
        """
        from node.ext.python.parser import AttributeParser
        ap = AttributeParser(  # XXX give it some astnode! how?
            model="foo"
        )
        #ap()
        self.assertTrue(ap)

        pass

    def test_findattributeend(self):
        """test the _definitionends function in AttributeParser
        """
        from node.ext.python.parser import AttributeParser
        ap = AttributeParser(
            model="foo"
        )
        self.assertTrue(ap)
        # XXX test for something  specific to AttributeParser


class Test_ModuleParser(unittest.TestCase):
    """
    tests for node.ext.python.parser.py:ModuleParser
    """
    def test_call(self):
        """ test the ModuleParser
        """
        pass

    def test_parse(self):
        """
        test the _parse function in ModuleParser
        """
        from node.ext.python.parser import ModuleParser
        mp = ModuleParser(
            model="foo"
        )
        self.assertTrue(mp)
        # XXX test for something  specific to ModuleParser

    def test_extractencoding(self):
        """
        test the _extractencoding function in ModuleParser

        XXX honestly, maybe I'm doing otherwise, but it gets partly covered
        """
        import os
        modulepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..',
            'testing', 'data', 'parseme.py')
        from node.ext.python import Module
        Module._do_parse = False  # disable auto-parsing

        module = Module(modulepath)
        self.assertTrue(module)
        # read the file
        file = open(module.filepath, 'r')
        module._buffer = file.readlines()
        file.close()
        print("module.buffer: ")
        print module.buffer  # yields None ??? XXX

        print(dir(module))
        #print("module.encoding: ")
        #print module.encoding
        self.assertEquals(module.encoding, 'utf-8')
        #
        #
        #
        # trying to get an astnode to work...........
        #import ast
        #module.astnode = ast.parse(''.join(module.buffer))
        #print("dir(module.astnode):")
        #print(dir(module.astnode))


class Test_ClassParser(unittest.TestCase):
    """
    tests for node.ext.python.parser.py:ClassParser
    """
    def test_call(self):
        """ test the ClassParser
        """
        from node.ext.python.parser import ClassParser
        cp = ClassParser(
            model='foo'  # how to instantiate this the right way?
        )
        self.assertTrue(cp)

    def test_definitionends(self):
        """
        test the _parse function in ClassParser
        """
        from node.ext.python.parser import ClassParser
        cp = ClassParser(
            model="foo"
        )
        #print(help(cp.model))
        #print(dir(cp.model))
        import ast
        cp.model.astnode = ast.parse(''.join(cp.buffer))
        self.assertTrue(False)
        self.assertTrue(cp)
        # XXX test for something  specific to ClassParser
