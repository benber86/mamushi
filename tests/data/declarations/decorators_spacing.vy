@internal
@payable
@test(a,b)
@ test  ( b  ,  a  )
def a():
    pass
# output
@internal
@payable
@test(a, b)
@test(b, a)
def a():
    pass
