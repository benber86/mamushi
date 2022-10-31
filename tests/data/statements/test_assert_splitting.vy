@internal
def foo():
    assert (some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting == some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting)
# output
@internal
def foo():
    assert (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        == some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )
