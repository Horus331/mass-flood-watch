# More and better labels for the District 3 road-closure model: data sources, people, and how to use them (24 Oct 2026)

This is a research note. No code was changed. It builds on `obs/CATALOG.md`, `obs/LABELS_EXPANSION.md`, `recall/RECALL.md`,
`scoring/BASELINE_v2_expanded.md`, `ROADMAP_research.md` (section G) and the older `docs/research/data_sources.md` (section 4). Where those
already cover a source (NFIP claims, Groundsource, GFM/OPERA, NAACC), this note only adds what is new. "Verified" means checked against the
source on 24 Oct 2026. "Unverified" means I could not reach the source or confirm a detail.

## 0. Bottom line

**The problem.** The model is limited by labels, not by capacity:
- 25 storms and about 181 scored sites. 90 are held out, but 2–7 sites per storm.
- Labels are positive-only and report-biased. Outside the Leominster DPW city domain no false alarm can be measured.
- Almost no labels carry a closure time or duration.
- The NWS LSR/Storm Events and news well is nearly dry: 2024–2026 added nothing (`LABELS_EXPANSION.md` §4).

**What would change that.** Sources that are **(a) time-stamped, (b) all-roads, and (c) complete within some domain**, so that true negatives exist.
Three kinds of source meet that bar:
- **Dispatch logs.** Police, fire and DPW CAD records (public records requests), plus the dispatch logs some towns already post.
- **MassDOT's own records.** Crash reports with road surface "Water (standing or moving)", the Highway Operations Center event log, and the Waze
  feed MassDOT has received as a Waze partner since June 2016.
- **Probe speeds on the National Highway System (NPMRDS).** These give closures *and* confident negatives on the same segments.

**Cheapest win: fix our own parsing, then add WX1BOX.** The current label parser loses roads that are already in the LSRs.
- **aug2026:** one Leominster LSR names Union St and Washington St at Washington Sq (both closed), and one Lunenburg LSR names Sunny Hill Rd
  (impassable). All three are missing from the labels.
- **aug2023:** Speen St, Natick, is missing.
- **aug2026, wrong row:** the Allen Hill Rd row is a *basement* report.

The WX1BOX SKYWARN storm-report compilations then add reports that never reached the LSRs: Mirick Rd, Princeton (aug2026), and Main St,
Westminster (jul2023b, outside the box).

**Honest negatives.**
- **Sentinel-1/OPERA/Planet will not see these floods.** They are sub-daily urban flash floods, gone in hours.
- **USGS STN has no District 3 high-water marks in 2018–2026.** Checked against the repo's `docs/validation/stn_ma.json`.
- **FEMA Public Assistance for Sept 2023 was denied.** So OpenFEMA has no project worksheets for it.
- **Twitter/X is unaffordable, and Nextdoor is closed.**

### Top 10 by value per effort

| rank | source | gives | new labels (realistic) | effort | elapsed | why it ranks here |
|---|---|---|---|---|---|---|
| 1 | **Re-split multi-street LSR/Storm Events text, plus WX1BOX SKYWARN compilations** | positives with clock time | +15–35 sites over 25 storms | 1–2 d | days | Public now. Verified: 4 roads lost by our parser (aug2026, aug2023), 2 WX1BOX-only roads. |
| 2 | **MassDOT crash records, surface = 6 "Water (standing or moving)"** | positives with time and exact XY, all roads; discovers new storm days | +25–100 crash-sites (pilot first) | 1–2 d | days | Public and statewide, 2002–present, every road class. Cheap pilot. |
| 3 | **Police/fire dispatch (CAD) logs** for storm days (MA Public Records Law), plus logs towns already post | positives with time; near-complete per town → negatives | +100–300 sites | 3–5 d work | 2–6 weeks | The only source that is time-stamped *and* close to complete in a town. |
| 4 | **MassDOT HOC event log + archived Waze partner alerts (2018–2026)**, by request | closures with start/end; Waze flood alerts on all roads | 0 to several hundred (unknown until asked) | 1 d ask + 3 d parse | 2–8 weeks | Possibly the biggest single source. The repo's events logger only starts in Oct 2026. |
| 5 | **NPMRDS 5-min probe speeds** (via MassDOT/CMRPC/MRPC RITIS access) | closures and durations on NHS; **true negatives** on NHS | +20–60 positive sites; thousands of negative segment-storms | 4–6 d | 1–4 weeks | Gives a "complete domain" (NHS) for CSI/precision, which no other source gives. |
| 6 | **Municipal damage inventories collected for the Sept 2023 FEMA request** (MEMA and towns) | complete damage inventories like Leominster DPW's | +50–150 points (sep2023 box, dev storm) | 1 d ask + 2 d | 3–8 weeks | Leominster's layer is one of these. Other towns filed too. |
| 7 | **Worcester 311 (since Jul 2023) and DPW work orders**, by request | resident reports with time; DPW response | +10–40 sites per Worcester storm | 2 d | 2–4 weeks | Worcester is our biggest domain. Covers jul2023, aug2023b and future storms. |
| 8 | **Waze closed-loop pilot with Leominster DPW** (§3) | driver confirmations **and denials** of our forecast | 10–100 per year | 4–6 d build | first storm | Forward only, but the only source of labelled false alarms. A publishable experiment. |
| 9 | **MRMS FLASH products as model inputs** (CREST max unit streamflow, QPE ARI, QPE/FFG ratio) | inputs | n/a; targets the flash-miss class | 2–3 d | days | NWS-tested flash-flood signals at 1 km / 10 min. Archive availability needs a check. |
| 10 | **Town Hazard Mitigation Plans and MVP reports: "Locally identified areas of flooding" tables** | static flood-prone road list for every D3 town | 200–400 static locations (priors, not storm labels) | 2–3 d | days | Feeds the PU propensity e(x) and a prior. Covers towns that never report. |

Next tier: mPING; the CoCoRaHS Significant Weather reports; the Meta Content Library (Facebook pages of town police and DPW); NewsBank (T&G)
via a library; Broadcastify audio for aug2026; NFIP/IA by ZIP; MassDEP sewage-overflow notifications as a drainage-overload indicator; the
MassDOT Road Inventory curb fields; and forward logging of the MassDOT GoTime feed, camera stills and any Waze layer. Details are in §2.

## 1. What a useful new label needs (and what we lack)

| property | current labels | why it matters for us |
|---|---|---|
| clock time of onset and end | LSR "report" time only; news day-level; DPW day-level | T8 conditioning, nowcast lead, duration rule (ROADMAP E) |
| all road classes | biased to state routes and Worcester streets | RECALL: rural washouts, small culverts are invisible |
| negatives (known open / dry) | none outside Leominster DPW | CSI, precision, calibration (BSS −0.17) and SAR-PU propensity |
| exact location | 38 of 50 Leominster misses are `approx` | strict 30 m matching; RECALL class C |
| new storms 2024–2026 | almost none | held-out power; current-climate test |

Every source below is judged on these five columns.

## 2. Candidate sources

Each entry gives: **G** = gives (L = labels, I = inputs, N = negatives); **Cov** = coverage; **Access** (URL or contact role); **Cost/terms**;
**Transform** (the algorithm to labels or features); **Yield**; **Effort**; **Risks**.

