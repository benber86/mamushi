@internal
def foo():
    a = some_iterable[1+2+3]
    a = some_iterable[   ~  a]
    a = some_iterable[   1 +  3]
# output
@internal
def foo():
    a = some_iterable[1 + 2 + 3]
    a = some_iterable[~a]
    a = some_iterable[1 + 3]
