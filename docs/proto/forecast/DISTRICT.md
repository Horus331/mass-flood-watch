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

## 2. Results

(pending)
