import pytest
from mamushi import gen_vyper_files_in_dir


def test_gen_python_files_in_dir(tmp_path):
    valid_files = []
    for i, dir in enumerate(["build"] + list("abc")):
        fake_dir = tmp_path / dir
        fake_dir.mkdir()
        for j, ext in enumerate([".py", ".vy"]):
            fake_file = fake_dir / ("test" + ext)
            fake_file.write_text("test")
            if i * j:
                valid_files.append(fake_file)
    found_files = gen_vyper_files_in_dir(tmp_path)
    assert set(valid_files) == set(found_files)
