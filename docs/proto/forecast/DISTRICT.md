# District 3 forecast: how much should the HRRR rain be spread?

**Problem** (`STATUS.md` §4 a3). The District 3 GPU hindcast of 11 Sept 2023 from the 18z HRRR cycle with the live spreading
(`LF_HRRR_NBHD=20,90`) flags **888 segments (615 km)** at P ≥ 0.5. The radar-driven run (`turing/d3_sep2023_p`) flags **276 (197 km)**.
That is about 3x too many across the district, even though the box-level hindcasts (`HINDCAST.md`, `ENSEMBLE.md`) looked fine.
Its district mean rain is 95 mm, against 46 mm in the radar run (whose peak is higher: 207 vs 158 mm).

## 1. Pre-registration (fixed 28 Oct 2026, before any of the runs below was scored)

**Settings compared.** `LF_HRRR_NBHD` R km / P-th percentile:

- 20,90 (live)
- 10,90 (less area)
- 20,75 (lower intensity)
- 0,50 (a 1-cell footprint, i.e. the raw HRRR field)

**A. District 3 (decision), Turing GPU.** The 18z cycle with each setting: `turing/hindcast_d3_sep2023_18z` (20,90),
`hindcast_d3_18z_nb10p90`, `hindcast_d3_18z_nb20p75`, `hindcast_d3_18z_raw`. Jobs 2426406-8 were submitted before this commit. Every run is
compared with the radar run `turing/d3_sep2023_p` (P ≥ 0.5: 276 segments, 197.0 km).

| metric | definition | role |
| --- | --- | --- |
| ratio_n, ratio_km | flagged segments (P ≥ 0.5) and their km / the radar run's | gate |
| CSI | \|F ∩ R\| / \|F ∪ R\| (= Jaccard), where F = the run's P ≥ 0.5 set and R = the radar set, from `segments.geojson` | ranking |
| radar recall, precision | \|F ∩ R\| / \|R\|, \|F ∩ R\| / \|F\| | reported |
| site recall, lift | `proto/score_v2.py --storm sep2023`, rule and top 3 %; sep2023 is a development storm | reported only |

**Decision rule** (`proto/forecast_nbhd.py decide`):

1. **Gate.** A setting is eligible when ratio_n and ratio_km are both within ±30 % of the radar run (0.7 to 1.3).
2. **Ranking.** Among the eligible settings, the one with the highest CSI wins. Settings within 0.01 of the best CSI are tied. A tie goes to
   the box-level winner (B below): most OOS-7 sites under 2 of 8 at short lead, then most single-cycle OOS-7 sites (short + long lead), then
   the higher 2-of-8 lift. If a run has no `segments.geojson`, CSI cannot be computed. Eligible runs are then ranked by |ln ratio_n|.
3. **None eligible.** The setting with the smallest |ln ratio_n| is chosen, but only if it at least halves 20,90's |ln ratio_n|.
   Otherwise 20,90 stays and the item stays open.
4. **Box-level veto.** The live setting is switched away from 20,90 only if the winner loses at most 1 OOS-7 site, pooled over 29 sites,
   relative to 20,90 under 2 of 8 at short lead. If the winner's ensemble tier did not finish, the test uses the single cycle, short and long
   lead pooled.
5. **Missing runs.** A Turing run that has not published within about 4 h of this commit is left out, and this file says so.
6. **If a different setting wins,** it becomes the live default in `.github/workflows/forecast.yml` and `proto/turing/run_forecast.slurm`.
   `GATE.md` and `STATUS.md` each get a one-line note.

**B. Boxes (veto, tie-break, robustness), GitHub Actions.** These are the hindcast storms with HRRR archives: sep2023 and aug2021 (dev),
plus the 7 OOS storms of `ENSEMBLE.md` §4. They use the same boxes, members, leads, labels and strict `label_recall`.

- **Set-up.** Exactly the `ENSEMBLE.md` set-up: CN × 0.91, default step, CPU. The 20,90 arm is therefore the published `ensemble/*_nb`
  members. Four 20,90 issue cycles are re-run at today's commit to check that reuse is valid (Jaccard of the flagged sets).
- **Absolute numbers.** They differ from the live CN × 0.88 parity set-up, so only the differences between settings are read.
- **Rules.**
  - Single cycle at short and long lead.
  - 2 of 8 at short lead. The 8 members are those of `ENSEMBLE.md`; they include the long-lead issue cycle.
