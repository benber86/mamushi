@external
def foo():
    a: decimal = 1_0000.1
    b: uint256 = 1111_2222_33_4_5555
    c: uint256 = 12_234_56
    d: uint256 = 0o_12_122_0
    e: uint256 = 0O_12_122_0
    f: Bytes[1] = 0b0_1_1_0_1_0_0_1
    g: address = 0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7
# output
@external
def foo():
    a: decimal = 1_0000.1
    b: uint256 = 1111_2222_33_4_5555
    c: uint256 = 12_234_56
    d: uint256 = 0o_12_122_0
    e: uint256 = 0O_12_122_0
    f: Bytes[1] = 0b0_1_1_0_1_0_0_1
    g: address = 0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7
