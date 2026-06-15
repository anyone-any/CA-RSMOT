# Reproducibility

## Minimal Verification

Install the package and run the toy example:

```bash
python -m pip install -e .

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

Expected validation output includes `valid: true`, `track_files: 4`, method
`cost_agent`, and a relative-cost proxy between 1.0 and 4.0.

Run tests:

```bash
python -m unittest discover -s tests
```

## Full Experiment Checklist

Prepare:

- Original-stream detector statistics.
- HRTI-stream detector statistics.
- Candidate tracking outputs for every stream-policy pair in the policy pool.
- A frozen configuration with method, budget, and policy rules.
- A separate benchmark-evaluation step using the target evaluator.

The scheduler emits all selected track sources and verifier decisions, so the scheduling artifact can be audited independently of the evaluator.

## Upload Checklist

Before pushing to GitHub, check:

```bash
python -m unittest discover -s tests
python scripts/check_anonymity.py
```

The second command should report no author-identifying metadata or local paths
during anonymous review. You can add venue-specific markers with `--pattern`,
or add `--strict-secrets` for a stricter credential-word scan.
