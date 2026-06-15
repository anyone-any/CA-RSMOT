"""Optional structured LLM adapter for future Cost-Agent experiments.

The paper's frozen results do not use this adapter. The default scheduler is
deterministic and verifier-bounded. This module is provided for researchers who
want to study language-model policy proposals over the same structured,
image-free sequence cards while preserving fail-closed validation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .planner import HeuristicPlanner, PlannerConfig
from .schemas import ALLOWED_POLICIES, ALLOWED_STREAMS, DEFAULT_DECISION, RISK_LEVELS
from .verifier import normalize_decision


LLM_SYSTEM_PROMPT = """You are a structured policy proposal module for Cost-Agent MOT.
You receive only sequence-card metadata and candidate-policy metadata.
You never see images, crops, detector tensors, ground-truth labels, boxes to edit, or track IDs to rewrite.
Return exactly one compact JSON object with:
{"selected_stream":"original","selected_policy":"standard","confidence":0.9,"risk_level":"low","reason":"short"}
selected_stream must be original or hrti.
selected_policy must be standard, strict, or crowded_scene.
risk_level must be low, medium, high, or unknown.
Be conservative and do not invent visual evidence.
"""


@dataclass(frozen=True)
class LLMAdapterConfig:
    mode: str = "off"
    min_confidence: float = 0.60
    cache_path: str | None = None
    log_path: str | None = None
    dry_run: bool = True


class StructuredLLMPolicyAdapter:
    """Fail-closed adapter around structured LLM policy proposals.

    The adapter intentionally exposes no network client. Users can subclass
    ``call_model`` or wrap this class with their preferred provider. Invalid,
    low-confidence, or disabled responses fall back to the deterministic
    Cost-Agent planner.
    """

    def __init__(self, config: LLMAdapterConfig | None = None):
        self.config = config or LLMAdapterConfig()
        self.fallback = HeuristicPlanner(PlannerConfig(name="cost_agent"))
        self.cache = _JsonCache(self.config.cache_path)
        self.log_path = Path(self.config.log_path) if self.config.log_path else None

    @property
    def enabled(self) -> bool:
        return self.config.mode not in {"", "off", "none"}

    def propose(self, card: dict[str, Any], *, selected_stream: str) -> dict[str, Any]:
        fallback = self.fallback.propose(card, selected_stream=selected_stream)
        if not self.enabled:
            self._log(card, None, fallback, {"source": "disabled", "fallback": True})
            return fallback

        key = _cache_key(card, selected_stream)
        raw = self.cache.get(key)
        source = "cache" if raw is not None else "model"
        if raw is None:
            raw = self.call_model(card, selected_stream=selected_stream)
            self.cache.set(key, raw)

        decision = normalize_decision(raw)
        meta = {"source": source, "fallback": False, "errors": []}
        if decision["selected_stream"] not in ALLOWED_STREAMS:
            meta["errors"].append("invalid_stream")
        if decision["selected_policy"] not in ALLOWED_POLICIES:
            meta["errors"].append("invalid_policy")
        if decision["risk_level"] not in RISK_LEVELS:
            meta["errors"].append("invalid_risk")
        if float(decision.get("confidence", 0.0)) < self.config.min_confidence:
            meta["errors"].append("below_min_confidence")
        if decision["selected_stream"] != selected_stream:
            meta["errors"].append("stream_override_not_allowed")

        if meta["errors"]:
            meta["fallback"] = True
            self._log(card, raw, fallback, meta)
            return fallback
        self._log(card, raw, decision, meta)
        return decision

    def call_model(self, card: dict[str, Any], *, selected_stream: str) -> dict[str, Any]:
        """Return a model proposal.

        The base implementation is deterministic dry-run behavior. Override
        this method to connect an OpenAI-compatible or local model endpoint.
        """
        if not self.config.dry_run:
            raise RuntimeError("No model client configured. Subclass call_model or use dry_run=True.")
        return self.fallback.propose(card, selected_stream=selected_stream)

    def _log(
        self,
        card: dict[str, Any],
        raw: dict[str, Any] | None,
        decision: dict[str, Any],
        meta: dict[str, Any],
    ) -> None:
        if self.log_path is None:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "sequence": card.get("sequence"),
            "raw": raw,
            "decision": decision,
            "meta": meta,
            "boundary": "structured_cards_only_no_visual_inputs",
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


class _JsonCache:
    def __init__(self, path: str | None):
        self.path = Path(path) if path else None
        self.data: dict[str, Any] = {}
        if self.path and self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, key: str) -> dict[str, Any] | None:
        value = self.data.get(key)
        return value if isinstance(value, dict) else None

    def set(self, key: str, value: dict[str, Any]) -> None:
        if self.path is None:
            return
        self.data[key] = value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _cache_key(card: dict[str, Any], selected_stream: str) -> str:
    payload = {
        "sequence": card.get("sequence"),
        "selected_stream": selected_stream,
        "frames": card.get("frames"),
        "density_score": card.get("density_score"),
        "uncertainty_score": card.get("uncertainty_score"),
        "delta_score": card.get("delta_score"),
        "base_card_score": card.get("base_card_score"),
        "cost_agent_score": card.get("cost_agent_score"),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
