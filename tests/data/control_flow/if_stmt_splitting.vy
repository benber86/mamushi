@internal
def foo():
    if not long_variable_name and (long_variable_name * 2 - 10 ** 18 > long_variable_name + 2 * long_variable_name) or (long_variable_name and long_variable_name) and not (long_variable_name <= long_variable_name):
        pass
    elif (some_very_long_variable_name_that_will_require_splitting or some_very_long_variable_name_that_will_require_splitting and some_very_long_variable_name_that_will_require_splitting or a < 2):
        pass
    else:
        pass
# output
@internal
def foo():
    if (
        not long_variable_name
        and (
            long_variable_name * 2 - 10**18
            > long_variable_name + 2 * long_variable_name
        )
        or (long_variable_name and long_variable_name)
        and not (long_variable_name <= long_variable_name)
    ):
        pass
    elif (
        some_very_long_variable_name_that_will_require_splitting
        or some_very_long_variable_name_that_will_require_splitting
        and some_very_long_variable_name_that_will_require_splitting
        or a < 2
    ):
        pass
    else:
        pass
