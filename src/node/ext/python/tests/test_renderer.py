import unittest


class TestBaseRenderer(unittest.TestCase):
    """
    test renderer.py:BaseRenderer from node.ext.python
    """

    def test__init__(self):
        from node.ext.python.renderer import BaseRenderer
        model = "some model?"  # XXX give it a proper model
        br = BaseRenderer(model)
        self.assertTrue('<node.ext.python.renderer.BaseRenderer object at' in str(br))

    def test__call__(self):
        from node.ext.python.renderer import BaseRenderer
        model = "some model?"  # XXX give it a proper model
        br = BaseRenderer(model)
        #print br
        #br()
        #self.assertRaises(NotImplemented)
#
#
#        with self.assertRaises(NotImplemented) as ni:
#            br()
#        print ni
#


    def _calcpostlf(self):
        pass


if __name__ == '__main__':
    unittest.main()
