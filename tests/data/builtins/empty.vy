@internal
def foo():
    a: uint256 = empty(         uint256 )
    b: uint256[2][5] = empty(      uint256[2][5]        )
    c: uint256[2][5] = empty(
                     uint256[2][5]
      )
    d: uint256[2][5] = empty(uint256[2][5])

# output
@internal
def foo():
    a: uint256 = empty(uint256)
    b: uint256[2][5] = empty(uint256[2][5])
    c: uint256[2][5] = empty(uint256[2][5])
    d: uint256[2][5] = empty(uint256[2][5])

