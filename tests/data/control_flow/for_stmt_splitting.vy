@internal
def a():
    for i in [some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting]:
        pass

    for some_very_long_variable_name_that_will_require_splitting in range(some_very_long_variable_name_that_will_require_splitting):
        pass

    for some_very_long_variable_name_that_will_require_splitting in some_very_long_variable_name_that_will_require_splitting:
        pass
# output
@internal
def a():
    for i in [
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    ]:
        pass

    for some_very_long_variable_name_that_will_require_splitting in range(
        some_very_long_variable_name_that_will_require_splitting
    ):
        pass

    for some_very_long_variable_name_that_will_require_splitting in some_very_long_variable_name_that_will_require_splitting:
        pass
