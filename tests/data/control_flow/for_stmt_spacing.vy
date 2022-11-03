@internal
def a():
    for     i   in range (  5  ) :
        pass
    for i    in  [ 0 ,    1 ,2,3]:
        pass
    for  i       in     B[0]    :
        pass
    for   i   in    B:
        pass
    for _ in B  :
        pass
# output
@internal
def a():
    for i in range(5):
        pass
    for i in [0, 1, 2, 3]:
        pass
    for i in B[0]:
        pass
    for i in B:
        pass
    for _ in B:
        pass
