from formatting.format import format_tree
from parsing.parser import parse_string
from utils.files import gen_python_files_in_dir

from typing import List
from pathlib import Path
import click


@click.command()
@click.option(
    "-l",
    "--line-length",
    type=int,
    default=80,
    help="Max line length",
    show_default=True,
)
@click.option(
    "--in-place",
    is_flag=True,
    help="Overwrite files in place",
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
)
@click.pass_context
def main(
    ctx: click.Context, line_length: int, in_place: bool, src: List[str]
) -> None:
    """The uncompromising code formatter."""
    sources: List[Path] = []
    if not src:
        src = [str(Path.cwd().resolve())]
    print("PAHT", src)
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.extend(gen_python_files_in_dir(p))
        elif p.is_file():
            # if a file was explicitly given, we don't care about its extension
            sources.append(p)
        else:
            raise FileNotFoundError(f"invalid path: {s}")

    for source in sources:
        with open(source, "r") as fp:
            contract = fp.read()
        res = format_tree(parse_string(contract), line_length)
        if in_place:
            with open(source, "w") as fp:
                fp.write(res)
        print(res)
        ctx.exit(0)


if __name__ == "__main__":
    main()
