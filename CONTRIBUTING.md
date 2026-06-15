# Contributing

This repository is an anonymous review artifact. During review, please keep
contributions focused on reproducibility, documentation, and bug fixes that do
not reveal author identity.

## Development Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python -m unittest discover -s tests
```

## Contribution Scope

Accepted changes should preserve the Cost-Agent boundary:

- Inputs are structured sequence cards and finite policy-pool metadata.
- The scheduler does not access images, crops, visual tokens, detector tensors,
  ground-truth test labels, or official-test tracking metrics.
- The executor only copies or symlinks existing candidate track files.
- No code path should edit boxes, interpolate trajectories, or rewrite track IDs.

## Pull Request Checklist

- [ ] Toy pipeline still runs.
- [ ] New files contain no private paths, credentials, dataset mirrors, or author-identifying metadata.
- [ ] Claims remain bounded to cost-aware scheduling over validated candidates.
- [ ] Documentation states whether a feature is part of the paper protocol or an optional extension.
