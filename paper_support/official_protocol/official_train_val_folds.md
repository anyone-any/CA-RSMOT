# Official-Train Internal Validation Folds

These folds are built only from the 75 official training sequences. They are intended for scheduler/budget/verifier tuning before the frozen final evaluation on the 50 official test sequences.

| fold | val seq | val frames | val boxes | train seq | train frames | train boxes |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 15 | 1690 | 44910 | 60 | 6682 | 247269 |
| 1 | 15 | 1670 | 52740 | 60 | 6702 | 239439 |
| 2 | 15 | 1671 | 44386 | 60 | 6701 | 247793 |
| 3 | 15 | 1672 | 85849 | 60 | 6700 | 206330 |
| 4 | 15 | 1669 | 64294 | 60 | 6703 | 227885 |

Fold assignment is frame-balanced and does not use any tracking metric or test-label information.
