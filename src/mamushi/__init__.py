from mamushi.__version__ import __version__
from datetime import datetime
import io
import sys
from mamushi.formatting.format import format_tree
from mamushi.parsing.comparator import compare_ast
from mamushi.parsing.parser import Parser
from mamushi.utils.files import gen_vyper_files_in_dir
import traceback
from typing import List
from pathlib import Path
import click
from mamushi.utils.output import out, diff, color_diff
from mamushi.utils.report import Report, Changed


def format_stdin_to_stdout(src: str, dst: str):
    """Format file on stdin. Return True if changed.

    If content is None, it's read from sys.stdin.

    If `write_back` is YES, write reformatted code back to stdout. If it is DIFF,
    write a diff to stdout. The `mode` argument is passed to
    :func:`format_file_contents`.
    """
    then = datetime.utcnow()

    encoding, newline = "utf-8", ""

    f = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding=encoding,
        newline=newline,
        write_through=True,
    )
    now = datetime.utcnow()
    src_name = f"STDIN\t{then} +0000"
    dst_name = f"STDOUT\t{now} +0000"
    d = diff(src, dst, src_name, dst_name)
    d = color_diff(d)
    f.write(d)
    f.detach()


def reformat(
    src: Path,
    parser: Parser,
    safe: bool,
    diff: bool,
    in_place: bool,
    check: bool,
    line_length: int,
    report: "Report",
):
    with open(src, "r") as fp:
        contract = fp.read()
    try:
        src_content = parser.parse(contract)
    except Exception:
        if report.verbose:
            traceback.print_exc()
        report.failed(
            src,
            "Unable to parse input file, are you sure the Vyper code is valid?",
        )
        return True
    res = format_tree(src_content, line_length)

    changed = Changed.NO if res == contract else Changed.YES

    if safe and not compare_ast(contract, res):
        report.failed(src, "Formatting changed the AST, aborting")
        return False
    report.done(src, changed)
    if check:
        return False
    if diff:
        format_stdin_to_stdout(contract, res)
        return True

    if in_place:
        with open(src, "w") as fp:
            fp.write(res)
    else:
        print(res)


@click.command()
@click.version_option(__version__)
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
    type=bool,
    default=True,
    show_default=True,
    help="Overwrite files in place",
)
@click.option(
    "--safe",
    type=bool,
    default=True,
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
            sources.extend(gen_vyper_files_in_dir(p))
        elif p.is_file():
            # if a file was explicitly given, we don't care about its extension
            sources.append(p)
        else:
            raise FileNotFoundError(f"invalid path: {s}")
    parser = Parser()
    for source in sources:
        reformat(
            src=source,
            parser=parser,
            safe=safe,
            diff=diff,
            in_place=in_place and not (check or diff),
            check=check,
            line_length=line_length,
            report=report,
        )

    error_msg = "Oh no! 💥 💔 💥"
    if verbose or not quiet:
        out(error_msg if report.return_code else "All done! ✨ 🍰 ✨")
        if in_place:
            click.echo(str(report), err=True)
    ctx.exit(report.return_code)


if __name__ == "__main__":
    main()
