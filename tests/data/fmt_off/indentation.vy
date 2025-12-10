@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    z:uint256=3
    # fmt: on
    a: uint256       =        4
# output
@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    z:uint256=3
    # fmt: on
    a: uint256 = 4
