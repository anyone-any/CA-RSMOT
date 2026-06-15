"""Traceable executor for materializing mixed detector-tracker outputs."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io_utils import clean_dir, link_or_copy, read_csv_rows, to_float, write_csv_rows, write_json, write_jsonl
from .planner import score_key
from .schemas import SELECTION_FIELDS


@dataclass(frozen=True)
class PolicyEntry:
    policy_id: str
    stream: str
    tracker_policy: str
    track_dir: Path
    description: str = ""


def _resolve_path(value: str, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def load_policy_pool(path: str | Path) -> dict[tuple[str, str], PolicyEntry]:
    path = Path(path)
    pool: dict[tuple[str, str], PolicyEntry] = {}
    for row in read_csv_rows(path):
        stream = row["stream"].strip().lower()
        tracker_policy = row["tracker_policy"].strip().lower()
        pool[(stream, tracker_policy)] = PolicyEntry(
            policy_id=row.get("policy_id", f"{stream}_{tracker_policy}").strip(),
            stream=stream,
            tracker_policy=tracker_policy,
            track_dir=_resolve_path(row["track_dir"].strip(), path.parent),
            description=row.get("description", ""),
        )
    return pool


class TraceableExecutor:
    def __init__(self, policy_pool: dict[tuple[str, str], PolicyEntry], *, materialize: str = "copy"):
        self.policy_pool = policy_pool
        self.materialize = materialize

    @property
    def allowed_pairs(self) -> set[tuple[str, str]]:
        return set(self.policy_pool)

    def build_mixed_tracker(
        self,
        *,
        cards: list[dict[str, Any]],
        executable_decisions: list[dict[str, Any]],
        output_track_dir: str | Path,
        selection_csv: str | Path,
        trace_jsonl: str | Path,
        report_json: str | Path,
        method: str,
        budget_frac: float,
        original_cost: float = 1.0,
        hrti_cost: float = 4.0,
    ) -> dict[str, Any]:
        if len(cards) != len(executable_decisions):
            raise ValueError("cards and executable decisions must have the same length")
        out_dir = clean_dir(output_track_dir, "*.txt")
        rows: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []
        stream_counts: Counter[str] = Counter()
        pair_counts: Counter[str] = Counter()
        hrti_frames = 0
        total_frames = sum(int(card.get("frames", 0)) for card in cards)
        ranking_key = score_key(method)

        for card, decision in zip(cards, executable_decisions):
            seq = str(card["sequence"])
            stream = str(decision["selected_stream"])
            tracker_policy = str(decision["selected_policy"])
            entry = self.policy_pool.get((stream, tracker_policy))
            if entry is None:
                raise KeyError(f"No policy-pool entry for {(stream, tracker_policy)}")
            src = entry.track_dir / f"{seq}.txt"
            dst = out_dir / f"{seq}.txt"
            link_or_copy(src, dst, mode=self.materialize)

            frames = int(card.get("frames", 0))
            if stream == "hrti":
                hrti_frames += frames
            stream_counts[stream] += 1
            pair_counts[f"{stream}+{tracker_policy}"] += 1
            rows.append(
                {
                    "sequence": seq,
                    "method": method,
                    "budget_frac": budget_frac,
                    "detector_stream": stream,
                    "executed_policy": tracker_policy,
                    "confidence": decision.get("confidence", ""),
                    "risk_level": decision.get("risk_level", ""),
                    "frames": frames,
                    "base_card_score": to_float(card.get("base_card_score")),
                    "cost_agent_score": to_float(card.get("cost_agent_score")),
                    "ranking_key": ranking_key,
                    "ranking_score": to_float(card.get(ranking_key)),
                    "reason": decision.get("reason", ""),
                    "track_source": str(src),
                }
            )
            trace.append(
                {
                    "sequence": seq,
                    "method": method,
                    "budget_frac": budget_frac,
                    "sequence_card": trace_card(card),
                    "raw_planner_decision": decision.get("raw_planner_decision", {}),
                    "verifier": decision.get("verifier", {}),
                    "executor": {"source_track": str(src), "target_track": str(dst)},
                }
            )

        hrti_frac = hrti_frames / max(total_frames, 1)
        relative_cost = (original_cost * (total_frames - hrti_frames) + hrti_cost * hrti_frames) / max(total_frames, 1)
        report = {
            "method": method,
            "budget_frac": budget_frac,
            "output_track_dir": str(out_dir),
            "num_sequences": len(cards),
            "total_frames": total_frames,
            "hrti_frames": hrti_frames,
            "hrti_frame_frac": hrti_frac,
            "relative_cost": relative_cost,
            "stream_counts": dict(stream_counts),
            "stream_policy_counts": dict(pair_counts),
            "structured_input_only": True,
            "no_image_or_box_editing": True,
            "materialize": self.materialize,
        }
        write_csv_rows(selection_csv, rows, SELECTION_FIELDS)
        write_jsonl(trace_jsonl, trace)
        write_json(report_json, report)
        return report


def trace_card(card: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "frames",
        "det_ratio",
        "det_delta_frac",
        "low_score_delta",
        "volatility",
        "class_mix",
        "density_extreme",
        "density_score",
        "uncertainty_score",
        "base_card_score",
        "cost_agent_score",
    ]
    return {key: card.get(key) for key in keys}

