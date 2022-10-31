@internal
def foo():
    raise          "test"
    raise
    raise   "test"
    raise"test"
    raise("test")
# output
@internal
def foo():
    raise "test"
    raise
    raise "test"
    raise "test"
    raise ("test")