### 2.1 Public text we have not mined yet

**(1) WX1BOX SKYWARN storm-report compilations** (verified)
- **G:** L.
- **Cov:** NWS Boston/Norton area, per significant event, 2023 onward seen; earlier years unverified.
- **Access:** PDFs such as `https://wx1box.org/wp-content/uploads/2026/08/reports_8_3_26.pdf` and `.../2023/07/reports_7_10_23.pdf`.
  - The amateur-radio SKYWARN group that supports NWS Boston/Norton compiles flood, rain and wind reports per event, with times and street detail.
  - Files named `LSR_<date>.pdf` are only the NWS preliminary LSR summary. The `reports_<date>.pdf` files are the compilations.
- **Evidence** (checked against `obs/lsr_<id>.csv` and the label files):
  - **aug2026:** the compilation lists 10 Worcester County road reports. **Mirick Rd, Princeton (closed, 10:00)** is in no NWS LSR.
  - **aug2026, parser losses:** three more roads *are* in the LSR text but are missing from `labels_aug2026_leominster.csv`, because the parser
    keeps at most three roads per report: **Union St (closed)**, **Washington St at Washington Sq (closed)** and **Sunny Hill Rd, Lunenburg
    (impassable)**.
  - **aug2026, wrong row:** `Allen Hill Road: flooded` is an LSR about a basement and should be dropped.
  - **aug2023:** loses **Speen St near Nottingham Dr, Natick** the same way.
  - **jul2023b:** the compilation adds **Main St, Westminster (flooded and impassable, 17:15)**, which is in no 2023 LSR. It is outside the box.
- **Cost/terms:** free, public. Credit WX1BOX/NWS.
- **Transform:**
  1. Find all `reports_*.pdf` (site index or search), 2018–2026.
  2. Run `pdftotext`.
  3. Parse the "Flood reports" section into rows of time, town and text.
  4. Dedup against LSR/Storm Events (same town, ±10 min, text similarity > 0.6).
  5. Geocode with the existing `label_geocode.py`, `source=WX1BOX`.
  6. **Also split every multi-street LSR into one row per road.** The Sunny Hill case shows the current parser loses sites.
- **Yield:** the parser split gives perhaps +10–20 over all storms (4 found in two storms). WX1BOX gives about +1 per storm where a
  compilation exists, perhaps +5–15. Together, +15–35.
- **Effort:** 1–2 days. The sandbox proxy blocks wx1box.org, so run it in Actions.
- **Risks:** the same reporting bias as LSRs. Some entries are relayed from social media; keep a `source_detail` field.

**(2) MassDOT crash records with road surface "Water (standing or moving)"** (code verified; extract fields need a check)
- **G:** L (+ storm discovery).
- **Cov:** every police-reported crash in MA, all road classes. The IMPACT portal holds 2002–present.
- **Access:** MassDOT IMPACT Crash Open Data Portal (`apps.impact.dot.state.ma.us`, "Data Extract").
  - The MA crash report manual defines road surface **code 6 "Water (Standing or Moving)": "covered with an excessive amount of water," usually
    from flooding and typically localized.** Code 2 is ordinary wet pavement.
- **Cost/terms:** free, public.
- **Transform:**
  1. Extract D3 towns, 2018–2026, `road_surface = 6`, with crash date/time and X/Y.
  2. Keep crashes inside a storm window (t0 − 2 h to t0 + hours + 6 h).
  3. Each one becomes a site: `type=flooded`, `time_quality=report` (crash time ≈ water present), `coord_quality=exact` if X/Y is given.
  4. Run a **storm-discovery pass**: days with ≥ 3 code-6 crashes in a 20 × 20 km box are candidate storms, *independent of NWS*. That helps the
     thin 2024–2026 years.
  5. Code 2 crashes on the same storm days are *not* negatives. Code-6 rates on non-storm wet days give a background rate.
- **Yield:** unknown; pilot first. My guess is 1–5 per storm day in the box, so +25–100, plus 2–6 new storm days.
- **Effort:** half a day for the pilot (one county-year), 1–2 days in all.
- **Risks:**
  - Officer coding is inconsistent.
  - Crashes need traffic, so night-time floods are under-sampled.
  - Some code-6 crashes are hydroplaning in ordinary ponding, not closures. Label them `flooded`, not `closed`.

**(3) NWS text products beyond LSRs** (IEM AFOS archive; unverified yield)
- **G:** L (minor).
- **Access:** `https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=FFSBOX&sdate=...&edate=...` (also `FLSBOX`, `PNSBOX`).
- **Transform:**
  - Regex for "reported", "closed", "impassable" plus street names in the follow-up statements to Flash Flood Warnings.
  - The "locations impacted" lists are forecasts, so skip them.
- **Yield:** small. Most of it duplicates LSRs. **Effort:** 0.5 d. Worth one pass with item 1.

**(4) Town dispatch logs already posted online** (verified for one centre)
- **Example:** Dudley posts monthly logs of the **South Worcester County Communications Center** (`https://www.dudleyma.gov/Archive.aspx?ADID=93`).
  - Each entry has call time to the second, call reason, location and action.
  - That regional centre dispatches several southern Worcester County towns, including Webster, which is in sep2022. Other towns post weekly
    police logs, and local papers print them.
- **Transform:**
  1. For each storm day and town, pull the log.
  2. Keep call reasons such as "Safety Hazard", "Road/Traffic Hazard", "DPW Call Out", "Water problem" and "MV stuck" whose narrative matches
     `flood|water|wash|impass|closed|stuck`.
  3. Geocode the location field.
  4. Set the **time = call time**.
  5. When "road open" or "cleared" appears, the close-out time gives a duration.
- **Yield:** 2–15 calls per town per bad storm. **Effort:** 1–2 days for the towns that post. Everything else needs a request (2.4).
- **Risks:** narratives are terse. Names of callers must not be stored. Keep location, time and reason only.

**(5) Hazard Mitigation Plans and MVP reports: "Locally identified areas of flooding"** (verified that the tables exist)
- **G:** static L/prior.
- **Cov:** every District 3 town has a FEMA-approved HMP. Most were written by CMRPC or MRPC, and most also have MVP reports on mass.gov.
  - The Fitchburg 2020 HMP-MVP has a "Table 4-3 Locally Identified Areas of Flooding".
  - Worcester's 2025 HMP update has a flooding chapter.
  - CMRPC hosts Mendon, West Brookfield and others.
- **Transform:**
  - Parse the tables to road/area names, geocode, and give each a recurrence flag.
  - Use them as **(i)** a prior feature `known_flood_spot` within 150 m (careful: this is target leakage if the same spots are scored; use it only
    for the PU propensity e(x) or as a separate baseline), and **(ii)** a "reporting propensity" covariate: towns that list many spots also
    report more.
- **Yield:** 5–20 spots per town × ~40 towns. **Effort:** 2–3 days (PDF tables vary).
- **Risks:** static, undated and opinion-based. Never score against them.

