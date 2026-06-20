error Error1:
    caller: address
    # This should be indented
# This should not

error Error2:
    code: uint256

# This should not

@external
def fail():
    pass
# output
error Error1:
    caller: address
    # This should be indented


# This should not

error Error2:
    code: uint256


# This should not

@external
def fail():
    pass
