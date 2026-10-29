# MassDOT Stormwater Asset Database: snapshot 2026-10-29

Source: `https://gisstg.massdot.state.ma.us/arcgis/rest/services/Assets/Stormwater/FeatureServer` (MassDOT **staging** GIS server; it can change or disappear without notice). Snapshot taken 2026-10-29T22:29Z by `.github/workflows/stormwater_snapshot.yml` (`proto/archive_feeds.py stormwater`), statewide, every layer and table, all fields, geometry in EPSG:4326.

**Copyright / licence (service `copyrightText`, verbatim):** (empty)

Layer-level `copyrightText`: "This data is in the public domain and therefore can be used by anyone for any purpose. MassDOT shall not be held liable for any errors in this data. This includes errors of omission, commission, errors concerning the content of the data, and relative and positional accuracy of the data. This data cannot be construed to be a legal document. Primary sources from which this data was compiled must be consulted for verification of information contained in this data."

**Full copy:** Hugging Face dataset `mohabeldokla/mass-flood-watch-tiles`, folder `massdot_stormwater/2026-10-29/`: per layer `NN_<name>.geojson.gz` (layers), `NN_<name>.csv.gz` (attributes; points also get lon / lat), `NN_<name>.layer.json` (the layer's REST metadata), and `summary.json` (this page's numbers). Read back: `huggingface_hub.hf_hub_download('mohabeldokla/mass-flood-watch-tiles', 'massdot_stormwater/2026-10-29/<file>', repo_type='dataset')`, then `geopandas.read_file` or `pandas.read_csv`.

## Layers and tables

| id | kind | name | geometry | records statewide | District 3 | District field | Town field |
|---|---|---|---|---|---|---|---|
| 0 | layer | Stormwater Control Measure | Point | 1546 | 490 | District | Municipality |
| 1 | layer | Storm Discharge Point | Point | 19390 | 3 | District | Town |
| 2 | layer | Inlet | Point | 134871 | 28936 | District | Town |
| 3 | layer | Manhole | Point | 142452 | 20331 | District | Town |
| 4 | layer | Miscellaneous Structure | Point | 96 | – | District | Town |
| 5 | layer | Conveyance | Polyline | 6940 | 2 | District | Town |
| 6 | table | swConveyanceInspectionForm | – | 0 | – | – | – |
| 7 | table | swInletInspectionForm | – | 153 | – | – | – |
| 8 | table | swManholeInspectionForm | – | 0 | – | – | – |
| 9 | table | swSCMInspectionForm | – | 381 | – | – | – |
| 10 | table | swStormwaterDischargePointInspectionForm | – | 144 | – | – | – |
| 11 | table | swStructureInspectionForm | – | 0 | – | – | – |

**Notes on reading the counts.**

- **Licence:** the service-level `copyrightText` is empty; every layer's `copyrightText` says the data "is in the public domain and
  therefore can be used by anyone for any purpose" (quoted above), with MassDOT disclaiming liability for errors.
- **Town codes:** Inlet and Manhole (and some other rows) store the town as a number. These are the MassGIS / MassDOT `TOWN_ID`s
  (alphabetical, 1–351): 348 = Worcester, 100 = Framingham, 153 = Leominster. Stormwater Control Measure stores names. The table below
  keeps the values as published.
- **District 3 coverage is real only for Inlet (28,936), Manhole (20,331) and Stormwater Control Measure (490).** Storm Discharge Point
  and Conveyance have a `District` value on only a handful of rows (19,381 of 19,390 and 6,922 of 6,940 have none), and their few
  "District 3" rows are test entries (towns "Ujwalatown", "Test", "Redlands"). To place those layers in District 3, intersect their
  geometry with the district polygon. Miscellaneous Structure has no District values.
- The inspection tables (6–11) carry no District or Town; they link to assets through their key fields (see the layer JSON on HF).
  The Inlet inspection table has 153 forms statewide.

