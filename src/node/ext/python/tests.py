import os
import unittest
import doctest
import zope.component
from pprint import pprint
from interlude import interact


optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE


TESTFILES = [
    'renderer.rst',
    'parser.rst',
    'goparser.rst',
    'edgecases.rst',
    'nodes.rst',
    'utils.rst',
]


datadir = os.path.join(os.path.dirname(__file__), 'testing', 'data')


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint,
                   'datadir': datadir},
        ) for file in TESTFILES
    ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
