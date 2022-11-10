event Event1:
    a: indexed(address)
    b: uint256
# This should be indented

event Event2:
    c: indexed(address)

# This should not

@external
def foo():
    pass
# output
event Event1:
    a: indexed(address)
    b: uint256
    # This should be indented


event Event2:
    c: indexed(address)


# This should not


@external
def foo():
    pass
