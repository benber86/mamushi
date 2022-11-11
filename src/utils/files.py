from typing import Iterator, Optional
from pathlib import Path

from utils.report import Report

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


def normalize_path_maybe_ignore(
    path: Path,
    root: Path,
    report: Optional[Report] = None,
) -> Optional[str]:
    """Normalize `path`. May return `None` if `path` was ignored.

    `report` is where "path ignored" output goes.
    """
    try:
        abspath = path if path.is_absolute() else Path.cwd() / path
        normalized_path = abspath.resolve()
        try:
            root_relative_path = normalized_path.relative_to(root).as_posix()
        except ValueError:
            if report:
                report.path_ignored(
                    path, f"is a symbolic link that points outside {root}"
                )
            return None

    except OSError as e:
        if report:
            report.path_ignored(path, f"cannot be read because {e}")
        return None

    return root_relative_path
