# Longer lead and honest uncertainty: time-lagged HRRR ensembles and rain bias correction

**Question:** can the road-closure forecast be useful 9 to 10 h before a convective storm, not only 3 to 4 h before (`HINDCAST.md`)? And can
it say how sure it is?

**Set-up.** Same as `HINDCAST.md`: same 20 x 20 km boxes, 20 m LISFLOOD-FP on CPU (`LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2 LF_QOUT=1`),
`proto/prototype.py`, the same labels and the same scores (strict label recall at P >= 0.5, flagged share, chance-corrected lift, loose
recall). Every HRRR run uses the live neighbourhood setting `LF_HRRR_NBHD=20,90` unless the table says otherwise. Runs end when the MRMS
control ends. Each run stores P_depth for every segment in the box (`ensemble/<run>/seg.json`). This lets an ensemble be scored with exactly the
same `label_recall` as a single run (`proto/forecast_ens.py`).

Code: `proto/forecast_ens.py` (members, scoring, QM fit), `sim/colab/hrrr_ens.py` (lagged rain field and QM, used only when the env flags
`LF_HRRR_LAG` / `LF_HRRR_QMAP` are set; a 2-line hook in `hrrr_rain.hourly`), `.github/workflows/forecast_ens.yml`. Numbers:
`ensemble.json` (made with `python proto/forecast_ens.py report`), `qmap.json`. **The live forecast now runs the 8-member ensemble with the 2-of-8 rule (section "What is live"); `FORECAST_ENSEMBLE=0` falls back to the single cycle.**

Reference rows (from `HINDCAST.md`):

| | Sept 2023 Leominster | Aug 2021 Worcester |
| --- | --- | --- |
| MRMS radar, CPU control | 0.359 at 2.2 %, lift 11.1 | 0.333 at 1.5 %, lift 19.8 |
| live setting, long lead (Sept 12z = 9.2 h / Aug 06z = 9.6 h before the first report) | 0.077 at 0.3 %, lift 15.8 | 0.0 at 0.1 % |
| live setting, short lead (Sept 18z = 3.2 h / Aug 12z = 3.6 h) | 0.269 at 2.0 %, lift 9.2 | 0.583 at 2.4 %, lift 21.4 |

## 1. Time-lagged ensemble: one flood run per HRRR cycle, P(close) = share of members

A cycle's members are the 8 HRRR cycles that were on the web at its issue time and still cover the storm. These are 4 to 5 hourly cycles (18 h
horizon) back to the last one that reaches the end of the main rain, plus the 6-hourly 48 h cycles back 18 h. For example, for Sept 2023 12z
the members are 12, 11, 10, 09 and 08z plus 06z, 00z and Sept 10 18z. Each member is its own flood run (25 to 35 min of CPU, one matrix job).
A segment's ensemble probability is the share of members that close it (P_depth >= 0.5). "Synoptic" uses only the four 00/06/12/18z cycles,
which the live forecast already runs every 6 h.

Strict label recall, share of segments flagged and lift at each ensemble threshold:

| issue cycle (lead) | members | P_ens >= 1/N | >= 2/N | >= 3/N | >= 4/N |
| --- | --- | --- | --- | --- | --- |
| Sept 2023 12z (9.2 h) | 8 | **0.321** at 3.5 %, lift 6.3 | 0.141 at 1.4 %, 7.2 | 0.128 at 0.7 %, 12.5 | 0.077 at 0.4 %, 13.4 |
| Sept 2023 12z (9.2 h) | synoptic 4 | **0.321** at 3.5 %, 6.3 | 0.128 at 0.8 %, 10.4 | 0.077 at 0.3 %, 16.8 | 0 |
| Aug 2021 06z (9.6 h) | 8 | 0.583 at 4.6 %, 11.0 | **0.583 at 2.4 %, 20.8** | 0.333 at 0.7 %, 39.2 | 0 |
| Aug 2021 06z (9.6 h) | synoptic 4 | 0.583 at 4.6 %, 11.0 | **0.583 at 2.4 %, 20.8** | 0 | 0 |
| Sept 2023 18z (3.2 h) | 8 | 0.269 at 2.1 %, 8.8 | 0.244 at 1.7 %, 10.2 | 0.128 at 0.9 %, 10.2 | 0.128 at 0.5 %, 16.6 |
| Sept 2023 18z (3.2 h) | synoptic 4 | 0.269 at 2.0 %, 9.2 | 0.128 at 0.8 %, 10.4 | 0.077 at 0.3 %, 16.8 | 0 |
| Aug 2021 12z (3.6 h) | 8 | 0.583 at 3.9 %, 12.8 | 0.583 at 3.0 %, 16.7 | **0.583 at 2.2 %, 22.7** | 0 |
| Aug 2021 12z (3.6 h) | synoptic 4 | 0.583 at 3.0 %, 16.5 | **0.583 at 2.2 %, 22.7** | 0 | 0 |

Single members (strict recall / flagged share), so the spread is visible:

- **Sept 2023, at the 12z issue:**
  - 12z 0.077 / 0.3 %
  - 11z 0.077 / 0.4 %
  - 10z 0 / 0.2 %
  - 09z 0.141 / 1.0 %
  - 08z 0 / 0.0 %
  - 06z 0.128 / 0.8 %
  - 00z 0 / 0.1 %
  - Sept 10 18z (27 h lead) **0.321 / 3.6 %**
- **Aug 2021, at the 06z issue:**
  - 06z, 05z, 04z and 03z: 0 / 0.1 to 0.2 %
  - 02z 0.333 / 0.7 %
  - 00z 0 / 0.1 %
  - Aug 18 18z **0.583 / 2.9 %**
  - Aug 18 12z 0.583 / 4.1 %

What this shows:

1. **The lagged ensemble does extend the lead time on both storms.** At 9 to 10 h it recovers 0.32 (Sept) and 0.58 (Aug) of the labelled
   sites. The single newest cycle recovers 0.08 and 0. On Aug 2021 at 06z (>= 2 of 8, 2.4 % flagged, lift 21), the ensemble is as good as
   the deterministic run 6 h later and better than the radar control. On Sept 2023 it reaches 0.32 only at the "any member" threshold (3.5 %
   flagged, lift 6.3), which is about the radar control's recall at 1.6 times its flagged share.
2. **At short lead it costs little.** Sept 18z: 0.269 at 2.0 to 2.1 % (any member), the same as the single run. Aug 12z: 0.583 at
   2.2 % (>= 3 of 8 or >= 2 of 4), the same recall at a slightly smaller flagged share than the single run (2.4 %).
3. **The skill comes from whichever member happened to place the storm right, and that is often an older cycle.** Sept 10 18z (27 h before)
   and Aug 18 18z / 12z (22 to 28 h before) were the best members. The newer cycles moved the core away. That is why the probabilities are
   low: the labelled sites sit at P_ens = 1/8 to 5/8, never above 5/8. This is the honest statement. "1 to 3 of the last 8 forecasts
   flood this road" is a real 10 to 40 % signal, not a near-certain closure.
4. **The synoptic 4-member version (the cycles the live forecast already runs) carries almost all of it.** Any of 4: Sept 12z 0.321 at 3.5 %, Aug
   06z 0.583 at 4.6 %, Sept 18z 0.269 at 2.0 %, Aug 12z 0.583 at 3.0 %. >= 2 of 4 is sharper on Aug (2.2 to 2.4 %, lift 21 to 23) but drops Sept
   18z to 0.128. The hourly cycles mostly add noise, except Sept 09z and Aug 02z.

## 1b. Time-lagged rain field: one flood run on the combined rain of the 8 members

`LF_HRRR_LAG=1,2,3,4,6,12,18 LF_HRRR_LAG_STAT=<stat>` combines the same 8 cycles hour by hour and cell by cell, after the 20 km / 90th
neighbourhood, and runs the flood model once. That costs 8 times the rain download and 1 times the flood compute.