Records by District (statewide; `None` = no District value):

- 0 Stormwater Control Measure: 1: 45, 2: 104, 3: 490, 4: 343, 5: 339, 6: 189, None: 36
- 1 Storm Discharge Point: 2: 3, 3: 3, 4: 3, None: 19381
- 2 Inlet: 1: 10760, 2: 18346, 3: 28936, 4: 30210, 5: 35277, 6: 11103, None: 239
- 3 Manhole: 1: 4134, 2: 10485, 3: 20331, 4: 75135, 5: 19151, 6: 13208, None: 8
- 4 Miscellaneous Structure: None: 96
- 5 Conveyance: 1: 1, 2: 6, 3: 2, 4: 4, 5: 5, None: 6922
- 7 swInletInspectionForm: None: 153
- 9 swSCMInspectionForm: None: 381
- 10 swStormwaterDischargePointInspectionForm: None: 144

## District 3: records per town

| town | 0 Stormwater Control Measure | 1 Storm Discharge Point | 2 Inlet | 3 Manhole | 5 Conveyance |
|---|---|---|---|---|---|
| 100 | 0 | 0 | 1273 | 1276 | 0 |
| 101 | 0 | 0 | 440 | 324 | 0 |
| 103 | 0 | 0 | 560 | 286 | 0 |
| 11 | 0 | 0 | 226 | 121 | 0 |
| 110 | 0 | 0 | 399 | 354 | 0 |
| 115 | 0 | 0 | 216 | 167 | 0 |
| 12 | 0 | 0 | 420 | 33 | 0 |
| 125 | 0 | 0 | 405 | 74 | 0 |
| 134 | 0 | 0 | 484 | 514 | 0 |
| 136 | 0 | 0 | 160 | 102 | 0 |
| 138 | 0 | 0 | 76 | 87 | 0 |
| 139 | 0 | 0 | 291 | 138 | 0 |
| 14 | 0 | 0 | 100 | 122 | 0 |
| 140 | 0 | 0 | 124 | 51 | 0 |
| 141 | 0 | 0 | 315 | 267 | 0 |
| 147 | 0 | 0 | 469 | 183 | 0 |
| 151 | 0 | 0 | 285 | 312 | 0 |
| 153 | 0 | 0 | 934 | 825 | 0 |
| 158 | 0 | 0 | 587 | 216 | 0 |
| 162 | 0 | 0 | 155 | 186 | 0 |
| 17 | 0 | 0 | 908 | 425 | 0 |
| 170 | 0 | 0 | 710 | 601 | 0 |
| 174 | 0 | 0 | 216 | 326 | 0 |
| 175 | 0 | 0 | 275 | 167 | 0 |
| 177 | 0 | 0 | 205 | 227 | 0 |
| 179 | 0 | 0 | 97 | 39 | 0 |
| 185 | 0 | 0 | 446 | 425 | 0 |
| 186 | 0 | 0 | 470 | 213 | 0 |
| 187 | 0 | 0 | 250 | 260 | 0 |
| 188 | 0 | 0 | 55 | 21 | 0 |
| 19 | 0 | 0 | 173 | 181 | 0 |
| 198 | 0 | 0 | 655 | 606 | 0 |
| 2 | 0 | 0 | 473 | 263 | 0 |
| 212 | 0 | 0 | 15 | 10 | 0 |
| 215 | 0 | 0 | 344 | 198 | 0 |
| 216 | 0 | 0 | 164 | 144 | 0 |
| 222 | 0 | 0 | 16 | 3 | 0 |
| 226 | 0 | 0 | 649 | 154 | 0 |
| 228 | 0 | 0 | 180 | 36 | 0 |
| 232 | 0 | 0 | 226 | 196 | 0 |
| 241 | 0 | 0 | 182 | 58 | 0 |
| 25 | 0 | 0 | 394 | 278 | 0 |
| 257 | 0 | 0 | 290 | 101 | 0 |
| 269 | 0 | 0 | 143 | 59 | 0 |
| 270 | 0 | 0 | 62 | 12 | 0 |
| 271 | 0 | 0 | 697 | 523 | 0 |
| 277 | 0 | 0 | 360 | 192 | 0 |
| 278 | 0 | 0 | 250 | 334 | 0 |
| 28 | 0 | 0 | 118 | 10 | 0 |
| 280 | 0 | 0 | 281 | 214 | 0 |
| 282 | 0 | 0 | 804 | 166 | 0 |
| 286 | 0 | 0 | 117 | 50 | 0 |
| 287 | 0 | 0 | 1159 | 281 | 0 |
| 288 | 0 | 0 | 139 | 74 | 0 |
| 290 | 0 | 0 | 446 | 37 | 0 |
| 299 | 0 | 0 | 252 | 66 | 0 |
| 303 | 0 | 0 | 101 | 69 | 0 |
| 304 | 0 | 0 | 671 | 293 | 0 |
| 315 | 0 | 0 | 357 | 186 | 0 |
| 316 | 0 | 0 | 472 | 248 | 0 |
| 32 | 0 | 0 | 69 | 88 | 0 |
| 321 | 0 | 0 | 421 | 272 | 0 |
| 328 | 0 | 0 | 557 | 483 | 0 |
| 330 | 0 | 0 | 436 | 111 | 0 |
| 332 | 0 | 0 | 462 | 185 | 0 |
| 34 | 0 | 0 | 331 | 72 | 0 |
| 348 | 0 | 0 | 2644 | 3933 | 0 |
| 37 | 0 | 0 | 187 | 39 | 0 |
| 39 | 0 | 0 | 171 | 36 | 0 |
| 45 | 0 | 0 | 118 | 31 | 0 |
| 54 | 0 | 0 | 445 | 265 | 0 |
| 64 | 0 | 0 | 237 | 340 | 0 |
| 77 | 0 | 0 | 108 | 74 | 0 |
| 80 | 0 | 0 | 137 | 89 | 0 |
| 81 | 0 | 0 | 80 | 38 | 0 |
| 84 | 0 | 0 | 144 | 40 | 0 |
| 97 | 0 | 0 | 648 | 851 | 0 |
| Acton | 15 | 0 | 0 | 0 | 0 |
| Auburn | 36 | 0 | 0 | 0 | 0 |
| Ayer | 2 | 0 | 0 | 0 | 0 |
| Bellingham | 10 | 0 | 0 | 0 | 0 |
| Blackstone | 1 | 0 | 0 | 0 | 0 |
| Boston | 1 | 0 | 0 | 0 | 0 |
| Boxborough | 1 | 0 | 0 | 0 | 0 |
| Clinton | 4 | 0 | 0 | 0 | 0 |
| Dudley | 1 | 0 | 0 | 0 | 0 |
| Framingham | 31 | 0 | 0 | 0 | 0 |
| Franklin | 41 | 0 | 0 | 0 | 0 |
| Gardner | 7 | 0 | 0 | 0 | 0 |
| Grafton | 1 | 0 | 0 | 0 | 0 |
| Holden | 8 | 0 | 0 | 0 | 0 |
| Hopedale | 1 | 0 | 0 | 0 | 0 |
| Hudson | 12 | 0 | 0 | 0 | 0 |
| Lancaster | 13 | 0 | 0 | 0 | 0 |
| Leicester | 1 | 0 | 0 | 0 | 0 |
| Leominster | 10 | 0 | 0 | 0 | 0 |
| Littleton | 23 | 0 | 0 | 0 | 0 |
| Marlborough | 22 | 0 | 0 | 0 | 0 |
| Maynard | 1 | 0 | 0 | 0 | 0 |
| Medway | 1 | 0 | 0 | 0 | 0 |
| Milford | 4 | 0 | 0 | 0 | 0 |
| Millbury | 42 | 0 | 0 | 0 | 0 |
| Natick | 10 | 0 | 0 | 0 | 0 |
| Northborough | 1 | 0 | 0 | 0 | 0 |
| Northbridge | 1 | 0 | 0 | 0 | 0 |
| Oxford | 19 | 0 | 0 | 0 | 0 |
| Paxton | 1 | 0 | 0 | 0 | 0 |
| Redlands | 0 | 1 | 0 | 0 | 0 |
| Shirley | 3 | 0 | 0 | 0 | 0 |
| Shrewsbury | 7 | 0 | 0 | 0 | 0 |
| Sterling | 39 | 0 | 0 | 0 | 0 |
| Sturbridge | 13 | 0 | 0 | 0 | 0 |
| Sudbury | 6 | 0 | 0 | 0 | 0 |
| Sutton | 3 | 0 | 0 | 0 | 0 |
| Test | 0 | 0 | 0 | 0 | 1 |
| Town Of Auburn | 1 | 0 | 0 | 0 | 0 |
| Uj_Town_Stormdischargepoint | 0 | 1 | 0 | 0 | 0 |
| Ujwalatown | 0 | 1 | 0 | 0 | 0 |
| Uxbridge | 8 | 0 | 0 | 0 | 0 |
| Vfbgb | 0 | 0 | 0 | 0 | 1 |
| Wayland | 2 | 0 | 0 | 0 | 0 |
| West Boylston | 38 | 0 | 0 | 0 | 0 |
| Westborough | 7 | 0 | 0 | 0 | 0 |
| Westford | 9 | 0 | 0 | 0 | 0 |
| Worcester | 33 | 0 | 0 | 0 | 0 |

