@external
def foo():
    a: uint256[4] = [this_is_a_very_long_variable_which_will_force_a_delimiter_split, element, another, more]
    b: uint256[4] = [1, 2, 3, 4]
# output
@external
def foo():
    a: uint256[4] = [
        this_is_a_very_long_variable_which_will_force_a_delimiter_split,
        element,
        another,
        more
    ]
    b: uint256[4] = [1, 2, 3, 4]
