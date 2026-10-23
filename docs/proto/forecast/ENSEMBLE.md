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
`ensemble.json` (made with `python proto/forecast_ens.py report`), `qmap.json`. **The live forecast is unchanged.**

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

## Verdict and what would go live

- **Best option:** the time-lagged ensemble of separate flood runs. In its cheap form it uses the 4 synoptic cycles the live forecast already
  makes, with P(close) = share of the last 4 cycles that close the segment.
  - At 9 to 10 h lead it beats the current setup on both storms: recall 0.077 to 0.321 for Sept and 0 to 0.583 for Aug.
  - At 3 to 4 h lead it is neutral: recall unchanged on both, flagged share +0 / +0.6 points for "any of 4", or -0.2 points for Aug at
    ">= 2 of 4".
- **Not switched on.** `forecast.yml` and the live defaults are unchanged, for three reasons:
  1. The gain rests on single older members on just 2 storms.
  2. The threshold (any of 4 vs >= 2 of 4) was chosen after seeing these results, and the two storms prefer different ones.
  3. Doing it live needs each cycle's per-segment P kept and merged across cycles whose boxes may sit in different places. That changes how
     the forecast status is written, which belongs to the site, so it is not a one-flag change.
- **Recommended next step:** keep the per-segment P of every live cycle (a seg.json like the ones here) and publish "closed in k of the last 4
  cycles" next to the current run. Before quoting general numbers, score the 4-cycle ensemble on Jul 2021, Sep 2021, Jul 2023, Aug 2023b and
  Aug 2026 with `forecast_ens.yml`. Each storm costs 4 to 8 member jobs of about 25 min.
- **Cheaper single-run alternative**, if per-cycle state is not kept: the lagged p90 rain field (`LF_HRRR_LAG=6,12,18 LF_HRRR_LAG_STAT=p90`
  for synoptic only; it was tested here with 8 members). It gave 0.27 / 0.50 at 9 to 10 h lead for 3 to 4 % flagged, but cost some lift at
  short lead and gives no probability.
- **Dropped:** quantile mapping, and the lagged mean / max rain fields.

## Runs

All runs are in `docs/proto/forecast/ensemble/` (summary, points, score, seg.json, w9_log):

- members: `<storm>_m<DDHH>z_nb`
- lagged fields: `<storm>[_<cycle>]_lag8_<stat>_nb`, where no cycle means the long-lead cycle
- quantile mapping: `<storm>_<cycle>_<raw|nb>_qm<raw|nb>`

Workflow inputs: `what=runs` with `cases` JSON, or empty for the default members, and `what=qmfit`.
