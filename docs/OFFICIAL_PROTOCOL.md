# Official Protocol Boundary

Cost-Agent should be frozen before official-test reporting.

## Selection Boundary

Method selection, score weights, budget choice, and policy rules should be fixed using training-side validation only. Official-test tracking metrics are for final reporting and post-hoc diagnostics, not scheduler selection.

## Cost-Agent Boundary

Cost-Agent selects among legal detector-tracker candidate outputs. It is not a detector, not a tracker, and not a visual agent. It consumes structured sequence cards, budget information, and a finite policy pool.

## HRTI Boundary

High-Resolution Tiled Inference (HRTI) is represented as an enhanced detector stream. On frames that fit within the configured high-resolution call, HRTI can instantiate as one high-resolution full-frame detector call per frame. Users should describe the exact deployment configuration used in their experiments.

## Cost Boundary

The reported relative cost is a deployment-time proxy:

```text
relative_cost = 1 + 3 * hrti_frame_fraction
```

It is not measured latency, energy, or hardware-level cost.

