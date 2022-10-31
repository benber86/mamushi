@internal
def foo() -> (uint256, uint256):
    return          ( a ,  b )

@internal
def bar() -> bool:
    if True:
        return(True)
    else:
        return                   False

@internal
def baz() -> (uint256,uint256):
    return(a,b)
# output
@internal
def foo() -> (uint256, uint256):
    return (a, b)


@internal
def bar() -> bool:
    if True:
        return (True)
    else:
        return False


@internal
def baz() -> (uint256, uint256):
    return (a, b)
