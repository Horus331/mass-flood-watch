# Leominster parametric study, clean rerun on the deployed model: pre-registration (24 Nov 2026)

Brief: Project doc `claude/model_colab/2026-11-24_Prompt_Parametric_Study_Clean_Rerun.md` (Mo approved 24 Nov, 11:55). Advisor request
(3 Nov, Prof. Tao): show the impact of culvert clogging, soil saturation and frozen ground on Leominster, framed as inspection priorities.
Committed before any run; results go to `PARAMETRIC_CLEAN.md` and `parametric_clean.json` whatever they are. The 15/16 Nov studies
(`PARAMETRIC.md`, `PARAMETRIC_T2.md`) are kept; this set replaces them for presentation only, because they mixed the pre-T2 terrain and
the depth series from before the 17 Nov start-up fix.

**What this is.** A sensitivity study on the calibration storm (in-sample by design). No scenario becomes a default; the live forecast,
the map and the site are not changed. Free GitHub runners only.

## Base = the deployed physics and closure rule
Workflow `parity_test.yml`, dest `docs/proto/phase1/parametric_clean`, storm `sep2023`, catalogue box `162000,908000,182000,928000`,
36 h, 20 m, MRMS rain. Every run carries the live forecast's model settings (`.github/workflows/forecast.yml`):
`LF_PARITY=1 LF_LOSS=cn LF_CN_AMC=II LF_CN_SCALE=0.88 LF_INFIL_MMH=2 LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1 LF_QOUT=1 LF_VOUT=1 LF_SAVEINT=300`
and the live closure rule `PROTO_RES_CONSISTENT=1 PROTO_RC_START_H=rain`, plus `PROTO_CASCADE=1` (access readout) and `PM_KEEP_Z=1` (ground
grids for the crest readout; no effect on the model). Not carried: `LF_PHASE=1` (rain/snow split from HRRR temperature; inactive for an
MRMS replay of a September storm), the forecast's HRRR, nowcast and spin-up settings (forecast-only).

## Scenarios (one change from the base each, plus one combination)
| id | scenario | added setting | source |
|---|---|---|---|
| `B` | base | none | deployed |
| `C20`, `C50`, `C100` | every culvert in the box blocked 20 / 50 / 100 % (bridges stay open) | `LF_XINGS_PARTIAL=0.2 / 0.5 / 1.0` | ARR 2016 Book 6 Ch 6 (Weeks et al. 2013) |
| `CS` | smallest-capacity third of NAACC-sized culverts blocked 100 % | `LF_XINGS_PARTIAL=1.0 LF_XINGS_SET=small` | ARR 2016 (opening vs debris length) |
| `ARC1`, `ARC3` | dry / wet antecedent soil | `LF_CN_AMC=I` / `III` (NEH 630 Ch 10 Table 10-1 via the Chow et al. 1988 conversion already in `w9_lisflood.py`; the 0.88 calibration factor stays) | NRCS NEH 630 Ch 10 (2004) |
| `FZ` | frozen ground | `LF_CN_FROZEN=knisel LF_INFIL_MMH=0` (CN → 95 if ≤ 80 else 98; no soak-in) | Knisel 1985 (CREAMS); SWAT theory |
| `C50W` | 50 % blockage + wet soil | `LF_XINGS_PARTIAL=0.5 LF_CN_AMC=III` | summer 2023 very wet before the storm |

A technical failure is rerun unchanged; no run is dropped after a result is seen.

## Readouts (`proto/parametric_clean_eval.py` → `parametric_clean.json` + `.csv`)
1. Road segments closed at the peak (half-hourly series) and at any time (deployed rule, `p_close ≥ 0.5`); closed length (km) for both.
2. Emergency access lost at the peak with **hospital 30 / fire 8 / police 4 min** (TAB_BOARD thresholds; recomputed from each run's
   `segments.geojson` with `proto/cascade.py`; report-only), the share of those residents on roads that stay dry, the network delay at
   the peak and over the storm (vehicle-hours; Ganin et al. 2017 reading). Change from `B` for each.
3. Crossings, **crest-relative readout** (`whatif_v3` constants, as `PARAMETRIC_T2.md`): segments within 60 m of a crossing with water
   ≥ 0.30 m over the road crest; crossings overtopped; median pool rise. The deployed closure count near crossings is not used for blockage.
4. **Culvert inspection list:** top 10 crossings by water-level rise over the road crest under `C100`, and under `CS`, against `B`,
   joined with NAACC condition, street and town; marked if also in the top 10 under `C50W`.
5. Internal check (records only): storm reports (of 89) and Leominster DPW points (of 54) caught per scenario, as `PARAMETRIC.md`.

## Reading rules (fixed now)
- A condition "matters for roads" if closed length at any time changes by ≥ 10 % from `B`; "matters for access" if residents losing
  access at the peak change by ≥ 10 %. Smaller changes are reported as "little effect".
- **Robust** (for the advisors) = the direction is the same under both readouts that apply (peak and any-time closures for soil/frozen;
  crest readout and any-time closures for blockage), and not driven by fewer than 3 segments. Findings that fail this are reported in
  the results file but marked not robust.
- The inspection list is robust if ≥ 6 of its top 10 under `C100` are also in the top 10 under `CS` or `C50W`, or in the 16 Nov T2 list.
- Nothing is tuned; no scenario is compared with damage to choose a setting.
