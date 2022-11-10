@external
def a():
    self.b(0, # first comment
            1  # 2nd comment
            , # to be merged
            # stand alone
            3, # 5th comment
            4, 5) # final comment

    z(1,
    # comment
    2)
# output
@external
def a():
    self.b(
        0,  # first comment
        1,  # 2nd comment  # to be merged
        # stand alone
        3,  # 5th comment
        4,
        5,
    )  # final comment

    z(
        1,
        # comment
        2,
    )
