from tests.reader import all_data_cases, read_data, all_data
import pytest
from mamushi.formatting.format import format_tree

test_cases = [
    (category, case)
    for category in all_data()
    for case in all_data_cases(category)
]


@pytest.mark.parametrize("category,case", test_cases)
def test_format(case: str, category: str, parser):
    source, expected = read_data(category, case)
    assert format_tree(parser.parse(source)).strip() == expected.strip()
