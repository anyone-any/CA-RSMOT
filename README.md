# Cost-Agent for Remote-Sensing MOT

This repository provides the anonymous paper artifact for **Cost-Agent**, a bounded scheduler for cost-aware remote-sensing multi-object tracking (MOT).

Cost-Agent selects among a finite pool of precomputed detector-tracker candidate outputs. It operates on structured sequence cards, candidate metadata, a budget constraint, and a verifier. It does not access images, crops, detector tensors, boxes to edit, or track IDs to rewrite.

> Paper boundary: Cost-Agent is a verifier-bounded finite-action scheduler. It is not an LLM tracker, not a generative visual agent, not a detector, and not a module that edits trajectories.

## Repository Contents

- `cost_agent_mot/`: reusable Python package for card construction, budgeted stream selection, policy verification, and traceable materialization.
- `scripts/`: command-line entry points for card building, scheduling, and artifact validation.
- `examples/toy/`: a small runnable example with synthetic detector statistics and tiny MOT-style candidate tracks.
- `configs/`: public configuration templates for a frozen Cost-Agent run.
- `paper_support/tables/`: paper-facing CSV support tables for protocol, trace, budget, and scheduler diagnostics.
- `docs/`: reproducibility, data, artifact, protocol, and claim-boundary notes.
- `.github/workflows/ci.yml`: GitHub Actions workflow for the toy pipeline.

The repository intentionally excludes raw datasets, model weights, private paths, and author-identifying information.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

## Quick Start

Run from this repository root with the installed CLI:

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

Generated artifacts:

- `outputs/toy/sequence_cards.csv`
- `outputs/toy/sequence_cards.jsonl`
- `outputs/toy/cost_agent_b055/track/*.txt`
- `outputs/toy/cost_agent_b055/agent_artifacts/selection.csv`
- `outputs/toy/cost_agent_b055/agent_artifacts/trace.jsonl`
- `outputs/toy/cost_agent_b055/agent_artifacts/report.json`

You can also run the repository test:

```bash
python -m unittest discover -s tests
```

The legacy script entry points remain available:

```bash
python scripts/build_sequence_cards.py --help
python scripts/run_cost_agent.py --help
python scripts/validate_artifacts.py --help
```

## Method Boundary

Cost-Agent is a scheduler, not a detector or tracker. Its pipeline is:

1. Build image-free sequence cards from original and HRTI detector statistics.
2. Rank sequences with a fixed Cost-Agent ranking score.
3. Select HRTI only while the frame-weighted enhanced-frame budget is respected.
4. Choose one tracker policy from a finite policy pool using density-aware rules.
5. Verify every stream-policy pair before execution.
6. Materialize the selected candidate track files and emit traceable artifacts.

The relative-cost proxy is:

```text
relative_cost = 1 + 3 * hrti_frame_fraction
```

It estimates detector-stream calls under the selected schedule. It is not measured wall-clock latency, energy, or hardware-level cost.

## Paper Support

The paper-facing support files are under `paper_support/tables/`:

- frozen official-test sequence decisions and trace examples;
- scheduler-ablation, validation-curve, and runtime-cost proxy tables;
- contextual tracker-baseline tables used only for positioning;
- sequence-card schema and policy-pool documentation.

These files are for reproducibility inspection and manuscript support. They are not used as official-test scheduler inputs.

## Real Candidate Outputs

To run on a real benchmark, provide:

- Per-sequence detector statistics for the original stream.
- Per-sequence detector statistics for the HRTI stream.
- Candidate tracking result directories for every legal stream-policy pair.
- A `policy_pool.csv` with paths to those candidate directories.

The scheduler only copies or symlinks already-generated candidate track files. Benchmark evaluation should be performed separately with the target dataset's official evaluator.

## Optional LLM Adapter

`cost_agent_mot.llm_adapter` provides an optional fail-closed structured JSON adapter for future experiments inspired by tool-orchestration workflows. It is disabled by default and is not part of the paper's frozen official results. See `docs/LLM_ADAPTER.md`.

## Anonymity

This archive uses anonymous placeholders and repository-local paths. Add author names, affiliations, external dataset links, and a final project URL after review policy permits de-anonymization.

## Documentation Map

- `docs/REPRODUCIBILITY.md`: minimal verification and full experiment checklist.
- `docs/OFFICIAL_PROTOCOL.md`: train-validation selection and frozen-test protocol notes.
- `docs/CLAIM_BOUNDARY.md`: statements that this artifact supports and does not support.
- `docs/DATA.md`: dataset, weights, and generated-output policy.
- `docs/ARTIFACTS.md`: generated run artifact layout.
- `docs/LLM_ADAPTER.md`: optional structured LLM adapter boundary.
- `CONTRIBUTING.md`: anonymous-review contribution checklist.
- `CITATION.cff`: citation metadata placeholder for the anonymous artifact.
