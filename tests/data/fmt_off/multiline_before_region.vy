@external
def foo():
    x: uint256 = [
        1,
        2,
    ][0]
    # fmt: off
    y:    uint256     =     2
    # fmt: on
    z:     uint256 = 3
# output
@external
def foo():
    x: uint256 = [
        1,
        2,
    ][0]
    # fmt: off
    y:    uint256     =     2
    # fmt: on
    z: uint256 = 3
