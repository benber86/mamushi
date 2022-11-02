@internal
@payable
@test(some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting)
def a():
    pass
# output
@internal
@payable
@test(
    some_very_long_variable_name_that_will_require_splitting,
    some_very_long_variable_name_that_will_require_splitting,
    some_very_long_variable_name_that_will_require_splitting,
)
def a():
    pass