**(6) Newspaper full text** (Telegram & Gazette, Sentinel & Enterprise, Patch)
- **Access:** NewsBank/ProQuest through a library. WPI's library guides list newspapers, but I could not verify T&G full text at WPI. The
  Worcester Public Library and many town libraries carry NewsBank with the T&G.
- **Transform:** query `(flood* OR washout OR impassable OR "road closed") AND <town>` for each storm date ±2 days, then hand-extract road, time
  and source.
- **Yield:** +1–3 sites per storm beyond the TV stories already read. **Effort:** 2–3 days of reading.
- **Risks:** day-level times only, and paywall terms (store quotes ≤ 25 words, as now).

**(7) Google Groundsource** — already in `docs/research/data_sources.md` 4.4. It is town-level with about 60 % place and time accuracy. Use it only
for storm discovery in 2024–2026, not for site labels.

### 2.2 Traffic and probe data

**(8) NPMRDS (FHWA National Performance Management Research Data Set)** (access rules partly verified)
- **G:** L + **N**.
- **Cov:** National Highway System TMC segments. In District 3 that means I-90, I-290, I-190, I-395, I-495, and Routes 2, 9, 12, 20, 122, 140 and
  146, plus NHS principal arterials in Worcester.
  - Data from Jan 2017 (with a 2016 backfill), at 5-min epochs, as speed and travel time.
  - About **22 % of our 350 label rows (76) name a numbered route**, so NPMRDS can check about a fifth of existing sites.
- **Access:**
  - The core data is free to state DOTs and MPOs at FHWA's expense, through RITIS (CATT Lab, UMD). If a state DOT licenses it, its MPOs get access
    too (INRIX).
  - MassDOT uses NPMRDS as its main travel-time source (FHWA case study).
  - Researchers get accounts through a sponsoring agency (MassDOT Office of Transportation Planning, CMRPC for central MA, MRPC for
    Montachusett).
  - Separately, IEEE/CATT Lab run **NTDAS** (`https://innovate.ieee.org/ntdas/`), which offers NPMRDS analytics to university researchers. Pricing
    is unverified.
- **Cost:** free through an agency.
- **Transform** (per TMC segment s and 5-min epoch t):
  1. Baseline: median speed v̄(s, how) and data completeness c̄(s, how) by hour of week, over 8 dry weeks around the storm.
  2. **Probable closure/impassable**: `v(s,t) < 0.25·v̄` for ≥ 6 consecutive epochs (30 min), **or** data missing for ≥ 30 min while
     c̄ ≥ 0.9 and both neighbouring TMCs report.
     - A missing segment while its neighbours flow is the closure signature. Harris County work used null speeds as the inundation label and
       < 10 % of historical speed for prediction (arXiv 2104.02276).
  3. Exclude epochs within 1 km and 2 h of a crash or work-zone event (MassDOT events, IMPACT crashes).
  4. Require the rain condition: MRMS 1 h > 15 mm within 5 km.
  5. **Negatives**: `v ≥ 0.8·v̄` throughout the storm with c ≥ 0.8. These are confident "not closed".
  6. Duration = first to last flagged epoch.
- **Yield:** maybe 1–3 closure segments per storm on NHS, so +20–60, but **thousands of true-negative segment-storms**. That enables CSI and
  precision on an "NHS complete domain".
- **Effort:** 4–6 days, plus 1–4 weeks to get access.
- **Risks:**
  - Night-time sparsity.
  - Congestion from rain alone gives speed drops without closure: use the < 25 % rule and duration.
  - TMCs are 0.5–5 km long. Map them to our segments by overlap and keep only TMC-level matching.

**(9) INRIX XD / HERE / TomTom arterial probe data** — commercial.
- The Eastern Transportation Coalition's marketplace sells it to member agencies.
- I could not verify that MassDOT holds an arterial-level license.
- Ask MassDOT and CMRPC whether they hold XD-level data in RITIS. If yes, the item-8 algorithm extends to most arterials. Otherwise skip it: the
  academic price is unverified and likely high.

**(10) RITIS event archive.** If MassDOT pushes its HOC events into RITIS, the archive goes back years. That is unverified for MA. It is the same
ask as item 13.

**(11) MassDOT continuous count stations** (MS2 Transportation Data Management System; CMRPC points there)
- **G:** L (weak).
- **Transform:** hourly volume below 30 % of the same hour-of-week median during the storm, with an adjacent station normal → disruption.
- **Yield:** low. There are few stations in D3, mostly on interstates. **Effort:** 1 day. Use it as a sanity check for NPMRDS, not as a primary
  source.

**(12) MassDOT GoTime travel times, traffic cameras, 511 events** (verified on mass.gov "Highway data for developers")
- **Access:**
  - GoTime third-party API: free, with a signup form.
  - Cameras: JPEG stills, 1 frame per 120 s, through TrafficLand (sales@trafficland.com).
  - The roadway-events XML is already logged by `events_log.yml`.
- **Archive:** none public. All of this is **forward only**.
- **Plan:**
  - Add GoTime to the storm-gated logger (§4).
  - Camera stills: ask TrafficLand or MassDOT for research access, and save stills from D3 cameras every 2 min during warnings. Over time that
    makes a labelled "water on road" image set. The labelling is manual at first. No useful history.

### 2.3 Crowdsourced

**(13) Waze alerts, historical** (verified that MassDOT has been a partner since June 2016)
- **Background:**
  - Waze partners receive a data feed refreshed every 2 min. Alerts carry type/subtype (`WEATHERHAZARD`/`HAZARD_WEATHER_FLOOD`), street,
    location, `pubMillis`, `nThumbsUp`, a `reliability` score (0–10) and a `confidence` score (−1 to 5). An alert with 2 "Not there" and no thumbs
    drops to −1 and disappears.
  - Partners can also query "over a year" of history in BigQuery.
- **Evidence it works for exactly our miss class:**
  - Dallas got 5,652 flood alerts in 23 months through its COG partner. They clustered at local surface depressions, not in river flood zones
    (Safaei-Moghadam et al. 2023).
  - A Norfolk study judged 72 % of Waze flood reports trustworthy.
- **Access paths, in order:**
  1. **Ask MassDOT** whether the Highway Operations Center or the data office archived its Waze feed. Request all `WEATHERHAZARD` flood and
     `ROAD_CLOSED` alerts inside District 3, 2018–2026.
  2. Any D3 municipality that is a partner can export its BigQuery history (about a year back). That would cover aug2026.
  3. Join the forward logger (§4).
- **Transform:**
  1. Keep flood alerts with reliability ≥ 5, or ≥ 1 thumbs up.
  2. Cluster within 100 m and 30 min.
  3. Drop bridges and elevated roads.
  4. Each cluster becomes a site with time = first `pubMillis`.
  5. Negatives: heavily travelled segments with Waze jams/traffic but no flood alert during the burst. These are weak, so use them as PU
     unlabelled data, not as negatives.
- **Yield:** potentially hundreds if MassDOT archived it. **Effort:** 3 days to parse.
- **Risks:**
  - Driver-density bias, though it is a *different* bias from the LSRs, so combining them helps the propensity model.
  - Terms: partner data must not be redistributed. Publish derived labels only.