| stat | Sept 12z (9.2 h) | Aug 06z (9.6 h) | Sept 18z (3.2 h) | Aug 12z (3.6 h) |
| --- | --- | --- | --- | --- |
| mean | 0.077 at 0.3 %, lift 16.8 | 0.083 at 0.3 %, 26.0 | - | - |
| p75 | 0.128 at 0.7 %, 12.1 | 0.25 at 0.7 %, 32.0 | 0.077 at 0.4 %, 11.7 | 0.50 at 1.7 %, 25.5 |
| **p90** | **0.269 at 3.0 %, 6.1** | **0.50 at 3.7 %, 11.7** | 0.244 at 1.9 %, 8.8 | 0.583 at 3.4 %, 14.8 |
| max | 0.346 at 4.6 %, 5.2 | 0.583 at 6.5 %, 7.8 | 0.346 at 4.1 %, 5.9 | 0.583 at 5.8 %, 8.7 |

The mean smears displaced convective peaks. The peak hour drops to 10 to 12 mm, so the threshold-driven road model sees almost nothing. The
p90 field is a cheap approximation of the per-member ensemble at long lead: about 85 % of its recall, at a similar flagged share. At short lead
it is slightly worse than the single run (Sept 0.244 vs 0.269; Aug lift 14.8 vs 21.4). The max over-floods, like the 30 km maximum in
`HINDCAST.md`, with lift 5 to 9 and a large gauge rise error. The lagged field also loses the probability: it gives one closure set and no spread.

## 2. Quantile mapping of hourly HRRR rain to MRMS (leave one storm out)

`proto/forecast_ens.py qmfit` builds histograms of hourly accumulations at 1 km points over each AWS catalogue storm. Each storm contributes
its box plus a 20 km margin, over the catalogue MRMS window. The sources are MRMS Pass2 and the three HRRR cycles before the first report,
with leads of 3 to 20 h. Both raw HRRR and 20 km / 90th-neighbourhood HRRR are included, for 9 storms in all. The quantile map HRRR -> MRMS
for a storm is fitted on the other 8, each storm weighted equally (`qmap.json`, keys `loso_<storm>/raw|nb20p90`). The map is applied to every
sampled hourly field (`LF_HRRR_QMAP=qmap.json#key`).

- **Raw map:** HRRR is about right up to 10 mm/h and too weak above. Leaving out Sept 2023, it maps 20 to 24 mm, 30 to 39 mm and 50 to 70 mm.
- **Neighbourhood map:** it reduces the rain, because the 90th percentile already inflates it. 20 becomes 12.5 mm and 30 becomes 25 mm.

| | Sept 12z | Aug 06z | Sept 18z | Aug 12z |
| --- | --- | --- | --- | --- |
| raw + raw map | 0 at 0.1 % (raw: 0) | 0 at 0.1 % (raw: 0) | 0.051 at 0.4 % (raw: 0.051) | 0.25 at 0.9 % (raw: 0.167) |
| neighbourhood + raw map | 0.077 at 0.4 %, 12.8 (live: 0.077 at 0.3 %) | 0 at 0.1 % (live: 0) | 0.269 at 2.9 %, 6.5 (live: 0.269 at 2.0 %) | 0.583 at 3.2 %, 15.6 (live: 0.583 at 2.4 %) |
| neighbourhood + neighbourhood map | 0 | 0 | 0.09 at 0.6 % | 0.083 at 0.5 % |

**The bias correction does not help.** The long-lead failure is placement and timing, not intensity: Sept 12z put about 100 mm 10 to 15 km
west, and Aug 06z had the rain somewhere else. A distribution map cannot move rain. At short lead the raw map adds flagged segments without
adding recall, so the lift falls from 9.2 to 6.5 (Sept) and from 21 to 16 (Aug). The neighbourhood-fitted map removes the useful
over-forecast and loses the skill.

## 3. HREF / HRRR ensemble

Not used. The probe (`ensemble/href_probe.txt`, run from Actions) found no HREF, HRRRE or HRRR-ensemble bucket on AWS. `noaa-href-pds`,
`noaa-hrefv3-pds`, `noaa-nws-href-pds`, `noaa-hrrre-pds` and `noaa-hrrr-ensemble-pds` all return NoSuchBucket. `noaa-rrfs-pds` has only
retrospective / sample folders. HREF exists only on NOMADS (`href/prod`), as a rolling window of about 2 days, so 2021 / 2023 hindcasts
cannot be made. The NOMADS listing returned nothing to the runner. A live HREF member set would have to be validated going forward.

