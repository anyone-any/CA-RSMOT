"""TrackEval-style metric-summary helpers for local experiment artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_utils import read_json, to_float, write_csv_rows, write_json
from .schemas import SUMMARY_FIELDS


def parse_trackeval_summary(eval_dir: str | Path) -> dict[str, float] | None:
    path = Path(eval_dir) / "cls_comb_det_av_summary.txt"
    if not path.exists():
        return None
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    keys = lines[0].split()
    vals = lines[1].split()
    return {key: to_float(val) for key, val in zip(keys, vals)}


def summarize_existing_results(
    *,
    output_csv: str | Path,
    output_json: str | Path,
    baseline_eval_dirs: dict[str, str | Path] | None = None,
    experiment_roots: list[str | Path] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, eval_dir in (baseline_eval_dirs or {}).items():
        metrics = parse_trackeval_summary(eval_dir)
        if metrics is None:
            continue
        row = {"tracker": name, "source": "baseline", "eval_dir": str(eval_dir)}
        row.update({field: metrics.get(field, "") for field in SUMMARY_FIELDS})
        rows.append(row)

    for root in experiment_roots or []:
        root = Path(root)
        report = read_json(root / "agent_artifacts" / "report.json", default={}) or {}
        metrics = parse_trackeval_summary(root / "eval")
        row = {
            "tracker": root.name,
            "source": "cost_agent",
            "eval_dir": str(root / "eval"),
            "method": report.get("method", ""),
            "budget_frac": report.get("budget_frac", ""),
            "hrti_frame_frac": report.get("hrti_frame_frac", ""),
            "relative_cost": report.get("relative_cost", ""),
        }
        if metrics:
            row.update({field: metrics.get(field, "") for field in SUMMARY_FIELDS})
        rows.append(row)

    fields = ["tracker", "source", "method", "budget_frac", "hrti_frame_frac", "relative_cost", "eval_dir", *SUMMARY_FIELDS]
    write_csv_rows(output_csv, rows, fields)
    write_json(output_json, rows)
    return rows

