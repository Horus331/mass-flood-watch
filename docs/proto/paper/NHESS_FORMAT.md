# Paper 1 → NHESS: format plan (20 Nov 2026)

From the NHESS pages (manuscript types, submission, article processing charges), checked 20 Nov 2026.

## Fit
Research article: 6–24 journal pages, abstract 100–200 words. Our main text is ~4,850 words with 8 figures and 8 tables (~18–22
journal pages): fits. **Abstract cut to 199 words (done 20 Nov).**

## Required pieces we do not have yet
| Item | NHESS rule | Status |
|---|---|---|
| Short summary | ≤ 500 characters, non-technical, abbreviations spelled out | draft below |
| Code availability | code in a FAIR repository, cited with a DOI in the references | **embargo not mentioned in the NHESS guidelines**: an embargoed or restricted-access record (e.g. Zenodo restricted) may be questioned; ask the handling editor at submission, fallback "on request" with the reason |
| Data availability | before the acknowledgements, with persistent identifiers | section drafted; derived data (sites, scores, pre-registrations) need a DOI deposit (Mo creates the account) |
| Author contributions | CRediT recommended | to write once the advisors fix the order |
| Competing interests | exact wording if none: "The authors declare that they have no conflict of interest." | add |
| AI tool use | must be described in Methods or Acknowledgements | **add**: AI assistance (Claude) used for code, analysis scripts and drafting; all results checked by the authors |
| Financial support | after the acknowledgements | Mo to supply |

## Mechanics
- 1-column PDF with page and line numbers; Copernicus LaTeX package or Word template; figures and tables placed near first mention.
- References: alphabetical, author–year in text ("Smith et al., 2006"), abbreviated journal names, DOIs; convert `REFERENCES.md`.
- Figures: 300 dpi (ours are 200 dpi: re-render with `proto/paper_figs.py` at dpi=300), ≥ 8 cm wide, legends inside figures, one font
  family, colour schemes safe for colour-vision deficiency (check the depth and category palettes), panel labels "(a)".
- Tables: editable, horizontal rules only, no coloured cells.
- Maps: credit OpenStreetMap / USGS sources in captions.
- Process: public discussion preprint first, then review; APC for full articles submitted from 2025: €1,800 net flat (10 % off for EGU
  members; check whether WPI has a Copernicus institutional agreement).

## Short summary (draft, 465 characters)
Floods often close roads in small inland towns with little warning. We tested a computer flood model that uses radar rainfall to rank
which roads in central Massachusetts are most likely to flood, checking it on storms it had never seen. It found two to three times as many
reported flooded roads as warnings or flood-zone maps when flagging the same number of roads, and showed that most people cut off from
hospitals and fire stations live on roads that stay dry.
