# Official Test Paired Sequence Significance

This post-hoc check uses sequence-level TrackEval summaries after the frozen test-once evaluation. It is not used for tuning.

| metric | baseline | n | mean delta | 95% bootstrap CI | sign-flip p |
| --- | --- | ---: | ---: | ---: | ---: |
| HOTA | Original_stream_verified_policy | 50 | +0.173 | [-0.322, +0.670] | 0.5036 |
| HOTA | Always_HRTI_verified_policy | 50 | +0.036 | [-0.263, +0.363] | 0.8325 |
| HOTA | Original_BoT-SORT_BoT_SORT | 50 | +0.254 | [-0.167, +0.715] | 0.2863 |
| HOTA | Always-HRTI_BoT-SORT_BoT_SORT | 50 | -0.030 | [-0.344, +0.309] | 0.8668 |
