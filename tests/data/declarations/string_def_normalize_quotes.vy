@internal
def a():
    b: String[10] = 'abcd"ef""i'
    c: String[10] = 'abcdaefggi'
    d: String[10] = 'abcd"efggi'
    e: String[10] = "''''''''''"
    f: String[10] = '""""""""""'
# output
@internal
def a():
    b: String[10] = 'abcd"ef""i'
    c: String[10] = "abcdaefggi"
    d: String[10] = 'abcd"efggi'
    e: String[10] = "''''''''''"
    f: String[10] = '""""""""""'
