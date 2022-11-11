@internal
def foo():
    a[0]+=1
    a[0]-=1
    a[0]^=1
    a[0]/=1
    a[0]  *=1
    a[0]  **=1
    a[0] |=        1
# output
@internal
def foo():
    a[0] += 1
    a[0] -= 1
    a[0] ^= 1
    a[0] /= 1
    a[0] *= 1
    a[0] **= 1
    a[0] |= 1
