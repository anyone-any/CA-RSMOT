#!/usr/bin/env python
"""Build Cost-Agent sequence cards from detector statistics."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cost_agent_mot.stats_encoder import build_sequence_cards, write_sequence_cards


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-stats", required=True, help="CSV with original-stream detector statistics.")
    parser.add_argument("--enhanced-stats", required=True, help="CSV with HRTI detector statistics.")
    parser.add_argument("--out-csv", required=True, help="Output flattened card CSV.")
    parser.add_argument("--out-jsonl", required=True, help="Output JSONL preserving nested detector statistics.")
    parser.add_argument("--original-seq-col", default="seq", help="Sequence column in original statistics.")
    parser.add_argument("--enhanced-seq-col", default="sequence", help="Sequence column in HRTI statistics.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cards = build_sequence_cards(
        args.original_stats,
        args.enhanced_stats,
        original_seq_col=args.original_seq_col,
        enhanced_seq_col=args.enhanced_seq_col,
    )
    write_sequence_cards(cards, args.out_csv, args.out_jsonl)
    print(f"Wrote {len(cards)} sequence cards")


if __name__ == "__main__":
    main()
