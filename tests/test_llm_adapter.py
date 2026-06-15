from __future__ import annotations

import unittest

from cost_agent_mot.llm_adapter import LLMAdapterConfig, StructuredLLMPolicyAdapter


class BadAdapter(StructuredLLMPolicyAdapter):
    def call_model(self, card, *, selected_stream):
        return {
            "selected_stream": "hrti",
            "selected_policy": "not_a_policy",
            "confidence": 0.1,
            "risk_level": "unknown",
            "reason": "invalid proposal",
        }


class LLMAdapterTest(unittest.TestCase):
    def test_disabled_adapter_uses_fallback(self) -> None:
        adapter = StructuredLLMPolicyAdapter(LLMAdapterConfig(mode="off"))
        decision = adapter.propose({"sequence": "S001", "density_score": 1.0}, selected_stream="original")
        self.assertEqual(decision["selected_stream"], "original")
        self.assertIn(decision["selected_policy"], {"standard", "strict", "crowded_scene"})

    def test_invalid_model_output_falls_back(self) -> None:
        adapter = BadAdapter(LLMAdapterConfig(mode="on", dry_run=False))
        decision = adapter.propose({"sequence": "S001", "density_score": 1.0}, selected_stream="original")
        self.assertEqual(decision["selected_stream"], "original")
        self.assertIn(decision["selected_policy"], {"standard", "strict", "crowded_scene"})


if __name__ == "__main__":
    unittest.main()
