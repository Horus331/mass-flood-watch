# Paper 2 outline (draft, 20 Nov 2026): beyond closure — where a flash flood damages the road itself

Direction approved by Mo on 20 Nov 2026: road-edge washout index as the core, groundwater as a section, culvert list as the applied part.
Every number below has its source file; all Leominster results are in-sample (Sept 2023 is Paper 1's calibration storm).

## 1. Introduction
- Paper 1 predicts closures (water over the road). Damage is a different failure: 50 of 54 Leominster DPW damage points were washouts,
  and 33 of 54 lie on segments the closure rule did not flag, 26 of them edge washouts with ~2 cm modelled depth
  (`phase1/LEOMINSTER_MISSES.md`).
- Gap: road-flood models score inundation; road agencies repair erosion. Cascade framing (Yanites et al. 2025; Gill & Malamud 2014):
  rain → surface flow along the road → edge erosion / subgrade weakening → road failure.

## 2. Study area and data
- Leominster, Sept 2023 (calibration storm, 54 DPW points, 21 damaged segments of 712 with lidar coverage).
- 1 m 3DEP lidar (USGS image service); the Paper 1 flood run on the T2 terrain; SSURGO seasonal high water table; 23 USGS 15-minute wells;
  NAACC culvert surveys; crossings inventory.
- Second inventory for the out-of-sample test: MEMA / FEMA Public Assistance Category C (request drafted, Mo to send).

## 3. Methods
3.1 Road-edge stream-power index (v1 spec `paper2/RQ1_INDEX_SPEC.md`; v2 with crossings removed and 50 m windows, `PREREG_RQ1_V2_DRAFT.md`).
3.2 Groundwater association with terrain held constant (`groundwater/PREREG_A.md`): Mantel–Haenszel over 15 height-above-drainage ×
    slope strata, with a surface-water negative control.
3.3 Culvert blockage what-ifs and the crest readout (`phase1/PARAMETRIC_T2.md`).
3.4 Pre-registration of every test; in-sample results reported as descriptive.

## 4. Results
4.1 Edge index vs damage (in-sample, `paper2/RQ1_RESULT.md`): AUC 0.85 [0.78, 0.92]; adds over depth + traffic (p = 0.0001); 5 of 8
    missed washout segments in the top 10 %. Post-hoc: length (AUC 0.87) and crossings (0.83) explain much of it; with both controlled
    the index still adds (p = 0.016). v2 is length-neutral (rank correlation with length 0.36 vs 0.65; `RQ1_V2_CHECK.md`).
4.2 Groundwater (`groundwater/PREREG_A_RESULT.md`): odds ratio 2.70 [1.02, 7.12] for damage on a water table ≤ 50 cm with terrain held
    constant, but surface-water closures show the same association (2.68): not separable from wet low ground with this data.
    Wells: water tables peak 4–7 days after storms; 36 % of District road length sits on a water table within 50 cm (`groundwater/SCOUT.md`).
4.3 Culverts: blockage raises pools 0.6–2.3 m and closes 8–82 more segments near crossings, but explains none of the missed damage;
    robust top-9 inspection list (`phase1/PARAMETRIC_T2.md`).
4.4 Out-of-sample test of index v2 on the second inventory [pending data].

## 5. Discussion
- Two failure modes need two indicators: depth for closure, edge flow for erosion. Groundwater is the slow link: it changes the next
  storm and the subgrade, not same-day closure, and needs pavement / subgrade data to be tested as a mechanism.
- Practical output: a ranked list of road edges for post-storm inspection, complementing the closure list.

## 6. Limitations
One storm, one town, 21 damaged segments; lidar shows no storm drains; SSURGO describes natural soils, not road fill; in-sample until 4.4.

## What is needed to finish
1. The second damage inventory (Mo's request). 2. Freeze v2's reading rules, run 4.4. 3. Pavement condition data from MassDOT (for the
groundwater mechanism; would make 4.2 a real test).
