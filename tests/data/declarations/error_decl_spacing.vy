error             Unauthorized :
    caller    : address
    expected:uint256
    amounts   : DynArray[ uint256 , 10 ]

@external
def fail():
    raise    Unauthorized( caller = msg.sender, expected = 1, amounts = [1, 2, 3] )
    assert    False,    Unauthorized( caller = msg.sender, expected = 2, amounts = [4, 5] )
# output
error Unauthorized:
    caller: address
    expected: uint256
    amounts: DynArray[uint256, 10]


@external
def fail():
    raise Unauthorized(caller=msg.sender, expected=1, amounts=[1, 2, 3])
    assert False, Unauthorized(caller=msg.sender, expected=2, amounts=[4, 5])
