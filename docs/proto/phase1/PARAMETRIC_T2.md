# Leominster culvert blockage on the deployed (T2) terrain: results (16 Nov 2026)

Pre-registration: `PARAMETRIC_T2_PREREG.md` (committed before any run). Runs: GitHub Actions 43857548688, 5 of 5 succeeded.
Readouts: `PM_SET=t2 python proto/parametric_eval.py` then `python proto/parametric_t2_eval.py` → `parametric_t2.json`.
One code fix in the readout after the runs (a segment absent from a run's file was looked up directly; now read as depth 0). No model
setting was changed.

## 1. Results (deployed closure readout, p ≥ 0.5)

| Scenario (T2 terrain) | Segments closed | Storm reports matched (of 89) | DPW points matched (of 54) | Newly closed, no report within 150 m | Base DPW misses now hit (of 33) | Residents losing access (peak) |
|---|---|---|---|---|---|---|
| Base (culverts open) | 85 | 33 | 21 | — | — | 34,154 |
| All culverts 20 % blocked | 86 | 32 | 19 | 11 | 0 | 33,629 |
| All culverts 50 % blocked | 85 | 25 | 15 | 18 | 0 | 32,810 |
| All culverts 100 % blocked | 97 | 23 | 8 | 29 | 0 | 31,325 |
| Smallest third 100 % blocked | 96 | 33 | 21 | 12 | 0 | 34,478 |

On T2 the base closes 85 segments (98 pre-T2) and matches 33 storm reports (35) and 21 DPW points (21). Chance recall at these shares
is 0.02–0.03.

## 2. Readings (rules fixed in the pre-registration)

1. **Blockage is still not readable from the deployed closure count.** At 100 % blockage the closed count rises (85 → 97, rule (a) met),
   but 23 of the 29 segments that stop closing lie within 60 m of a crossing (rule (b) needs fewer than half). Their median peak depth
   falls from 0.40 m to 0.13 m. T2 reduces the artifact (29 lost closures instead of 42) but does not remove it: on the deployed readout,
   stream water in an open notch still counts as road water. Report blockage through the crest readout and the pool rise only.
2. **The crest readout works on T2** (all 4 blocked runs: closures near crossings blocked ≥ open, pool rise ≥ 0).

   | Blocked run | Segments within 60 m of a crossing, closed (crest-relative), open → blocked | Crossings overtopped, open → blocked | Median pool rise (crossings wet in both) | Share with a higher pool |
   |---|---|---|---|---|
   | 20 % | 2 → 2 | 0 → 0 | +0.60 m (392) | 92 % |
   | 50 % | 2 → 10 | 0 → 5 | +1.56 m (375) | 94 % |
   | 100 % | 2 → 82 | 0 → 24 | +2.26 m (368) | 97 % |
   | smallest third, 100 % | 0 → 8 | 0 → 0 | +1.74 m (33) | 100 % |

   The effect grows with the blockage: 20 % changes no road; 50 % closes 8 more segments near crossings; full blockage closes 80 more
   and overtops 24 crossings.
3. **No scenario turns any of the 33 base DPW misses into a hit**, and none reaches Wachusett St or Hamilton St (as in the first study):
   the missing piece remains erosion / washout, not culvert blockage.
4. **The culvert priority list is robust to the terrain.** 8 of the T2 top 10 (full blockage) and 9 of 10 (smallest third) are in the
   pre-T2 top 10.

## 3. Culvert priority list on T2 (model-based candidates; needs condition data to confirm)

Robust = in both the pre-T2 and T2 top 10.

| # | Crossing (stream) | NAACC condition | Roads that close only when blocked | Pool rise | Robust |
|---|---|---|---|---|---|
| 1 | Route 2 / Dewey St (smallest-third run) | OK | Route 2, ramp South St → Route 2 WB, Dewey St (8 segments) | +0.4 m | yes |
| 2 | Meadow Pond Dr | no data | Meadowbrook Acres (4) | +2.6 m | yes |
| 3 | Commercial St / Putnam St / railroad (North Nashua River) | Poor (Commercial St) | Boulder Dr, Putnam St (3) | +2.1 to +4.0 m | yes |
| 4 | Columbia Ave / Dewey St / Route 2 | OK | Columbia Ave, Dewey St, Minneapolis Ave (3) | +1.6 to +2.0 m | yes (2 new Route 2 records join the cluster) |
| 5 | Bathrick Rd | OK / Poor | Bathrick Rd (1) | +2.1 m | yes |
| 6 | Justice Hill Rd (Rocky Brook) | OK | Justice Hill Rd (1) | +0.3 to +1.1 m | yes |
| 7 | Beaman Rd (Wilder Brook) | Poor | Tanglewood Rd (1) | +0.7 m | yes |
| 8 | Pierce Ave | OK | Harvard Ave (1) | +0.6 m | yes |
| 9 | Olin Ave | OK | Route 2 (1) | +0.5 m | yes |

Tisdale St / Manchester St (pre-T2 #5) drops out of the T2 top 10. Route 2 / Dewey St stays first on T2, so it is not the Route 2
chained-notch pit at the I-190 interchange (segment 51395, `terrain/TERRAIN.md`), which T2 removed.

## 4. What this means
- For the parametric story: blockage matters locally (8 to 82 more segments near crossings, pools 0.6 to 2.3 m higher), but it does not
  explain the Leominster damage the model misses.
- For the model: the deployed closure readout should not be used for culvert questions; the what-if explorer already uses the crest
  readout (`whatif/BLOCKED_V3.md`). The live closure rule keeps the cell depth at crossings on purpose: that water is the proxy that finds
  the documented culvert failures, and the crest-relative reading drops Leominster recall from 0.385 to 0.08 (`proto/prototype.py`,
  `whatif/PREREG_BLOCKED_V3.md`). So the live rule stays; the two readouts answer different questions (open-culvert failure vs. blockage).
- The 9 crossings above are the inspection candidates to send with the culvert-condition request.
