# C1 precipitation phase as an artifact fix for the live forecast: pre-registration (13 Nov 2026, ~01:30Z)

PROTOCOL §A.1 route. Written before the held-out check below is run.

1. **Artifact.** The model treats all precipitation as rain. Snow that falls is put on the ground as water at once (input-caused; shown from the
   inputs alone: HRRR 2 m temperature below 0 °C while precipitation falls). Live case: NWS Boston expects snow on the hills 13–14 Nov.
2. **Removal.** With `LF_PHASE=1` the frozen share is held as snow (smoke test 12 Nov: 5.2 % frozen on the hills box, 18Z HRRR).
3. **Non-inferior on the held-out 23.** Shortcut fixed now: a storm whose box never drops below 2 °C (HRRR analysis, every hour of its
   catalogue window, `proto/phase_check.py`) is unchanged by construction. If every held-out storm is unaffected, condition 3 holds exactly
   (difference 0). If any is affected, those storms are re-run with LF_PHASE=1 and the §A.1 thresholds applied to the full set.
4. **No tuning.** The 0–2 °C ramp is a fixed textbook rule, not fitted.

Decision: all four hold → `LF_PHASE=1` on in the live forecast (forecast.yml), reported as an artifact fix. Otherwise it stays off.
