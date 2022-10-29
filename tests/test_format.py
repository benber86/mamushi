from tests.reader import all_data_cases, read_data
import pytest
from mamushi import format_from_string


@pytest.mark.parametrize("case", all_data_cases("comments"))
def test_format_comments(case: str):
    source, expected = read_data("comments", case)
    assert format_from_string(source) == expected


@pytest.mark.parametrize("case", all_data_cases("declarations"))
def test_format_declaration(case: str):
    source, expected = read_data("declarations", case)
    assert format_from_string(source) == expected