**(14) mPING** (NSSL/OU) (license page verified)
- A research license gives the database minus the last 48 h. Apply via `https://mping.ou.edu/static/mping/access.html`.
- The flood categories (for example street flooding, road closed, vehicles stranded) need checking in the API menu.
- **Yield:** probably a handful per storm in central MA. mPING use is winter-heavy.
- **Effort:** 1 day once the token arrives. Cheap, so do it.

**(15) CoCoRaHS Significant Weather / Intense Precipitation reports** (`https://www.cocorahs.org/ViewData/ListIntensePrecipReports.aspx`; verified)
- Observers file them for ≥ 1 in/h or ≥ 2 in, often with flooding comments.
- Worcester County has at least 35 active stations, and flood reports "are immediately shared with NWS".
- **Uses:** (i) a time-stamped intense-rain gauge for T12 rain checks; (ii) occasional road-flooding comments.
- **Yield:** low for labels, useful for rain. **Effort:** 0.5 d.

**(16) Facebook pages of town police, fire and DPW**
- These post "Road X closed due to flooding" with timestamps for nearly every storm.
- **Access:**
  - The **Meta Content Library** (public Pages, groups and posts) is for researchers at qualified institutions. You apply through ICPSR/SOMAR and
    analyse in the SOMAR Virtual Data Enclave, where outputs are reviewed. Fees are unverified.
  - Manual viewing of the same pages is the low-tech alternative.
- **Transform:** search page posts for each storm date with `flood|closed|impassable|washout` → road, time.
- **Yield:** high in principle (+50–150), and it reaches towns that never feed the NWS.
- **Effort:** application 4–12 weeks; then 2–3 days.
- **Risks:** no automated scraping (Meta ToS). Store no personal data.

**(17) Reddit (r/WorcesterMA, r/massachusetts)**
- Historical dumps exist (Arctic Shift).
- **Yield:** tiny and mostly duplicates the news. **Skip,** except as a check on one storm.

**(18) YouTube/TikTok storm videos**
- They are geolocatable by title and landmarks.
- Labour per site is high (30–60 min) and the yield low. Use them only to add depth evidence at existing sites (photos of water depth on cars help
  the DV rule).

**(19) X/Twitter, Nextdoor, Ring Neighbors.** The X API costs thousands of dollars a month at the useful tier. Nextdoor and Ring have no research
access. **Skip.**

**(20) Broadcastify scanner audio** (verified: archives are kept up to 365 days)
- Only storms after about Oct 2025 are reachable, so **aug2026 and future storms**.
- Speech-to-text on the Leominster/Fitchburg police and fire feeds for 3 Aug 2026 would give closure and reopen times.
- **Risks:** premium subscription; personal names on air (store only road and time); unclear redistribution terms.
- **Effort:** 2 days for one storm. Optional.

### 2.4 Municipal and agency records (public records requests)

**MA Public Records Law, in practice** (G.L. c. 66 §10, 2016 reform; verified):
- **Response:** within 10 business days. If an exception applies, up to 15 more for state agencies or 25 for municipalities. Further extensions
  only from the Supervisor of Records.
- **Fees:**
  - copies ≤ $0.05/page;
  - search time free for the first 4 h at state agencies and the first 2 h at municipalities over 20,000 people (smaller towns may charge from
    hour one);
  - labour ≤ $25/h;
  - no fees if the 10-day deadline is missed;
  - a good-faith estimate is required.
- **Format:** electronic copies on request.
- **How to file:**
  1. Email the town's Records Access Officer (listed on every town site).
  2. Ask for **electronic, existing records** (no new compilation), a date-limited window and named fields.
  3. Ask for redaction of personal data and a fee estimate first.
- **Writing it:** short, numbered requests per storm get faster answers than one 8-year request.

**(21) Police/fire CAD logs**
- **Ask:** all calls for storm windows (dates in `catalog.json`) whose type or narrative matches flooding, water in roadway, road closure,
  vehicle stuck in water, washout or catch basin. Fields: time received, time cleared, location, type, disposition.
- **Towns:** Worcester PD/FD first (largest domain), then Leominster, Fitchburg, Shrewsbury, Auburn, Millbury, Oxford, Webster, Gardner and
  Holden.
- **Transform:** as item 4.
  - The CAD log of a town for a storm day is **near-complete for that town**. Define a "CAD-complete domain" there and score CSI and precision
    inside it (ROADMAP T1).
- **Yield:** +100–300 sites with times. **Effort:** 1 day to file, 3–4 days to parse. **Elapsed:** 2–6 weeks.
- **Risks:** CAD exports are messy; personal data (ask for redaction); the location field is sometimes "area of".

**(22) DPW work orders and catch-basin complaints** (Worcester DPW&P, Leominster, Fitchburg)
- Worcester's open-data front page shows a daily DPW&P work-order ticker, so a work-order system exists. Ask for orders on storm dates and the
  following 3 days with categories flooding, drainage, catch basin, washout, road damage, barricade.
- **Transform:**
  - An order created during or after the storm becomes a site.
  - Barricade/closure orders give durations.
  - Damage orders become `washout`/`culvert_failure` labels for T7.
- **Yield:** +20–80. **Effort:** 2 days.

**(23) Worcester 311** (launched July 2023; verified)
- Case status is "visible to public" in the app. No 311 open dataset was confirmed on `opendata.worcesterma.gov` (300+ datasets). I could not
  search the portal from here; check it by hand.
- **Ask:** an export of 311 cases, July 2023–present, in categories street flooding, catch basin, drainage, pothole/road damage, with created
  time, address and closed time.
- **Storms covered:** jul2023 (14 Jul 2023, three days after launch), aug2023b, the excluded single-site storms (24 Jun 2024, 29 Jul 2026), and
  all future storms.
- **Yield:** +10–40 per Worcester storm.

**(24) Damage inventories filed for the Sept 2023 disaster request** (MEMA and towns)
- FEMA-4780-DR (11–13 Sept 2023) gave Individual Assistance to Bristol and Worcester counties. **Public Assistance was requested for Hampden and
  Worcester and denied**, and the appeal was denied on 28 May 2024 (FEMA letter).
- So OpenFEMA has **no PA project worksheets** for this storm. But towns built site-by-site damage inventories for the request, with MEMA's help
  ("MEMA responded to seven communities").
- Leominster's `FlashFloodDamage` layer, "all flagged eligible for federal aid", is one of them.
- **Ask MEMA** (the regional office covering Worcester County) for the municipal damage-assessment submissions for 11–13 Sept 2023: town, site
  description, location and estimated cost.
- **Then ask the towns** for their GIS layers: Fitchburg, Lunenburg, Westminster, Sterling, Lancaster, Princeton and others.
- **Caveat:** sep2023 is a **dev** storm. These labels add *new towns and complete domains*, not new held-out storms. Use them for T7
  (damage fragility), CSI in complete domains and the propensity model.
- **Yield:** +50–150 points. **Effort:** 1 day of requests, 2 days of processing.
- Repeat the same ask for any later declared event.

**(25) School-bus delays, WRTA/MBTA detours, utility outages**
- WRTA detour notices on its website and social media are day-level and route-level.
- MBTA Fitchburg- and Worcester-line disruptions are rail, not road.
- Outages are wind-driven.
- **Low value. Skip,** except WRTA detours for Worcester storms as a cross-check.