## Fields

- **0 Stormwater Control Measure** (46 fields): `OBJECTID` (OID), `LEGACYID` (String), `WBID` (String), `District` (String), `Municipality` (String), `BMPType` (String), `SCM_Status` (String), `Lined` (String), `Underdrain` (String), `StaffGauge` (String), `FlowPath` (String), `AccessNotes` (String), `BMPNotes` (String), `InstallDate` (Date), `OWNEDBY` (String), `MAINTBY` (String), `SoilType` (String), `SCM_Vol` (Double), `BMP_WS_ac` (Double), `IC_WS_ac` (Double), `TreatDepth` (Double), `IC_pct_Red` (Double), `Red_IC_Des` (Double), `P_pct_Red` (Double), `Red_P_Des` (Double), `N_pct_Red` (Double), `Red_N_Des` (Double), `TSS_pct_Red` (Double), `Red_TSS_Des` (Double), `Source` (String), `ProjectNum` (Double), `ProjectName` (String), `SubmitBy` (String), `SubmitDate` (Date), `ReviewBy` (String), `ReviewDate` (Date), `PhotoPath` (String), `RecordPlans` (String), `Plans` (String), `ServiceStatus` (String), `created_date` (Date), `created_user` (String), `last_edited_date` (Date), `last_edited_user` (String), `GlobalID` (GlobalID), `AssetID` (String)
  - relationships: [{'id': 0, 'name': 'swSCMInspectionForm', 'related': 9, 'key': 'GlobalID'}]
