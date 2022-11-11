@external
def __init__(a: uint256, # first comment
            b: uint256  # 2nd comment
            , # to be merged
            # stand alone
            c: uint256, # 5th comment
            d: uint256, e: uint256): # final comment
    pass
# output
@external
def __init__(
    a: uint256,  # first comment
    b: uint256,  # 2nd comment  # to be merged
    # stand alone
    c: uint256,  # 5th comment
    d: uint256,
    e: uint256,
):  # final comment
    pass
