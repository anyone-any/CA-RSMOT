#!/usr/bin/env python
"""Check the public artifact for local paths and de-anonymization markers."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_PATTERNS = [
    r"/home/",
    r"LOCAL_PROJECT_NAME",
    r"AFFILIATION_TO_REMOVE",
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "outputs",
}
SKIP_FILES = {"scripts/check_anonymity.py"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--pattern", action="append", default=[], help="Additional regex to flag. Can be repeated.")
    parser.add_argument("--strict-secrets", action="store_true", help="Also flag generic credential words.")
    return parser.parse_args()


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.as_posix() in SKIP_FILES:
            continue
        if path.is_file():
            yield path


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    extra = []
    if args.strict_secrets:
        extra = [r"API[_-]?KEY", r"TOKEN", r"PASSWORD", r"SECRET", r"PRIVATE[_-]?KEY"]
    patterns = [re.compile(item, re.IGNORECASE) for item in DEFAULT_PATTERNS + extra + args.pattern]
    findings: list[str] = []
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                if pattern.search(line):
                    findings.append(f"{path}:{line_no}: matched {pattern.pattern}")
                    break
    if findings:
        raise SystemExit("Potential anonymity or secret findings:\n" + "\n".join(findings))
    print("No anonymity findings.")


if __name__ == "__main__":
    main()
