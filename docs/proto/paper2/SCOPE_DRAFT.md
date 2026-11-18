# Paper 2: scoping draft (proposal only; nothing run) — 18 Nov 2026

**Where Paper 1 stops.** Paper 1 covers rain → flood → road closure → lost access. Its clearest gap is damage that happens *without*
deep water: in Leominster (Sept 2023) 33 of 54 DPW damage points were missed, 26 of them edge washouts with a median modelled depth of
2.4 cm (`phase1/LEOMINSTER_MISSES.md`). No change to soil wetness, frozen ground or culvert blockage recovers them (`phase1/PARAMETRIC*.md`).
The next link of the cascade is therefore the **road structure**: erosion at the edge, and a weakened subgrade when the water table rises.

## Candidate research questions

### RQ1. Can a gutter-scale flow measure explain edge washouts that a ponding threshold misses?
- **Idea:** water concentrated along curb lines and road edges erodes the shoulder with little standing water. A 20 m grid cannot hold a
  gutter, but the 1 m lidar can give, for each road edge, the upslope area draining along it and its slope, i.e. a unit stream power
  index, combined with the model's rain.
- **What we have:** 54 surveyed damage points (50 washouts) for one storm; 1 m lidar in Leominster; the model's discharge and speed.
  Within Leominster, modelled depth separates damaged segments (AUC 0.87), traffic 0.85, peak speed 0.78; the model's existing
  washout flag 0.50 (no signal).
- **Ruled out already (§6):** the existing edge-erosion layer (+0 DPW sites; cannot be tested outside Leominster without labels); the
  bare ≥ 0.5 m/s flow test (63 % of all segments pass it). RQ1 is a *new* index, not these.
- **Test now:** only in-sample in Leominster (the calibration storm), so descriptive.
- **Needs for a real test:** a second damage inventory: MEMA / FEMA Public Assistance Category C (roads and bridges) for another storm
  (draft request ready, `claude/model_colab/2026-11-14_Damage_Inventory_Request_Draft.md`, Mo to send), or another town's DPW list.

### RQ2. Does a shallow water table add to damage risk after holding the terrain constant? (groundwater proposal A)
- **What we have:** 23 USGS 15-minute wells (rise 4–7 days after storms); seasonal water table under every District road (36 % of road
  length within 50 cm); damage on shallow water tables 81 % vs 43 % for all Leominster segments, but confounded with low ground
  (`groundwater/SCOUT.md` §5–6).
- **Test now:** the pre-registration draft (`groundwater/PREREG_A_DRAFT.md`, matched on height above drainage and slope, unit = segment).
  It waits for Mo's choice among A / B / C. Likely inconclusive with 23 damaged segments, but it decides whether RQ2 is worth data.
- **Needs for the mechanism:** pavement and subgrade observations (MassDOT pavement condition / distress, any falling-weight
  deflectometer data, boring logs); damage from more storms.

### RQ3. Which culverts would turn a storm into road failure, and does their condition predict it?
- **What we have:** the crest readout and pool rise per crossing (blockage 20 / 50 / 100 %), a robust top-9 priority list, NAACC condition
  (`phase1/PARAMETRIC_T2.md`).
- **Needs:** MassDOT culvert condition and failure records (requested via David Henriques, waiting); without them this stays a
  model-based inspection list.

## What fits where
| | Can start now | Main data gap | Fits the qualifying exam |
|---|---|---|---|
| RQ1 washout index | in-sample, Leominster | second damage inventory | **yes, core**: the structural link of the cascade, engineering mechanism (shear / stream power vs erodibility) |
| RQ2 groundwater | pre-registered association test (draft) | pavement / subgrade data | yes, as the geotechnical link; strong framing, thin data |
| RQ3 culverts | priority list exists | MassDOT condition data | applied section (inspection priorities, as the advisors asked on 3 Nov) |

**Suggestion (for discussion, nothing started):** Paper 2 = RQ1 as the core, with RQ2's test as a section and RQ3 as the applied output.
The single most useful action is **a second damage inventory** (the MEMA / FEMA request), because every structural question is
currently limited to one storm in one town. The qualifying-exam story becomes: closure (Paper 1) → structural damage (Paper 2) →
groundwater as the slow link (dissertation chapter).
