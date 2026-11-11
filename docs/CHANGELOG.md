# Changelog

Newest first. Model changes, live-system changes and evaluation results that change what the site says.

## 2026-11-11
- Golden-storm regression test in CI (`golden.yml`, `docs/proto/GOLDEN.md`).
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
