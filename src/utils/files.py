from typing import Iterator
from pathlib import Path

PYTHON_EXTENSIONS = {".vy"}
BLACKLISTED_DIRECTORIES = {
    "build",
    "buck-out",
    ".nox",
    "venv",
    ".direnv",
    ".eggs",
    "__pypackages__",
    "build",
    ".ipynb_checkpoints",
    "dist",
    "_build",
    ".git",
    ".hg",
    ".mypy_cache",
    ".tox",
    ".venv",
    ".idea",
}


def gen_python_files_in_dir(path: Path) -> Iterator[Path]:
    for child in path.iterdir():
        if child.is_dir():
            if child.name in BLACKLISTED_DIRECTORIES:
                continue

            yield from gen_python_files_in_dir(child)

        elif child.suffix in PYTHON_EXTENSIONS:
            yield child
