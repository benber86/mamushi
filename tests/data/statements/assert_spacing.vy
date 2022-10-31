@internal
def foo():
    assert(msg.sender==self.owner)
    assert x>5,"REVERT"
    assert a   == b,   "REVERT"
# output
@internal
def foo():
    assert (msg.sender == self.owner)
    assert x > 5, "REVERT"
    assert a == b, "REVERT"