**(26) Tow records** (towing companies are private; police tow logs come with CAD). They are covered by item 21.

### 2.5 Physical evidence and remote sensing (mostly honest "no")

| source | verdict | reason |
|---|---|---|
| USGS STN high-water marks | **no for D3 2018–2026** | the repo's `docs/validation/stn_ma.json` (1,866 MA marks) has only 2010 marks near D3; the July 2023 event is western MA/VT |
| FEMA PA (OpenFEMA) | **no for sep2023** (PA denied) | `PublicAssistanceFundedProjectsDetails` is county-level only anyway, with no site location |
| FEMA IA by ZIP (DR-4780) | weak town/ZIP check | 971 households approved in two counties; ZIP counts for the sep2023 box; not roads |
| NFIP claims (OpenFEMA v2) | weak block-group check | see `data_sources.md` 4.1; useful for the "over-wet" test only |
| Sentinel-1 / GFM / OPERA DSWx-S1 | **no** | 6–12 day revisit; flash floods drain in hours; urban and forest exclusion; the Prithvi study IoU ≈ 4 % in built-up areas |
| Planet (Education & Research Basic) | **marginal** | any university-affiliated researcher may apply; PlanetScope roughly daily at 3 m; a cloudy morning-after image may show *debris and washouts* (sep2023 Leominster, Wachusett St) but not standing water. Try one storm only |
| NOAA emergency-response aerials | **no** | flown for hurricanes and major coastal events, not MA flash floods |
| Google Street View history | **no for labels** | irregular dates; useful only to read inlet presence and kerb type (inputs, below) |
| First Street flood data | **inputs/benchmark only** | modelled risk, not observations; academic access by request; licensing restricts redistribution |
| NAACC / MassDOT culvert and bridge inspections | inputs | already planned (`data_sources.md` 5.1–5.2); MassDOT inspection reports by request for T7 |

### 2.6 Better model inputs from real data

**(27) MRMS FLASH products** (verified that the products exist and are distributed to NWS; the AWS archive needs a check)
- **Products:**
  - CREST **maximum unit streamflow**: 1 km, 10 min, max over the next 12 h, normalised by basin area. In the Houston example, values above
    2 m³/s/km² marked broad flooding and above 10 m³/s/km² localised severe flooding.
  - **QPE average recurrence interval (ARI)**.
  - **QPE-to-FFG ratio**.
- **Use:** as features (`flash_qmax_upstream`, `qpe_ari_1h`, `qpe_ffg_ratio`) at each segment's upstream crossing. These are the NWS's own
  flash-flood indicators and directly target the "light convective storm, model dry" failure of the 16 new storms.
- **Check:** list `s3://noaa-mrms-pds/CONUS/` from Actions for `FLASH_*` prefixes. The sandbox proxy blocks S3 here. If there is no archive
  (only LDM), compute ARI ourselves from MRMS QPE and NOAA Atlas 14.
- **Effort:** 2–3 days.

**(28) NOAA Atlas 15** (verified): CONUS preliminary estimates "no earlier than September 2026", published ones "no earlier than September 2027".
Use Atlas 14 (PFDS) for the ARI feature now and swap later. Atlas 15 also adds 5-min durations, which suit i(Tc) (ROADMAP T3).

**(29) MassDOT Road Inventory geometry fields** (verified in the data dictionary)
- Fields: `Curb` (0 none … 3 both sides, 5 all curbs), shoulder type and width (`Shldr_Rt_T`, `Shldr_Rt_W`), `Surface_Wd`, `Med_Type` (7 =
  depressed median).
- Kerbed roads with no shoulder hold gutter flow on the carriageway; earth shoulders erode (washouts).
- **Use:** as features for T5 and the edge/washout layer. They are free and statewide, and probably the cheapest physics proxy for RECALL class B/E.
- **Effort:** 1 day.

**(30) Catch-basin and inlet inventories**
- Leominster has provided its network.
- Worcester and others: under the 2016 MA MS4 general permit, towns must map their full storm-drain systems, including catch basins, on a
  multi-year schedule. Ask the DPW engineering divisions for the GIS layer. **Mapillary** point detections (40 point classes, free API) are the
  crowd alternative. Whether they include catch basins is unverified, so check the points list.
- **Use:** inlet density per segment for the HEC-22 capacity in pluvial rule v2 (T3), instead of "one inlet per 100 m".

**(31) Dense rain gauges**
- Weather Underground PWS: its API is now restricted to contributors. **Synoptic Data** (MesoWest) aggregates CWOP and other networks; it offers a
  14-day trial, an Open Access programme for eligible students, and paid tiers.
- Also IEM ASOS 1-min and CoCoRaHS (item 15).
- **Use:** T12 merging diagnostic only. The PWS quality control burden is high.

**(32) MassDEP sewage-overflow notifications** (314 CMR 16)
- Permittees must post public notifications of CSO/SSO events, with incident date, time and location. MassDEP says reports "can be viewed on the
  public database". I could not confirm the URL.
- **Use:**
  - a **time-stamped indicator that a town's drainage system surcharged** (Fitchburg CSOs, SSOs in Worcester, Leominster, Webster and Uxbridge);
  - a diagnostic for drains v2 (T9) and a feature `sso_in_town_during_storm` for the real-time update (T8). It covers events since about 2022.

## 3. Closed-loop Waze pilot with a District 3 town (Leominster DPW)

**Idea.** Norfolk, VA (with FloodMapp, a RISE challenge winner) has published model-predicted flooded road segments into Waze as flood hazard
icons since October 2021. Since then:
- Waze users have **confirmed more than 4,300 predicted flooded roads**;
- they have given **about 9,500 thumbs-ups** (mean 2.2 per hazard, maximum 72);
- the city and FloodMapp use these as ongoing validation (Esri ArcNews; GovTech; Newswire, Jan 2022).

We would do the same for District 3. **Driver confirmations and "Not there" denials become labels, including the false-alarm labels we lack.**

**Feed format** (verified, Waze CIFS spec):
- XML (JSON is also accepted per the partner-feed overview).
- **Required:** a stable `id`, `type`, a `polyline` (space-separated "lat lon" pairs, ≥ 6 decimals, ordered in the travel direction), `street`, and
  `starttime` (`yyyy-MM-dd'T'HH:mm:ss+HH:mm`).
- **Recommended:** `subtype`, `direction` (`BOTH_DIRECTIONS`), `endtime` (default 14 days, so **always set it**), and `description` (≤ 40 characters).
- **Use** `type=HAZARD`, `subtype=HAZARD_WEATHER_FLOOD`. This shows an icon and pop-up alerts but **does not change routing**.
- **Do not use `ROAD_CLOSED`.** It removes the road from routing, which would turn a forecast into an operational closure.
- Waze validates the feed when the partner submits the URL in the Partner Hub. The Waze Partners team then reviews it, and the feed is "automatically fetched".
- NCDOT's lesson: there is **no test environment**. Waze ran test closures on minor roads, and drawing or time errors closed real roads.

