@internal
def foo(hi: uint256, lo: uint256) -> uint256:
    for i: uint256 in range(10):
        if unsafe_sub(hi, lo) <= 1:
            return hi

        # keeps the blank line above
        y_new: uint256 = 0

        if y_new > 0:
            return y_new


        # keeps both blank lines above
        hi = y_new
    return 0
