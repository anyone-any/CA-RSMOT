#!/usr/bin/env python
"""Validate a generated Cost-Agent artifact directory."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cost_agent_mot.cli import main as cli_main

def main() -> None:
    cli_main(["validate", *sys.argv[1:]])


if __name__ == "__main__":
    main()
