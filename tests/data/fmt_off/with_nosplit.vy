@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    # fmt: on
    assert not self.user_to_challenge_to_has_solved[receiver][msg.sender], "You already solved this!" # nosplit
    # fmt: off
    z:uint256=3
    # fmt: on
# output
@external
def foo():
    x: uint256 = 1
    # fmt: off
    y:    uint256    =     2
    # fmt: on
    assert not self.user_to_challenge_to_has_solved[receiver][msg.sender], "You already solved this!"  # nosplit
    # fmt: off
    z:uint256=3
    # fmt: on
