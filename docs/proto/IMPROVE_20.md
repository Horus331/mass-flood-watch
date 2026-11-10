# Twenty improvements toward a calibrated failure probability: what exists, what is left (8 Nov 2026)

Goal (Mo's proposal): "this road has a 70 % probability of closing in the next 24 h", where 70 % is true about 70 % of the time.
Rule for every item: it goes live only if it passes the held-out storms (docs/proto/PROTOCOL.md, proto/score_v2.py), as T2 (5 Nov) and P1 (8 Nov) did.
Live set-up today: 20 m LISFLOOD-FP, T2 terrain, depth from rain onset, P1 rise rule, 8 time-lagged HRRR members (likely = 2 of 8).
Inventory below is from the repository docs (STATUS.md is from 25 Oct; CHANGE_2026-11-05.md and CHANGE_2026-11-08.md override it).

| # | Item | Already in the repository | Verdict so far | Left to do (order of work) |
|---|---|---|---|---|
| 0 | 5-min frames everywhere | live boxes 15 min, district shadow 60 min, what-if 15 min, replays 5 min | in progress 8 Nov (tools/frames_push.sh, LF_COMPACT) | test, then live |
| 1 | HRRR bias correction | qmfit, LF_HRRR_QMAP, forecast/ENSEMBLE.md §2 | rejected: lift falls, no recall gain; the error is where/when, not how much | volume fix that keeps placement: tested 10 Nov on 17 issue times, p90 F1 0.504 vs p80 0.442: live 20,90 kept (forecast/BOX_PERCENTILE.md) |
| 2 | more NWP members | REFS archived every 6 h since 29 Oct | not tried (no HREF hindcast archive) | forward-only check on the REFS archive |
| 3 | radar nowcast | live_feeds pysteps, display only | 0-1 h beats persistence 3 of 4 | blend 0-3 h into the forecast rain; verify |
| 4 | bigger ensemble | 8 lagged members live; n12 perturbation never scored | lagged adopted (recall 0.21 -> 0.34) | score perturbations; finish P2 |
| 5 | drains / inlets | LF_DRAINS, LF_INLETS | opt-in, not adopted (Δ0 recall, gauge error up) | drains v2 with the 28,936 MassDOT inlets |
| 6 | culverts | T2 live; p_culvert opt-in | T2 live; p_culvert helps learned model (+0.074) | culvert as a hydraulic structure |
| 7 | soils | CN live (x0.88) | DCIA, B0 rejected | Green-Ampt / SSURGO Ksat |
| 8 | antecedent wetness | LF_CN_AMC=auto/nwm | NWM retest pre-registered, pending | score it; groundwater |
| 9 | river inflows | LF_INFLOW (Vermont only) | not tried in D3 | pre-registered D3 test |
| 10 | finer grid | 10 m opt-in | 4x over-flag from a start-up artefact (since fixed by rain-onset depth) | 10 m urban sub-boxes retest |
| 11 | ML on top of physics | closure_ml, latent L1 | L1 passes (0.204 -> 0.327) but not wired | wire L1 under a new pre-registration |
| 12 | calibration | prior_platt.json, reliability plot | rule Brier skill -2.11 | isotonic calibration of p_close and the k-of-8 count |
| 13 | repeat-flood prior | massdot_repeat_flood_d3.csv (evaluation) | not tried; leakage risk | leakage-safe prior |
| 14 | 1/6/24 h windows | arrival_h, hours_over_30cm | not tried | window probabilities |
| 15 | emulator | proto/surrogate (pre-registered) | not run | run batch 1 |
| 16 | more labels | rounds 1-3, SeeClickFix | adopted 90 -> 98 sites | Waze / HOC when MassDOT sends them |
| 17 | negatives | DPW only | not adopted | confirmed-dry labels |
| 18 | in-storm update | none | not tried | report-conditioned update |
| 19 | evaluation protocol | PROTOCOL v2, score_v2, forward test | live (1 storm scored: false alarm) | keep scoring storms |
| 20 | damage fragility | proto/damage.py opt-in | AUC 0.78 vs 0.68 (CI includes 0) | second damage storm; pavement curves |

Order of work: 0, then 12 + 11 (they decide whether "70 %" is honest), 8 and 15 (already queued), 3 + 14, 1 (volume), 18, 9, 10, 7, 20, 5/6, 13, 17, 2, 16 when data arrives.
