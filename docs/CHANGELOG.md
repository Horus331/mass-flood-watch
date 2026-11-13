# Changelog

Newest first. Model changes, live-system changes and evaluation results that change what the site says.

## 2026-11-13
- Precipitation phase (snow kept out of the water) on in the live forecast as an artifact fix (`docs/proto/prospective/PHASE_LIVE.md`).
- Forecast: non-issue members skip the per-frame images (speed).

## 2026-11-12
- Road list ordered by pi in the forecast (`docs/proto/scoring/PI_RANK_v3.md`).
- What-if blocked culverts v2: not adopted; the culvert switch is labelled "not reliable yet" (`docs/proto/whatif/BLOCKED_V2.md`).
- Held-out calibration of the chance of flooding: not adopted (pooled 0.56 vs 0.67 needed); site keeps "k of 8" (`docs/proto/latent/PI_HELDOUT.md`).
- Model + stream crossing ranking: not adopted (`docs/proto/scoring/CROSSING_v3.md`).
- Failure Issues now polled by the sentinel (`tools/health_issues.py`).

## 2026-11-11
- Model + traffic ranking: not adopted (`docs/proto/scoring/HYBRID_v3.md`).
- Phase 1 Leominster deep dive: 33 of 54 DPW damage sites missed, mostly edge washouts with ~2 cm modelled water (`docs/proto/phase1/LEOMINSTER_MISSES.md`).
- Held-out calibration of the chance of flooding pre-registered (`docs/proto/latent/PREREG_PI_HELDOUT.md`); code ready, Turing job waiting.
- apt retries in the live workflows after a runner DNS failure broke two forecast runs.
- Golden-storm regression test in CI (`golden.yml`, `docs/proto/GOLDEN.md`); first reference, repeat run identical.
- Container with pinned dependencies (`container/`), golden storm passes inside it; published to ghcr.io/horus331/mass-flood-watch.
- Keeper also re-runs the sentinel when GitHub's schedule is late.
- Sentinel: QUIET / WATCH / ACTIVE every ~10 min, `/status/` page, auto Issues on failing live workflows (`docs/proto/live/SENTINEL.md`).
- Benchmark v3 against six named baselines (`docs/proto/scoring/BENCHMARK_v3.md`): on 81 District 4–6 storms the model beats all, every
  difference significant; on District 3 the static H×V×C score ranks ahead (reports there favour busy roads).
- ADR-001..004, RUNBOOK, CHANGELOG started.

## 2026-11-10
- Evaluation protocol v3 pre-registered (`docs/proto/PROTOCOL_v3.md`), amendment 1 on 11 Nov.
- Rain percentile test: live 20 km / 90th percentile kept (`docs/proto/forecast/BOX_PERCENTILE.md`).
- NWS flash-flood warning polygons fetched for 107 storms (`docs/proto/baselines/`).

## 2026-11-09
- Radar nowcast blended into the first forecast hours of the issue cycle (`docs/proto/forecast/NOWCAST_WINDOWS.md`).
- Calibrated chance-of-flooding text hidden until held-out calibration is proven (`docs/proto/latent/LIVE_PI.md`).
- 5-minute frames everywhere; GPU jobs split into GPU solve + CPU post.

## 2026-11-05
- Terrain fix T2 and closure depth from the rain onset live (`docs/proto/prospective/CHANGE_2026-11-05.md`).

## 13 Nov 2026 — What-if: blocked culverts fixed (version 3, adopted)
- The blocked-culvert switch closed fewer roads than the open one because stream water standing in the notch cut through the road was
  read as water on the road (diagnostic `docs/proto/whatif/diag_*.json`: 27 of 27 open-only closures). Read against the lidar road
  surface in both runs, blocking closes more roads near culverts in 12 of 12 scenario pairs and raises the pool behind them in 12 of 12
  (pre-registered, `docs/proto/whatif/PREREG_BLOCKED_V3.md` → `BLOCKED_V3.md`). The explorer's "not reliable yet" label is removed and it
  shows the version-3 numbers per scenario. The live forecast is unchanged.

## 13 Nov 2026 — Forecast gate: trigger without a box (fixed)
- The 00Z cycle of 13 Nov fired the trigger (Uxbridge 6 h ≈ 25.0 mm) but chose no flood-model box, so no flood run happened and the
  outlook said "Flood model run failed" for Thu–Sat. Cause: the town test compared the value rounded to 0.1 mm with 25 mm, the box score
  used the unrounded value (just under 25). Now both use the unrounded value, and a fired trigger always gets at least one box (the
  wettest point inside District 3), marked `fallback`.
