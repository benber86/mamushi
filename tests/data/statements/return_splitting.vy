@internal
def foo() -> (uint256, uint256, uint256):
    return (some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting)
@internal
def bar() -> (uint256):
    return some_very_long_variable_name_that_will_require_splitting-some_very_long_variable_name_that_will_require_splitting+some_very_long_variable_name_that_will_require_splitting
# output
@internal
def foo() -> (uint256, uint256, uint256):
    return (
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )


@internal
def bar() -> (uint256):
    return (
        some_very_long_variable_name_that_will_require_splitting
        - some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
