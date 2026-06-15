# Toy Example

This toy example is intentionally small and synthetic. It verifies the artifact
mechanics without requiring MMOT, detector weights, or large candidate outputs.

Files:

- `original_stats.csv`: image-free detector statistics for the original stream.
- `enhanced_stats.csv`: image-free detector statistics for the HRTI stream.
- `policy_pool.csv`: finite stream-policy pool with repository-local track directories.
- `tracks/`: tiny MOT-style candidate track files for each legal stream-policy pair.

Run:

```bash
cost-agent-mot build-cards \
  --original-stats examples/toy/original_stats.csv \
  --enhanced-stats examples/toy/enhanced_stats.csv \
  --out-csv outputs/toy/sequence_cards.csv \
  --out-jsonl outputs/toy/sequence_cards.jsonl

cost-agent-mot run \
  --cards outputs/toy/sequence_cards.jsonl \
  --policy-pool examples/toy/policy_pool.csv \
  --output-root outputs/toy \
  --experiment-name cost_agent_b055 \
  --budget 0.55

cost-agent-mot validate --artifact-root outputs/toy/cost_agent_b055
```
