@external # test 1
def a(): # test 2
    # test 3
    self.b()

@external
def b(): # test 4

    # test 5

    self.b(0,2,3)


@external
def c():

    # test 6


# test 7
    self.b(0,2,3)

# output
@external  # test 1
def a():  # test 2
    # test 3
    self.b()


@external
def b():  # test 4

    # test 5

    self.b(0, 2, 3)


@external
def c():

    # test 6


    # test 7
    self.b(0, 2, 3)
