# Paper 1: submission checklist (18 Nov 2026)

Draft: `MANUSCRIPT.md` (complete first draft, self-reviewed: `REVIEW_SELF.md`). Nothing has been sent to anyone.

## 1. Done
- Data availability section (code statement waits for decision C).
- Abstract, sections 1–7, Figs 1–8 with captions, Tables 1–8, reference list (R1–R40).
- Number-by-number source check (every paragraph carries a `<!-- src: -->` pointer); hostile-reviewer pass with 10 major and 9 minor
  points, all fixable ones fixed from existing results.
- Consequences on two storms (Sept 2023 calibration, Sept 2021 held-out, plan fixed before the run).
- Uncertainty on every headline number, with the interval level stated.

## 2. Still to do (no decision needed; mechanical)
1. Convert `R#` citations to the journal's reference style. *Draft list done (`REFERENCES.md`, 17 works, every DOI checked 18 Nov); the in-text conversion waits for the journal choice (A).*
2. Remove the `<!-- src: -->` comments (keep a private copy with them).
3. Figures at the journal's resolution and fonts (all are drawn by `proto/paper_figs.py`, 200 dpi now).
4. Supplementary material. *Index done (`SUPPLEMENT.md`) and per-storm tables as CSV (`supplement/`, 19 Nov). Left: original commit
   hashes for documents fixed before 7 Nov (full clone); Fig. S1 (vulnerability layer) drawn or dropped.*
5. Word version with track changes for the advisors (Mo's rule for advisor comments).
6. Language edit; word count against the journal limit.

## 3. Decisions for Mo and the advisors

### A. Target journal
| Option | Fit | Notes |
|---|---|---|
| **Natural Hazards and Earth System Sciences (NHESS)** | hazard + impact evaluation, pre-registration and out-of-sample testing are valued; open access | open discussion phase (reviews are public); article fee (check current rate and any WPI agreement) |
| ASCE Journal of Infrastructure Systems | road networks, resilience, DOT audience; we screened all 87 of its roadway-flooding papers | less hydrology depth expected; the evaluation protocol would be the selling point |
| Journal of Hydrology | hydrological modelling | the road-closure angle and the consequences are less central there |
| Transportation Research Part D | transport impacts of climate hazards | would need more on traffic and access, less on the flood model |

**Recommendation: NHESS**, with J. Infrastructure Systems as the second choice. Check both journals' current code and data policies before
deciding (see C).

### B. Authors
Suggested: Mohab Eldokla (first, corresponding), then the advisors in the order they prefer (Prof. Tao, Prof. Albano, Prof. Graff), plus
anyone who supplied data with substantial work and wants authorship (e.g. Leominster DPW for the damage inventory would normally be an
acknowledgement, not an author). **Mo and the advisors decide.**

### C. Data and code availability (Mo wants the model code private)
| Option | What it means |
|---|---|
| 1. **Code available on request**; data sources listed (all public) | simplest; some journals discourage it and reviewers may ask |
| 2. Code archived now in a private or embargoed archive with a DOI, opened at acceptance or later | keeps it private during review; satisfies most availability statements |
| 3. Public at acceptance | strongest for reproducibility; the code becomes public |

**Recommendation: option 2** if the chosen journal accepts it, otherwise option 1. Data used are public (MRMS, HRRR, 3DEP, NHDPlus, NLCD,
SSURGO, NBI, NAACC, NWS reports, Census) except the Leominster DPW inventory (shared by the City: ask before publishing it) and MassDOT
files (cite as received). The derived scores and labels could be released without the model code.

### D. The Sept 2021 consequence run
Now in the main text (§4.5, Table 7) next to Sept 2023. Alternative: move it to the supplement and keep §4.5 on one storm. **Recommendation:
keep it in the main text**: it is the held-out check of the dry-road finding, decided before the run.

### E. Locked storms
The five locked storms are the cleanest final test (Conclusions mention them). Opening them is Mo's decision; once opened they cannot be
locked again. **Recommendation:** open them only after the model and paper settings are frozen for submission, and report the result
whatever it is.

## 4. Decisions taken (Mo, 20 Nov 2026: "I approve all your recommendations")
A NHESS (second choice J. Infrastructure Systems) · B authors as suggested, final order by the advisors · C code archived under embargo
with a DOI, opened at acceptance; "on request" until then (Mo creates the archive account at submission; Claude does not create
accounts) · derived data (sites, scores, pre-registrations) released with the paper · Ganin et al. 2017 cited for the consequence
metrics · D Sept 2021 run stays in the main text · E locked storms opened only after the settings are frozen for submission.
