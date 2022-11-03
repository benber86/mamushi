@internal
def foo():
    some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting=self.bar()
# output
@internal
def foo():
    (
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    ) = self.bar()
