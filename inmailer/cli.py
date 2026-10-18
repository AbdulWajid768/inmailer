"""Command-line interface for :mod:`inmailer`.

Usage::

    inmailer input.html -o output.html
    cat input.html | inmailer > output.html
"""

import argparse
import os
import sys
from typing import List, Optional

from . import __version__
from .core import inline_css


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inmailer",
        description="Inline the CSS of an HTML document for email clients.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="HTML file to process (reads from stdin when omitted).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write the result to this file (prints to stdout when omitted).",
    )
    parser.add_argument(
        "-c",
        "--extra-css",
        help="Path to an additional CSS file to inline alongside the HTML.",
    )
    parser.add_argument(
        "--css-file",
        action="append",
        default=[],
        metavar="PATH",
        dest="css_files",
        help="External CSS file to inline (repeatable).",
    )
    parser.add_argument(
        "--base-path",
        help="Directory for resolving <link> hrefs and --css-file paths "
        "(defaults to the input file's directory).",
    )
    parser.add_argument(
        "--no-resolve-links",
        action="store_false",
        dest="resolve_links",
        help="Do not read and inline <link rel='stylesheet'> tags.",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Fetch http(s) stylesheet links over the network (off by default).",
    )
    parser.add_argument(
        "--remove-classes",
        action="store_true",
        help="Strip class attributes after inlining.",
    )
    parser.add_argument(
        "--keep-style-tags",
        action="store_true",
        help="Also keep the original CSS inside a <style> tag.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact HTML instead of pretty-printed output.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding for reading and writing files (default: utf-8).",
    )
    parser.add_argument("-V", "--version", action="version", version=f"inmailer {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = args.base_path
    if args.input:
        with open(args.input, "r", encoding=args.encoding) as handle:
            html_content = handle.read()
        if base_path is None:
            base_path = os.path.dirname(os.path.abspath(args.input))
    else:
        html_content = sys.stdin.read()

    extra_css = None
    if args.extra_css:
        with open(args.extra_css, "r", encoding=args.encoding) as handle:
            extra_css = handle.read()

    result = inline_css(
        html_content,
        extra_css=extra_css,
        css_files=args.css_files,
        base_path=base_path,
        resolve_links=args.resolve_links,
        allow_remote=args.allow_remote,
        encoding=args.encoding,
        remove_classes=args.remove_classes,
        keep_style_tags=args.keep_style_tags,
        pretty_print=not args.compact,
    )

    if args.output:
        with open(args.output, "w", encoding=args.encoding) as handle:
            handle.write(result)
    else:
        sys.stdout.write(result)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
