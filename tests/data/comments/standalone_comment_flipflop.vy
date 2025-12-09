@external
def rate_write(_for: address = msg.sender) -> uint256:
    # Update controller list
    n_controllers: uint256 = self.n_controllers
    n_factory_controllers: uint256 = (
        staticcall CONTROLLER_FACTORY.n_collaterals()
    )
    if n_factory_controllers > n_controllers:
        self.n_controllers = n_factory_controllers
        for _: uint256 in range(MAX_CONTROLLERS):
            self.controllers[
                n_controllers
            ] = staticcall CONTROLLER_FACTORY.controllers(n_controllers)
            n_controllers += 1
            if n_controllers >= n_factory_controllers:
                break

        # Update candles


    total_debt: uint256 = 0
    debt_for: uint256 = 0
    total_debt, debt_for = self.get_total_debt(_for)


# output
@external
def rate_write(_for: address = msg.sender) -> uint256:
    # Update controller list
    n_controllers: uint256 = self.n_controllers
    n_factory_controllers: uint256 = (
        staticcall CONTROLLER_FACTORY.n_collaterals()
    )
    if n_factory_controllers > n_controllers:
        self.n_controllers = n_factory_controllers
        for _: uint256 in range(MAX_CONTROLLERS):
            self.controllers[
                n_controllers
            ] = staticcall CONTROLLER_FACTORY.controllers(n_controllers)
            n_controllers += 1
            if n_controllers >= n_factory_controllers:
                break

        # Update candles


    total_debt: uint256 = 0
    debt_for: uint256 = 0
    total_debt, debt_for = self.get_total_debt(_for)
