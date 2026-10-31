# USGS gauge data: move off NWIS WaterServices (2026-10-31)

**Why.** USGS is retiring NWIS WaterServices (`waterservices.usgs.gov`, `nwis.waterservices.usgs.gov`): degraded service from
November 2026, outages in January 2027, switched off on **22 February 2027**
([USGS bulletin](https://content.govdelivery.com/accounts/USDOIGS/bulletins/42b03d7)). The replacement is the Water Data OGC API,
[`https://api.waterdata.usgs.gov/ogcapi/v1`](https://api.waterdata.usgs.gov/ogcapi/v1). Its collections are `continuous` (the 15-min
"IV" values), `time-series-metadata`, `monitoring-locations` and `latest-continuous`. Version **v0**, which the repo used before
this change, is served only until **June 2027** ([USGS blog, API v1 release](https://waterdata.usgs.gov/blog/api-v1-release/)),
so the move is to v1, with v0 as a fallback. The design follows the official client
[`dataretrieval`](https://github.com/DOI-USGS/dataretrieval-python) 1.4 (`dataretrieval.waterdata`). We read its source for
parameter names, page limits (10 000 rows per page for `continuous`), the rule that `monitoring-locations` ignores comma lists of ids,
and the v0 retirement date. The package itself is not a dependency: the helper only needs `requests`.

**API key.** None is needed. A free personal key raises the hourly rate limit. If it is in the repo secret `API_USGS_PAT`, it is sent
as `X-Api-Key`, and only to `api.waterdata.usgs.gov`. The proto/cameras.py workflows already pass that secret. No account was
created. If the rate limit ever bites, the owner can register at <https://api.waterdata.usgs.gov/signup/> and add the secret to the
workflows that need it.

## 1. Every place that pulls USGS data (before → after)

| Where | What it pulled | Before | After |
|---|---|---|---|
| `proto/obs_fetch.py` `gauges / gauges_ogc / gauges_legacy` | 00060 + 00065, storm box. Used by `obs_catalog.py`, `storm_archive.py`, `transfer_d456.py`, workflows `obs*.yml`, `archive_followup.yml`, `obs_ogc_test.yml` | OGC **v0**, whole-state `continuous` query filtered to the box; legacy bBox as fallback | `usgs_api.iv(bbox=…)` (v1 bbox discovery); legacy = `usgs_api` legacy path; output layout unchanged (local-time strings) |
| `proto/transfer_d456.py` `gauges_fast` | 00060 + 00065 for 81 catalogue boxes | **legacy only** (`gauges_legacy`) | `obs_fetch.gauges` → OGC first, legacy fallback |
| `proto/rain/rain_fetch.py` `usgs_rain` | 00045 rain gauges, box + 0.35° | **legacy only** | `usgs_api.iv(bbox=…, params=('00045',))` |
| `sim/gauges_fetch.py` (workflow `gauges.yml` → HF `data/gauges_v2/`) | MA-wide 00060 / 00065, hourly max, plus boundary sites | OGC v0 `state_code=25`; legacy fallback | `usgs_api.iv(state='25')` + `iv(sites=…)` |
| `sim/colab/vt_inputs.py` `fetch_gauges` (Turing `stage_inputs.sh`, `proto_vt.yml`) | 00060 + 00065, box | OGC v0 state query; legacy fallback | `usgs_api.iv(bbox=…)` |
| `sim/colab/lf_inflow.py` `gauge_q` (opt-in `LF_INFLOW=usgs` only) | 00060 one site → pandas Series m³/s | OGC v0 only, no paging | `usgs_api.iv` + `to_pandas`; the inline v0 query is kept as an import fallback |
| `tools/usgs_legacy_archive.py` (`usgs_archive.yml`) | annual peaks, ratings, site files | legacy NWIS web services | **left as is on purpose**: a one-off archive to run *before* the shutdown. The new API has `peaks` and a ratings STAC catalogue if this is ever needed again |
| `proto/cameras.py`, `hwm*.yml`, `sim/nwm_compare.py`, `sim/colab/lf_domain.py`, `lf_inflow` NLDI | NIMS cameras, STN high-water marks, NLDI basins | already on `api.waterdata.usgs.gov` / `api.water.usgs.gov` | no change (not NWIS WaterServices) |
| `sim/colab/w1_data.py`, `probe.yml` | STN on `stn.wim.usgs.gov` | old STN host (not part of this retirement) | no change; `hwm*.yml` already use `api.waterdata.usgs.gov/stnservices` |
| `docs/about.html` | text only ("USGS NWIS") | — | wording for the lead to update (UI file not touched) |
| `docs/site/build_data.py`, `refresh/`, `docs/site/*.js` | — | no USGS pulls | — |

## 2. The shared helper: `proto/usgs_api.py`

`iv(sites=… | bbox=(w,s,e,n) | state='25', start, end, params=('00060','00065'), source=None, meta=True)` returns `(G, used)`:

```
G = {site: {site, name, lon, lat, datum_ft, vdatum, drain_mi2, series: {pcode: [(t_utc '2023-09-12T04:30:00+00:00', value), ...]}}}
used = 'ogc-v1' | 'ogc-v0' | 'legacy' | 'none'
```

* **Discovery.** For a box, `time-series-metadata?bbox=…&parameter_code=…` lists the sites with an instantaneous series that overlaps
  the window, and `monitoring-locations?bbox=…` gives the names, locations, datum and drainage area. A state works the same way:
  `monitoring-locations?state_code=…`, then a bbox around those sites. A site list reads `monitoring-locations/items/USGS-<id>`
  one site at a time.
* **Values.** `continuous?monitoring_location_id=USGS-a,USGS-b,…&parameter_code=…&time=a/b`, 10 sites per request. It follows the
  `rel=next` page links. When a site has several series for one parameter it keeps the fullest one (the primary), as the old
  readers did. It drops values ≤ −999 and empty values.
* **Rate limits and errors.** A 429 waits for `Retry-After`. A 5xx or network error is retried with back-off (6 tries). An HTTP
  400/404 from v1 makes that collection switch to v0. `STATS` records the request count and `x-ratelimit-remaining`.
* **Switch.** `USGS_SOURCE=auto` (default) uses the OGC API first and falls back to legacy only if the OGC API returns nothing.
  `ogc` uses the OGC API only. `legacy` forces the old WaterServices path: the pre-migration bBox / sites / stateCd IV query plus
  `/site` rdb metadata. From 2027-02-22 the legacy fallback is skipped automatically (`USGS_FORCE_LEGACY=1` overrides). Other
  settings: `USGS_OGC_VERSION` (default `v1,v0`) and `USGS_OGC_ROOT`.
* `to_pandas(G, site, pcode)` returns a float Series with a UTC index.

Each caller converts `G` back to its old shape. `obs_fetch` uses local-time strings `…000-04:00`. `gauges_fetch` uses UTC-hour
maxima. `vt_inputs` uses UTC ISO times. `rain_fetch` uses mm per increment with naive-UTC minute strings. `lf_inflow` uses a
Series in m³/s.

**Intended differences (small).**
1. When the legacy service returns several method series for one site and parameter, `obs_fetch` used to keep the *last* one and
   `gauges_fetch` the *first*. Both now keep the *fullest*.
2. `rain_fetch` no longer writes `[t, None]` rows for blank legacy values.
3. `transfer_d456.gauges_fast` now tries the OGC API first. It used to be legacy only.

## 3. Equivalence test: `.github/workflows/usgs_api_test.yml` (workflow_dispatch)

This workflow runs each query through both sources (`proto/usgs_api.py compare`). It also re-runs the ported `proto/obs_fetch.py`
both ways against the committed file, probes the v1 and v0 schemas, and writes a sample of the live summary. Logs are in
`docs/proto/usgs/_logs/`. The table below is from run 41217678074 on 2026-10-31, for 11–13 Sep 2023 (local days):

| Test | Sites | Series | Values compared | Max \|OGC − legacy\| | Result |
|---|---|---|---|---|---|
| 3 District 3 gauges: 01094400 North Nashua at Fitchburg, 01094500 near Leominster, 01109730 Blackstone at Millbury (00060 + 00065) | 3 | 6 | 1 643 | **0** | PASS |
| District 3 bbox (00060 + 00065); the path used by transfer_d456, vt_inputs, obs_fetch | 30 | 59 | 17 197 | **0** | PASS |
| District 3 bbox + 0, rain 00045 (rain_fetch) | 5 | 5 | 1 204 | **0** | PASS |
| Whole of MA, `state='25'` (sim/gauges_fetch.py) | 121 | 225 | 73 553 | **0** | PASS |
| `obs_fetch.py --gauge-source ogc` and `legacy` vs committed `docs/proto/obs/gauges_sep2023.json` (10 gauges, `obs_compare.py`) | 10 | | | peaks identical | PASS both |

* The same timestamps, values, peaks and site metadata come back from both services. Peaks: 1540 cfs / 6.21 ft at Fitchburg
  (01:15Z on 12 Sep), 5560 cfs / 12.54 ft at Leominster, 956 cfs / 4.43 ft at Millbury.
* In 2023 these data are *Approved*, so provisional data cannot cause differences here. For recent data, both services serve the
  same current provisional values.
* One difference showed up in the first run (41217314022). With `siteStatus=all`, a legacy state query also lists 7 sites whose
  series are empty in the window, for example 01097480 Sudbury at Ashland and two MassDOT I-95 stations. The legacy path now skips
  empty series, as the OGC path does.
* The probe confirmed several things:
  * v1 is live for every collection used.
  * Values come as strings.
  * `continuous` takes comma lists of ids.
  * `monitoring-locations/items/USGS-<id>` works.
  * `time-series-metadata` v1 dropped `begin_utc` / `end_utc` (`begin` / `end` are UTC).
  * No `x-ratelimit` headers were returned to unauthenticated GitHub runners. All ~210 requests succeeded with no 429.

## 4. Live District 3 gauges: `usgs_api.now()` → `docs/site/data/live/gauges.json`

Not scheduled here: Agent A owns `live_feeds.yml`. To wire it in, add a step that runs
`python proto/usgs_api.py now --out docs/site/data/live/gauges.json` (`pip install requests`; about 1–2 min; optional
`env: API_USGS_PAT: ${{ secrets.API_USGS_PAT }}`), or call `usgs_api.now(bbox=D3_BBOX, hours=24)` from Python. It reads:
* USGS 00060 / 00065 for the last 24 h, for every gauge in the District 3 box (lon/lat −72.3796, 41.9511, −71.4267, 42.7646 =
  EPSG:26986 128000, 856000, 206000, 946000).
* The reference storm peak: the largest peak of that gauge among the committed `docs/proto/obs/gauges_<storm>.json` files.
* NWS NWPS flood categories for gauges that have a USGS id. It uses `GET /nwps/v1/gauges?bbox.*`, then `/gauges/{lid}` for
  categories and observed status, then `/gauges/{lid}/stageflow` for the forecast peak
  ([NWPS API](https://api.water.noaa.gov/nwps/v1/docs/)).

Schema:

```jsonc
{
  "generated": "2026-10-31T16:00:00Z", "window_utc": ["…Z", "…Z"], "hours": 24, "bbox": [w, s, e, n],
  "source": "ogc-v1",              // or ogc-v0 / legacy / none
  "nwps": "ok",                    // or 'nwps list failed' / 'off'
  "ref_note": "…", "links": {"usgs": "…", "nwps": "…"}, "n": 27,
  "gauges": [{
    "site": "01094500", "name": "NORTH NASHUA RIVER NEAR LEOMINSTER, MA", "lon": -71.72, "lat": 42.52, "drain_mi2": 110.0,
    "url": "https://waterdata.usgs.gov/monitoring-location/USGS-01094500/",
    "q_cfs":    {"latest": 120.0, "latest_t": "…+00:00", "max": 130.0, "max_t": "…", "min": 110.0, "n": 96,
                 "change_3h": -2.0, "hourly_max": [["2026-10-31T15:00Z", 121.0], …]} | null,
    "stage_ft": { same fields } | null,
    "ref": {"peak_q_cfs": 5560.0, "q_storm": "sep2023", "peak_stage_ft": 12.54, "stage_storm": "sep2023"},
    "pct_ref_peak_q": 2.2, "pct_ref_peak_stage": 31.1,          // latest / largest catalogued storm peak, %
    "nwps": null | {"lid": "LEOM3", "name": "…", "stage_units": "ft", "action_ft": …, "minor_ft": …, "moderate_ft": …, "major_ft": …,
                    "observed_category": "no_flooding", "observed_stage": …, "observed_t": "…", "forecast_category": …,
                    "forecast_peak_ft": …, "forecast_peak_t": "…", "pct_flood_stage": 40.2, "ft_below_flood_stage": 5.8}
  }]
}
```

UI hooks for the lead:
* Map points: `gauges[].lon/lat`.
* Colour: `nwps.pct_flood_stage` where present, otherwise `pct_ref_peak_stage`.
* Tooltip: `q_cfs.latest`, `stage_ft.latest`, `stage_ft.change_3h`, `nwps.observed_category`, `nwps.forecast_peak_ft`.
* Sparkline: `q_cfs.hourly_max`.
* Link: `url`.

Live sample (`_logs/gauges_now_sample.json`, 2026-10-31 16:00Z): 37 USGS gauges in the box. 23 are matched to an NWPS gauge, and
12 of those have a flood stage. Example: Fitchburg FBGM3 is at 2.33 ft against a minor flood stage of 6.5 ft, so 35.8 % and
4.17 ft below flood stage. The box reaches into NH and CT, so a few gauges outside MA (for example NSHN3) are included.
Percent of stage depends on the gauge datum, so it is a rough guide. Percent of flood stage (`minor_ft`) is the meaningful number.

## 5. Limits / to do
* After 22 Feb 2027 the legacy path is dead code and can be deleted, together with `USGS_SOURCE=legacy`.
* The OGC API returns current data, so recent data that was *provisional* when a file was committed may since have been revised or
  approved. Differences against old committed files are not a fault of the reader (see section 3).
* `time-series-metadata` and `monitoring-locations` field names were checked against `dataretrieval` 1.4 and the live probe in
  section 3.
