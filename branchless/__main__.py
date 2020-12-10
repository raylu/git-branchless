"""Main entry-point."""
import argparse
import logging
import sys
from typing import List, TextIO

from .hide import hide, unhide
from .hooks import hook_post_checkout, hook_post_commit, hook_post_rewrite
from .init import init
from .navigation import next, prev
from .restack import restack
from .smartlog import smartlog
from .undo import undo


def main(argv: List[str], *, out: TextIO, err: TextIO) -> int:
    """Run the provided sub-command.

    Args:
      argv: List of command-line arguments (e.g. from `sys.argv`).
      out: Output stream to write to (may be a TTY).

    Returns:
      Exit code (0 denotes successful exit).
    """
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="branchless", add_help=False)
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message and exit"
    )
    subparsers = parser.add_subparsers(
        dest="subcommand",
    )

    # Command parsers.
    subparsers.add_parser(
        "init", help="Initialize the branchless workflow for this repository."
    )
    subparsers.add_parser(
        "smartlog",
        aliases=["sl"],
        help=smartlog.__doc__,
    )
    hide_parser = subparsers.add_parser("hide", help="Hide a commit from the smartlog.")
    hide_parser.add_argument(
        "hash", type=str, help="The commit hash to hide.", nargs="*"
    )
    hide_parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Hide all visible descendant commits as well.",
    )
    unhide_parser = subparsers.add_parser(
        "unhide", help="Unhide a previously-hidden commit from the smartlog."
    )
    unhide_parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Unhide all visible descendant commits as well.",
    )
    unhide_parser.add_argument(
        "hash", type=str, help="The commit hash to unhide.", nargs="*"
    )
    prev_parser = subparsers.add_parser("prev", help="Go to a previous commit.")
    prev_parser.add_argument(
        "num_commits", type=int, help="The number of commits backward to go.", nargs="?"
    )
    next_parser = subparsers.add_parser("next", help="Go to a later commit.")
    next_parser.add_argument(
        "num_commits", type=int, help="The number of commits forward to go.", nargs="?"
    )
    next_parser_towards_group = next_parser.add_mutually_exclusive_group()
    next_parser_towards_group.add_argument(
        "-o",
        "--oldest",
        help="When encountering multiple next commits, choose the oldest.",
        dest="towards",
        action="store_const",
        const="oldest",
    )
    next_parser_towards_group.add_argument(
        "-n",
        "--newest",
        help="When encountering multiple next commits, choose the newest.",
        dest="towards",
        action="store_const",
        const="newest",
    )
    subparsers.add_parser(
        "restack",
        help="Rebase abandoned commits onto their most up-to-date counterparts.",
    )
    subparsers.add_parser(
        "undo",
        help="Return to a past state of the repository.",
    )

    # Hook parsers.
    hook_post_rewrite_parser = subparsers.add_parser(
        "hook-post-rewrite", help="Internal use."
    )
    hook_post_rewrite_parser.add_argument("rewrite_type", type=str)
    hook_post_checkout_parser = subparsers.add_parser(
        "hook-post-checkout", help="Internal use."
    )
    hook_post_checkout_parser.add_argument("previous_commit", type=str)
    hook_post_checkout_parser.add_argument("current_commit", type=str)
    hook_post_checkout_parser.add_argument("is_branch_checkout", type=int)
    subparsers.add_parser("hook-post-commit", help="Internal use.")

    args = parser.parse_args(argv)

    if args.help:
        parser.print_help(file=out)
        return 0
    elif args.subcommand == "init":
        return init(out=out)
    elif args.subcommand in ["smartlog", "sl"]:
        return smartlog(out=out)
    elif args.subcommand == "hide":
        return hide(out=out, hashes=args.hash, recursive=args.recursive)
    elif args.subcommand == "unhide":
        return unhide(out=out, hashes=args.hash, recursive=args.recursive)
    elif args.subcommand == "prev":
        return prev(out=out, err=err, num_commits=args.num_commits)
    elif args.subcommand == "next":
        return next(
            out=out, err=err, num_commits=args.num_commits, towards=args.towards
        )
    elif args.subcommand == "restack":
        return restack(out=out, err=err, preserve_timestamps=False)
    elif args.subcommand == "undo":
        return undo(out=out)
    elif args.subcommand == "hook-post-rewrite":
        hook_post_rewrite(out=out)
        return 0
    elif args.subcommand == "hook-post-checkout":
        hook_post_checkout(
            out=out,
            previous_head_ref=args.previous_commit,
            current_head_ref=args.current_commit,
            is_branch_checkout=args.is_branch_checkout,
        )
        return 0
    elif args.subcommand == "hook-post-commit":
        hook_post_commit(out=out)
        return 0
    else:
        parser.print_usage(file=out)
        return 1


def entry_point() -> None:
    sys.exit(main(sys.argv[1:], out=sys.stdout, err=sys.stderr))


if __name__ == "__main__":
    try:
        from pytest_cov.embed import init as pytest_cov_init

        pytest_cov_init()
    except ImportError:  # pragma: no cover
        pass

    entry_point()
