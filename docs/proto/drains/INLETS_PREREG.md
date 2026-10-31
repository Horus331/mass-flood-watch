# Pre-registration: catch basins as a capped, clogging-aware sink (`LF_INLETS=1`)

**Fixed 31 Oct 2026. This file and all the code it names were committed before any `LF_INLETS` run of any storm.** It follows
`docs/proto/PROTOCOL.md` v2 (held-out 23 decision set, §5a). Nothing below may change after a score has been seen. A change would make this a
new test with a new date. Code: `sim/colab/lf_inlets.py` (the sink), `sim/colab/w9_lisflood.py` (the `LF_INLETS` blocks),
`proto/turing/run_inlets.slurm`, `proto/turing/collect_scores.slurm`, `proto/turing/plans/inlets_v1.json`, `proto/inlets_eval.py` (the scorer
for this test).

## 1. Why this test

The earlier pipe sink (`DRAINS.md`, `LF_DRAINS`) put the full-flow capacity of every Leominster pipe on every cell above it, with inlets that
were 100 % efficient. It cut city flags by about a third, but it removed documented flood sites in proportion. It did not improve the ranking at
an equal flag budget. Its write-up named the next things to test: inlet efficiency and clogging. In a real street, water enters the pipes only at
the inlets. Each inlet takes at most what its grate passes at the ponding depth, minus what leaves and debris block. The pipe network that the
inlet drains into can carry only so much. This test checks whether a sink built that way improves the closure ranking.

## 2. The sink, fixed (`sim/colab/lf_inlets.py`)

| piece | fixed value | source |
|---|---|---|
| inlets | MassDOT Inlet layer, in service (state highways only). Snapshot of 29 Oct 2026, cut to District 3 plus every catalogue box (+2 km): `proto/data/inlets/massdot_inlets.csv.gz` (30,447 rows). `.github/workflows/inlets_table.yml` / `proto/inlets_table.py` | `docs/proto/stormwater/SNAPSHOT.md` |
| | Leominster municipal inlets: the City DPW layer (`proto/data/drains/leominster_drain_pipe.zip`) has pipes only, no structures. Each distinct pipe end node (1 m snap) counts as **0.587 inlet**. 0.587 is the MassDOT District 3 share of inlets among inlets + manholes: 28,936 / (28,936 + 20,331). Nodes within 10 m of a MassDOT inlet are dropped as duplicates. | assumption, from the inventory |
| types | Inventory: 25,488 rows have no type, 4,258 are Catch Basin, 156 Double Catch Basin, 226 Drop Inlet, 63 CBCI, plus a few others. 27,054 covers are "Square Frame & Grate". Every inlet is a **grate in a sag**. Double inlets count as 2. Scuppers (bridge-deck drains), outlet control structures, headwalls and flared ends are not inlets. Statuses "Proposed Installation" and "Retired" are dropped. | `proto/data/inlets/inventory.json` |
| grate | 0.6 m × 0.6 m (the 2 ft square frame and grate), 50 % clear opening. The inventory has no grate-size field. | assumption (MassDOT standard square frame & grate) |
| capacity | HEC-22 3rd ed. (FHWA-NHI-10-009, §4.4.6, inlets in sag), SI. Weir: Q = 1.66 P d^1.5, with P = 2W + L = 1.8 m. Orifice: Q = 0.67 A_g (2 g d)^0.5. The smaller of the two is used. (Curb opening, used for no inventory type: Q = 1.60 L d^1.5, L = 1.5 m.) | FHWA HEC-22 |
| design depth | **d = 0.15 m**, the 6 in curb reveal. Above it water spills out of the gutter; HEC-22 sag design limits ponding to about curb height. The sink is a fixed rate per cell, so capacity is taken at one depth. At 0.15 m the weir governs: **0.174 m³/s per grate**. | HEC-22; LISFLOOD-FP infilfile (§3) |
| clogging | Q_cap = Q × (1 − clog). **clog = 0.50**: the HEC-22 sag-grate design assumption. **Leaf-fall season** (storm start 15 Oct – 30 Nov): **clog = 0.65**. That is 35 % of the unobstructed conveyance under heavy leaf litter, from full-scale tests by Poirier, Rahman & van Duin, *World Environmental and Water Resources Congress 2025*, ASCE, pp. 1190–1200. The one-year Barcelona inspection (Gómez et al., cited by Hao, Mu & Shi 2021, *Water* 13(6) 826) found 26.5–67.4 % capacity loss. **No catalogue storm falls in the leaf window (all are May–Sep), so the seasonal value is not tested here.** | literature, fixed in advance |
| network limit | Pipes with a known size: Leominster DPW (8,683 of 11,484 in the sep2023 box), and MassDOT Conveyance (`proto/data/inlets/massdot_conveyance.csv.gz`; only 4 of 6,940 have a size, so in practice none). These are joined into networks by shared ends (`lf_drains.networks`). Pipes of 48 in and larger are left to the surface model, as in DRAINS, and so are MassDOT culverts. An inlet within 15 m of a pipe belongs to that pipe's network. A network's summed (clogged) inlet capacity is scaled down to the full-flow Manning capacity of its largest known-size pipe (`lf_drains.full_flow_q`; slope from inverts, else ground, floored at 0.005). Everywhere else the per-inlet cap is the only cap. | task spec; HEC-22 / ASCE MOP 77 (Manning) |
| cells | Inlets add up in their 20 m cell. Water and channel cells get no sink. The rate is in mm/h. | |
| outfalls | Drained water leaves the model. It is not put back at the outfalls, as in DRAINS. | known limitation |

