@internal
def a():
    e = (self.f) + self.transform(self.b.func(0) + self.some_very_long_variable_name_that_will_require_splitting(0) * (self.some_very_long_variable_name_that_will_require_splitting.some_very_long_variable_name_that_will_require_splitting(5)))
    e = (some_very_long_variable_name_that_will_require_splitting().
    some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    .some_very_long_variable_name_that_will_require_splitting)
# output
@internal
def a():
    e = (self.f) + self.transform(
        self.b.func(0)
        + self.some_very_long_variable_name_that_will_require_splitting(0)
        * (
            self.some_very_long_variable_name_that_will_require_splitting.some_very_long_variable_name_that_will_require_splitting(
                5
            )
        )
    )
    e = (
        some_very_long_variable_name_that_will_require_splitting().some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting.some_very_long_variable_name_that_will_require_splitting
    )
