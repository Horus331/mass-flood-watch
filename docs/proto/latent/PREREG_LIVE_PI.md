# Live calibrated flooding probability (π): pre-registration (8 Nov 2026)

Committed before any π is computed on the runs named below. Results go to `LIVE_PI.md` whatever they are.

## Why

The forecast's number today is a count of members ("likely" = 2 or more of 8 HRRR runs close the road). That count is not a probability
of the road actually flooding: on held-out storms the rule's Brier skill is −2.11 (`parity/catalog/ml/LOSO.md`). The latent model
(`LATENT.md`, `proto/latent_label.py`) estimates π = P(the road really floods | model output), with the detection of each report source
modelled separately. It is the only model here with positive Brier skill (+0.14, Leominster complete inventory), and in Leominster its
top fifth of roads predicts 0.28 flooded against 0.24 observed (`results.json` calibration).

## What would go live (fixed now)

- Coefficients: `fit_all.json` (θ, standardisation `stats`), frozen at commit 2026-10-28. No refit on anything below.
- Inputs per forecast member run: the same 11 hazard terms as `latent_label.hazard` (from `proto/closure_ml.py` features), computed on
  the member's prototype output. Offset o from that member's peak depth **above the depth at rain onset** (the live P1 convention).
- Road probability shown = mean of π over the members that ran (members that did not flood a road give that road its π, not 0).
- Shown as "chance of flooding, X %" on the road rows and in the CSV, next to the existing likely / possible count. The headline stays
  the k-of-8 count until the checks below pass on the forward test as well.

## Checks (all on runs with the live settings: T2, rain-onset depth, P1, 5-min frames)

Runs: the 9 T2 replay runs used for P1 (`prospective/p1_rise_test_t2.json`), the three 5-7 Nov 2026 replays, and every archived forecast
cycle with radar rain (`archive_followup`). Locked storms stay closed.

1. **Calibration in the large**: Σπ over all segments of a storm, times the fitted detection of the sources operating there, against
   the observed number of matched reports. Pass: pooled ratio between 0.67 and 1.5, and no storm above 3 or below 0.33.
2. **Ranking**: share of report sites in the top 3 % of π versus top 3 % of p_close (score_v2 box domain). Pass: π not lower by more than
   0.03 (non-inferiority, as T2).
3. **Leominster complete inventory (sep2023, DPW)**: Brier skill of π against the DPW inventory > 0, and in the top fifth of π the
   predicted share within ±0.1 of the observed share.
4. **No-rain check**: the forced water-map cycles (WATER_MM runs with rain below the gate): mean π of the top 10 roads below 0.2.

Adopt (shown on the site, headline unchanged) only if 1-4 pass. If any fails, the result is written up and nothing changes on the site.