- **1 Storm Discharge Point** (25 fields): `OBJECTID` (OID), `AssetID` (String), `Town` (String), `District` (String), `WBID` (String), `TS4_Reg` (String), `NUTRIENT` (String), `DISCHARGETYPE` (String), `TYPE` (String), `MATERIAL` (String), `DIAMETER` (String), `GATE` (String), `DATASOURCE` (String), `OWNEDBY` (String), `MAINTBY` (String), `NOTES` (String), `PhotoPath` (String), `RecordPlans` (String), `ServiceStatus` (String), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date), `GlobalID` (GlobalID), `SCMID` (String)
  - relationships: [{'id': 1, 'name': 'swStormwaterDischargePointInspectionForm', 'related': 10, 'key': 'GlobalID'}]
- **2 Inlet** (38 fields): `OBJECTID` (OID), `AssetID` (String), `Town` (SmallInteger), `District` (SmallInteger), `Location` (String), `InletType` (String), `CoverType` (String), `isLocking` (String), `Hood` (String), `Valve` (String), `SumpDepth` (Double), `DataSource` (String), `OwnedBy` (String), `MaintBy` (String), `Notes` (String), `PhotoPath` (String), `RecordPlans` (String), `ServiceStatus` (String), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date), `GlobalID` (GlobalID), `Town_txt` (String), `District_txt` (String), `SCMID` (String), `Road` (String), `RoadwayType` (String), `ReducedSaltZone` (String), `Ramp` (String), `Hotspot` (String), `CleaningFrequency_Years` (Double), `Owner` (String), `Route_ID` (String), `St_Name` (String), `Schedule` (String), `attRule` (String), `FollowUpNeeded` (String)
  - relationships: [{'id': 2, 'name': 'DBO.rcInletInspectionForm', 'related': 7, 'key': 'GlobalID'}]
