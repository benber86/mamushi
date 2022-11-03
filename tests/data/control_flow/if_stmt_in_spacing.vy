@internal
def foo():
    if a in [1,2,3]:
        pass
    if a in (     1    , 2  ,  3   )   :
        pass
    if a in (  a    | b   | c):
        pass
# output
@internal
def foo():
    if a in [1, 2, 3]:
        pass
    if a in (1, 2, 3):
        pass
    if a in (a | b | c):
        pass
