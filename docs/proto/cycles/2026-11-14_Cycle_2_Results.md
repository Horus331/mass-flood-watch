# Cycle 2 results (11–14 Nov 2026): why the model misses, what does and doesn't help, and the second live storm

## One-page summary

**What was done.** Every test below had its rule committed before any number was computed (PROTOCOL v3). Ten decisions:
2 adopted for skill, 3 adopted as fixes or for the explorer, 5 not adopted.

| test | decided on | result | verdict |
|---|---|---|---|
| Rank roads by the chance of flooding (π) instead of depth | 81 District 4–6 storms (never in the fit) | top-3 % site recall **0.206 → 0.251**, CI [+0.002, +0.086] | **adopted** (forecast road list ordered by π) |
| Show π as a percentage (leave-one-storm-out calibration) | 9 storms | pooled reported / expected 0.56 (needs 0.67–1.5); Leominster DPW check passes (top fifth 27 % vs 24 %) | not adopted: site keeps "k of 8" |
| Model + traffic (AADT) | District 4–6 | 0.196 vs 0.206, CI [−0.041, +0.021] (helps in District 3 only: 0.286) | not adopted |
| Model + stream-crossing flag | District 4–6 | worse: model alone better, CI [+0.036, +0.094] | not adopted |
| Catch-basin sink (capped, clogging-aware) | 23 held-out D3 storms | +0.000 at 3 %; removes sites with flags | not adopted |
| Storm-drain sink on built-up roads (25 mm/h, C2) | 23 held-out D3 storms | 0.194 → 0.184; rule-hit sites 7 → 5 | not adopted |
| Rain vs snow split (C1, HRRR 2 m temperature) | artifact route | no held-out storm below 2 °C, skill unchanged | **adopted as a fix** (live 13 Nov) |
| Blocked culverts in the what-if explorer, v2 | 12 scenario pairs | 0 of 12 in the right direction (artifact: stream water in the culvert notch) | not adopted |
| Blocked culverts v3 (crest-relative reading) | 12 pairs | 12 of 12 direction, 12 of 12 pool rise (+1.4–1.7 m) | **adopted** for the explorer |
| Forecast gate, latency, Zenodo cache | operations | gate bug fixed; closure step 7–19 → 0–2 min; source zip cached | **fixed** |

**Why the model misses (Leominster, 54 DPW damage points: 21 hit, 33 missed).** The misses had almost no modelled water (median 2.4 cm;
hits 79 cm). 26 of the 33 are **edge washouts**: erosion along curb lines and gutters, which a 20 m grid and a 30 cm ponding threshold
cannot see. Crossings are **16 ×** over-represented among damage points (17 of 54 vs 1.9 % of road length); 11 of those 17 were hit.

**Second live storm (12–13 Nov, 19.9 mm District 3 mean, long light rain).** Every forecast said "no road closures"; nothing was
reported (MassDOT, NWS, storm reports). A radar replay with the live rules also found 0. Raw HRRR was ~35 % low across District 3,
but the live 20 km / 90th-percentile spreading gave the forecast box **1.8–3.5 × the radar rain**, and still no false closure.

**What it means for a MassDOT engineer**
- The road list is now ordered by the chance of flooding, which finds about 1 in 4 reported sites in the top 3 % on unseen storms.
- Percentages stay hidden: the model knows *where* water goes, but not yet how often a flood gets *reported*.
- Drains, traffic and crossings do not improve the closure ranking. Drains in the model remove exactly the water that marks real failures
  (the reported sites are where drains were overwhelmed or blocked). Traffic and crossings help only where reports come from busy roads
  or DPW damage lists; they belong in a crew checklist as separate columns.
- The what-if explorer can now show the value of culvert maintenance: blocked culverts raise the pool behind the road by ~1.5 m and
  multiply overtopped crossings (e.g. 2 → 14 at normal ground, 7 → 37 on frozen ground).

**Named limitations**
1. Two quiet live storms so far: the forward test has shown no false alarms but has not yet seen a flooding storm.
2. Edge erosion, the main missed mechanism in Leominster, is not modelled; it needs curb-line flow, not ponding depth.
3. One city (Leominster) has a complete damage inventory; the detection part of π needs more DPW-type lists.
4. The π gain on Districts 4–6 is small (lower bound +0.002); the forward test will show whether it holds.

**What is next (cycle 3)**
- Edge-erosion indicator from curb-line flow (pre-register; Leominster DPW layer if Mo can share it in the repo).
- More complete damage inventories (DPW requests) to calibrate the detection part of π.
- Whole-District 3 map: keep 20,90 footprint, fix the rain amounts (volume-preserving neighbourhood), still a shadow run.
- Solver latency (~1.5 h per member on 4 cores) is the last big delay in each cycle.
- HF forecast archive (waits for the scoped token).

## Slide bullets (complete story)
- **Last time → this update:** we benchmarked against six methods; this cycle asked *why* the model misses and tested five fixes, all with rules fixed first.
- **The miss mechanism:** most missed Leominster damage is edge erosion with ~2 cm of modelled water; ponding depth can't see it.
- **Adopted:** ranking by the chance of flooding (unseen storms 21 % → 25 % of reported sites in the top 3 %).
- **Rejected honestly:** drains (twice), traffic, crossing flag, showing a percentage; each failed its pre-set rule.
- **Live system:** second real storm (13 Nov): correct "no closures", radar replay agrees; three operational faults found and fixed during the storm.
- **Explorer:** blocked culverts now read correctly: ~1.5 m higher pools and 5–7 × more overtopped crossings.
