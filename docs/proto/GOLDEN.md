# Golden storm: regression test of the model (Phase 0.6, 11 Nov 2026)

`.github/workflows/golden.yml` + `tools/golden.py`. On every push or pull request that touches the model (`sim/**`, `proto/prototype.py`,
`proto/closure*.py`), it runs one small fixed storm with the live settings and compares the result with `docs/proto/golden/reference.json`.

- **Storm:** Leominster, 11 Sep 2023 (the tuning storm), observed MRMS rain, 12 h from the catalogue t0 (16:00 UTC).
- **Box:** 8 × 8 km over the city (EPSG:26986 168000,914000 – 176000,922000), 20 m, CPU (GitHub runner).
- **Settings:** as the live forecast (CN × 0.88 AMC II, parity mode, T2 terrain fix, 2 mm/h infiltration; closures with the rise rule).
- **Fingerprint and tolerances:** rain in (0.1 %), flooded land ≥ 0.1 m and ≥ 0.3 m (2 %), 99th-percentile depth on land (5 cm), number of
  road segments in the box (exact), closures (± 2) and which segments close (overlap ≥ 0.9).

A failure means the change moved the model. If that was intended, rerun the workflow by hand with `update = true`, which commits a new
reference, and say why in `CHANGELOG.md`.

## Reference history

| date | reference from | why |
|---|---|---|
| 2026-11-11 | run 43019264848 (sha 20c67cca) | first reference. Repeat run on the same code: identical (closures 5 → 5, flooded ≥ 0.3 m 0.551 → 0.551 km², rain 186 / 84.4 mm). CI time about 6 min, solver about 2–3 min. |

Reference values: 290 road segments in the box, 5 closed, 3.32 km² of land wetter than 0.1 m and 0.55 km² wetter than 0.3 m, storm total 186 mm, peak hour 84.4 mm.
