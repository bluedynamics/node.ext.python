import unittest


class TestWalker(unittest.TestCase):
    """
    tests for node.ext.python.gowalker.py:Walker
    """
    def test__init__(self):
        """
        test gowalker.Walker.init()
        """
        from node.ext.python.gowalker import Walker
        filename = "foo.py"  # just some filename, nonexistant
        wlkr = Walker(filename)
        self.assertTrue(wlkr)  # is it sufficient to test for True? XXX

    def test_createNodeByType(self):
        """
        test gowalker.Walker.createNodeByType()
        """
        from node.ext.python.gowalker import Walker
        filename = "foo.py"  # just some filename, nonexistant
        wlkr = Walker(filename)
        wlkr.createNodeByType(
            "gopnodefoo",  # gopnode
            # force (default: None)
        )
        import pdb;pdb.set_trace()
        self.assertTrue(wlkr)  # is it sufficient to test for True? XXX
