"""Shared schema constants for public Cost-Agent artifacts."""

from __future__ import annotations

ALLOWED_STREAMS = {"original", "hrti"}
ALLOWED_POLICIES = {"standard", "strict", "crowded_scene"}
RISK_LEVELS = {"low", "medium", "high", "unknown"}

DEFAULT_DECISION = {
    "selected_stream": "original",
    "selected_policy": "standard",
    "confidence": 1.0,
    "risk_level": "unknown",
    "reason": "verified fallback",
}

SEQUENCE_CARD_FIELDS = [
    "sequence",
    "frames",
    "orig_det_count",
    "hrti_det_count",
    "orig_mean_det_per_frame",
    "hrti_mean_det_per_frame",
    "orig_mean_score",
    "hrti_mean_score",
    "orig_low_score_frac",
    "hrti_low_score_frac",
    "det_ratio",
    "det_delta_frac",
    "low_score_delta",
    "volatility",
    "class_mix",
    "density_extreme",
    "density_score",
    "uncertainty_score",
    "delta_score",
    "base_card_score",
    "cost_agent_score",
    "split",
]

SELECTION_FIELDS = [
    "sequence",
    "method",
    "budget_frac",
    "detector_stream",
    "executed_policy",
    "confidence",
    "risk_level",
    "frames",
    "base_card_score",
    "cost_agent_score",
    "ranking_key",
    "ranking_score",
    "reason",
    "track_source",
]

SUMMARY_FIELDS = ["HOTA", "MOTA", "IDF1", "CLR_TP", "CLR_FN", "CLR_FP", "IDSW", "Frag", "Dets", "IDs"]

