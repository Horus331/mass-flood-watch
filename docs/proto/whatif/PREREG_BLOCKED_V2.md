# Blocked culverts, version 2: pre-registration (12 Nov 2026)

Committed before any version-2 run. Results go to `BLOCKED_V2.md` whatever they are.

## Finding that prompted it (what-if explorer, version 1)
In the 13 complete open / blocked pairs of the 32 Leominster what-if scenarios, blocking the culverts gave **fewer** closures within 60 m of
a blocked crossing in 11 pairs (e.g. rain × 1, dry ground: 9 open → 3 blocked), and fewer closures overall in 9. Blocked culverts should
pond water behind the road and overtop it, so this is the wrong direction. Cause (from the code, `block_crossings`): version 1 raises the
3 × 3 cells at each crossing to their **highest** cell, which lifts the road there above its surveyed height (shoulders, guard rails,
embankment tops), so the water finds another way and the road at the crossing stays dry. A "value of maintenance" computed from version 1
would be negative, which is an artefact.

## Version 2 (fixed now)
`LF_XINGS_BLOCKED=2`: at each mapped non-bridge crossing the 3 × 3 cells keep the **lidar surface** (the road over a culvert as surveyed;
lidar does not see the pipe), only the channel burn is undone there (so the burnt stream line cannot pass under the road), and the
40 m block stays protected from depression breaching. No cell is raised above the lidar. Everything else as version 1.

## Runs
Turing, `whatif_pipeline` (GPU solve + CPU post): the 16 blocked scenarios with version 2, plus the two open scenarios that are missing
(r050_normal_open, r075_dry_open). The 14 open scenarios already done are unchanged.

## Checks
1. **Direction.** Within 60 m of a blocked crossing, closures blocked ≥ open in at least 75 % of the complete pairs.
2. **Ponding.** Peak wet area (km²) blocked ≥ open in at least 75 % of the complete pairs.

## Decision
Both pass → version 2 replaces version 1 in the what-if explorer, and the value of maintenance is reported as closures (within 60 m of
a crossing, and box-wide) avoided by clear vs blocked culverts, per scenario, with the run-to-run churn stated. Either fails → the
explorer's culvert switch is labelled "not reliable yet" and no maintenance value is reported.