**Who must own it.**
- Eligibility is "a government agency or a private road operator". A university is not listed.
- So **the City of Leominster (or MassDOT) must own the Waze for Cities account** and submit the feed URL.
- We host the feed: a static `docs/waze/leominster.xml`, written by `forecast.yml` only when the gate fires. The city can switch it off in the
  Partner Hub at any time.
- The same account gives the city the 2-min data feed and BigQuery history. It may share access with us (a colleague can be added to the
  BigQuery project).

**Liability and approval** (for the city to decide; not legal advice):
1. **Phase 0, shadow (no publishing).** We log what we *would* publish for 1–2 storms and compare it with the city's own knowledge.
2. **Phase 1, human in the loop.** The DPW or emergency-management duty officer approves each batch, with one click on a page we host.
   - Text: "Possible street flooding (forecast)".
   - Hazards only, never closures.
   - `endtime` ≤ 3 h, and only the top-ranked segments (≤ 15 per storm).
3. **Phase 2, automatic** at the "likely closed" tier only, if phase 1 precision is acceptable.

A written MOU should cover data use (research only, no raw Waze data published) and an off-switch. City counsel should review. The
Massachusetts Tort Claims Act (G.L. c. 258 §10) has exemptions for discretionary functions and for failure to prevent harm. Whether they cover
a forecast advisory is a question for counsel, not us.

**Logging confirmations.**
1. With the city's data-feed URL (a secret in Actions), poll every 2–5 min while the gate is on and for 6 h after.
2. Store each alert's `uuid`, `type/subtype`, `street`, `location`, `pubMillis`, `reliability`, `confidence`, `nThumbsUp` and `reportDescription`, as
   a time series.
3. Match our hazards by id or location (≤ 50 m).
4. Assign labels:
   - **Confirmed:** ≥ 1 thumbs up or comment, or an independent user flood alert within 150 m and ±60 min.
   - **Denied:** removed early with confidence −1 (that is, 2 × "Not there"). Confirm whether partner hazards can be removed this way; ask the
     Waze Partners team.
   - **No reaction:** censored. Weight by exposure, using Waze jams or AADT.
5. Ask Waze for the per-hazard reaction counts they gave Norfolk. The partner feed may not show "Not there" counts directly.

**Expected label volume.** Norfolk floods tidally dozens of times a year. Leominster (about 43k people) has perhaps 2–5 road-flooding storms a
year. Assume up to 15 hazards per storm and 30–60 % with any reaction (unverified for a city this size). That gives **roughly 10–40 labelled
hazards per year, including denials**, so tens per year, not hundreds. That is too slow to be the main training source. Its value is:
(i) **real false-alarm labels**; (ii) a real-time outcome stream for T8; (iii) a demonstrable "warning → driver feedback" loop for the
dissertation and for funders. Partnering a second town (Worcester, which has more traffic) would roughly triple the volume.

**Effort:**
- CIFS writer from the forecast output: 1 day.
- Approval page: 1 day.
- Data-feed logger: 1 day (shared with §4).
- Matching and labels: 1–2 days.
- City onboarding: weeks.

**Pitch email to Leominster DPW:** see §6, email 6.

## 4. Public Waze layers in Massachusetts, and a storm-gated logger

**Search result.** Some partners republish their Waze feed as a public ArcGIS service, for example:
- Baton Rouge `maps.brla.gov/.../Transportation/Waze_Alert/MapServer`, "refreshed every two minutes", live only;
- Virginia Beach;
- Delaware DelDOT `DE_TMC_Traffic_Feeds` (WAZE Alerts layer);
- Charleston (internal);
- DC (`Waze_Data`, which now returns "Service not found");
- a FEMA partner service, `gis.fema.gov/arcgis/rest/services/Partner/WAZE_Reports/MapServer`. Its extent and fields could not be read from here,
  and it may be national.

**I found no public Waze layer covering Massachusetts** (MassDOT, Worcester, Boston, CMRPC, MRPC, MAPC or a town), by web search. The
sandbox proxy blocks arcgis.com, so the authoritative check is the discovery job below. Esri's "Waze Live Alerts data pipeline" lets a partner
write alerts to an ArcGIS layer every 15 min or less, with a retention policy. **A partner that already uses ArcGIS could turn on history in
minutes.** That is worth asking MassDOT and Worcester.

**Plan: `.github/workflows/waze_log.yml`** (same pattern as `events_log.yml`, which already runs at `7,22,37,52 * * * *`):

1. **Discovery (manual dispatch, run once a month):**
   - query `https://www.arcgis.com/sharing/rest/search?q=waze AND (massachusetts OR worcester OR leominster OR fitchburg OR massdot OR boston)&f=json&num=100`
     and keep Feature/Map services;
   - query `gis.fema.gov/.../Partner/WAZE_Reports/MapServer?f=pjson` and `/0/query?geometry=<D3 bbox>&geometryType=esriGeometryEnvelope&inSR=4326&where=1=1&outFields=*&returnCountOnly=true&f=json`;
   - write `docs/proto/obs/waze/sources.json` listing URL, fields, extent and count in D3.
2. **Gate (every 5 min; exits within 10 s when off):** on if any of these holds, and kept on for 6 h after the last one:
   - `api.weather.gov/alerts/active?area=MA` has a Flash Flood Warning or Flood Advisory whose polygon intersects `D3_BOX`;
   - our live forecast gate (`docs/live.json`) is ≥ "watch" for any D3 box;
   - MRMS Pass1 shows > 20 mm/h in D3.
3. **Snapshot when the gate is on.** For each source in `sources.json`, plus the partner data feed if a partner shares one (URL in a repo
   secret), plus GoTime:
   - query alerts in the D3 bbox, keeping `type`, `subtype`, `street`, `city`, `pubMillis`, `uuid`, `reliability`, `confidence`, `nThumbsUp`
     and the geometry;
   - append changed records to `docs/proto/obs/waze/YYYY-MM.jsonl`, with `seen.json` holding first-seen, last-seen and the thumbs series;
   - an alert that disappears gets `gone_at`.
4. **Storage and terms:**
   - keep raw partner-feed records in a **private** repo or branch (partner terms; attribution required);
   - publish only derived site labels (`labels_<storm>_waze.csv`: road, time first seen, last seen, max thumbs, confidence).
5. **Cadence caveat:** GitHub cron runs at best every 5 min and is often 5–15 min late. A 2-min source will miss short-lived alerts. Acceptable
   for labels (alerts usually live 30+ min); for Phase 2 of §3, use a small always-on runner instead.

## 5. People and organisations to contact

