# @version 0.3.1
"""
TEST TEST
    TEST
            TEST
"""

def a():
    """
       -----------   docstring
 test
0
    """
    pass
# output
# @version 0.3.1

"""
TEST TEST
    TEST
            TEST
"""

def a():
    """
           -----------   docstring
     test
    0
    """
    pass
