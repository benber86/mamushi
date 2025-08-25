@external
@view
def foo():

    b:   DynArray[ uint256 ,  foo.BAR] = abi_decode(
        _d,    DynArray[ uint256 ,  foo.BAR ]
    )

# output
@external
@view
def foo():
    b: DynArray[uint256, foo.BAR] = abi_decode(_d, DynArray[uint256, foo.BAR])
