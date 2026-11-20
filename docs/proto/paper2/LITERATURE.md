# Paper 2: literature scan for the structural link (road damage, not inundation) — 20 Nov 2026

First scan; each entry read from its abstract or record page (not yet in full). PDFs to go to OneDrive `04_References` only with Mo's OK.

| Work | What it does | Relevance to Paper 2 |
|---|---|---|
| **Mallick, Tao, Daniel, Jacobs, Veeraragavan (2014/15)**, *J. Flood Risk Management*, "Development of a methodology and a tool for the assessment of vulnerability of roadways to flood-induced damage" ([UNH record](https://scholars.unh.edu/faculty_pubs/570)) | System-dynamics model of the time until the unbound base of a flooded asphalt road saturates and the surface layer fails (T_critical); web tool | **Co-authored by Prof. Tao.** The mechanism behind RQ2 (groundwater / subgrade): turns water-table rise and flood duration into a failure time. Natural partner for the groundwater section and for MassDOT pavement data. |
| **Anderson, Rizzo, Huston, Dewoolkar (2017)**, *ASCE J. Bridge Engineering*, "Stream power application for bridge-damage probability mapping based on empirical evidence from Tropical Storm Irene" ([ASCE](https://ascelibrary.com/doi/10.1061/%28ASCE%29BE.1943-5592.0001022), [UVM summary](https://epscor.w3.uvm.edu/2/node/3488)) | 313 bridges (span > 6 m) damaged by Irene in Vermont; specific stream power and event stream power separate damaged from undamaged bridges; empirical fragility curves | **Closest precedent for RQ1**: stream power as a damage predictor in New England, at bridges. RQ1 moves the same idea to road edges at 1 m and tests it against a municipal damage list. Also a template for fragility curves (damage probability vs stream power). |
| Kalantari et al. (2014), *J. Environmental Management*, "A method for mapping flood hazard along roads" ([PubMed 24361730](https://www.pubmed.gov/24361730/); authors to confirm) | GIS catchment descriptors + PCA / PLS at road–stream sites after a severe rain event in western Sweden; key drivers: topographic wetness index, road density, gravel soils, local channel slope | Statistical precedent for predicting road-flood sites from terrain; supports using slope and wetness terms; different outcome (flooding, not damage). |
| **Amaddii, Castelli, Arrighi (2026)**, *Natural Hazards* 122, 108, "Assessing road–watercourse crossing overtopping potential using GIS and remote sensing" ([Springer](https://link.springer.com/article/10.1007/s11069-025-07907-8)) | 1 m lidar DSM/DTM + OSM: 2,307 crossings in the Magra basin (Italy); deck height minus bank height → overtopping class; MAE 0.5 m on larger streams, 1.2 m on small ones; says the method suits bridges, not culverts | Precedent for RQ3 (crossings) from lidar alone; our crest readout covers culverts, which they exclude. |
| **Tao & Mallick (2020)**, *Best Practice for Assessing Roadway Damages Caused by Flooding*, LTRC report FHWA/LA.19/615 (LADOTD / FHWA) ([ROSA P dot 56249](https://rosap.ntl.bts.gov/view/dot/56249); in the Project as `FR_615_flooded pavement.pdf`) | **Prof. Tao (WPI).** Literature review + national DOT survey: all pavement types show flood damage, thin-asphalt flexible pavements most vulnerable; water in the unbound layers does the most structural damage; base/subbase gradation controls drain-down time; in-situ tools FWD, DCP, GPR; risk factor = hazard × vulnerability × consequence (high 64–125, medium 27–64, low < 27) mapped to an assessment level | The outcome a second inventory should record (damage type, layer, severity) and the field tests that would make RQ2 a mechanism test; the risk-factor framework is the natural home for the edge index (hazard) and pavement type (vulnerability). |

## Read in more detail (20 Nov)
**Anderson et al. 2017, VTrans report "Prediction and mitigation of scour and scour damage to Vermont bridges"** ([ROSA P dot 32042](https://rosap.ntl.bts.gov/view/dot/32042)),
chapters 3–4. Stream power Ω = γQs, specific ω = γQs/b; Q = bankfull (2-year) flow from regional regressions (drainage area, wetlands,
rainfall); upstream areas from a 1/3 arc-second (~10 m) DEM; slope from geomorphic-assessment reaches; width from regional regressions;
the Irene version (ISSP) scales Q to the recurrence interval of each place's 12-h Irene rainfall. Sample: 313 damaged bridges (span > 6 m)
vs 951 undamaged in the same subwatersheds. Kruskal–Wallis: SSP p < 0.001 (means 204 vs 151 W/m²), ISSP p < 0.001 (871 vs 609 W/m²);
both significant across damage levels. Fragility curves: lognormal fits per damage level, scaled by the damaged/undamaged ratio; statewide
maximum probability 9.5 %. **No AUC, accuracy or out-of-sample test reported.** Stated limits: high-probability reaches without damage
(missing factors such as surficial geology), stream power alone is not enough, bridge characteristics matter, damage counts differ between
sources (326 vs 389, partly culverts counted as bridges).
→ For Paper 2: same physical idea at a much coarser scale (reach, 10 m, design flow), bridges only, in-sample. RQ1 adds 1 m road-edge
flow paths, the actual storm's model rain, an AUC with intervals, and a pre-registered out-of-sample test.

**WEPP:Road** (Elliot, Hall, Scheele, USDA Forest Service, 1999 draft; [documentation](https://forest.moscowfsl.wsu.edu/fswepp/docs/wepproaddoc.html)):
sediment from **unpaved forest** road segments (gradient, drain spacing, width, insloped/outsloped, ruts, soil texture, climate);
"at best ± 50 %", no direct validation, no channel erosion. → Different problem (chronic sediment from unpaved roads), but its segment
inputs (gradient × contributing length between drains) are the same ingredients as our edge index.

**Gap Paper 2 fills:** stream power has been linked to bridge damage (Anderson et al. 2017) and saturation to pavement failure
(Mallick, Tao et al. 2014), but no study we found scores **road edges** (curb lines, shoulders) for washout from lidar flow paths and tests
it against a recorded damage list, nor combines it with a closure model.

**To do:** read Mallick, Tao et al. (2014/15) in full (no open copy found yet; ask Prof. Tao); Irene road (not bridge) damage studies;
confirm the Kalantari et al. author list (catalogue pages blocked).
