@internal
def foo():
    if(not a)and(a>b)or(a<=b)or(not(a==b)and(a!=b)):
        pass
    if (a>=b)or(b<a):
        pass
@internal
def foo():
    if         a       <= b :
        pass
    elif       c >= d :
        pass
    else :
        pass
# output
@internal
def foo():
    if (not a) and (a > b) or (a <= b) or (not (a == b) and (a != b)):
        pass
    if (a >= b) or (b < a):
        pass


@internal
def foo():
    if a <= b:
        pass
    elif c >= d:
        pass
    else:
        pass
