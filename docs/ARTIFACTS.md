# Artifact Layout

A Cost-Agent run writes:

- `track/*.txt`: selected candidate tracking result files, one per sequence.
- `agent_artifacts/selection.csv`: executable stream-policy decision per sequence.
- `agent_artifacts/trace.jsonl`: sequence card, planner proposal, verifier result, and executor source/target paths.
- `agent_artifacts/report.json`: budget, HRTI frame fraction, relative-cost proxy, and decision counts.

The executor copies or symlinks existing candidate track files. It does not repair boxes, interpolate trajectories, or rewrite identities.

## Paper Support Tables

`paper_support/tables/` contains paper-facing CSV tables for protocol and reproducibility documentation. These tables support manuscript inspection and should not be used as official-test scheduler inputs.

