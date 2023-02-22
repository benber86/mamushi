import os
from pathlib import Path

import pytest
import mamushi
from mamushi.utils.output import dump_to_file

from tests.const import MINIMAL_CONTRACT, DATA_DIR
from tests.reader import read_data


def test_diff_file(runner):
    source, _ = read_data("assignments", "aug_assign_spacing.vy")
    tmp_file = Path(dump_to_file(source))
    try:
        result = runner.invoke(mamushi.main, ["--diff", str(tmp_file)])
        assert result.exit_code == 0
        assert "would reformat" in result.stderr
        assert "would be reformatted" in result.stderr
        assert "\033[1m" in result.stdout
        assert "\033[36m" in result.stdout
        assert "\033[32m" in result.stdout
        assert "\033[31m" in result.stdout

    finally:
        os.unlink(tmp_file)
    post_source, _ = read_data("assignments", "aug_assign_spacing.vy")
    assert (
        post_source == source
    ), "Source file was modified when requesting diff"


def test_diff_file_no_diffs(runner):
    tmp_file = Path(dump_to_file(MINIMAL_CONTRACT))
    try:
        result = runner.invoke(mamushi.main, ["--diff", str(tmp_file)])
        assert result.exit_code == 0
        assert "left unchanged" in result.stderr
    finally:
        os.unlink(tmp_file)


def test_diff_file_no_diffs_verbose(runner):
    tmp_file = Path(dump_to_file(MINIMAL_CONTRACT))
    try:
        result = runner.invoke(
            mamushi.main, ["--diff", "--verbose", str(tmp_file)]
        )
        assert result.exit_code == 0
        assert "already well formatted" in result.stderr
    finally:
        os.unlink(tmp_file)


def test_check_file_no_diffs(runner):
    tmp_file = Path(dump_to_file(MINIMAL_CONTRACT))
    try:
        result = runner.invoke(mamushi.main, ["--check", str(tmp_file)])
        assert result.exit_code == 0
        assert "left unchanged" in result.stderr
    finally:
        os.unlink(tmp_file)


def test_check_file(runner):
    source, _ = read_data("assignments", "aug_assign_spacing.vy")
    tmp_file = Path(dump_to_file(source))
    try:
        result = runner.invoke(mamushi.main, ["--check", str(tmp_file)])
        assert result.exit_code == 1
        assert "would reformat" in result.stderr
        assert "would be reformatted" in result.stderr

    finally:
        os.unlink(tmp_file)
    post_source, _ = read_data("assignments", "aug_assign_spacing.vy")
    assert (
        post_source == source
    ), "Source file was modified when requesting check"


def test_line_length(runner):
    source = "a: constant(uint256) = 10000000000 + 10000000000"
    tmp_file = Path(dump_to_file(source))
    try:
        result = runner.invoke(
            mamushi.main, ["--line-length", 20, str(tmp_file)]
        )
        assert result.exit_code == 0
        assert "file reformatted" in result.stderr

    finally:
        os.unlink(tmp_file)


def test_check_multiple_files(runner):
    result = runner.invoke(
        mamushi.main, ["--check", str(DATA_DIR / "imports")]
    )
    assert result.exit_code == 1
    assert "would reformat" in result.stderr
    assert "files would be reformatted" in result.stderr


def test_invalid_file(runner):
    result = runner.invoke(mamushi.main, ["--check", "AAAAAAAAAAAAAAAA.x"])
    assert result.exit_code == 2
    assert "does not exist" in result.stderr


def test_code_with_parse_error(runner):
    source = "a: (error) = invalid"
    tmp_file = Path(dump_to_file(source))
    try:
        result = runner.invoke(
            mamushi.main, ["--check", "--verbose", str(tmp_file)]
        )
        assert result.exit_code == 123
        assert "UnexpectedToken" in result.stderr
        assert "Unable to parse" in result.stderr
        assert "fail to reformat" in result.stderr

    finally:
        os.unlink(tmp_file)


def test_output_to_console(runner):
    source = "a: constant( uint256 ) = 0"
    tmp_file = Path(dump_to_file(source))
    try:
        result = runner.invoke(
            mamushi.main, ["--in-place", False, str(tmp_file)]
        )
        assert result.exit_code == 0
        assert "(uint256)" in result.stdout
        assert "file" not in result.stderr
        with open(str(tmp_file), "r") as fp:
            post_source = fp.read()
        assert (
            post_source.strip() == source.strip()
        ), "File was modified despite --in-place = False"
    finally:
        os.unlink(tmp_file)
