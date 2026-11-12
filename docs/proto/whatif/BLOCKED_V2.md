# Blocked culverts, version 2: result (12 Nov 2026)

Pre-registration: `PREREG_BLOCKED_V2.md`. Turing job `whatif_blocked_v2` (2514222). Raw: `blocked_v2.json`. 12 complete open / blocked
pairs (4 blocked scenarios did not finish: r050_frozen, r050_normal, r100_dry, r125_frozen).

| check | needed | result |
|---|---|---|
| 1 closures within 60 m of a blocked crossing, blocked ≥ open | ≥ 75 % of pairs | **0 of 12** |
| 2 peak wet area, blocked ≥ open | ≥ 75 % of pairs | 4 of 12 |

**Decision: not adopted.** No value of maintenance is reported. The what-if explorer's culvert switch now says "not reliable yet".

What the numbers show: with version 2 the blocked runs still close fewer roads near crossings (rain × 1, normal ground: 13 open → 5
blocked) and report far fewer overtopped crossings (106 → 33), while the wet area changes little (6.18 → 5.99 km²). The physics alone
does not explain that. The likely cause is in the closure rules, not the flood: at a crossing, a closure comes mainly from the culvert
rule, which compares the headwater at the culvert's notch cell with the road crest (`prototype.py culvert_probability`). A blocked crossing
has no notch, so that rule loses its input and the pool behind the road is not compared with the crest. The comparison therefore measures
a rule difference, not a physical one. The overlap of closed roads between paired runs is also low (Jaccard 0.0–0.45), so the model's
closure list is sensitive to small terrain changes far from the crossings.

Next (version 3, post-processing only, no new GPU runs): for blocked crossings, close the road when the pool within 40 m upstream
(max of water surface z + h) exceeds the road crest at the crossing; re-run the post step on the existing solves; same two checks,
pre-registered before.
