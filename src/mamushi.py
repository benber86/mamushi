from formatting.format import format_tree
from parsing.comparator import compare_ast
from parsing.parser import Parser
from utils.files import gen_python_files_in_dir, normalize_path_maybe_ignore
import traceback
from typing import List, Sized
from pathlib import Path
import click
from utils.output import out
from utils.report import Report, Changed


def path_empty(
    src: Sized, msg: str, quiet: bool, verbose: bool, ctx: click.Context
) -> None:
    """
    Exit if there is no `src` provided for formatting
    """
    if not src:
        if verbose or not quiet:
            out(msg)
        ctx.exit(0)


def reformat(
    src: Path,
    parser: Parser,
    safe: bool,
    in_place: bool,
    line_length: int,
    report: "Report",
):
    with open(src, "r") as fp:
        contract = fp.read()
    changed = Changed.NO
    try:
        src_content = parser.parse(contract)
    except Exception as exc:
        if report.verbose:
            traceback.print_exc()
        report.failed(src, str(exc))
    res = format_tree(src_content, line_length)
    if res == src_content:
        return False
    else:
        changed = Changed.YES
    if safe and not compare_ast(contract, res):
        report.failed(src, "Formatting changed the AST, aborting")
        return False
    report.done(src, changed)

    if in_place:
        with open(src, "w") as fp:
            fp.write(res)
    else:
        print(res)


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
    default=True,
    show_default=True,
    help="Overwrite files in place",
)
@click.option(
    "--safe",
    type=bool,
    default=False,
    show_default=True,
    help="Compares input and output AST to ensure similarity",
)
@click.option(
    "--check",
    is_flag=True,
    help=(
        "Don't write the files back, just return the status. Return code 0 means"
        " nothing would change. Return code 1 means some files would be reformatted."
        " Return code 123 means there was an internal error."
    ),
)
@click.option(
    "--diff",
    is_flag=True,
    help="Don't write the files back, just output a diff for each file on stdout.",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=(
        "Don't emit non-error messages to stderr. Errors are still emitted; silence"
        " those with 2>/dev/null."
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=(
        "Also emit messages to stderr about files that were not changed or were ignored"
        " due to exclusion patterns."
    ),
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
)
@click.pass_context
def main(
    ctx: click.Context,
    line_length: int,
    in_place: bool,
    diff: bool,
    check: bool,
    verbose: bool,
    quiet: bool,
    safe: bool,
    src: List[str],
) -> None:
    sources: List[Path] = []
    report = Report(check=check, diff=diff, quiet=quiet, verbose=verbose)
    if not src:
        src = [str(Path.cwd().resolve())]

    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.extend(gen_python_files_in_dir(p))
        elif p.is_file():
            # if a file was explicitly given, we don't care about its extension
            sources.append(p)
        else:
            raise FileNotFoundError(f"invalid path: {s}")
    parser = Parser()
    for source in sources:
        reformat(source, parser, safe, in_place, line_length, report)

    error_msg = "Oh no! 💥 💔 💥"
    if verbose or not quiet:
        out(error_msg if report.return_code else "All done! ✨ 🍰 ✨")
    ctx.exit(report.return_code)


if __name__ == "__main__":
    main()