| who (role) | what to ask | why them |
|---|---|---|
| **MassDOT Highway Operations Center / Traffic Operations (data and ITS)** | archived Waze partner alerts and HOC/511 event logs with "flood", D3, 2018–2026; whether events go to RITIS | MassDOT has been a Waze partner since 2016 and runs the HOC; the repeat-flood list in `proto/data/massdot_repeat_flood_d3.csv` implies they log durations |
| **MassDOT District 3 (Worcester) maintenance and operations engineer** | district flood-closure logs, maintenance work orders, drainage complaint lists | they wrote the repeat-flood list |
| **MassDOT Office of Transportation Planning, data/performance group** | NPMRDS/RITIS account sponsorship for a WPI researcher; whether XD-level data exist | MassDOT uses NPMRDS as its primary travel-time source |
| **CMRPC transportation data staff** (Deputy Executive Director, Transportation, listed on the CMRPC data page) and **MRPC transportation staff** | RITIS/NPMRDS access through the MPO; their count programme; HMP flood-location tables they wrote | MPOs get NPMRDS when the state licenses it; CMRPC and MRPC wrote most D3 HMPs |
| **Records Access Officers**: Worcester PD, FD, DPW&P, 311; Leominster, Fitchburg, Shrewsbury, Auburn, Millbury, Oxford, Webster, Gardner, Holden | CAD extracts for storm windows; DPW work orders; 311 cases | legal right of access; near-complete per town |
| **MEMA, regional office covering Worcester County** | municipal damage-assessment submissions for 11–13 Sept 2023 (FEMA-4780-DR request) and other events | complete inventories like Leominster's |
| **NWS Boston/Norton Warning Coordination Meteorologist** | raw spotter and EM reports not in LSRs; storm-data drafts; whether WX1BOX logs are archived; interest in verifying our forecasts | they own the LSR pipeline and the SKYWARN relationship |
| **WX1BOX SKYWARN coordinators** | an index of all `reports_*.pdf` compilations since 2018, and permission to cite | the compilations hold extra sites |
| **Southern New England CoCoRaHS state coordinators** | export of Significant Weather and intense-rain reports for D3, 2018–2026 | time-stamped intense-rain reports |
| **City of Leominster DPW / City Engineer** (existing contact) | the Waze pilot (§3); Waze for Cities account status; DPW work orders and closure durations for aug2026 | already shares data; frequent flash floods |
| **UMass Transportation Center / MassDOT Research Section** | a MassDOT Project Champion for a research problem statement ("probe- and crowd-based flood-closure detection"); the spring solicitation | an academic needs a MassDOT Project Champion to submit; this is how a funded project starts |
| **WPI Worcester Community Project Center** | an IQP team to run the Worcester records requests and NewsBank and Facebook reading for 25 storms | cheap, well-suited student labour |
| **Northeastern / BU urban-flood and mobility researchers** | shared Waze or probe datasets for MA; co-authorship | they may already hold MA Waze or probe data |

## 6. Ready-to-send emails (top 5 contacts, plus the Waze pitch)

Each is 4–6 lines. Replace the bracketed items.

**1. MassDOT Highway Operations Center, Traffic Operations data team**
> Subject: Research request: archived flood-related events and Waze alerts, District 3, 2018–2026
>
> I am a WPI PhD student (Civil & Environmental Engineering; advisors Profs. Tao, Albano and Graff) building a flash-flood road-closure forecast
> for District 3, and my validation data are the main bottleneck. Does MassDOT keep (a) HOC/511 event records whose description mentions
> flooding, water or washout, and (b) an archive of the Waze partner alerts (WEATHERHAZARD/flood and ROAD_CLOSED) for District 3 towns,
> 2018–2026? I would use them only for model validation, publish only aggregated results, and share the findings with MassDOT. If this is
> better handled as a public records request, I am happy to file one. [Name, WPI email, phone]

**2. CMRPC (and MRPC) transportation data staff**
> Subject: NPMRDS/RITIS access for a WPI flood-closure study in Central Massachusetts
>
> I am a WPI PhD student developing a flash-flood road-closure forecast for Worcester County. I want to use 5-minute NPMRDS speeds to detect
> past closures, and confirmed open roads, during about 25 storms since 2018. Could CMRPC sponsor a RITIS/NPMRDS account for this research, or
> run a short extract for listed storm dates? I would also value your HMP "locally identified flooding" tables in digital form. I will share
> results that could support your hazard-mitigation and CMP work. [Name, contact]

**3. Records Access Officer, City of Worcester (template for other towns)**
> Subject: Public records request: police/fire dispatch entries for flooding on specific storm dates
>
> Under G.L. c. 66 §10, I request electronic copies of existing CAD/dispatch records for the dates and times listed below, limited to calls
> whose type or narrative involves flooding, water in the roadway, road closure, vehicles stuck in water, washouts or catch basins. Fields: time
> received, time cleared, location, call type, disposition. Please redact personal information. This is for non-commercial WPI research on
> flood warnings. Please send a fee estimate before any work beyond the free hours. [Date list; name, address, email]

**4. MEMA, regional office covering Worcester County**
> Subject: Municipal damage assessments, 11–13 Sept 2023 storm (FEMA-4780-DR), for flood-model validation
>
> I am a WPI PhD student validating a road-flooding forecast for Central Massachusetts. The City of Leominster kindly shared its site-level
> damage inventory from the September 2023 storm. Could MEMA share, or point me to, the municipal damage-assessment submissions (town, site
> description, location, estimated cost) for Worcester County communities from that event and any later flood events? Only aggregated or
> anonymised results will be published, and I will share the analysis with MEMA. [Name, contact]

**5. NWS Boston/Norton Warning Coordination Meteorologist (cc WX1BOX SKYWARN coordinators)**
> Subject: Road-flooding reports for Central MA verification: spotter/EM reports and WX1BOX compilations
>
> I am a WPI PhD student building a road-level flash-flood forecast for MassDOT District 3, verified against your LSRs. The WX1BOX
> compilations contain road reports that are not in the LSRs. Is there an archive of these compilations, or of raw spotter and EM reports, for
> 2018–2026 that I could use with attribution? I would gladly share verification results, which may help with warning polygons. [Name, contact]

**6. City of Leominster DPW / City Engineer: Waze pilot**
> Subject: Pilot proposal: forecast street-flooding alerts in Waze, with driver feedback
>
> Thank you again for the September 2023 damage data, which already improved our flood model. Norfolk, VA publishes model-predicted flooded
> streets to Waze as flood-hazard icons (not closures). Drivers have confirmed over 4,300 of them since 2021, which validates the model. I
> propose a small Leominster pilot:
> - the city's Waze for Cities account points to a feed we host;
> - only "possible street flooding" hazards are shown, each lasting at most 3 hours, after one-click approval by your duty officer;
> - we log driver confirmations to improve the forecast;
> - there is no cost to the city, and the city can switch the feed off at any time.
>
> Could we meet for 30 minutes to discuss? [Name, contact]

## 7. What will not work, or is not worth it now

- **Satellite flood maps** (Sentinel-1, GFM, OPERA, Planet) for street flash floods. At most, Planet may show washout scars after sep2023.
- **USGS STN**: no D3 marks 2018–2026.
- **OpenFEMA PA for Sept 2023**: denied, so no worksheets. Go to MEMA and the towns instead (item 24).
- **X/Twitter, Nextdoor, Ring**: cost or no access.
- **Reddit and YouTube** at scale: tiny yield per hour.
- **Utility outage maps and MBTA alerts**: not road flooding.
- **Commercial arterial probe data** (INRIX XD/HERE) without an agency licence: unverified academic price, likely high. Ask MassDOT first.
- **Using HMP "flood-prone" lists as scoring labels**: undated and opinion-based. Use them only as priors or propensity.

## 8. Suggested order of work