## 4. Out-of-sample test on 7 more storms, with the rules fixed in advance

Sections 1 to 3 used only Sept 2023 and Aug 2021, and the thresholds were picked after seeing them. This section tests the ensemble honestly
on the other 7 AWS-era catalogue storms (`docs/proto/obs/catalog.json`). Everything below was fixed before any of these runs:

- **Box:** the catalogue box (20 x 20 km, 20 m), with the same model and scoring as above.
- **Lead:**
  - long lead = the newest 00/06/12/18z cycle issued at least 8 h before the first report (8 to 14 h);
  - short lead = the next synoptic cycle, 6 h later (2 to 8 h).
- **Members:** the issue cycle, the 3 synoptic cycles before it (-6, -12, -18 h) and the 4 hourly cycles before it (-1 to -4 h).
- **Rules:** a segment counts as closed by a rule when, at P_depth >= 0.5:
  - **single cycle** = the issue cycle alone (today's live setup);
  - **any of 4** = at least 1 of the 4 synoptic cycles closes it;
  - **2 of 4** = at least 2 of the 4 synoptic cycles;
  - **2 of 8** = at least 2 of all 8 members.

The run took 98 matrix jobs: 91 members plus 7 MRMS controls (`proto/forecast_ens.py matrix --which all`). Numbers: `ensemble.json`
(`ensembles.<storm>_<lead>.rules`, `pooled`).

Strict label recall / share of segments flagged:

| storm (sites) | lead | single cycle (today) | any of 4 | 2 of 4 | 2 of 8 | MRMS control |
| --- | --- | --- | --- | --- | --- | --- |
| jul2021 (5) | 09 06z, 9.8 h | 0.6 / 2.7 % | 0.8 / 5.6 % | 0.6 / 3.0 % | 0.6 / 3.4 % | 0.0 / 0.3 % |
|  (5) | 09 12z, 3.8 h | 0.0 / 0.3 % | 0.6 / 3.0 % | 0.6 / 2.7 % | 0.6 / 3.2 % |  |
| sep2021 (5) | 01 18z, 11.9 h | 0.4 / 4.7 % | 0.6 / 6.7 % | 0.4 / 5.4 % | 0.6 / 5.6 % | 0.6 / 3.7 % |
|  (5) | 02 00z, 5.9 h | 0.4 / 4.7 % | 0.6 / 6.7 % | 0.4 / 5.6 % | 0.6 / 6.1 % |  |
| sep2022 (4) | 05 00z, 13.9 h | 0.0 / 0.2 % | 0.0 / 2.7 % | 0.0 / 0.2 % | 0.0 / 0.4 % | 0.0 / 0.8 % |
|  (4) | 05 06z, 7.9 h | 0.0 / 0.3 % | 0.0 / 2.7 % | 0.0 / 0.3 % | 0.0 / 0.3 % |  |
| jul2023 (5) | 14 06z, 9.5 h | 0.0 / 0.1 % | 0.2 / 5.9 % | 0.0 / 1.6 % | 0.4 / 5.7 % | 0.0 / 0.1 % |
|  (5) | 14 12z, 3.5 h | 0.0 / 0.1 % | 0.0 / 1.6 % | 0.0 / 0.1 % | 0.0 / 0.1 % |  |
| aug2023 (4) | 08 06z, 8.1 h | 0.0 / 1.3 % | 0.25 / 3.6 % | 0.0 / 2.8 % | 0.25 / 3.3 % | 0.25 / 1.9 % |
|  (4) | 08 12z, 2.1 h | 0.0 / 1.3 % | 0.25 / 3.6 % | 0.0 / 2.8 % | 0.25 / 3.4 % |  |
| aug2023b (2) | 18 00z, 12.6 h | 0.0 / 0.1 % | 0.0 / 0.9 % | 0.0 / 0.5 % | 0.0 / 0.7 % | 0.0 / 0.1 % |
|  (2) | 18 06z, 6.6 h | 0.0 / 0.1 % | 0.0 / 0.8 % | 0.0 / 0.2 % | 0.0 / 0.7 % |  |
| aug2026 (4) | 03 00z, 11.8 h | 0.25 / 3.7 % | 0.25 / 3.8 % | 0.25 / 2.7 % | 0.25 / 2.7 % | 0.25 / 1.6 % |
|  (4) | 03 06z, 5.8 h | 0.0 / 1.1 % | 0.25 / 3.7 % | 0.25 / 1.7 % | 0.25 / 2.2 % |  |
| sep2023 (78), in-sample | 11 12z, 9.2 h | 0.077 / 0.3 % | 0.321 / 3.5 % | 0.128 / 0.8 % | 0.141 / 1.4 % | |
|  | 11 18z, 3.2 h | 0.269 / 2.0 % | 0.269 / 2.0 % | 0.128 / 0.8 % | 0.244 / 1.7 % | |
| aug2021 (12), in-sample | 19 06z, 9.6 h | 0.0 / 0.1 % | 0.583 / 4.6 % | 0.583 / 2.4 % | 0.583 / 2.4 % | |
|  | 19 12z, 3.6 h | 0.583 / 2.4 % | 0.583 / 3.0 % | 0.583 / 2.2 % | 0.583 / 3.0 % | |

| pooled (site-weighted recall / mean flagged share / max flagged share / lift) | single cycle | any of 4 | 2 of 4 | 2 of 8 |
| --- | --- | --- | --- | --- |
| 7 out-of-sample storms, long lead (29 sites) | 0.207 / 1.8 % / 4.7 % / 5.27 | 0.345 / 4.2 % / 6.7 % / 4.03 | 0.207 / 2.3 % / 5.4 % / 4.24 | 0.345 / 3.1 % / 5.7 % / 5.43 |
| 7 out-of-sample storms, short lead (29 sites) | 0.069 / 1.1 % / 4.7 % / 2.71 | 0.276 / 3.2 % / 6.7 % / 4.21 | 0.207 / 1.9 % / 5.6 % / 4.96 | 0.276 / 2.3 % / 6.1 % / 5.7 |
| all 9 storms, long lead (119 sites) | 0.101 / 1.5 % / 4.7 % / 7.79 | 0.353 / 4.1 % / 6.7 % / 5.92 | 0.193 / 2.2 % / 5.4 % / 8.55 | 0.235 / 2.8 % / 5.7 % / 7.49 |
| all 9 storms, short lead (119 sites) | 0.252 / 1.4 % / 4.7 % / 9.02 | 0.302 / 3.0 % / 6.7 % / 7.85 | 0.193 / 1.8 % / 5.6 % / 9.35 | 0.286 / 2.3 % / 6.1 % / 9.21 |

How to read it:

- The label sets are small, 2 to 5 sites per storm and 29 in all, so one site moves a storm's recall by 0.2 to 0.5.
- The out-of-sample pooled numbers are 6 vs 10 sites (long lead) and 2 vs 8 sites (short lead).
- The MRMS radar control is not better than the forecast rules on these storms: 0 on Jul 2021 and Jul 2023, 0.6 on Sep 2021, 0.25 on Aug 2023
  and Aug 2026. Several of these storms are labelled with approximate locations, and the 20 m model misses them even with observed rain.

**Plain verdict.**

1. **"2 of 8" is the one rule that clearly beats today's single-cycle setup out of sample.**
   - On every one of the 14 storm-lead cases it is at least as good, and better in 7. It never loses a site the single cycle finds.
   - Pooled recall rises from 0.21 to 0.34 at long lead and from 0.07 to 0.28 at short lead.
   - Lift rises from 5.3 to 5.4 and from 2.7 to 5.7.
   - The flagged share stays reasonable: mean 3.1 % / 2.3 % vs 1.8 % / 1.1 %, and at most 6.1 % (Sep 2021, where the single cycle already flags
     4.7 %).
   - The only case where it is slightly worse is the in-sample Sept 2023 18z (0.244 vs 0.269).
   - **Cost:** it needs the 4 hourly cycles before each synoptic cycle, so 5 flood runs per box instead of 1 when the gate fires.
2. **"Any of 4" (the cycles the live forecast already runs) finds as much as "2 of 8", but flags about 2 to 3 times as many segments.**
   - Pooled recall 0.345 / 0.276, mean flagged 4.2 % / 3.2 % (max 6.7 %). Its lift is lower than the single cycle at long lead (4.0 vs 5.3).
   - Read it as a **watch** layer: roads any recent forecast closed. It is not a warning.
3. **"2 of 4" is not better than the single cycle.** It ties at long lead (0.207) and gains at short lead (0.21 vs 0.07). Lift is mixed and Sept
   2023 drops.
4. **At short lead the single newest cycle is weaker out of sample than on the two development storms.** Pooled 0.07, against 0.27 and 0.58 on
   Sept 2023 and Aug 2021. On these storms the ensemble is what makes the 3 to 8 h forecast useful at all.

## What is live

**The forecast is the 8-member time-lagged ensemble, with the 2-of-8 rule validated above** (`.github/workflows/forecast.yml`,
`proto/forecast_kofn.py`).

1. **Gate.** The gate reads the newest 00/06/12/18z cycle T, exactly as before (`GATE.md`).
   - If the gate is quiet, there is one cheap job and the quiet card. Nothing else runs.
2. **Members and boxes.** If the gate fires, `forecast_kofn.py members` builds the 8 members: T, T-6, T-12 and T-18 h (48 h cycles) and
   T-1 to T-4 h (18 h hourly cycles).
   - The boxes are T's boxes first. Then come the boxes each older member's own gate places on its rain after T.
   - A box that overlaps a box already chosen by more than 25 % is dropped (deduplication). At most `FORECAST_MAX_BOXES`, default 4.
   - Every member runs on every box as one matrix job: up to 32 jobs, at most 20 at a time on the free runners, about 25 to 40 min each.
     The flood settings are unchanged (20 m, `LF_HRRR_NBHD=20,90`, CN losses).
3. **Ensemble.** `forecast_kofn.py ensemble` computes, per segment:
   - k = how many members close it (P(close) >= 0.5 in a run whose box holds it);
   - n = how many members finished a run that covers it.
   - **Likely closed = k >= 2 of 8. Possible = k = 1.** A failed member is left out of n; the rule stays "2 or more".
4. **Published** in `forecast_status.json`:
   - top level: `likely_closed` (k >= 2), `possible`, `ensemble` (members, rule) and `k_of_n` (members, which finished per box, counts
     k>=1..8, top 200 segments with k, n and the members that close them). The headline counts likely and possible segments.
   - `runs[]`: `likely_closed`, `possible`, `likely_closed_single` (the issue cycle alone), `k_of_n` (segment, road, town, k, n), and k on
     each `top` entry.
5. **Viewer pack.** `docs/site/data/forecast_latest[_bN]/` is the replay of the issue cycle's run (or the newest member that finished).
   - `roads.json` features carry `k` / `kn`. Segments that only older members close are added with their geometry.
   - `meta.json` carries `kofn` = {n, finished, likely, possible}.
   - `docs/site/viewer.js` adds, for forecast runs only (`meta.kofn` present):
     - an agreement layer (red = 2 or more of 8, amber = 1 of 8) with a labelled legend item, built in JS;
     - the k in the road popup;
     - the likely / possible counts in the stats line.
   - The replay of past storms is unchanged.
6. **Fallback to the single cycle.** Set the repository variable `FORECAST_ENSEMBLE=0`, or run the workflow with input `ensemble=0`. This
   runs the issue cycle only, with no k-of-n, exactly the previous behaviour.
7. **Tests.** Input `prefix=<name>` (anything other than `forecast_latest`) writes `docs/site/data/<name>[_bN]/` and
   `<name>_status.json` and leaves the live status alone. Input `max_boxes` limits the boxes.

Not used live: quantile mapping and the lagged mean / max rain fields (sections 1b, 2). The cross-cycle `record` / `combine` commands in
`forecast_kofn.py` are kept but are not called.

## Runs

All runs are in `docs/proto/forecast/ensemble/` (summary, points, score, seg.json, w9_log):

- members: `<storm>_m<DDHH>z_nb`
- lagged fields: `<storm>[_<cycle>]_lag8_<stat>_nb`, where no cycle means the long-lead cycle
- quantile mapping: `<storm>_<cycle>_<raw|nb>_qm<raw|nb>`

Workflow inputs: `what=runs` with `cases` JSON, or empty for the default members, and `what=qmfit`.
