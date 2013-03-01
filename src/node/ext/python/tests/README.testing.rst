===============
A Note on tests
===============

During artsprint 2013 I sat down with gogo to look at the goparser.
And look at tests. We set up some unit tests, to get the parser going.

You can actually run the tests with the enhanced python (pyagx)
built by buildout, just by calling the test file:
(because we put a if __name__ == '"__main__" in it.)
::

   agx.dev$ bin/pyagx devsrc/node.ext.python/src/node/ext/python/tests/test_goparser.py


You will receive output like the following:
::
|   ....
|   []
|   .......E.....F..-------before------------------
|   I am a multiline string object
|        with quite a few trailing blank lines
|
|
|        
|   -------------------------
|   -------after------------------
|   I am a multiline string object
|        with quite a few trailing blank lines
|
|
|        
|   -------------------------
|   FF.
|   ======================================================================
|   ERROR: test_correct_docstrings (__main__.TestMetanode)
|   ----------------------------------------------------------------------
|   Traceback (most recent call last):
|     File "devsrc/node.ext.python/src/node/ext/python/tests/test_goparser.py", line 148, in test_correct_docstrings
|       mn.correct_docstrings()
|     File "/opt/agx/agx.dev/devsrc/node.ext.python/src/node/ext/python/goparser.py", line 98, in correct_docstrings
|       while self.is_empty(self.strip_comments(self.sourcelines[e])):
|   TypeError: string indices must be integers, not NoneType
|
|   ======================================================================
|   FAIL: test__init__ (__main__.TestGoParser)
|   ----------------------------------------------------------------------
|   Traceback (most recent call last):
|     File "devsrc/node.ext.python/src/node/ext/python/tests/test_goparser.py", line 242, in test__init__
|       self.assertTrue(0)
|   AssertionError: 0 is not true
|
|   ----------------------------------------------------------------------
|   Ran 32 tests in 0.658s
|
|   FAILED (failures=5, errors=1)


The last line is important :-)



Nose and Nosetests
==================

You can get much better output, not only to screen, but also files (even html)
telling you about the **coverage** your tests have on your code.
Failing tests will verbosely present their output. 
(Hint: while writing tests, you sometimes want to make a test fail
to actually see the output of print statements) 
::
|   ======================================================================
|   FAIL: test for goparser.metanode:remove_trailing_blanklines
|   ----------------------------------------------------------------------
|   Traceback (most recent call last):
|     File "/opt/agx/agx.dev/devsrc/node.ext.python/src/node/ext/python/tests/test_goparser.py", line 127, in test_remove_trailing_blanklines
|       self.assertNotEquals(schmoo, mn.sourcelines)
|   AssertionError: 'I am a multiline string object\n        with quite a few trailing blank lines\n\n\n        ' == 'I am a multiline string object\n        with quite a few trailing blank lines\n\n\n        '
|   -------------------- >> begin captured stdout << ---------------------
|   
|                 ------- before remove_trailing_blanklines() ------------------
|                 
|   I am a multiline string object
|           with quite a few trailing blank lines
|   
|   
|           
|   -------------------------------------------------------------
|   ------- after remove_trailing_blanklines() ------------------
|   I am a multiline string object
|           with quite a few trailing blank lines
|   
|   
|           
|   -------------------------------------------------------------
|   
|   --------------------- >> end captured stdout << ----------------------
|   
|   ======================================================================
|   FAIL: Strip comment should remove comments from
|   ----------------------------------------------------------------------
|   Traceback (most recent call last):
|     File "/opt/agx/agx.dev/devsrc/node.ext.python/src/node/ext/python/tests/test_goparser.py", line 65, in test_strip_comments_if_one_exists
|       self.assertTrue(result == "foo = 2")
|   AssertionError: False is not true
|   
|   Name                         Stmts   Miss  Cover   Missing
|   ----------------------------------------------------------
|   node.ext.python                 24      0   100%   
|   node.ext.python.gonodes        212    142    33%   49-58, 62, 66, 70, 74-79, 82, 85, 88, 91-94, 97-100, 103-106, 109-112, 116-121, 124, 141, 147, 153-157, 160-161, 164-168, 171-172, 175-193, 204-205, 209-219, 226, 233, 240-243, 250-264, 268-271, 274-287, 294-300, 330, 337-341, 370-382, 386, 389
|   node.ext.python.goparser       229    138    40%   80, 87-89, 99-113, 119-124, 132-154, 159-160, 167-184, 189, 194, 200, 207-214, 221, 232-262, 279-321, 366-369, 375-382, 385-393, 396-400, 403-408, 412-413, 421-429, 434, 439-442, 448-455, 458-463
|   node.ext.python.interfaces      65      0   100%   
|   node.ext.python.nodes          484    367    24%   41-50, 53, 57-59, 63, 67-71, 75-80, 83, 86, 89, 92-95, 98-101, 104-107, 110-113, 116-121, 125-146, 157-169, 173-175, 179-187, 190, 194, 200, 206-208, 211-212, 215-219, 222-223, 234-241, 244-261, 267-281, 284, 287, 299-305, 308-325, 336-343, 346-364, 370-373, 377-380, 389-396, 399-402, 405, 411, 415-420, 431-434, 437-469, 472-483, 492, 495-498, 501-502, 511-518, 522, 526-537, 540, 549-556, 559-562, 566-573, 576-579, 582, 588, 592-601, 610-618, 621-627, 630, 636-639, 643-650, 659-666, 670-673, 676-679, 683-685, 688
|   node.ext.python.parser         477    418    12%   46, 49, 52-83, 86-88, 91-101, 104-117, 120-124, 127-146, 149-162, 165, 168-199, 202-206, 212, 221-226, 229-270, 273-280, 283-291, 294-331, 334-347, 350-378, 381-394, 400-407, 410-422, 428-446, 449-464, 467-474, 477-482, 488-504, 507-510, 513-519, 525-533, 536-552, 555-565, 571-589, 592-602
|   node.ext.python.renderer       324    284    12%   22, 25, 28-53, 61-74, 80-92, 98-116, 122-127, 133-167, 174-178, 181-183, 186-190, 193-196, 199-222, 225-261, 267, 270-297, 303, 306-321, 327, 330-373, 379-413
|   ----------------------------------------------------------
|   TOTAL                         1815   1349    26%   
|   ----------------------------------------------------------------------
|   Ran 32 tests in 0.594s
|   
|   FAILED (errors=1, failures=5)
|   christoph@s3:/opt/agx/agx.dev$ bin/nosetests devsrc/node.ext.python/src/node/ext/python/tests/ --with-coverage --cover-package=node.ext.python


The listing shows all the packages and files we want to see coverage information for,
showing the lines of code that were **not** run.
This way you can easily find bad spots in your code,
like branches that were never visited.



Continuous Integration
======================

If you run tests on a regular basis, like after each push to your repository,
you might also want to have some fancy output.
Maybe a graph of successful and failing tests.

check the options nose offers by asking for --help.


Unittest common assertions
==========================

When writing unittests, at the end of (or even during) each test,
you tests for certain conditions to be True, False, for parameters to be equal
and so on. Look at the documentation to figure out possible options:

`Unittest TestCase methods to check for and report failures <http://docs.python.org/2/library/unittest.html#unittest.TestCase.debug>`_ 
