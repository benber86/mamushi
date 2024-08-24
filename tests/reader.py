from pathlib import Path
from typing import List, Tuple

from tests.const import DATA_DIR, PROJECT_ROOT, VYPER_SUFFIXES


def get_base_dir(data: bool) -> Path:
    return DATA_DIR if data else PROJECT_ROOT


def all_data(data: bool = True) -> List[str]:
    return [data_path.stem for data_path in get_base_dir(data).iterdir()]


def all_data_cases(subdir_name: str, data: bool = True) -> List[str]:
    cases_dir = get_base_dir(data) / subdir_name
    assert cases_dir.is_dir()
    return [case_path.stem for case_path in cases_dir.iterdir()]


def get_case_path(subdir_name: str, name: str, data: bool = True) -> Path:
    """Get case path from name"""
    base_path = get_base_dir(data) / subdir_name / name

    for suffix in VYPER_SUFFIXES:
        case_path = base_path.with_suffix(suffix)
        if case_path.is_file():
            return case_path
    raise FileNotFoundError(f"No .vy or .vyi file found for {base_path}")


def read_data(
    subdir_name: str, name: str, data: bool = True
) -> Tuple[str, str]:
    """read_data('test_name') -> 'input', 'output'"""
    return read_data_from_file(get_case_path(subdir_name, name, data))


def read_data_from_file(file_name: Path) -> Tuple[str, str]:
    with open(file_name, "r", encoding="utf8") as test:
        lines = test.readlines()
    _input: List[str] = []
    _output: List[str] = []
    result = _input
    for line in lines:
        if line.rstrip() == "# output":
            result = _output
            continue
        result.append(line)
    if _input and not _output:
        # If there's no output marker, treat the entire file as already pre-formatted.
        _output = _input[:]
    return "".join(_input).strip() + "\n", "".join(_output).strip() + "\n"
