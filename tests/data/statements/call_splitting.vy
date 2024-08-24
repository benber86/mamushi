@internal
def foo():
    self.bar(0,0,0,0)
    self.baz(self.bar(some_very_long_variable_name_that_will_require_splitting,
                        some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting, 3),
            msg.sender,
                empty(address),
            3,
            some_very_long_variable_name_that_will_require_splitting)
    call(some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting)
    abi_encode(some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting, some_very_long_variable_name_that_will_require_splitting,some_very_long_variable_name_that_will_require_splitting)
    abi_decode(some_very_long_variable_name_that_will_require_splitting, uint256, unwrap_tuple=False)
# output
@internal
def foo():
    self.bar(0, 0, 0, 0)
    self.baz(
        self.bar(
            some_very_long_variable_name_that_will_require_splitting,
            some_very_long_variable_name_that_will_require_splitting,
            some_very_long_variable_name_that_will_require_splitting,
            3,
        ),
        msg.sender,
        empty(address),
        3,
        some_very_long_variable_name_that_will_require_splitting,
    )
    call(
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )
    abi_encode(
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
        some_very_long_variable_name_that_will_require_splitting,
    )
    abi_decode(
        some_very_long_variable_name_that_will_require_splitting,
        uint256,
        unwrap_tuple=False,
    )