- **3 Manhole** (28 fields): `OBJECTID` (OID), `AssetID` (String), `Town` (SmallInteger), `District` (SmallInteger), `Location` (String), `ManholeType` (String), `Utility` (String), `isLocking` (String), `Sump` (String), `Valve` (String), `INVNUM` (Double), `CastingSize` (Double), `DataSource` (String), `OWNEDBY` (String), `MAINTBY` (String), `Notes` (String), `PhotoPath` (String), `RecordPlans` (String), `ServiceStatus` (SmallInteger), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date), `GlobalID` (GlobalID), `Town_old` (String), `District_old` (String), `St_Name` (String), `Route_ID` (String)
- **4 Miscellaneous Structure** (20 fields): `OBJECTID` (OID), `AssetID` (String), `SCMID` (String), `Town` (String), `District` (String), `Location` (String), `Type` (String), `isLocking` (String), `DataSource` (String), `OwnedBy` (String), `MaintBy` (String), `Notes` (String), `PhotoPath` (String), `RecordPlans` (String), `ServiceStatus` (String), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date), `GlobalID` (GlobalID)
  - relationships: [{'id': 3, 'name': 'swStructureInspectionForm', 'related': 11, 'key': 'GlobalID'}]
- **5 Conveyance** (20 fields): `OBJECTID` (OID), `MATERIAL` (String), `PIPESIZE` (String), `OWNEDBY` (String), `MAINTBY` (String), `Notes` (String), `DATASOURCE` (String), `RecordPlans` (String), `GlobalID` (GlobalID), `AssetID` (String), `CULVERT` (String), `District` (String), `LINETYPE` (String), `ServiceStatus` (String), `Town` (String), `created_date` (Date), `created_user` (String), `last_edited_date` (Date), `last_edited_user` (String), `Shape__Length` (Double)
  - relationships: [{'id': 4, 'name': 'swConveyanceInspectionForm', 'related': 6, 'key': 'GlobalID'}]
- **6 swConveyanceInspectionForm** (23 fields): `OBJECTID` (OID), `InspDate` (Date), `FacilityID` (String), `Discovered` (String), `Action` (String), `Sediment` (String), `Condition` (String), `Needs` (String), `Notes` (String), `Inspector` (String), `LastUpdate` (Date), `LastEditor` (String), `Attachments` (Blob), `GUID` (GUID), `CreationDate` (Date), `Creator` (String), `EditDate` (Date), `Editor` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date)
  - relationships: [{'id': 4, 'name': 'Conveyance', 'related': 5, 'key': 'GUID'}]
