# Method note: District 3 road-segment flood vulnerability layer

*One page. Mohab Eldokla, WPI (Mass Flood Watch). Files and fields: [README.md](README.md). Code: `proto/arcgis_export.py`.*

**Question.** Which District 3 road segments flood repeatedly in simulated historical storms, and which of those matter most when they do?

**1. Storm simulations.** Each storm is replayed with LISFLOOD-FP 8.2 (local-inertial 2-D shallow-water solver; Bates et al. 2010) on a
20 m grid built from the USGS 3DEP 10 m DEM with NHDPlus HR channels burnt in and road-stream crossings opened. Rain is hourly NOAA MRMS
multi-sensor QPE. Losses are the NRCS curve number (SSURGO soil group, NLCD imperviousness, AMC II) scaled by 0.88, plus 2 mm/h
infiltration. The scale was chosen once, by a pre-set rule, on the two USGS gauges of the Sept 2023 Leominster storm
(`docs/proto/parity/BASELINE.md` §1). Two sets of runs are used, both at these settings:
- the **catalogue**: 25 non-locked District 3 storms from 2018–2026, each on its own box (`docs/proto/parity/catalog/`);
- one **District-wide run** of 11–13 Sept 2023 (78 × 90 km, 48 h, 45,099 segments; `docs/proto/turing/d3_sep2023_p`).
Five older storms are held back as a locked test set (`docs/proto/PROTOCOL.md`) and are not used here.

**2. Per-segment closure probability.** From the modelled peak water depth *d* on the road (second-highest road point of the segment):
p_close = Φ((d − 0.30 m) / 0.10 m). This is combined as 1 − Π(1 − Pᵢ) with three other terms: freeboard (water beside the road above its
crest), culvert overtopping (FHWA HDS-5 headwater over the crest) and fast water (depth × velocity). The thresholds come from the
literature and are not fitted to closures. A segment is **flagged** when p_close ≥ 0.5. It is in the **"may close"** layer when the
stream reaches the road crest (p_may_close ≥ 0.5) and p_close < 0.5.

**3. Repeat-flagging.** For each segment: the number of catalogue storms whose box contains it (`n_cov`), the number that flag it
(`n_flag`), the share (`flag_rate`) and the maximum p_close and depth.

**4. Observations attached.** 320 documented reports for the 25 storms (NWS, NCEI Storm Events, news, WX1BOX, Leominster DPW, MA state,
MassDOT water-surface crashes, SeeClickFix; `proto/data/labels_tiered_<storm>.csv`). Each report with a street-level location goes to its
nearest segment within 30 m (310 assigned). The 38 MassDOT District 3 repeating flood sites go to the nearest segment within 100 m.

**5. Consequence (cascade).** On the Sept 2023 District run, `proto/cascade.py` closes segments at ≥ 30 cm and slows them at 5–30 cm with
the Pregnolato et al. (2017) depth–speed curve. Traffic of each closed stretch is re-routed on the shortest wet path (capped at 30 min).
Delay is integrated over 48 h. The result is the vehicle-hours caused by each segment (`vh_delay`) and the load each dry detour corridor
carries (`peak_vc`). The engine reproduces the published District totals exactly (166,239 vehicle-hours). Loss of emergency-service
coverage is computed per Census block over the network and cannot be assigned to a single segment.

**6. Crossing damage (experimental).** At each road-stream crossing, specific stream power ω = γQS/w is computed from the modelled peak
discharge, the channel slope and the bankfull width. Damage score = logistic(b₀ + b₁ ln(ω/300) + b₂·overtopping), fitted on Leominster
2023 damage reports (`docs/proto/damage/`). The score kept is the maximum over 10 runs, ranked over 4,733 crossings.

**7. Class rule.** First match wins.
- **High:** flagged in ≥ 2 catalogue storms; *or* flagged (catalogue or Sept 2023 District run) *and* carrying a documented report or
  MassDOT site.
- **Medium:** flagged in one catalogue storm; *or* flagged only in the District run; *or* carrying a report or MassDOT site; *or* in the
  "may close" layer at least once.
- **Low:** everything else.

Result: 152 High (102 km), 1,267 Medium (793 km), 47,526 Low. Damage and delay are attached but do not set the class.

**What the evidence supports.** On the parity baseline the depth rule flags about 1 % of segments and catches 41 of 132 documented
sites over 9 storms. Lift is 11.7 on Sept 2023 (`BASELINE.md` §2). Ranking is clearly better than chance; recall is modest. Light storms
are under-predicted. Only 4 of the 38 MassDOT repeating sites are on model-flagged segments, because ponding from undersized drainage
is not resolved. The layer is a **screening and prioritisation aid** for field verification. It is not a closure forecast or a
design flood map.

**References** (as cited in the repository): Bates, Horritt & Fewtrell (2010), J. Hydrology 387; Pregnolato et al. (2017), Transportation
Research Part D 55; FHWA HDS-5 (2012); Magilligan (1992), Geomorphology 5; Anderson et al. (2017), J. Bridge Eng. 22(5).
