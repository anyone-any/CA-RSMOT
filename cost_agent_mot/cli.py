"""Command-line interface for the Cost-Agent MOT artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io_utils import read_jsonl
from .scheduler import run_scheduler
from .stats_encoder import build_sequence_cards, write_sequence_cards


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cost-agent-mot",
        description="Build sequence cards, run Cost-Agent scheduling, and validate run artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-cards", help="Build image-free sequence cards.")
    build.add_argument("--original-stats", required=True, help="CSV with original-stream detector statistics.")
    build.add_argument("--enhanced-stats", required=True, help="CSV with HRTI detector statistics.")
    build.add_argument("--out-csv", required=True, help="Output flattened card CSV.")
    build.add_argument("--out-jsonl", required=True, help="Output JSONL preserving nested detector statistics.")
    build.add_argument("--original-seq-col", default="seq", help="Sequence column in original statistics.")
    build.add_argument("--enhanced-seq-col", default="sequence", help="Sequence column in HRTI statistics.")

    run = subparsers.add_parser("run", help="Run Cost-Agent on sequence cards and a finite policy pool.")
    run.add_argument("--cards", required=True, help="Sequence-card JSONL.")
    run.add_argument("--policy-pool", required=True, help="CSV with legal stream-policy candidate directories.")
    run.add_argument("--output-root", required=True, help="Directory for generated experiment artifacts.")
    run.add_argument("--experiment-name", default="cost_agent_b055", help="Subdirectory name for this run.")
    run.add_argument("--budget", type=float, default=0.55, help="Frame-weighted HRTI budget fraction.")
    run.add_argument("--method", default="cost_agent", help="Ranking method.")
    run.add_argument("--materialize", choices=["copy", "symlink"], default="copy", help="Materialization mode.")
    run.add_argument("--min-confidence", type=float, default=0.60, help="Verifier confidence threshold.")
    run.add_argument(
        "--no-density-policy",
        action="store_true",
        help="Disable verifier correction to the density-derived tracker policy.",
    )

    validate = subparsers.add_parser("validate", help="Validate a generated Cost-Agent artifact directory.")
    validate.add_argument("--artifact-root", required=True, help="Run root containing track/ and agent_artifacts/.")

    return parser


def command_build_cards(args: argparse.Namespace) -> None:
    cards = build_sequence_cards(
        args.original_stats,
        args.enhanced_stats,
        original_seq_col=args.original_seq_col,
        enhanced_seq_col=args.enhanced_seq_col,
    )
    write_sequence_cards(cards, args.out_csv, args.out_jsonl)
    print(json.dumps({"sequence_cards": len(cards), "out_csv": args.out_csv, "out_jsonl": args.out_jsonl}, indent=2))


def command_run(args: argparse.Namespace) -> None:
    report = run_scheduler(
        cards=read_jsonl(args.cards),
        policy_pool_csv=args.policy_pool,
        output_root=args.output_root,
        experiment_name=args.experiment_name,
        method=args.method,
        budget_frac=args.budget,
        materialize=args.materialize,
        min_confidence=args.min_confidence,
        enforce_density_policy=not args.no_density_policy,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


def command_validate(args: argparse.Namespace) -> None:
    root = Path(args.artifact_root)
    required = [
        root / "agent_artifacts" / "selection.csv",
        root / "agent_artifacts" / "trace.jsonl",
        root / "agent_artifacts" / "report.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    track_files = sorted((root / "track").glob("*.txt"))
    if not track_files:
        missing.append(str(root / "track" / "*.txt"))
    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(missing))
    report = json.loads((root / "agent_artifacts" / "report.json").read_text(encoding="utf-8"))
    result = {
        "valid": True,
        "track_files": len(track_files),
        "method": report.get("method"),
        "budget_frac": report.get("budget_frac"),
        "hrti_frame_frac": report.get("hrti_frame_frac"),
        "relative_cost": report.get("relative_cost"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build-cards":
        command_build_cards(args)
    elif args.command == "run":
        command_run(args)
    elif args.command == "validate":
        command_validate(args)
    else:
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
