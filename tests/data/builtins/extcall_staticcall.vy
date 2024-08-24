def foo():
    extcall                      foobar.test1()

def bar():
    return          extcall                      foobar.test1()

def foo_two():
    extcall                      staticcall.test1()

def bar_two():
    return          staticcall                      foobar.test1()
# output
def foo():
    extcall foobar.test1()


def bar():
    return extcall foobar.test1()


def foo_two():
    extcall staticcall.test1()


def bar_two():
    return staticcall foobar.test1()
