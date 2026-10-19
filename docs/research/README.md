# docs/research — research-scout notes

Literature, competitor and data scouting for mass-flood-watch. These notes inform decisions; nothing here changes the engine or the validation protocol by itself.
Claims are tagged [paper] / [preprint] / [vendor] / [news] / [bg] (background, not re-checked) in the files.

| file | what |
|---|---|
| [`sota_2026-10-19.md`](sota_2026-10-19.md) | State of the art as of Oct 2026: (a) fast 2-D engines (LISFLOOD-FP 8.1, SFINCS sub-grid, HEC-RAS 2D, TUFLOW HPC, RIM2D, Itzï, TRITON/SERGHEI, NOAA HAND-FIM) and how they treat structures, steep reaches and infiltration; (b) ML surrogates and global models (Google Flood Hub incl. Mar 2026 flash floods + Groundsource, FloodCast, mSWE-GNN, Flood-LDM, TabPFN, FIMserv, Prithvi); (c) infrastructure failure / cascading / digital twins; (d) competitors (First Street, Fathom, JBA, ICEYE, Floodbase, 7Analytics, Google, NWS, MassDOT, USGS/UMass) — each with "better than us / we do that they don't". |
| [`data_sources.md`](data_sources.md) | Public data not yet used: URL, coverage, format, access, licence, and where it plugs in (input / calibration / validation / ML label / baseline); **BIAS** flags for the steep-reach high water levels and over-wet roads. Includes the USGS legacy-API shutdown (Nov 2026 – Q1 2027). |
| [`ideas.md`](ideas.md) | Ranked backlog: 12 testable hypotheses for the high bias and Dec 2023 over-wet roads (A1–A12), engine accuracy/speed (B), ML and labels (C), cascade/failure (D), uncertainty/warning (E), publications (F); each with effort, data and the protocol test. |

## Changelog
- **2026-10-19** — first pass (research scout): SOTA, data sources, ideas backlog. Read-only on code; one quick local check (MA vs Bieger bankfull on the 365-row crossings sample) recorded in `ideas.md` A4. Pages blocked to the agent: HEC-RAS 2025 product page, PMC12106317. `ideas.md` section A cross-referenced with the repo's own diagnosis (Conway sill, BREACH=1 queued, Avery bias mostly metric).
