# Paper 2 manuscript draft: where a flash flood damages the road (working title)

Status: §1 drafted 21 Nov 2026. Every number carries a `<!-- src -->` pointer; citations are checked in `LITERATURE.md`.

## 1. Introduction

Road-flood models are judged on whether they put water on the right road. That is the question a closure warning needs, and it is the
one our first study answered for central Massachusetts: a physics-based screen that ranks road segments by modelled depth and catches
about one in five documented flood sites in the top 3 % of segments on storms it never saw. But the cost that a road agency carries after
the water recedes is damage to the road itself, and damage does not need deep water. When the City of Leominster surveyed its roads after
the storm of 11 September 2023, 50 of the 54 damage points it recorded were washouts, and 33 of the 54 lay on segments the closure rule did
not flag, most of them edges eroded where the model put about 2 cm of water.
<!-- src: paper/MANUSCRIPT.md §4.2–4.3 (0.204 / 0.210 at 3 %); groundwater/SCOUT.md §6 (damage types: 50 washout, 2 culvert, 2 other); phase1/LEOMINSTER_MISSES.md (33 misses, 26 edge washouts, median 2.4 cm) -->

Closure and damage are different links of the same cascade. Rain becomes surface flow; flow that runs along a road concentrates at curbs
and shoulders and erodes them; water that stays in the ground raises the water table under the pavement and weakens its base for days.
The distinction between a hazard that triggers the next one and hazards that merely coincide is central to the cascading-hazard
literature (Gill and Malamud, 2014; Pescaroli and Alexander, 2015; Yanites et al., 2025), but road-flood studies rarely follow the chain
past inundation.
<!-- src: PROJECT_LOG §4 (14 Nov, cascading framing); RESEARCH_LOG 3.3 -->

Two strands of work point to the missing link. For bridges, stream power separates structures damaged by Tropical Storm Irene in
Vermont from undamaged ones (313 damaged against 951 undamaged; Anderson et al., 2017), and has been turned into damage-probability
curves; but the analysis works at the scale of stream reaches, with design flows rather than the storm's own, and reports no predictive
test. For pavements, the time a flooded base takes to saturate and the surface to fail has been modelled (Mallick et al., 2015), and
practice for assessing flood damage to roads has been reviewed, showing that water in the unbound layers does the most structural damage
(Tao and Mallick, 2020). Neither has been applied to the road edges of an ordinary town network, or tested against a recorded damage list.
<!-- src: paper2/LITERATURE.md (Anderson et al. 2017 VTrans report, ch. 3–4; Tao & Mallick 2020 LTRC 615; Mallick, Tao et al. 2014/15) -->

This paper asks three questions, each pre-registered before it was run. (1) Does a road-edge stream-power index computed from 1 m lidar
identify the segments that were damaged, beyond what flood depth and traffic already explain? (2) Is damage more common where the seasonal
water table is shallow once terrain is held constant, or is that association just low ground? (3) Which culverts would turn a storm into a
road failure if blocked, as a list for inspection? We answer them for Leominster, where a complete municipal damage inventory exists, report
those answers as in-sample, and set up the out-of-sample test of the index for the next inventory.
<!-- src: paper2/PREREG_RQ1.md; groundwater/PREREG_A.md; paper2/RQ3_INSPECTION_LIST.md; paper2/PREREG_RQ1_V2_DRAFT.md -->
