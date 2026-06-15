# Official-Train Validation Agent Selection

Selection uses only the 75 official training sequences split into five held-out validation folds.
No official test metric is used. Cost cap: relative_cost <= 2.650.

| rank | experiment | method | budget | enh. frac | cost | val HOTA | val IDF1 | val IDSW | eligible |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | cost_agent_cost_agent_b055 | cost_agent | 0.55 | 0.547 | 2.640 | 72.385±2.581 | 81.984±2.282 | 2636.600±502.309 | True |
| 2 | cost_agent_cost_agent_b060 | cost_agent | 0.60 | 0.600 | 2.800 | 72.376±2.596 | 81.930±2.321 | 2652.800±516.652 | False |
| 3 | cost_agent_density_high_b050 | density_high | 0.50 | 0.498 | 2.495 | 72.333±2.559 | 81.888±2.229 | 2667.600±521.347 | True |
| 4 | cost_agent_cost_agent_b050 | cost_agent | 0.50 | 0.500 | 2.499 | 72.323±2.589 | 81.866±2.283 | 2662.400±517.939 | True |
| 5 | cost_agent_density_high_b030 | density_high | 0.30 | 0.297 | 1.891 | 72.313±2.563 | 81.870±2.237 | 2660.400±539.603 | True |
| 6 | cost_agent_density_high_b045 | density_high | 0.45 | 0.448 | 2.343 | 72.311±2.539 | 81.842±2.195 | 2668.800±522.717 | True |
| 7 | cost_agent_agent_v2_b050 | agent_v2 | 0.50 | 0.499 | 2.496 | 72.297±2.590 | 81.823±2.328 | 2667.800±539.993 | True |
| 8 | cost_agent_density_high_b040 | density_high | 0.40 | 0.398 | 2.194 | 72.292±2.550 | 81.821±2.227 | 2663.800±532.862 | True |
| 9 | cost_agent_agent_v2_b040 | agent_v2 | 0.40 | 0.399 | 2.197 | 72.287±2.621 | 81.815±2.338 | 2681.600±556.571 | True |
| 10 | cost_agent_cost_agent_b040 | cost_agent | 0.40 | 0.399 | 2.197 | 72.285±2.590 | 81.823±2.279 | 2670.200±546.148 | True |

## Frozen Selection

`cost_agent_cost_agent_b055` is frozen for official test-once evaluation.
Validation HOTA: 72.385±2.581; relative cost: 2.640.
