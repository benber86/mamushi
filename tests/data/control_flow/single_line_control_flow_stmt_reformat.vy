@internal
def a() -> bool:
    b: uint256 = 0
    for i in range(5): b += 1
    for i in range(5):
        if b == 0: break
        elif b == 2: pass
        else: continue
    if b == 0: pass
    if b == 1: return False
    if b == 2: assert 3 == b
    if b == 3: raise "test"
    return False

@internal
def c() -> bool: return True
# output
@internal
def a() -> bool:
    b: uint256 = 0
    for i in range(5):
        b += 1
    for i in range(5):
        if b == 0:
            break
        elif b == 2:
            pass
        else:
            continue
    if b == 0:
        pass
    if b == 1:
        return False
    if b == 2:
        assert 3 == b
    if b == 3:
        raise "test"
    return False


@internal
def c() -> bool:
    return True
