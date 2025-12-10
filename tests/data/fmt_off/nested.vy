@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    # fmt: off
    z:      uint256      =      3    # inner region
    # fmt: on
    a:uint256=4  # outer region continues
    # fmt: on
    b: uint256     =      5
# output
@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    # fmt: off
    z:      uint256      =      3    # inner region
    # fmt: on
    a:uint256=4  # outer region continues
    # fmt: on
    b: uint256 = 5
