@internal
def foo():
    if not long_variable_name and (long_variable_name * 2 - 10 ** 18 > long_variable_name + 2 * long_variable_name) or (long_variable_name and long_variable_name) and not (long_variable_name <= long_variable_name):
        pass
# output
@internal
def foo():
    if not long_variable_name and (
        long_variable_name * 2 - 10**18
        > long_variable_name + 2 * long_variable_name
    ) or (long_variable_name and long_variable_name) and not (
        long_variable_name <= long_variable_name
    ):
        pass
