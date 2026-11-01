# Terrain conditioning: crossing notches and buried streams (pre-registered 1 Nov 2026, PROTOCOL v2)

Fixed and committed **before any candidate run below was started or scored**. Nothing about these candidates has been scored on any storm.
What was looked at beforehand: the model DEM only (inputs, no flood run, no labels), in three boxes, listed in §1.

## 1. The artefacts and their cause (diagnosis, inputs only)

Known symptoms in the published replays: Martin Luther King Jr Blvd, Foster St and segment 12771 in downtown Worcester hold 1–3.7 m of water in
every Worcester box run (0.65–1.4 m even in a 32 mm storm, jul2023); Route 2 (segment 51395) in Leominster holds 8.5 m in sep2023.

`proto/diag_terrain.py` builds the model DEM exactly as `sim/colab/w9_lisflood.py` does and finds every closed basin the solver sees
(D4 priority flood from the box edge: LISFLOOD-FP passes water across cell faces only). Run on GitHub Actions (`probe.yml` on branch
`terrain-fix`, run 41318487771). Two separate causes:

**(a) Chained, disconnected crossing notches (Route 2, segment 12771).** `open_crossings` opens a 3 × 3-cell notch at every mapped crossing down
to the lowest ground within 40 m. It reads that minimum from the DEM *already lowered by the notches opened before it*. Where crossings are
dense (interchanges, a stream crossed by several roads) a deep cut is copied from notch to notch. At the Route 2 / I-190 interchange in
Leominster six crossings (TIGER road-stream intersections `u52483`, `u54660`, `u62881`, `u62898`, `u67824` and NAACC `xy4252683071730952`,
a culvert under I-190, not a bridge) chain a 89.3 m level up to Route 2, whose lidar crest is 114.4 m: a 3 × 3 pit 25 m deep under the road.
The cell that set the level is often only corner-adjacent to the notch, and the depression breaching refuses to carve more than 4 m
(`LF_BREACH_MAX`), so the pit stays closed and fills with rain: 8.5–11 m of "water on Route 2". Segment 12771 (Worcester, near Lincoln
Square) is the same: crossing `u120131` copies 164.25 m from two neighbouring crossings, 8.6 m below the street, leaving a closed pit 5.4 m deep.
**There is no bridge there**: the nearest NBI structure carrying Route 2 is 341 m away, so the bridge mask is not what missed it.

**(b) A buried stream (MLK Jr Blvd, Foster St).** Mill Brook runs in a conduit under downtown Worcester. Its NHDPlus HR flowline is in the
channel grid and every street over it is a mapped crossing, but between streets the lidar keeps buildings and grade over the conduit, so the
burnt flowline climbs over each block. The hollows beside it (MLK Jr Blvd: bottom 138.1 m, spill 141.7 m, 0.06 km², 58,000 m³) are closed
basins the breaching does not open, because its carve path must also cut the climbing flowline.

| box (inputs only) | setting | cells in closed basins > 1 m | road points in basins > 1 m / > 3 m | segments in basins > 3 m |
|---|---|---|---|---|
| Worcester jul2023 | default | 1,883 | 105 / 21 | 12771, 29688, 45256, 45260 (MLK), 49346 |
| | notch fix (a) | 1,867 | 88 / 13 | 45256, 45260, 49346 |
| | notch fix + channel enforcement (a + b) | 857 | 7 / 7 | 49346 |
| Worcester aug2021 | default | 729 | 145 / 28 | 11183, 12771, 29688, 45256, 45260, 49346, 49618 |
| | a + b | 235 | 40 / 14 | 11183, 49346, 49618 |
| Leominster sep2023 | default | 1,825 | 26 / 16 | 544, 884, 51395 (Route 2) |
| | notch fix (a) | 1,816 | 11 / 1 | 544 |
| | a + b | 1,144 | 9 / 1 | 544 |

## 2. Candidates (exact settings; code in this commit)

Both are opt-in switches of `w9_lisflood.py`; the default model does not change. Every run uses the deployed physics
(`LF_PARITY=1 LF_CN_SCALE=0.88`, `LF_LOSS=cn`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, 20 m, CPU) plus:

- **T1 `LF_NOTCH_FIX=1`** — every notch reads its lowest ground, crest and outlet cell from the DEM as it was before any notch (no chaining),
  and is joined to that outlet cell by a face-connected path cut to the notch level (`open_crossings(fix=True)`, `notch_outlet_path`).
- **T2 `LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`** — T1, then the mapped flowlines (channel grid + notch cells, corner steps closed) are
  hydro-enforced before the ordinary breaching: a breach restricted to the channel network, from the box edge, cut per cell ≤ 10 m
  (`LF_CHAN_ENFORCE_MAX`, default 10, fixed a priori as a typical maximum cover over a culvert or conduit, not tuned). Off-channel cells are
  never lowered by this step; lakes keep their lidar level.

No parameter is fitted to labels; both are "physics changes with no fitted parameter" (PROTOCOL §2) and are scored directly.

## 3. Runs

GitHub Actions `parity_test.yml` (branch `terrain-fix`, CPU, LISFLOOD-FP 8.2), the 25 non-locked catalogue storms on their catalogue boxes and
windows (`docs/proto/parity/catalog/*/config.json`), all at the same commit:

- `docs/proto/terrain/runs/base/` — **in-run baseline**: the deployed settings, no extra env (PROTOCOL §3: same commit, same solver).
- `docs/proto/terrain/runs/t1/` — T1.
- `docs/proto/terrain/runs/t2/` — T2.

(The B0 candidate of `runoff/B0_V2_PREREG.md` shares the in-run baseline.) A run that fails for a technical reason is rerun unchanged.

## 4. Decision (PROTOCOL v2 §5a, k = 2)

`python proto/score_arms.py score` per arm, then
`python proto/score_v2.py --compare docs/proto/terrain/score_base.json docs/proto/terrain/score_t<i>.json --protocol v2 --k 2`.
A candidate is adopted only if all five §5a conditions hold on the held-out 23 (gain ≥ +0.04 at 3 %, one-sided lower bound > 0 at
α = 0.05 / 2, FSS@300 not lower, no ≥ 3-site storm loses > 1 site, alert-tier lift ≥ 0.8 × baseline). If both pass, the one with the larger
gain is adopted. Dev storms (sep2023, aug2021) are reported separately. The in-run baseline is also checked against
`obs/round2/score_round2.json` (parity group): if they differ, that is reported and the in-run baseline is still the reference.

**Reported whatever the verdict:** per-storm sites, rule and 3 % recall; the artefact counts per arm (segments with peak depth > 1 / 2 / 3 m,
flagged segments) and the list of segments whose depth changes by ≥ 0.5 m or whose rule flag flips (`score_arms.py depths`); the depths at
MLK Jr Blvd, Foster St, 12771 and Route 2 before / after; USGS gauge rise errors from each run's `score.json`.

**Display.** The public replays change only if a candidate is adopted; then the whole-district / box display reruns take its env. If neither
is adopted both stay opt-in, and the site's limitations text names the artefacts and the opt-in fix.

Results go to `docs/proto/terrain/TERRAIN.md`.
