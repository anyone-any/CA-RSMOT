"""Deterministic reasoning-only planner used by Cost-Agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .verifier import policy_for_stats


SCORE_KEYS = {
    "cost_agent": "cost_agent_score",
    "density_only": "density_score",
    "uncertainty_only": "uncertainty_score",
    "delta_only": "delta_score",
    "base_card": "base_card_score",
}


@dataclass(frozen=True)
class PlannerConfig:
    name: str = "cost_agent"


class HeuristicPlanner:
    """Feature-only planner bounded by the stream schedule and finite policies."""

    def __init__(self, config: PlannerConfig | None = None):
        self.config = config or PlannerConfig()

    def propose(self, card: dict[str, Any], *, selected_stream: str) -> dict[str, Any]:
        stats = card.get("hrti") if selected_stream == "hrti" else card.get("orig")
        stats = stats or card
        policy = policy_for_stats(stats)
        density = float(stats.get("mean_det_per_frame", card.get("density_score", 0.0)))
        score = float(card.get("cost_agent_score", 0.0))
        reason = (
            f"{selected_stream} stream selected by {self.config.name}; "
            f"density={density:.3f}, cost_agent_score={score:.3f}"
        )
        return {
            "selected_stream": selected_stream,
            "selected_policy": policy,
            "confidence": 0.90,
            "risk_level": risk_level(card),
            "reason": reason,
            "source": "deterministic_cost_agent",
        }


def build_planner(config: PlannerConfig) -> HeuristicPlanner:
    return HeuristicPlanner(config)


def score_key(method: str) -> str:
    if method not in SCORE_KEYS:
        raise ValueError(f"Unknown scheduler method {method!r}. Choices: {sorted(SCORE_KEYS)}")
    return SCORE_KEYS[method]


def risk_level(card: dict[str, Any]) -> str:
    density = float(card.get("density_score", 0.0))
    uncertainty = float(card.get("uncertainty_score", 0.0))
    if density >= 35.0 or uncertainty >= 0.80:
        return "high"
    if density >= 15.0 or uncertainty >= 0.45:
        return "medium"
    return "low"

