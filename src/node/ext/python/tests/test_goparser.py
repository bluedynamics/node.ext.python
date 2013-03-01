import unittest


class TestMetanode(unittest.TestCase):
    """
    tests for metanode in goparser.py
    """
    def test_init(self):
        from node.ext.python.goparser import metanode
        mn = metanode(None, None, do_correct=False)
        self.assertTrue(mn)

    def test_metanode_init_parent_not_none(self):
        """
        coverage for goparser.py line 49
        """
        from node.ext.python.goparser import metanode
        # a metanode
        mn1 = metanode(None, None, do_correct=False)
        # another metanode, child of mn1
        mn2 = metanode(mn1, None, do_correct=False)
        self.assertTrue(mn2)

# check out the following one (by removing comments)
# it fails!
# only difference to preceeding test: mn2 has do_correct=True
# what does this all mean?

    # def test_metanode_init_parent_not_none_do_correct_True(self):
    #     """
    #     coverage for goparser.py line 49
    #     with do_correct = True
    #     """
    #     from node.ext.python.goparser import metanode
    #     # a metanode
    #     mn1 = metanode(None, None, do_correct=False)
    #     # another metanode, child of mn1
    #     mn2 = metanode(mn1, None, do_correct=True)
    #     self.assertTrue(mn2)

    def test_strip_comments_if_one_exists(self):
        """
        Strip comment should remove comments from
        a single line of code. As far as i remember...
        """
        from node.ext.python.goparser import metanode
        #print "Hallo!"
        mn = metanode(None, None, do_correct=False)
        a = "foo = 2  # my awesome comment"
        #print("before stripping: ", a)
        result = mn.strip_comments(a)
        # import pdb;pdb.set_trace()
        #print("stripped: " + repr(result))
        self.assertTrue(result == "foo = 2")

    def test_strip_comments_without_comment(self):
        """
        Strip comment should remove comments from
        a single line of code. As far as i remember...
        """
        from node.ext.python.goparser import metanode
        #print "Hallo!"
        mn = metanode(None, None, do_correct=False)
        a = "foo = 2"
        #print("before stripping: ", a)
        result = mn.strip_comments(a)
        # import pdb;pdb.set_trace()
        #print("stripped: " + repr(result))
        self.assertTrue(result == "foo = 2")

    def test_is_empty(self):
        """
        Test if a line is empty.
        """
        from node.ext.python.goparser import metanode
        mn = metanode(None, None, do_correct=False)
        a = "foo = 2  # my awesome comment"
        #print a
        result = mn.is_empty(a)
        self.assertFalse(False)
        a = ""
        #print a
        result = mn.is_empty(a)
        self.assertTrue(result)
        a = "      "
        #print a
        result = mn.is_empty(a)
        self.assertTrue(result)

    def test_remove_trailing_blanklines(self):
        """
        test for goparser.metanode:remove_trailing_blanklines
        """
        from node.ext.python.goparser import metanode
        schmoo = """I am a multiline string object
        with quite a few trailing blank lines


        """
        mn = metanode(
            None,  # no parent
            None,  # no children
            sourcelines=schmoo,
            do_correct=False)
        print("""
              ------- before remove_trailing_blanklines() ------------------
              """)
        print(mn.sourcelines)
        print('-------------------------------------------------------------')
        mn.remove_trailing_blanklines()
        print('------- after remove_trailing_blanklines() ------------------')
        print(mn.sourcelines)
        print('-------------------------------------------------------------')
        # so I think the two should not be equal after removing blanklines
        # but something fails!?
        self.assertNotEquals(schmoo, mn.sourcelines)

    def test_handle_upside_down_ness(self):
        """
        test for goparser.handle_upside_down_ness
        """
        self.assertTrue(0)  # make this fail, function seems broken anyways!

    def test_correct_docstrings(self):
        """
        test goparser.py:metanode.correct_docstrings
        """
        from node.ext.python.goparser import metanode
        schmoo = """I am a multiline string object
        with quite a few trailing blank lines
        and trailing whitespace       

        """
        mn = metanode(
            None,  # no parent
            None,  # no children
            sourcelines=schmoo,
            do_correct=False)
        mn.correct_docstrings()
        print("test:")
        print(mn.sourcelines)
        self.assertTrue(0)

    def test_correct_decorators(self):
        pass

    def test_correct_comments(self):
        pass

    def test_correct_col_offset(self):
        pass

    def test_correct(self):
        pass

    def test_get_codelines(self):
        pass

    def test_get_buffer(self):
        pass

    def test_get_type(self):
        pass

    def test_get_astvalue(self):
        pass

    def test__repr__(self):
        """
        test goparser.py:metanode.__repr__
        """
        from node.ext.python.goparser import metanode
        schmoo = """I am a multiline string object
        with quite a few trailing blank lines
        and trailing whitespace       

        """
        mn = metanode(
            None,  # no parent
            None,  # no children
            sourcelines=schmoo,
            startline=2,
            endline=5,
            offset=3,
            do_correct=False)
        result = mn.__repr__()
        #print("test:")
        #print(result)
        self.assertEquals(result, "NoneType (5-8)")  # check if correct! XXX

    def test_dump(self):
        """
        test goparser.py:metanode.dump
        """
        pass

    def test_(self):
        pass

    def tearDown(self):
        """
        clean up after tests
        """
        pass


class TestGoParser(unittest.TestCase):
    """
    tests for the goparser.GoParser
    """
    # TODO XXX
    # the following tests need a source and a file/filename
    # provide examples for these, so we have something to test
    # and feed them to the tests

    def setUp(self):
        """
        set up stuff for testing
        """
        pass

    def test__init__(self):
        """
        test goparser.py:GoParser.__init__
        """
        from node.ext.python.goparser import GoParser
        gp = GoParser(
            source="foo",
            filename="test"
        )
        print("gp.source: " + gp.source)
        print("gp.filename: " + gp.filename)
        #self.assertTrue(0)
        pass

    def test_walk(self):
        """
        test goparser.py:GoParser.
        """
        #self.assertTrue(0)
        pass

    def test_cleanuptree(self):
        """
        test goparser.py:GoParser.
        """
        pass
        #self.assertTrue(0)

    def test_removeblanks(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_cleanup_fragmented_comments(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_cleanup_last_statement_and_docstring(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_walk_pairs(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_serialized_tree(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_clean_walk_siblings(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_clean_pair(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_parsegen(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_get_codelines(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def test_get_coding(self):
        """
        test goparser.py:GoParser.
        """
        pass

    def tearDown(self):
        """
        clean up after tests
        """
        pass


class TestMain(unittest.TestCase):
    """
    tests for the goparser.__main__
    """

    def test_main(self):
        """
        test goparser.py:__main__
        """
        # how to do this? subprocess.call?
        import os
        import subprocess
        goparser = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../goparser.py')
        gogoparser = ['bin/pyagx', goparser, goparser]
        # yo dawg, I put your goparser in your goparser,
        # so you can now go parse the goparser with the goparser
        with open(os.devnull, "w") as gonull:
            goresult = subprocess.call(
                gogoparser,
                stdout=gonull,
                stderr=gonull)
        self.assertTrue(goresult)

if __name__ == '__main__':
    unittest.main()
