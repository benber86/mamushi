from tests.reader import all_data_cases, read_data
import pytest
from mamushi import format_from_string


@pytest.mark.parametrize("case_file", all_data_cases("comments"))
def test_format_comments(case_file: str):
    source, expected = read_data("comments", case_file)
    assert format_from_string(source) == expected
