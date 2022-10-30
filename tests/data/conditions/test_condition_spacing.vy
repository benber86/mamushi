@internal
def foo():
    if(not a)and(a>b)or(a<=b)or(not(a==b)and(a!=b)):
        pass
    if (a>=b)or(b<a):
        pass
# output
@internal
def foo():
    if (not a) and (a > b) or (a <= b) or (not (a == b) and (a != b)):
        pass
    if (a >= b) or (b < a):
        pass
