B: constant(uint256) = 2
@external
def foo() -> uint256:
    a: int256 = - B
    c: int256 = + a
    c = - 255
    c = -256 + 48
    return shift(256, -B)
# output
B: constant(uint256) = 2


@external
def foo() -> uint256:
    a: int256 = -B
    c: int256 = +a
    c = -255
    c = -256 + 48
    return shift(256, -B)
