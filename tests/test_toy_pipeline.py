from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cost_agent_mot.io_utils import read_json
from cost_agent_mot.scheduler import run_scheduler
from cost_agent_mot.stats_encoder import build_sequence_cards, write_sequence_cards


class ToyPipelineTest(unittest.TestCase):
    def test_toy_pipeline_writes_artifacts(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        cards = build_sequence_cards(
            repo_root / "examples" / "toy" / "original_stats.csv",
            repo_root / "examples" / "toy" / "enhanced_stats.csv",
        )
        self.assertEqual(len(cards), 4)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_sequence_cards(cards, out / "sequence_cards.csv", out / "sequence_cards.jsonl")
            report = run_scheduler(
                cards=cards,
                policy_pool_csv=repo_root / "examples" / "toy" / "policy_pool.csv",
                output_root=out,
                experiment_name="cost_agent_test",
                budget_frac=0.55,
            )
            artifact_root = out / "cost_agent_test" / "agent_artifacts"
            self.assertTrue((artifact_root / "selection.csv").exists())
            self.assertTrue((artifact_root / "trace.jsonl").exists())
            self.assertTrue((artifact_root / "report.json").exists())
            self.assertEqual(len(list((out / "cost_agent_test" / "track").glob("*.txt"))), 4)
            self.assertEqual(report["method"], "cost_agent")
            self.assertEqual(read_json(artifact_root / "report.json")["num_sequences"], 4)


if __name__ == "__main__":
    unittest.main()