## 3. How it enters LISFLOOD-FP

The sink goes through the same mechanism as `LF_DRAINS`. LISFLOOD-FP 8.2's `infilfile` (an ESRI ascii grid in mm/h) is applied per cell on wet
cells by the `mfw-drains` patch to `infevap.cpp` FPInfiltration. The rate is removed only where there is water, and never below zero. At the
start of every run, w9 runs `probe_sink`, and the run stops if the volume ratio is not 1 ± 0.05. Tested here on a local CPU build of the 8.2
source: volume ratio 1.00. The sink is run-tested on the CPU solver only, so **both arms run on the CPU**. `LF_INLETS` without `=1` leaves
w9 byte-identical: the blocks are inert, `--selftest` passes, and the meta gets an `inlets` key only when the sink is on.

## 4. Arms, storms, settings

- **Arms.** `base` (no sink) vs `inlets` (`LF_INLETS=1`, all defaults above). Both run in the same Turing batch, at one pinned commit, on the
  same CPU build of LISFLOOD-FP 8.2 (`proto/turing/run_inlets.slurm`, `PIN` = the commit that adds this file).
- **Baseline.** Under PROTOCOL §3, a candidate is compared with a baseline on the same commit and solver. The baseline is therefore the `base`
  arm of this batch, not the published Actions catalogue. As a sanity check, the base arm's rule share and 3 % hits are reported next to
  `docs/proto/parity/catalog`. That check changes nothing.
- **Settings** (parity baseline, `parity/BASELINE.md`): `LF_PARITY=1 LF_LOSS=cn LF_CN_SCALE=0.88 LF_INFIL_MMH=2 LF_QOUT=1 LF_VOUT=1`, 20 m. Each
  storm uses its catalogue box and hours (`docs/proto/parity/catalog/<storm>_<area>_20m/config.json`). Plan: `proto/turing/plans/inlets_v1.json`,
  50 runs.
- **Storms.**
  - **sep2023** (Leominster, catalogue box, 36 h): the calibration storm, **reported only**. Its "towns" domain is Leominster city
    (`score_v2.DOMAIN_OVERRIDE`), which gives the DRAINS-comparable city numbers.
  - **Held-out 23** (OOS-7 + NEW16): the **decision set**.
  - aug2021 is not run. The locked storms are not run.
