@internal
def foo():
    if a in [some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting]:
        pass
    if a in (some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting):
        pass
    if a in (some_very_long_variable_name_that_will_require_splitting|some_very_long_variable_name_that_will_require_splitting|some_very_long_variable_name_that_will_require_splitting):
        pass
# output
@internal
def foo():
    if a in [
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    ]:
        pass
    if a in (
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    ):
        pass
    if a in (
        some_very_long_variable_name_that_will_require_splitting
        | some_very_long_variable_name_that_will_require_splitting
        | some_very_long_variable_name_that_will_require_splitting
    ):
        pass
