"""Budget-aware Cost-Agent scheduler."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .executor import TraceableExecutor, load_policy_pool
from .planner import PlannerConfig, build_planner, score_key
from .verifier import verify_decision


def select_hrti_sequences(cards: list[dict[str, Any]], method: str, budget_frac: float) -> set[str]:
    """Select whole sequences for HRTI under a frame-weighted budget."""
    if budget_frac <= 0:
        return set()
    if budget_frac >= 1:
        return {str(card["sequence"]) for card in cards}
    total_frames = sum(int(card.get("frames", 0)) for card in cards)
    allowed = budget_frac * total_frames
    key = score_key(method)
    ranked = sorted(cards, key=lambda card: (float(card.get(key, 0.0)), -int(card.get("frames", 0))), reverse=True)
    selected: set[str] = set()
    used = 0
    for card in ranked:
        frames = int(card.get("frames", 0))
        if used + frames <= allowed + 1e-9:
            selected.add(str(card["sequence"]))
            used += frames
    return selected


def build_decisions(
    cards: list[dict[str, Any]],
    *,
    method: str,
    budget_frac: float,
    allowed_pairs: set[tuple[str, str]],
    planner_config: PlannerConfig | None = None,
    min_confidence: float = 0.60,
    enforce_density_policy: bool = True,
) -> list[dict[str, Any]]:
    config = planner_config or PlannerConfig(name=method)
    planner = build_planner(config)
    selected_hrti = select_hrti_sequences(cards, method, budget_frac)
    decisions: list[dict[str, Any]] = []
    for card in cards:
        stream = "hrti" if str(card["sequence"]) in selected_hrti else "original"
        raw = planner.propose(card, selected_stream=stream)
        executable, meta = verify_decision(
            card,
            raw,
            allowed_pairs=allowed_pairs,
            min_confidence=min_confidence,
            enforce_density_policy=enforce_density_policy,
        )
        executable["raw_planner_decision"] = raw
        executable["verifier"] = meta
        decisions.append(executable)
    return decisions


def run_scheduler(
    *,
    cards: list[dict[str, Any]],
    policy_pool_csv: str | Path,
    output_root: str | Path,
    experiment_name: str,
    method: str = "cost_agent",
    budget_frac: float = 0.55,
    materialize: str = "copy",
    planner_config: PlannerConfig | None = None,
    min_confidence: float = 0.60,
    enforce_density_policy: bool = True,
) -> dict[str, Any]:
    pool = load_policy_pool(policy_pool_csv)
    executor = TraceableExecutor(pool, materialize=materialize)
    decisions = build_decisions(
        cards,
        method=method,
        budget_frac=budget_frac,
        allowed_pairs=executor.allowed_pairs,
        planner_config=planner_config or PlannerConfig(name=method),
        min_confidence=min_confidence,
        enforce_density_policy=enforce_density_policy,
    )
    output_root = Path(output_root)
    track_dir = output_root / experiment_name / "track"
    artifact_dir = output_root / experiment_name / "agent_artifacts"
    return executor.build_mixed_tracker(
        cards=cards,
        executable_decisions=decisions,
        output_track_dir=track_dir,
        selection_csv=artifact_dir / "selection.csv",
        trace_jsonl=artifact_dir / "trace.jsonl",
        report_json=artifact_dir / "report.json",
        method=method,
        budget_frac=budget_frac,
    )