1. **This week (no permissions needed):** WX1BOX and multi-street LSR split (item 1); IMPACT code-6 crash pilot (item 2); posted dispatch logs
   (item 4); Road Inventory curb fields (item 29); MRMS FLASH archive check (item 27); `waze_log.yml` discovery run (§4).
2. **Send now (they take weeks):** emails 1–5; records requests to Worcester and 4–6 more towns; the mPING research licence; the Leominster
   pilot meeting.
3. **When data arrive:** NPMRDS closure and negative extraction; CAD-complete domains in T1 scoring; SAR-PU propensity built from the mix of
   source types (NWS, crash, CAD, Waze have different biases); then re-score held-out storms with the new sites, with no rule changes first.

## Sources

- Waze CIFS specification: https://developers.google.com/waze/data-feed/cifs-specification ; partner feed overview: https://developers.google.com/waze/data-feed/overview
- Waze data feed fields, reliability and confidence, 2-min refresh: https://support.google.com/waze/partners/answer/10618035 ; tools: https://support.google.com/waze/partners/answer/10618047 ; eligibility: https://support.google.com/waze/partners/answer/10453062 ; BigQuery history: https://support.google.com/waze/partners/answer/10715739
- Norfolk/FloodMapp Waze: https://www.esri.com/about/newsroom/arcnews/real-time-flood-intelligence-helps-coastal-city-build-resilience ; https://www.newswire.com/news/rise-challenge-winner-floodmapp-launches-integration-with-waze-to-help-21595349 ; https://govtech.com/analytics/norfolk-va-offers-real-time-flood-data-to-drivers
- NCDOT automated Waze closures (lessons, no test environment): https://connect.ncdot.gov/groups/NCSTIC/STIC%20Projects/STIC%20Incentive%20Final%20Report%20-%20Automating%20Waze%20Road%20Closures.pdf
- MassDOT–Waze partnership (2016): https://www.wbur.org/news/2016/06/16/massdot-waze-partnership
- Public Waze ArcGIS layers: https://maps.brla.gov/gis/rest/services/Transportation/Waze_Alert/MapServer ; https://geo.vbgov.com/mapservices/rest/services/Public_Safety/Waze_Road_Alerts_and_Traffic_Jams/MapServer ; https://enterprise.firstmaptest.delaware.gov/arcgis/rest/services/Transportation/DE_TMC_Traffic_Feeds/MapServer/0 ; https://gis.fema.gov/arcgis/rest/services/Partner/WAZE_Reports/MapServer/layers ; Esri pipeline: https://www.esri.com/arcgis-blog/products/arcgis-solutions/announcements/introducing-the-waze-live-alerts-data-pipeline
- Waze flood studies: Safaei-Moghadam et al. 2023, https://nhess.copernicus.org/articles/23/1/2023/ ; Norfolk trustworthiness, https://par.nsf.gov/biblio/10291591
- NPMRDS: https://inrix.com/blog/transportation-agencies-use-npmrds/ ; IEEE NTDAS: https://innovate.ieee.org/ntdas/ ; MassDOT use of NPMRDS: https://ops.fhwa.dot.gov/trafficanalysistools/pdfs/CaseStudy_FHWA-HOP-21-066_MA_20230309.pdf ; Harris County probe-speed inundation: https://arxiv.org/pdf/2104.02276
- CMRPC data: https://cmrpc.org/transportation/transportation-planning-areas/traffic-and-travel-data-collection/
- MassDOT developer feeds (GoTime, cameras via TrafficLand, events, WZDx): https://www.mass.gov/info-details/highway-data-for-developers
- MA crash report manual, road surface codes: https://masscrashreportmanual.com/crash/road-surface/ ; IMPACT portal help: https://apps.impact.dot.state.ma.us/helpcdp/topics/idh-topic110.htm
- MassDOT Road Inventory data dictionary: https://www.mass.gov/doc/road-inventory-data-dictionary/download
- WX1BOX compilations: https://wx1box.org/wp-content/uploads/2026/08/reports_8_3_26.pdf ; https://wx1box.org/wp-content/uploads/2023/07/reports_7_10_23.pdf ; NWS LSR summary example: https://wx1box.org/wp-content/uploads/2023/08/LSR_8_18_23.pdf
- IEM AFOS text archive: https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?help
- mPING access and licence: https://mping.ou.edu/static/mping/access.html ; https://mping.ou.edu/license.html
- CoCoRaHS intense-precipitation reports: https://www.cocorahs.org/ViewData/ListIntensePrecipReports.aspx ; SNE newsletter: https://media.cocorahs.org/docs/MA%2FSummer%202026%20SNE%20CoCoRaHS%20Newsletter.pdf
- Worcester 311 launch: https://worcesterma.gov/announcements/worcester-launches-311-application-for-non-emergency-requests ; open data portal: https://www.worcesterma.gov/announcements/worcester-revamps-open-data-portal
- South Worcester County Communications Center log (Dudley): https://www.dudleyma.gov/Archive.aspx?ADID=93
- MA Public Records Law 2016 reform: https://www.muckrock.com/news/archives/2016/jul/01/whats-massachusetts-updated-public-records-law
- Meta Content Library via ICPSR: https://www.icpsr.umich.edu/sites/icpsr/news/icpsr-to-facilitate-researcher-access-to-metas-api-products
- Broadcastify archive retention: https://support.broadcastify.com/hc/en-us/articles/24128795860379-Audio-Archive-Retention-and-Use
- FEMA-4780-DR: https://www.fema.gov/disaster/4780/news-media ; PA denial letter: https://www.mma.org/wp-content/uploads/2024/05/FEMA-PA-Denial-letter.pdf ; state release: https://www.mass.gov/news/healey-driscoll-administration-celebrates-federal-disaster-assistance-for-communities-impacted-by-september-storms ; OpenFEMA PA projects fields: https://www.fema.gov/openfema-dataset-public-assistance-funded-projects-details-v1
- Hazard mitigation plans: https://www.worcesterma.gov/communications/document-center/worcester-hazard-mitigation-plan-update.pdf ; https://www.fitchburgma.gov/DocumentCenter/View/13697/Fitchburg-HMP-MVP_Draft-Final_Combined ; https://cmrpc.org/mendon-hazard-mitigation-plan-2017
- MRMS FLASH maximum unit streamflow: https://vlab.noaa.gov/web/wdtd/-/maximum-unit-streamflow ; NSSL FLASH: https://inside.nssl.noaa.gov/nsslnews/2021/09/how-nssl-research-provides-real-time-precipitation-estimations-and-flash-flood-prediction-for-high-impact-events/
- NOAA Atlas 15 status: https://water.noaa.gov/about/atlas15
- Planet Education & Research: https://support.planet.com/hc/en-us/articles/360016570538-How-Can-I-Register-for-the-Education-and-Research-Basic-Program
- Synoptic academic access: https://synopticdata.com/solutions/academic-research/
- MassDEP sewage notification system: https://www.mass.gov/doc/sewage-notification-data-system-instructions-2/download
- Mapillary detections: https://help.mapillary.com/hc/en-us/articles/115000967191
- MassDOT research problem statements (Project Champion rule): https://www.umasstransportationcenter.org/umtc/Problem_Statement_Solicitation.asp
