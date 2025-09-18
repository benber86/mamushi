@external
def foo():
    _ :  uint256   = 1
    ___ : uint256 = 2
    _, _ , a = foo()
# output
@external
def foo():
    _: uint256 = 1
    ___: uint256 = 2
    _, _, a = foo()
