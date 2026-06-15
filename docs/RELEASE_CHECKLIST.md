# Release Checklist

Use this checklist before uploading the anonymous GitHub artifact.

## Required

- [ ] `python -m unittest discover -s tests` passes.
- [ ] `cost-agent-mot build-cards`, `cost-agent-mot run`, and
  `cost-agent-mot validate` pass on `examples/toy`.
- [ ] No raw dataset files, model weights, private candidate outputs, or caches
  are committed.
- [ ] No local absolute paths, user names, API keys, tokens, or author
  affiliations appear in tracked files.
- [ ] README states that Cost-Agent is a scheduler over validated candidates.
- [ ] Optional LLM adapter is labeled as non-paper, disabled-by-default
  research code.
- [ ] `paper_support/tables/` contains only paper-facing support tables, not
  full benchmark data or private outputs.

## Suggested Commands

```bash
python -m pip install -e .
python -m unittest discover -s tests

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

python scripts/check_anonymity.py
```

Remove `outputs/` before committing unless you intentionally want to publish a
small generated toy run.
