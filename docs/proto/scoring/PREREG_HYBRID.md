# Model + traffic ranking: pre-registration (11 Nov 2026)

Committed before the hybrid is fitted or scored on anything. Results go to `HYBRID_v3.md` whatever they are.

## Why
In the v3 benchmark the static H×V×C score (driven by traffic) beat the model in District 3 (32 % vs 20 % of report sites at 3 %), but was
at chance in Districts 4–6. In Leominster's complete DPW inventory, traffic separates damaged segments well (ROC-AUC 0.85, `phase1/LEOMINSTER_MISSES.md`; looked at before this file, which is why the test is on other storms only).

## Candidate (fixed now)
H = logistic regression on the **Leominster sep2023 complete domain only** (1,521 segments, DPW + all sources as positives, as in
PROTOCOL_v3), with two inputs: the model's p_close and log10(1 + AADT). Unregularised MLE (sklearn, C = 1e6). Frozen, then applied to every
test storm. Score = H's probability; ranking = by score; yes/no flag = top 3 % of segments per storm.

## Test (PROTOCOL_v3 rules, `proto/bench_v3.py`)
- Primary: Test 2, the 81 District 4–6 storms. Secondary: Test 1, the 23 held-out District 3 storms.
- Metric: share of report sites in the top 3 %, paired storm bootstrap (2,000) of H − M; PR-AUC reported.

## Decision
Adopt H as the ranking (behind the site's "most likely roads" list) only if, on Test 2, the 95 % interval of H − M for site recall at 3 %
is above 0, and on Test 1 the point estimate of H − M is not below −0.03. Otherwise the model ranking stays and the result is written up.
