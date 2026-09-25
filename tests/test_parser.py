import pytest
from mamushi import compare_ast


@pytest.mark.parametrize("module", ["contracts.utils", ".", "..utils"])
@pytest.mark.parametrize(
    "names",
    [
        "constants",
        "constants as c",
        "constants, roles",
        "constants as c, roles",
        "constants, roles as r",
        "constants as c, roles as r, permissions",
    ],
)
def test_from_import_parentheses_preserve_ast(module, names):
    assert compare_ast(
        f"from {module} import {names}\n",
        f"from {module} import ({names})\n",
    )


def test_comparator():
    test_input = """
# @version=0.0.1
@internal
def a():
    '''test'''
    pass
    """
    should_parse_similarly = """
# @version=0.0.1

# test

@internal
def a():
    '''docstring text does not count'''
    pass  # test
    """
    should_not_parse_similarly = """
# @version=0.0.1
@external
def b():
    pass
    """
    assert compare_ast(test_input, test_input)
    assert compare_ast(test_input, should_parse_similarly)
    assert not compare_ast(test_input, should_not_parse_similarly)