- **Secondary, not a decision: clog sensitivity.** `LF_INLETS_CLOG=0` (clean grates) and `LF_INLETS_CLOG=0.65` (leaf-season value), on
  **sep2023 only**. They are never scored on the held-out 23, so the decision has **k = 1**.

## 5. Metrics and pass rule

Everything comes from `proto/score_v2.py`, through `proto/inlets_eval.py`, which builds `BASE.json` / `CAND.json` from the per-run `score_v2.json`
and calls `score_v2.compare`.

- **Decision: PROTOCOL v2 §5a (ranking route), held-out 23, box-wide, k = 1, 2000 bootstrap replicates.** All five must hold:
  1. pooled site recall at 3 % flagged gains **≥ +0.04**;
  2. the one-sided 5 % lower bound of the gain is **> 0**;
  3. FSS at 300 m at 3 % **does not drop**;
  4. no held-out storm with ≥ 3 sites loses **> 1 site** at 3 %;
  5. the pooled rule lift (`p_close ≥ 0.5`) is **≥ 0.8 ×** the base's.

  §5b (alert-tier route) is not used. The sink changes the depth field, and so the ranking.
- **Reported with the verdict, not part of it:**
  - site and label recall at the rule, with lift and flagged share;
  - recall at 1 / 2 / 5 / 10 %;
  - PR-AUC;
  - gauge rise error and bias (`score.py`);
  - the sink totals (m³/s, inlets, cells).
- **Explicit failure-mode check (DRAINS.md), reported:** "the sink removes documented sites in proportion to flags". This is computed pooled over
  the held-out 23, and separately for sep2023 in Leominster city. The flag drop is 1 − (rule-flagged segments with inlets / base). The site drop
  is 1 − (rule-hit sites with inlets / base). The failure mode is called **present** when the site drop ≥ **0.8 ×** the flag drop (and the flag
  drop > 0).
- **Dev storm:** a drop of more than 2 sites at 3 % on sep2023 must be explained in `INLETS.md`. It does not block adoption.

## 6. Process

- The runs go through the Turing queue (`turing-queue` branch): `run_inlets` (array 0–49, `PIN`) and `collect_scores`. The collector waits for all
  tasks, then pushes only the small json files (`score_v2.json`, `score.json`, `points.json`, `flood_meta.json`) to
  `docs/proto/drains/inlets_v1/`.
- A run that fails for a technical reason (download, timeout, node) is rerun **unchanged** under a new queue id. No storm is dropped or re-boxed
  after a result has been seen. Until all 23 decision storms have both arms, the verdict is "incomplete".
- Scoring: `python proto/inlets_eval.py` writes `compare.json`, `eval.json` and `eval.md`. The verdict and the failure-mode check go to
  `docs/proto/drains/INLETS.md` whatever they are.
- If the test is not adopted, `LF_INLETS` stays opt-in, off by default, as `LF_DRAINS` does. If it is adopted, the leaf-season value is still
  untested (§2) and must be flagged as such wherever it is used live.

## 7. Known limitations (stated before the result)

- **Static capacity.** The capacity is fixed at one ponding depth. Real inlets take less at shallow depth, but the cell then has less water
  to remove. They take more when the grate is submerged.
- **No on-grade inlets.** Every inlet is treated as a sag inlet, with no bypass flow. This is an upper bound for inlets on grade.
- **Grate size assumed.** The inventory records no grate size.
- **Leominster municipal inlets are inferred.** They come from pipe nodes, with a fixed inlet share.
- **MassDOT covers state highways only.** Municipal streets outside Leominster have no inlets in this sink.
- **No outfall return.** Drained water is not put back in the receiving streams, so downstream gauges will read low, as in DRAINS.
- **Labels are positive-only.** "False alarm" is judged by flagged share and lift, not by confirmed dry roads.
