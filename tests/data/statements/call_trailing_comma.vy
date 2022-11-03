@external
def test():
    self.a(some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,)
    a = self.b(some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,)
# output
@external
def test():
    self.a(
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )
    a = self.b(
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )
