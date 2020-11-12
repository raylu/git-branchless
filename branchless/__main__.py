import argparse
import logging
import sys
from typing import List, TextIO

from .hide import hide
from .smartlog import smartlog


def main(argv: List[str], *, out: TextIO) -> int:
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="branchless", add_help=False)
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message and exit"
    )
    subparsers = parser.add_subparsers(
        dest="subcommand",
    )
    smartlog_parser = subparsers.add_parser(
        "smartlog",
        aliases=["sl"],
        help=smartlog.__doc__,
    )
    smartlog_parser.add_argument(
        "--show-old", action="store_true", help="Show old commits (hidden by default)."
    )
    hide_parser = subparsers.add_parser("hide", help="hide a commit from the smartlog")
    hide_parser.add_argument("hash", type=str, help="The commit hash to hide.")
    args = parser.parse_args(argv)

    if args.help:
        parser.print_help(file=out)
        return 0
    elif args.subcommand in ["smartlog", "sl"]:
        return smartlog(out=out, show_old_commits=args.show_old)
    elif args.subcommand == "hide":
        return hide(out=out, hash=args.hash)
    else:
        parser.print_usage(file=out)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], out=sys.stdout))
