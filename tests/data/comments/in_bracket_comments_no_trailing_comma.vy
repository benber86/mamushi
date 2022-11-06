@external
def a():
    self.b(0, # first comment
            1  # second comment
            ,
            3, # last comment
            4, 5)
    c = [0, # 1
    2 # 2
    ,
    3  #4
    ]
# output
@external
def a():
    self.b(0, 1, 3, 4, 5)  # first comment  # second comment  # last comment
    c = [0, 2, 3]  # 1  # 2  # 4
