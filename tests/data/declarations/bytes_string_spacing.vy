@internal
def a():
    b: String[10] = '1234567890'




    c: Bytes[100] = b"\x01"


    d: Bytes[100] =    x"01afef"

    d: Bytes[100] =    x'01afef'
# output
@internal
def a():
    b: String[10] = "1234567890"

    c: Bytes[100] = b"\x01"

    d: Bytes[100] = x"01afef"

    d: Bytes[100] = x"01afef"
