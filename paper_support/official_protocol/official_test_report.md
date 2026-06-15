# Frozen Official Test Report

This report is generated after freezing the method and budget using only official-train validation folds.
The official test split is used only for this final evaluation step.

| Method | Enh. frac | Rel. cost | HOTA | MOTA | IDF1 | IDSW | Frag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen train-val-selected Cost-Agent | 0.547 | 2.641 | 62.614 | 62.138 | 73.338 | 6465 | 6051 |
| Original stream + verified policy | 0.000 | 1.000 | 61.882 | 60.656 | 72.410 | 6829 | 6731 |
| Always-HRTI + verified policy | 1.000 | 4.000 | 62.457 | 62.156 | 73.252 | 6647 | 6016 |
| Original BoT-SORT BoT_SORT | 0.000 | 1.000 | 61.823 | 60.659 | 72.323 | 6769 | 6574 |
| Always-HRTI BoT-SORT BoT_SORT | 1.000 | 4.000 | 62.430 | 62.037 | 73.131 | 6831 | 6020 |

## Frozen Agent Deltas

- vs Original stream + verified policy: HOTA +0.732, IDF1 +0.928, IDSW -364.
- vs Always-HRTI + verified policy: HOTA +0.157, IDF1 +0.086, IDSW -182; cost saving 34.0% relative to the 4x HRTI proxy.
- vs Original BoT-SORT BoT_SORT: HOTA +0.791, IDF1 +1.015.
- vs Always-HRTI BoT-SORT BoT_SORT: HOTA +0.184, IDF1 +0.207.

## Claim Boundary

Safe claim: the frozen reasoning-only agent improves over the original-stream baselines and approaches the always-HRTI result while using about half of the enhanced frames.
Do not claim statistically significant superiority over always-HRTI without a paired sequence-level significance test.