- **Run tiers**, in priority order (`forecast_nbhd.py matrix`, `.github/workflows/forecast_nbhd.yml`, artifacts only, no commits):
  1. The issue cycles × 3 new settings, plus the 4 re-checks (58 jobs).
  2. The other 6 short-lead members for 10,90 and 20,75 (108 jobs).
  3. The same for raw (54 jobs).

  Whatever has finished when the decision is due is used. A setting whose ensemble is incomplete falls back to the single-cycle test (rule 4).
- **Pooling.** OOS-7 is the decision pool, reported separately from the dev storms. No OOS-7 number for 10,90, 20,75 or raw had been looked
  at before this commit.

**C. Area or intensity? (diagnostic, not part of the decision).**

- **District.** The over-forecast is "mainly area" if 10,90 removes more of 20,90's excess (ln(n₂₀,₉₀ / n)) than 20,75 does. Otherwise it is
  "mainly intensity".
- **Rain.** `forecast_nbhd.py rain` reports HRRR storm totals for each setting against MRMS over the same window. It covers District 3 18z
  and every box issue cycle, on a 0.01° grid. The numbers are the volume ratio, the area ratio above 50 and 100 mm, and the CSI of those
  areas.

## 2. Results (29 Oct 2026, 03:40 UTC)

Files are in `district/`:

- `rain.json`: section C.
- `boxes.json`: the flagged segment ids of the 220 new box runs (artifacts of runs 40788271812, 40788315952 and 40788360475, collected
  through the branch `nbhd-data`).
- `box_scores.json`: section B.
- `district.json` and `decision.json`: section A.

Reproduce with:

```
forecast_nbhd.py boxes --runs docs/proto/forecast/district/boxes.json --out docs/proto/forecast/district/box_scores.json
forecast_nbhd.py district --out docs/proto/forecast/district/district.json
forecast_nbhd.py decide --district docs/proto/forecast/district/district.json --boxes docs/proto/forecast/district/box_scores.json
```

### A. District 3: the Turing runs did not arrive

None of `hindcast_d3_18z_nb10p90`, `_nb20p75` or `_raw` was published within 4 h of the pre-registration. The repo was polled every 15 min
from 23:36 to 03:36 UTC. By rule 5 they are left out.

The only district run is 20,90: 888 segments and 615 km, against the radar's 276 and 197 km. That is ratio_n 3.22 and ratio_km 3.12. It has
no `segments.geojson`, so its CSI is not available. The radar run scores 29 of 80 sites at the rule (lift 35).

**Decision under the pre-registered rule: keep `LF_HRRR_NBHD=20,90` live.** The rule found no eligible setting (rule 3).

This verdict does not depend on the missing runs. The box veto (rule 4) already rejects every alternative (table B): it allows the loss of at
most 1 OOS-7 site, and 10,90 loses 2 while 20,75 and raw lose 3. So when the Turing runs land, they can no longer change the live default.
They are still worth scoring (`district`) for the diagnosis in section C.

### B. Boxes: less spreading loses sites out of sample

The 4 re-runs of 20,90 at today's commit reproduce the published members: Jaccard 0.97 to 1.00. Reusing those members is therefore valid.
Each cell gives OOS-7 sites hit out of 29, then mean / max flagged share, then lift:

| setting | single cycle, short lead | single cycle, long lead | **2 of 8, short lead** | dev (sep2023 + aug2021, 90 sites), 2 of 8 short |
| --- | --- | --- | --- | --- |
| 20,90 (live) | 2, 1.1 / 4.7 %, 2.7 | 6, 1.8 / 4.7 %, 5.3 | **8, 2.3 / 6.1 %, 5.7** | 26, 2.3 %, 11.3 |
| 10,90 | 2, 0.9 / 4.0 %, 3.3 | 6, 1.7 / 3.7 %, 5.9 | 6, 1.9 / 5.1 %, 5.0 | 27, 2.3 %, 10.0 |
| 20,75 | 2, 0.8 / 3.7 %, 3.8 | 6, 1.3 / 3.7 %, 7.2 | 5, 1.3 / 4.7 %, 5.8 | 10, 0.5 %, 30.3 |
| 0,50 (raw) | 2, 0.6 / 2.7 %, 4.8 | 6, 1.0 / 2.5 %, 9.6 | 5, 1.0 / 3.7 %, 7.4 | 4, 0.3 %, 11.5 |

