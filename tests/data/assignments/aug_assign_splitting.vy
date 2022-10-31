@internal
def foo():
    a+=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    a-=(some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting)
    a&=some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting
    c|=some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting
    c^=some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting & some_very_long_variable_name_that_will_require_splitting
    a%=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    a/=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    b*=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    b**=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    c<<=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
    c>>=some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting + some_very_long_variable_name_that_will_require_splitting
# output
@internal
def foo():
    a += (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    a -= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    a &= (
        some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
    )
    c |= (
        some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
    )
    c ^= (
        some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
        & some_very_long_variable_name_that_will_require_splitting
    )
    a %= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    a /= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    b *= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    b **= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    c <<= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
    c >>= (
        some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
        + some_very_long_variable_name_that_will_require_splitting
    )
