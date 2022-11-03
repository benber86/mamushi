@external
def test():
    return (1 == 2 and
            (name, description, self.default, self.selected, self.auto_generated, self.parameters, self.meta_data, self.schedule) ==
            (name, description, othr.default, othr.selected, othr.auto_generated, othr.parameters, othr.meta_data, othr.schedule))
# output
@external
def test():
    return (
        1 == 2
        and (
            name,
            description,
            self.default,
            self.selected,
            self.auto_generated,
            self.parameters,
            self.meta_data,
            self.schedule,
        )
        == (
            name,
            description,
            othr.default,
            othr.selected,
            othr.auto_generated,
            othr.parameters,
            othr.meta_data,
            othr.schedule,
        )
    )
