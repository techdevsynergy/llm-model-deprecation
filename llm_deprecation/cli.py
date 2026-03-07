"""CLI for llm-deprecation: scan projects for deprecated LLM model usage."""

import argparse
import sys
from pathlib import Path

from llm_deprecation.scanner import format_scan_output, scan_project


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="llm-deprecation",
        description="Check LLM model deprecations in your project.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan project for deprecated/retired model references")
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=Path,
        help="Path to project root (default: current directory)",
    )
    scan_parser.add_argument(
        "--fail-on-deprecated",
        action="store_true",
        help="Exit with code 1 if any deprecated or retired models are found (for CI)",
    )
    scan_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print findings; no 'Scanning project...' line",
    )

    args = parser.parse_args()

    if args.command == "scan":
        root = args.path.resolve()
        if not root.is_dir():
            print(f"Error: not a directory: {root}", file=sys.stderr)
            return 2
        if not args.quiet:
            print("Scanning project...")
        findings = scan_project(root)
        out = format_scan_output(findings, root=root)
        if out:
            print(out)
            if args.fail_on_deprecated:
                return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
