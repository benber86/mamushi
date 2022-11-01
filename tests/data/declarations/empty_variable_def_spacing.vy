a: constant(uint256) = empty ( uint256 )

@internal
def foo():
    b: address = empty (   address   )
    c: uint256[2] = empty (   uint256 [  2  ]   )
# output
a: constant(uint256) = empty(uint256)


@internal
def foo():
    b: address = empty(address)
    c: uint256[2] = empty(uint256[2])
