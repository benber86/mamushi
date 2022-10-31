@external
def foo():
    a: uint256[4] = [some_very_long_variable_name_that_will_require_splitting, element, another, more]
    b: uint256[4] = [1, 2, 3, 4]
# output
@external
def foo():
    a: uint256[4] = [
        some_very_long_variable_name_that_will_require_splitting,
        element,
        another,
        more,
    ]
    b: uint256[4] = [1, 2, 3, 4]
