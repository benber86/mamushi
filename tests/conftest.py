from mamushi import Parser
import pytest


@pytest.fixture(scope="session")
def parser():
    return Parser()
