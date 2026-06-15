# Data

This repository does not include raw remote-sensing frames, annotations, detector weights, or tracker weights.

Required runtime inputs:

- `original_stats.csv`: per-sequence detector statistics for the original stream.
- `enhanced_stats.csv`: per-sequence detector statistics for the HRTI stream.
- `policy_pool.csv`: legal detector-stream and tracker-policy candidate directories.
- Candidate track files: one `SEQUENCE.txt` file per sequence under every candidate directory referenced by the policy pool.

Candidate track files should follow the benchmark format expected by the downstream evaluator. The toy example uses compact MOT-style rows only to demonstrate repository mechanics.

