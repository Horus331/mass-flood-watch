# C1 precipitation phase in the live forecast: decision (13 Nov 2026, ~02:00Z)

Pre-registration: `PREREG_PHASE_LIVE.md` (PROTOCOL §A.1 artifact-fix route).

1. **Artifact:** all precipitation treated as rain; NWS forecasts snow on the hills 13–14 Nov. Shown from inputs (HRRR 2 m temperature).
2. **Removed:** smoke test 12 Nov, hills box, 18Z HRRR: 5.2 % of the precipitation held as snow (max 1.3 mm water) instead of rain.
3. **Held-out 23 (+ sep2023, aug2021):** `phase_check.json` (HRRR analysis 2 m temperature, every hour of each storm's window, minimum over
   the box): the coldest storm hour anywhere is **11.1 °C** (may2018); no storm drops below 2 °C, so LF_PHASE changes none of them and the
   held-out skill is unchanged exactly (difference 0). The golden storm (sep2023, 16.5 °C minimum) is unchanged too.
4. **No tuning:** fixed 0–2 °C ramp.

**Decision: adopted as an artifact fix.** `LF_PHASE=1` is on in `forecast.yml` from the next cycle. Not a skill gain. Limitation: snow is
held, never melted within a run (rain-on-snow melt is not modelled).
