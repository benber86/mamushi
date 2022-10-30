from tests.reader import all_data_cases, read_data, all_data
import pytest
from mamushi import format_from_string

test_cases = [
    (category, case)
    for category in all_data()
    for case in all_data_cases(category)
]


@pytest.mark.parametrize("category,case", test_cases)
def test_format(case: str, category: str):
    source, expected = read_data(category, case)
    assert format_from_string(source) == expected
