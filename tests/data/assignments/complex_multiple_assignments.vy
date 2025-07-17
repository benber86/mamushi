@internal
def foo():
    (a,
            b,
            c, d) = abi_decode(
            slice(data,
                   A,
            B),
            (uint256,
                        uint256,            uint256,
                         uint256),
        )



    a,  b,  c, d = abi_decode(  slice(              data, A,  B),         (uint256,
                        uint256,            uint256  ,
                         uint256),
        )

# output
@internal
def foo():
    (a, b, c, d) = abi_decode(
        slice(data, A, B),
        (uint256, uint256, uint256, uint256),
    )

    a, b, c, d = abi_decode(
        slice(data, A, B),
        (uint256, uint256, uint256, uint256),
    )
