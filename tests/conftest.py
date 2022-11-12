from mamushi import Parser
import pytest
from typing import Dict, Any
import click
from click.testing import CliRunner


class MamushiRunner(CliRunner):
    """Make sure STDOUT and STDERR are kept separate when testing Black via its CLI."""

    def __init__(self) -> None:
        super().__init__(mix_stderr=False)


@pytest.fixture(scope="session")
def runner():
    return MamushiRunner()


@pytest.fixture(scope="session")
def parser():
    return Parser()
