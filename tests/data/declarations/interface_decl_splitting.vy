interface x:
    def a(some_very_long_variable_name_that_will_require_splitting: uint256, some_very_long_variable_name_that_will_require_splitting_2: uint256[2], e: uint256, f: uint256) -> uint256: view
    def b(some_very_long_variable_name_that_will_require_splitting: uint256, some_very_long_variable_name_that_will_require_splitting_2: uint256) -> uint256: payable
# output
interface x:
    def a(
        some_very_long_variable_name_that_will_require_splitting: uint256,
        some_very_long_variable_name_that_will_require_splitting_2: uint256[2],
        e: uint256,
        f: uint256,
    ) -> uint256: view
    def b(
        some_very_long_variable_name_that_will_require_splitting: uint256,
        some_very_long_variable_name_that_will_require_splitting_2: uint256,
    ) -> uint256: payable