**The single cycle.** Every setting finds the same sites. Less spreading only cuts the flagged share, so the lift rises.

**2 of 8 at short lead, where the live rule works.** 20,90 keeps the most sites. The 3 sites it alone keeps are:

- sep2021: 3 of 5 sites against 2 of 5;
- aug2023: 1 of 4 against 0;
- aug2026: 1 of 4 against 0, lost by 20,75 and raw only.

These are 29 sites in all, so the differences are 2 to 3 sites.

**Dev storms.** 20,75 and raw fall apart: Leominster 0.08 / 0.05 against 0.24 to 0.27, and Worcester 0.33 / 0.00 against 0.58. 10,90 is
close to 20,90.

**How much less does each setting flag?** On the boxes, 10,90 cuts the flagged share by 15 to 20 % and 20,75 / raw by 40 to 55 %. None of
them comes close to a factor of 3 on the boxes.

### C. Why the district over-forecasts: intensity of the 90th percentile, not radius

District 3, 18z cycle, storm-total rain over 48 h. The volume ratio and the area ratios compare HRRR with MRMS over the same window:

| rain field | district mean (mm) | max (mm) | volume / MRMS | area ≥ 50 mm / MRMS | area ≥ 100 mm / MRMS | CSI of the ≥ 50 mm area | peak hour (mm) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MRMS (radar) | 49.9 | 211 | 1 | 1 (34 % of D3) | 1 (8.8 %) | - | 100 |
| 20,90 (live) | 95.2 | 158 | **1.91** | 2.41 | **5.92** | 0.39 | 48 |
| 10,90 | 88.1 | 206 | 1.77 | 2.12 | 5.05 | 0.34 | 65 |
| 20,75 | 39.1 | 78 | 0.78 | 0.95 | 0.00 | 0.43 | 28 |
| raw | 35.1 | 134 | 0.70 | 0.76 | 0.19 | 0.20 | 77 |

- **The live spreading nearly doubles the district's rain volume and gives 6 times the radar's area above 100 mm.** The CN losses and the
  0.30 m closure depth are thresholds, so this turns into about 3 times the flagged roads.
- **Halving the radius (10,90) removes only about a tenth of that excess** (volume 1.91 → 1.77). Dropping the percentile to the 75th removes
  all of it (0.78). The over-forecast is therefore **mainly intensity, i.e. the 90th percentile, not the spreading area.** A 90th percentile
  over a 20 km disk raises every cell near a convective core to near-core totals. Across a 78 × 90 km district, that amounts to a large
  rain surplus.
- **The same holds on the boxes, to a smaller degree.** At short lead, 20,90 is 1.25 to 1.56 times the MRMS volume on sep2023, aug2021,
  sep2021, sep2022 and aug2026, and 0.65 to 0.94 on the others. 20,75 and raw are 0.36 to 0.85 on all of them except sep2021.

  A 20 x 20 km box sits on the storm core, where the radar total is high. There, the 20,90 surplus is what makes up for a displaced or
  too-weak core. That is why the boxes looked fine.

  Spread over a district, most cells are away from the core, and the surplus becomes a false alarm. The raw HRRR is too dry everywhere
  (district volume 0.70; box volume 0.19 to 0.62 except sep2021).

### Verdict and next step

**Keep 20,90 live on the boxes.** The 2-of-8 rule at 20,90 is the best box forecast out of sample. No setting with less spreading or a lower
percentile passes the pre-registered box test.

**Fix the district map separately.** The district over-forecast is a volume bias of the 90th percentile over large domains, so it cannot be
fixed with the same knob without hurting the boxes. Candidates for a new pre-registration:

- (a) **2 of 8 on the D3 GPU run.** This needs 8 Turing member runs: about 4 GPU-hours.
- (b) **A volume-preserving neighbourhood.** Rescale each hour's 20,90 field to the raw HRRR domain volume. This keeps the placement spread
  and drops the surplus.
- (c) **Use the D3 run only as a "watch" layer**, and show the district map with the k-of-n agreement only.

Until one of these is tested, the D3 forecast map should not be shown as a warning map.
