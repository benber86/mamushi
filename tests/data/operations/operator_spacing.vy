@external
def foo():
    a: uint256 = 1+2-3/4*5%6&7^8|9
    b: uint256 = 10 ** 18
# output
@external
def foo():
    a: uint256 = 1 + 2 - 3 / 4 * 5 % 6 & 7 ^ 8 | 9
    b: uint256 = 10**18
