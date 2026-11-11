# Held-out calibration of the chance of flooding (π): pre-registration (11 Nov 2026)

Committed before any fold below is fitted. Results go to `PI_HELDOUT.md` whatever they are.

## Why
`LIVE_PI.md` checks 1–4 passed, but with the frozen fit (`fit_all.json`) that had seen every storm it was checked on. The master prompt
requires calibration shown on held-out storms before any percentage is displayed. The benchmark (`scoring/BENCHMARK_v3.md`) also showed that
an isotonic map fitted on Leominster alone does not transfer, so this is a real question.

## Design (fixed now)
- Runs: the T2 replay runs used in `LIVE_PI.md` (`results/site_*_t2` on Turing, live physics: T2 terrain, depth from rain onset).
- For each run's storm t: refit the latent model exactly as `latent_label.em` (same priors, sources, hazard and reporting terms) on the
  cached parity storms **without t** (24 storms); standardise with that fold's statistics; town activity from the fold's storms only
  (`latent_label.design_new`). Then π and the fold's detection P(report | flooded) on t's T2 run.
- No other change. No tuning of anything after seeing a fold.

## Checks (the LIVE_PI.md thresholds, now held out)
1. **Calibration in the large:** Σ π × detection vs observed reported segments. Pass: pooled ratio 0.67–1.5 and every storm within 1/3–3.
2. **Leominster sep2023, complete DPW domain, with sep2023 held out of the fit:** Brier skill > 0 against a constant at the observed rate,
   and in the top fifth of π the predicted share within ±0.10 of the observed share.
3. Reported, not a pass condition: pooled reliability in 10 bins of expected reports (π × detection) vs observed; ranking (share of report
   sites in the top 3 %) of held-out π vs the published depth rule.

## Decision rule
Pass 1 and 2 → the road rows show "chance of flooding X %" again (`viewer.js PI_SHOW = true`), next to the k-of-8 count, which stays the
headline; the forward test keeps checking it. Either fails → the site keeps "k of 8" only, and the result is written up.
