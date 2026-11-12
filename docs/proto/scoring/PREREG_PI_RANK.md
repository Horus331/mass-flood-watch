# Ranking roads by the chance of flooding (π) instead of depth: pre-registration (12 Nov 2026)

Committed before π is computed on any District 4–6 storm. Results go to `PI_RANK_v3.md` whatever they are.

## Why
Held out of the fit, π ranked District 3 report sites better than the depth rule (0.35 vs 0.22 at the deployed share, 9 T2 storms,
`latent/PI_HELDOUT.md`). Its percentage is not calibrated enough to show, but a ranking needs only order.

## Candidate (fixed now)
P = π from the frozen fit (`latent/fit_all.json`, 28 Oct 2026, fitted on 25 District 3 storms; `latent_live.pi_rows` on each run's
features). No refit. Flag = top 3 % per storm.

## Test
`proto/bench_v3.py`, PROTOCOL_v3 rules. **Decision on Test 2 only** (81 District 4–6 storms, never used in the fit). Test 1 is reported but
in-sample for π (its storms were in the fit).

## Decision
Use π to order the site's "most likely roads" list (the k-of-8 count stays the headline; no percentage shown) only if on Test 2 the 95 %
storm-bootstrap interval of P − M for site recall at 3 % is above 0 and P's PR-AUC is not below M's.
