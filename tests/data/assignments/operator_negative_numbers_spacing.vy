@external
def foo(x: int256) -> int256:
    c: uint256 = as_wei_value(     0.0375,   "ether")
    if x <= -  41_446_531_673_892_822_313:
        return empty(int256)
    a: int256 = x + (  - 123)
    b: int256 = 100 * - 2
    return a * - b * -convert(1e-8, int256)
# output
@external
def foo(x: int256) -> int256:
    c: uint256 = as_wei_value(0.0375, "ether")
    if x <= -41_446_531_673_892_822_313:
        return empty(int256)
    a: int256 = x + (-123)
    b: int256 = 100 * -2
    return a * -b * -convert(1e-8, int256)
