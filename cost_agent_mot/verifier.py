"""Conservative verifier for Cost-Agent stream and tracker-policy decisions."""
from __future__ import annotations

from typing import Any

from .schemas import ALLOWED_POLICIES, ALLOWED_STREAMS, DEFAULT_DECISION, RISK_LEVELS


def policy_for_stats(stats: dict[str, Any]) -> str:
    """Map sequence density to the finite tracker-policy pool."""
    density = float(stats.get("mean_det_per_frame", stats.get("orig_mean_det_per_frame", 0.0)))
    if density < 5.5:
        return "strict"
    if density >= 35.0:
        return "crowded_scene"
    return "standard"


def normalize_decision(raw: dict[str, Any] | None) -> dict[str, Any]:
    decision = dict(DEFAULT_DECISION)
    if isinstance(raw, dict):
        decision.update(raw)
    stream = str(decision.get("selected_stream", "original")).strip().lower()
    policy = str(decision.get("selected_policy", "standard")).strip().lower()
    if stream not in ALLOWED_STREAMS:
        stream = "original"
    if policy not in ALLOWED_POLICIES:
        policy = "standard"
    try:
        confidence = float(decision.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    risk = str(decision.get("risk_level", "unknown"))
    if risk not in RISK_LEVELS:
        risk = "unknown"
    return {
        "selected_stream": stream,
        "selected_policy": policy,
        "confidence": max(0.0, min(1.0, confidence)),
        "risk_level": risk,
        "reason": str(decision.get("reason", ""))[:500],
    }


def verify_decision(
    card: dict[str, Any],
    raw_decision: dict[str, Any],
    *,
    allowed_pairs: set[tuple[str, str]],
    min_confidence: float = 0.60,
    enforce_density_policy: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate a planner decision and return an executable decision plus metadata."""
    decision = normalize_decision(raw_decision)
    errors: list[str] = []

    if decision["confidence"] < min_confidence:
        errors.append("below_min_confidence")
        decision["selected_stream"] = "original"
        decision["selected_policy"] = policy_for_stats(card.get("orig", card))

    stats = card.get("hrti") if decision["selected_stream"] == "hrti" else card.get("orig")
    stats = stats or card
    expected_policy = policy_for_stats(stats)
    if enforce_density_policy and decision["selected_policy"] != expected_policy:
        errors.append(f"policy_corrected:{decision['selected_policy']}->{expected_policy}")
        decision["selected_policy"] = expected_policy

    if (decision["selected_stream"], decision["selected_policy"]) not in allowed_pairs:
        errors.append("stream_policy_pair_not_available")
        decision["selected_stream"] = "original"
        decision["selected_policy"] = policy_for_stats(card.get("orig", card))

    if (decision["selected_stream"], decision["selected_policy"]) not in allowed_pairs:
        errors.append("fallback_pair_not_available")
        decision["selected_stream"] = "original"
        decision["selected_policy"] = "standard"

    meta = {
        "allowed": not any(err in {"below_min_confidence", "stream_policy_pair_not_available", "fallback_pair_not_available"} for err in errors),
        "corrected": bool(errors),
        "errors": errors,
        "expected_density_policy": expected_policy,
        "message": "accepted" if not errors else ";".join(errors),
    }
    return decision, meta

