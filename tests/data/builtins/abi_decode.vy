@external
@view
def foo():
    x: uint256 = empty(uint256)
    y: Bytes[32] = empty(Bytes[32])
    x, y =  abi_decode(x,          (uint256,          Bytes[32]))
    x, y =  abi_decode(      x,
     ( uint256
               ,        Bytes[32]             ) )
    a: uint256 = abi_decode(x        , uint256,
    unwrap_tuple=
    False)

# output
@external
@view
def foo():
    x: uint256 = empty(uint256)
    y: Bytes[32] = empty(Bytes[32])
    x, y = abi_decode(x, (uint256, Bytes[32]))
    x, y = abi_decode(x, (uint256, Bytes[32]))
    a: uint256 = abi_decode(x, uint256, unwrap_tuple=False)


