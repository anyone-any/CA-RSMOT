# Optional LLM Adapter

The paper's frozen official results use the deterministic Cost-Agent scheduler.
They do not use an LLM, generative visual agent, or learned policy proposer.

This repository includes `cost_agent_mot.llm_adapter` only as an optional
research extension for future experiments. It follows the same boundary as the
main scheduler:

- Inputs are structured sequence cards and finite policy metadata.
- The adapter receives no images, crops, visual tokens, detector tensors,
  ground-truth test labels, boxes, or track IDs.
- Outputs are JSON proposals for `selected_stream`, `selected_policy`,
  `confidence`, `risk_level`, and `reason`.
- Invalid or low-confidence responses fall back to the deterministic planner.
- The verifier still checks stream-policy legality before execution.

## Minimal Dry Run

```python
from cost_agent_mot.llm_adapter import LLMAdapterConfig, StructuredLLMPolicyAdapter

adapter = StructuredLLMPolicyAdapter(LLMAdapterConfig(mode="dry_run", dry_run=True))
decision = adapter.propose(sequence_card, selected_stream="original")
```

## Connecting A Model

Subclass `StructuredLLMPolicyAdapter.call_model` and return a JSON-like Python
dictionary. Keep provider credentials outside the repository and avoid logging
private data.

```python
class MyAdapter(StructuredLLMPolicyAdapter):
    def call_model(self, card, *, selected_stream):
        # Build an image-free prompt from card fields only.
        # Call your model provider here.
        return {
            "selected_stream": selected_stream,
            "selected_policy": "standard",
            "confidence": 0.8,
            "risk_level": "medium",
            "reason": "structured dry example",
        }
```

When reporting results produced with this extension, label them separately from
the paper's frozen deterministic Cost-Agent results.
