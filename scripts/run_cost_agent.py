#!/usr/bin/env python
"""Run Cost-Agent on sequence cards and a finite policy pool."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cost_agent_mot.io_utils import read_jsonl
from cost_agent_mot.scheduler import run_scheduler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cards", required=True, help="Sequence-card JSONL.")
    parser.add_argument("--policy-pool", required=True, help="CSV with legal stream-policy candidate directories.")
    parser.add_argument("--output-root", required=True, help="Directory for generated experiment artifacts.")
    parser.add_argument("--experiment-name", default="cost_agent_b055", help="Subdirectory name for this run.")
    parser.add_argument("--budget", type=float, default=0.55, help="Frame-weighted HRTI budget fraction.")
    parser.add_argument("--method", default="cost_agent", help="Ranking method.")
    parser.add_argument("--materialize", choices=["copy", "symlink"], default="copy", help="How selected tracks are materialized.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_scheduler(
        cards=read_jsonl(args.cards),
        policy_pool_csv=args.policy_pool,
        output_root=args.output_root,
        experiment_name=args.experiment_name,
        method=args.method,
        budget_frac=args.budget,
        materialize=args.materialize,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

