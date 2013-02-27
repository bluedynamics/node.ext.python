import unittest


class TestGoParser(unittest.TestCase):
    """
    tests for the goparser.GoParser
    """

    def setUp(self):
        """
        set up stuff for testing
        """
        pass

    def test_strip_comments(self):
        """
        Strip comment should remove comments from
        a single line of code. As far as i remember...
        """
        from node.ext.python.goparser import metanode
        print "Hallo!"
        mn = metanode(None, None, do_correct=False)
        a = "foo = 2  # my awesome comment"
        print a
        result = mn.strip_comments(a)
        # import pdb;pdb.set_trace()
        print repr(result)
        self.assertTrue(a == "foo = 2")

    def test_is_empty(self):
        """
        Test if a line is empty.
        """
        from node.ext.python.goparser import metanode
        mn = metanode(None, None, do_correct=False)
        a = "foo = 2  # my awesome comment"
        print a
        result = mn.is_empty(a)
        self.assertFalse(False)
        a = ""
        print a
        result = mn.is_empty(a)
        self.assertTrue(result)
        a = "      "
        print a
        result = mn.is_empty(a)
        self.assertTrue(result)

    def tearDown(self):
        """
        clean up after tests
        """
        pass


class TestGofooParser(unittest.TestCase):
    """
    tests for the goparser.GoParser
    """

    def setUp(self):
        """
        set up stuff for testing
        """
        pass

    def test_foo(self):
        """
        test some aspect of foo
        """
        self.assertTrue(1)

    def tearDown(self):
        """
        clean up after tests
        """
        pass


if __name__ == '__main__':
    unittest.main()
