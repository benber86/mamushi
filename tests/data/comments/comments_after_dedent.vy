@internal
def foo(hi: uint256, lo: uint256) -> uint256:
    for iteration: uint256 in range(10):
        if unsafe_sub(hi, lo) <= 1:
            return hi
        # comment A
        # comment B
        y_new: uint256 = 0
    return 0