- **7 swInletInspectionForm** (33 fields): `OBJECTID` (OID), `InspDate` (Date), `Discovered` (String), `Action` (String), `Sediment` (String), `Condition` (String), `Notes` (String), `Inspector` (String), `Attachments` (Blob), `GUID` (GUID), `GrateClogged` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date), `InspAffil` (String), `IDDE` (String), `FOLLOW_UP_NEEDED` (String), `CLEAN_STRUCTURE` (String), `CLEAN_PIPE` (String), `REMOVE_DEBRIS` (String), `REPAIR_STRUCTURE` (String), `REPLACE_GRATE_FRAME` (String), `REPAIR_HOOD` (String), `REPLACE_HOOD` (String), `REBUILD_STRUCTURES` (String), `CONTRACTNO` (String), `Offline` (SmallInteger), `DepthToSedimentBefore_ft` (Double), `DepthToSedimentAfter_ft` (Double), `SedimentVolumeRemoved_cy` (Double), `FollowUpRuleTrigger` (String)
  - relationships: [{'id': 2, 'name': 'DBO.Inlet', 'related': 2, 'key': 'GUID'}]
- **8 swManholeInspectionForm** (22 fields): `OBJECTID` (OID), `InspDate` (Date), `Discovered` (String), `Action` (String), `Sediment` (String), `FrameCover` (String), `Condition` (String), `Needs` (String), `Notes` (String), `Inspector` (String), `LastUpdate` (Date), `LastEditor` (String), `GUID` (GUID), `CreationDate` (Date), `Creator` (String), `EditDate` (Date), `Editor` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date)
- **9 swSCMInspectionForm** (34 fields): `OBJECTID` (OID), `InspDate` (Date), `Discovered` (String), `Erosion` (String), `VegHealth` (String), `WoodyVeg` (String), `Condition` (String), `DateRain` (Date), `StandingWater` (String), `ActionPerformed` (String), `Notes` (String), `Inspector` (String), `LastUpdate` (Date), `LastEditor` (String), `ReviewStatus` (String), `Reviewer` (String), `Attachments` (Blob), `GUID` (GUID), `StartTime` (String), `EndTime` (String), `Trash` (String), `ActionNeeded` (String), `Sediment` (String), `Spillway` (String), `BMPAccess` (String), `CreationDate` (Date), `Creator` (String), `EditDate` (Date), `Editor` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date)
  - relationships: [{'id': 0, 'name': 'Stormwater_Control_Measures', 'related': 0, 'key': 'GUID'}]
- **10 swStormwaterDischargePointInspectionForm** (28 fields): `OBJECTID` (OID), `InspDate` (Date), `Discovered` (String), `Sediment` (String), `Erosion` (String), `Condition` (String), `Flow` (String), `FlowCont` (String), `FieldTest` (String), `Needs` (String), `Notes` (String), `Inspector` (String), `LastUpdate` (Date), `LastEditor` (String), `Attachments` (Blob), `GUID` (GUID), `DateRain` (Date), `Action` (String), `Energy` (String), `CreationDate` (Date), `Creator` (String), `EditDate` (Date), `Editor` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date)
  - relationships: [{'id': 1, 'name': 'Storm_Discharge_Points', 'related': 1, 'key': 'GUID'}]
- **11 swStructureInspectionForm** (23 fields): `OBJECTID` (OID), `InspDate` (Date), `Discovered` (String), `Action` (String), `Sediment` (String), `Condition` (String), `Needs` (String), `Notes` (String), `Inspector` (String), `LastUpdate` (Date), `LastEditor` (String), `Attachments` (Blob), `GUID` (GUID), `GrateClogged` (String), `CreationDate` (Date), `Creator` (String), `EditDate` (Date), `Editor` (String), `GlobalID` (GlobalID), `created_user` (String), `created_date` (Date), `last_edited_user` (String), `last_edited_date` (Date)
  - relationships: [{'id': 3, 'name': 'Miscellaneous', 'related': 4, 'key': 'GUID'}]
