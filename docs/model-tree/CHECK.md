# Model tree check (2026-11-15 12:56Z)

`python proto/model_tree.py check`: every parameter on the tree re-read from the code and the live forecast workflow (`.github/workflows/forecast.yml`) and compared with `docs/model-tree/tree.json`.

**Result: PASS** — 51 parameters match the code, 4 are stated values (not code settings), 0 differ; 0 code links point to missing files; 41 source links listed.

| node | parameter | on the tree | in the code (where) | |
|---|---|---|---|---|
| dem20 | grid cell size | 20 | 20 (.github/workflows/forecast.yml env RES) | OK |
| channels | flowline enforcement (live terrain fix T2) | 1 | 1 (.github/workflows/forecast.yml env LF_CHAN_ENFORCE) | OK |
| channels | maximum enforcement cut | 10 | 10 (sim/colab/w9_lisflood.py default of LF_CHAN_ENFORCE_MAX) | OK |
| notch | search radius for the notch level | 40 | 40 (sim/colab/w9_lisflood.py default of LF_BREACH_M) | OK |
| notch | notch fix (live terrain fix T2) | 1 | 1 (.github/workflows/forecast.yml env LF_NOTCH_FIX) | OK |
| breach | maximum cut | 4 | 4 (sim/colab/w9_lisflood.py default of LF_BREACH_MAX) | OK |
| breach | 4-connected carving | 1 | 1 (sim/colab/w9_lisflood.py default of LF_BREACH_D4) | OK |
| cn | antecedent moisture class | II | II (.github/workflows/forecast.yml env LF_CN_AMC) | OK |
| cn | curve-number scale c | 0.88 | 0.88 (.github/workflows/forecast.yml env LF_CN_SCALE) | OK |
| cn | steady loss after runoff | 2 | 2 (.github/workflows/forecast.yml env LF_INFIL_MMH) | OK |
| cn | loss taken from the hourly excess (parity mode) | 1 | 1 (.github/workflows/forecast.yml env LF_PARITY) | OK |
| manning | channel / water n | 0.035 | 0.035 (sim/colab/w9_lisflood.py default of LF_N_CHAN) | OK |
| manning | floodplain n | 0.08 | 0.08 (sim/colab/w9_lisflood.py default of LF_N_FP) | OK |
| lisflood | parity settings: time-step cap Δt_max = 1 s, soil loss taken from the rain | 1 | 1 (.github/workflows/forecast.yml env LF_PARITY) | OK |
| lisflood | Courant number α | 0.7 | (stated) | n/a |
| lisflood | default floodplain friction (fpfric) | 0.08 | (stated) | n/a |
| lisflood | snapshot interval | 300 | 300 (.github/workflows/forecast.yml env LF_SAVEINT) | OK |
| velocity | velocity output | 1 | 1 (.github/workflows/forecast.yml env LF_VOUT) | OK |
| roadpts | edited-cell tolerance | 0.05 | 0.05 (proto/prototype.py EDIT_TOL_M) | OK |
| onset | rain-onset threshold | 1.0 | 1.0 (proto/prototype.py RC_RAIN_ONSET_MM) | OK |
| onset | rise needed after onset | 30.0 | 30.0 (proto/forecast.py RISE_CM) | OK |
| pclose | closure depth d₀ | 0.3 | 0.3 (proto/prototype.py FAIL_M) | OK |
| pclose | uncertainty σ | 0.1 | 0.1 (proto/prototype.py SIGMA_M) | OK |
| pclose | flag threshold | 0.5 | 0.5 (proto/forecast.py CLOSE_P) | OK |
| culvert | flow uncertainty σ_lnQ | 0.3 | 0.3 (proto/prototype.py Q_SIGMA_LN) | OK |
| culvert | blockage, NAACC "Poor" | 0.25 | 0.25 (proto/prototype.py BLOCKAGE['Poor']) | OK |
| culvert | blockage, NAACC "Critical" | 0.5 | 0.5 (proto/prototype.py BLOCKAGE['Critical']) | OK |
| culvert | crossing → road distance | 30.0 | 30.0 (proto/prototype.py XING_SEG_M) | OK |
| freeboard | design freeboard m | 0.3 | 0.3 (proto/prototype.py FB_MARGIN_M) | OK |
| freeboard | σ_fb | 0.15 | 0.15 (proto/prototype.py FB_SIGMA_M) | OK |
| freeboard | search radius | 30.0 | 30.0 (proto/prototype.py FB_RADIUS_M) | OK |
| fastwater | small-car limit d·V | 0.3 | 0.3 (proto/prototype.py DV0_M2S) | OK |
| fastwater | σ (log) | 0.35 | 0.35 (proto/prototype.py DV_SIGMA_LN) | OK |
| washout | permissible velocity | 1.5 | 1.5 (proto/prototype.py V_ERODE_MS) | OK |
| washout | σ (log) | 0.3 | 0.3 (proto/prototype.py V_SIGMA_LN) | OK |
| washout | minimum depth over the road | 0.1 | 0.1 (proto/prototype.py ERODE_MIN_H_M) | OK |
| edge | permissible speed | 1.0 | 1.0 (proto/prototype.py EDGE_V_MS) | OK |
| edge | permissible shear | 11.0 | 11.0 (proto/prototype.py EDGE_TAU_PA) | OK |
| edge | reference duration | 1.0 | 1.0 (proto/prototype.py EDGE_T_REF_H) | OK |
| pregnolato | no effect below | 5.0 | 5.0 (proto/cascade.py SLOW_CM) | OK |
| pregnolato | closed at | 30.0 | 30.0 (proto/cascade.py CLOSE_CM) | OK |
| access | hospital | 30.0 | 30.0 (proto/resilience.py ACCESS_MIN['hospital']) | OK |
| access | fire station | 8.0 | 8.0 (proto/resilience.py ACCESS_MIN['fire_station']) | OK |
| access | police | 10.0 | 10.0 (proto/resilience.py ACCESS_MIN['police']) | OK |
| gate | 6 h threshold G₆ | 25 | 25 (proto/forecast.py default of GATE_6H_MM) | OK |
| gate | 24 h threshold G₂₄ | 40 | 40 (proto/forecast.py default of GATE_24H_MM) | OK |
| gate | water-mode threshold | 8 | 8 (proto/forecast.py default of WATER_MM) | OK |
| gate | box size | 20 | 20 (proto/forecast.py BOX_KM) | OK |
| nbhd | radius, percentile | 20,90 | 20,90 (.github/workflows/forecast.yml env LF_HRRR_NBHD) | OK |
| spinup | spin-up | 12 | 12 (.github/workflows/forecast.yml env LF_SPINUP_H) | OK |
| phase | T_lo | 0.0 | 0.0 (sim/colab/lf_phase.py T_LO) | OK |
| phase | T_hi | 2.0 | 2.0 (sim/colab/lf_phase.py T_HI) | OK |
| phase | switch | 1 | 1 (.github/workflows/forecast.yml env LF_PHASE) | OK |
| matching | match distance | 30 | (stated) | n/a |
| matching | site clustering | 150 | (stated) | n/a |
