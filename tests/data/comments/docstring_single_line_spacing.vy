@internal
def a():
    """    asdasa """
    pass
def b():
    """"this\" will test this"""
    pass
def c():
    """This will test \"this\""""
    pass
def d():
    """This will test this\\\\"""
    pass
def e():
    """ """
    pass
# output
@internal
def a():
    """asdasa"""
    pass


def b():
    """ "this\" will test this"""
    pass


def c():
    """This will test \"this\" """
    pass


def d():
    """This will test this\\\\"""
    pass


def e():
    """ """
    pass
