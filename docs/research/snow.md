# Snow, frozen ground and snow-on-roads — data access and engine design

Pass of 19 Oct 2026 (research scout). Goal: add precipitation phase, a snowpack, melt and frozen ground to the GPU flood engine
(`sim/colab/w4_flood_gpu.py`, hourly, Colab/Kaggle with plain HTTPS), then a snow-on-roads hazard layer.
Tags as elsewhere in this folder: [paper] / [vendor] (agency or data-provider page) / [news] / [bg] (background knowledge, **not re-checked this pass**).
**VERIFIED** = seen on the provider's own listing or page this pass. **NOT VERIFIED** = pattern built from verified pieces but the file itself was not opened.
The agent cannot list S3 buckets or open the NSIDC/IEM directories directly (fetches to un-searched URLs are blocked), so the **first Colab cell should
run the `HEAD` checks in §1.6** before anything is built on these patterns.

---

## 0. Two findings that matter before any snow physics

1. **The engine's Jan 2018 rain is probably all zeros.** `mrms_hour()` reads
   `noaa-mrms-pds/CONUS/MultiSensor_QPE_01H_Pass2_00.00/...`. The AWS MRMS archive starts in **October 2020** ([IEM MRMS archive page](https://mesonet.agron.iastate.edu/archive/mrms.php);
   [planetary-datasets PR #55](https://github.com/jacobbieker/planetary-datasets/pull/55): "before the AWS archive starts in October 2020") [vendor].
   The MultiSensor Pass2 product also did not exist in 2017–18: the IEM directory for 2017-08-25 holds only `GaugeCorr_QPE_01H, PrecipFlag, PrecipRate,
   RadarOnly_QPE_01H, RadarOnly_QPE_24H, RadarQualityIndex, SeamlessHSR` ([listing](https://mtarchive.geol.iastate.edu/2017/08/25/mrms/ncep/)) **VERIFIED**.
   So a `jan2018` inland run will hit `RuntimeError` on every hour and fill them as dry (`MISSING` list in the log). **Check the jan2018 run log for
   "rain hours missing"**. Fix: for dates before 2020-10-14 read `GaugeCorr_QPE_01H` from the Iowa State mirror (§1.2).
   Do **not** fix this without the snow mask: Jan 4 2018 was a blizzard (13–18 in of snow across eastern/central MA, §5.2), so switching the rain on
   without a phase split would turn a correct-by-accident dry run into a large false flood.
2. **Dec 2023 fell as rain in Massachusetts; snow cannot make it drier.** Highs near 61 °F on Mon 18 Dec in Boston ([Boston Globe, 15 Dec 2023](https://www.bostonglobe.com/2023/12/15/metro/moderating-temps-into-weekend-will-set-stage-windy-rainstorm-sunday-night-into-monday)) [news],
   2.3–3.4 in of rain in Berkshire County ([NWS Albany event page](https://www.weather.gov/aly/December_18_2023_HeavyRain_Flooding)) [vendor]. A phase mask removes
   nothing; a snowpack only **adds** melt water. See §5 for what this means for the over-wet roads.

---

## 1. Data sources

### 1.1 Summary table

| # | Product | HTTPS pattern (Python f-string) | Example URL (status) | Resolution | Coverage | Format | Read in Python | Login |
|---|---|---|---|---|---|---|---|---|
| 1a | **MRMS PrecipFlag** (surface precipitation type), AWS | `https://noaa-mrms-pds.s3.amazonaws.com/CONUS/PrecipFlag_00.00/{d:%Y%m%d}/MRMS_PrecipFlag_00.00_{d:%Y%m%d-%H%M%S}.grib2.gz` | key `CONUS/PrecipFlag_00.00/20260921/MRMS_PrecipFlag_00.00_20260921-190000.grib2.gz` quoted in [dynamical-org/reformatters #1122](https://github.com/dynamical-org/reformatters/issues/1122) — **pattern VERIFIED; note that issue reports this exact top-of-hour object as a persistent 404**, so list the day and take the nearest file | 0.01° (~1 km), **2-min** product | **Oct 2020 →** (covers Sep/Jul/Dec 2023; **not Jan 2018**) | GRIB2, gzip | `gzip.decompress` → `pygrib.open(f)[1].values` (same code as `mrms_hour`); values are integer flags | No |
| 1b | **MRMS PrecipFlag**, Iowa State mtarchive mirror | `https://mtarchive.geol.iastate.edu/{d:%Y/%m/%d}/mrms/ncep/PrecipFlag/PrecipFlag_00.00_{d:%Y%m%d-%H%M%S}.grib2.gz` | directory `PrecipFlag/` exists for [2017-08-25](https://mtarchive.geol.iastate.edu/2017/08/25/mrms/ncep/) and [2023-08-11](https://mtarchive.geol.iastate.edu/2023/08/11/mrms/ncep/) **VERIFIED**; file name built from the verified sibling `GaugeCorr_QPE_01H_00.00_20170825-000000.grib2.gz` — **2018-01-04 directory and file cadence NOT VERIFIED** (fetch blocked) | 0.01° | NCEP-era MRMS since **Oct 2014** ([IEM](https://mesonet.agron.iastate.edu/archive/mrms.php)) | GRIB2, gzip | as 1a | No |
| 1c | **MRMS 1-h QPE for 2014–Oct 2020** (needed for Jan 2018) | `https://mtarchive.geol.iastate.edu/{d:%Y/%m/%d}/mrms/ncep/GaugeCorr_QPE_01H/GaugeCorr_QPE_01H_00.00_{d:%Y%m%d-%H}0000.grib2.gz` | `.../2017/08/25/mrms/ncep/GaugeCorr_QPE_01H/GaugeCorr_QPE_01H_00.00_20170825-000000.grib2.gz` **VERIFIED in listing** | 0.01°, hourly | 2014-10 → 2020-10 | GRIB2, gzip | identical to `mrms_hour` | No |
| 2 | **SNODAS** daily SWE + snow depth (NSIDC G02158, masked CONUS) | `https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{d:%Y}/{d:%m_%b}/SNODAS_{d:%Y%m%d}.tar` | template `.../masked/<year>/<month>/SNODAS_<date>.tar` quoted in [bluebird #449](https://github.com/zimmertr/bluebird/issues/449); month folder is `MM_Mon` (e.g. `12_Dec`, `01_Jan`) ([TrEnCh guide](https://bookdown.org/huckley/microclimate_users_guide/snodas.html)). Built: `.../masked/2023/12_Dec/SNODAS_20231217.tar`, `.../masked/2018/01_Jan/SNODAS_20180103.tar` — **NOT VERIFIED** (directory fetch blocked) | 30 arc-s (~1 km; 0.00833333°) | **30 Sep 2003 →** daily ([NSIDC G02158](https://nsidc.org/data/g02158/versions/1)) | tar of gzipped flat binaries (`.dat.gz`) + header text | §1.3 snippet | **No** per NSIDC's NOAA@NSIDC page: plain HTTPS/wget, no credentials in any example ([NSIDC help](https://nsidc.org/ru/node/180942)); the page does not say "no login" in words |
| 3a | **HRRR analysis** 2 m T, 2 m dew point, 10 m wind, surface pressure (+ categorical precip type, SWE) | `https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.{d:%Y%m%d}/conus/hrrr.t{d:%H}z.wrfsfcf00.grib2` (+ `.idx` for byte ranges) | `https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.20210719/conus/hrrr.t00z.wrfsfcf00.grib2` ([Herbie docs](https://herbie.readthedocs.io/en/latest/gallery/noaa_models/hrrr.html)) **VERIFIED as a documented key** | 3 km Lambert, hourly | **2014-07-30 →** ([Herbie HRRR model info](https://herbie.readthedocs.io/en/2024.7.0/_sources/user_guide/background/model-info/hrrr.md.txt); registry: "Archive of HRRR data since 2014" [registry](https://registry.opendata.aws/noaa-hrrr-pds)) — **covers Jan 2018 (HRRRv2)** and all 2023 storms (HRRRv4) | GRIB2 (~130 MB/file [bg]; fetch only the needed messages via `.idx` + HTTP Range) | §1.4 snippet; inventory line `:TMP:2 m above ground:anl` | No |
| 3b | **RTMA** 2.5 km analysis | `https://noaa-rtma-pds.s3.amazonaws.com/rtma2p5.{d:%Y%m%d}/rtma2p5.t{d:%H}z.2dvaranl_ndfd.grb2_wexp` | `https://noaa-rtma-pds.s3.amazonaws.com/rtma2p5.20240101/rtma2p5.t06z.2dvaranl_ndfd.grb2_wexp` ([Herbie RTMA/URMA](https://herbie.readthedocs.io/en/latest/gallery/noaa_models/rtma-urma.html)) **VERIFIED as documented key** | 2.5 km, hourly | "**start of 2019** until present" ([AWS registry](https://registry.opendata.aws/noaa-rtma)) — **not Jan 2018** | GRIB2 (small, ~10 vars) | `pygrib`, message `TMP:2 m above ground` | No |
| 3c | **URMA** 2.5 km analysis (obs-lagged, better than RTMA) | `https://noaa-urma-pds.s3.amazonaws.com/urma2p5.{d:%Y%m%d}/urma2p5.t{d:%H}z.2dvaranl_ndfd.grb2_wexp` | **NOT VERIFIED** (file name from [NCO inventory](https://www.nco.ncep.noaa.gov/pmb/products/rtma/urma2p5.t21z.2dvarges_ndfd.grb2_wexp.shtml) and Herbie's local paths; bucket exists per [registry](https://registry.opendata.aws/noaa-rtma)) | 2.5 km | 2019 → (same registry statement) | GRIB2 | as 3b | No |
| 4 | Daily T for the frozen-ground index (60 days before each storm) | gridMET `tmmn_{YYYY}.nc` / `tmmx_{YYYY}.nc` (U. Idaho) [bg, URL not re-checked]; or daily means of 3a | — | 4 km / 3 km | 1979 → / 2014 → | NetCDF / GRIB2 | xarray | No |
| 5 | **MassDOT crash records** with weather + road-surface fields | `https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT/MASSDOT_ODP_OPEN_{YEAR}/FeatureServer/0/query` — services exist for **2021, 2022, `2023v`, 2024, 2025, 2026** ([REST folder](https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT)) **VERIFIED** | layer list [2025](https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT/MASSDOT_ODP_OPEN_2025/FeatureServer/layers) **VERIFIED**; 2023 service = "2023 Crash" ([pjson](https://gis.crashdata.dot.mass.gov/arcgis/rest/services/MassDOT/MASSDOT_ODP_OPEN_2023v/MapServer?f=pjson)) | points | 2021 → in REST; **2018 not in the public REST folder** (2019 item info is behind a login page) | JSON / geoJSON / PBF, 2000 records per page | `requests` + `resultOffset` paging | No for 2021+; 2018 via IMPACT portal UI (§6.3) |

### 1.2 MRMS PrecipFlag code table ([NSSL operational GRIB2 tables](https://nssl.noaa.gov/projects/mrms/operational/tables.php)) [vendor] — VERIFIED
GRIB2 discipline 209, category 6, parameter 0, unit "flag", **2-min** frequency, missing = −1, no coverage = −3. Flag tables now live at
`github.com/NOAA-National-Severe-Storms-Laboratory/mrms-support`.

| flag | meaning | engine phase |
|---|---|---|
| −3 / −1 | no coverage / missing | fall back to temperature (§3.1) |
| 0 | no precipitation | — (if QPE > 0 anyway, use temperature) |
| 1 | warm stratiform rain | rain |
| **3** | **snow** | **snow** |
| 6 | convection | rain |
| 7 | hail | rain (liquid at ground for routing) |
| 10 | cool stratiform rain | rain — **note: "cool" = surface T ≤ 5 °C; this class carries most sleet/rain-snow transition error** |
| 91 | tropical stratiform rain | rain |
| 96 | tropical convective rain | rain |
| 2, 4, 5, 8, 9 | not used | — |

How MRMS decides "snow" ([NOAA WDTD SPT page](https://vlab.noaa.gov/web/wdtd/-/surface-precipitation-type-spt-)) [vendor]: surface temperature and **wet-bulb temperature thresholds from
RAP/HRRR**; hail if MESH > 0; warm vs cool stratiform split at surface T = 5 °C. The page does not give the snow thresholds (often quoted as T < 2 °C and
Tw < 0 °C [bg]). There is **no mixed / freezing-rain class**: freezing rain and sleet end up as "cool stratiform rain" or "snow".
So PrecipFlag is itself a model-temperature product; it adds radar echo information (bright band, echo type) on top of HRRR/RAP T.

**Hourly use:** files are every 2 min, and individual top-of-hour objects can be missing (reformatters #1122). For each engine hour, list the day prefix once
(`https://noaa-mrms-pds.s3.amazonaws.com/?list-type=2&prefix=CONUS/PrecipFlag_00.00/{YYYYMMDD}/` — S3 v2 listing, 1000 keys per page, ~720 files/day)
and compute **snow fraction = (# frames with flag 3) / (# frames with flag > 0)** per cell from e.g. every 10th minute (6 frames/h). This is ~6×1 MB downloads per hour
per storm — acceptable on Colab. If only one frame is affordable, take the one nearest the middle of the hour.

### 1.3 SNODAS details
Grid (masked CONUS, files starting `us_`), from NSIDC's own header text ([NSIDC help: import SNODAS into ArcGIS](https://nsidc.org/data/user-resources/help-center/how-do-i-import-snodas-data-arcgis)) [vendor] — VERIFIED:
`nrows 3351`, `ncols 6935`, `nbits 16`, `pixeltype signedint`, `byteorder M` (big-endian), `xdim = ydim = 0.00833333333`;
for data **after 1 Oct 2013**: `ulxmap −124.72916666666667`, `ulymap 52.87083333333334` (BIL-style **centre** of the upper-left cell; before Oct 2013 −124.72958333 / 52.87041667).
Massachusetts window (41.15–42.95 N, 73.55–69.85 W): rows **1190–1407**, cols **6141–6586** (computed here).

Not re-checked this pass [bg]: product codes inside the tar — `us_ssmv11034tS__T0001TTNATS{YYYYMMDD}05HP001.dat.gz` = **SWE**, `...11036tS...` = **snow depth**
(1025 precip, 1038 snowpack average temperature, 1039 sublimation, 1044 snowmelt runoff at base of pack, 1050 blowing-snow sublimation);
both SWE and depth stored as **mm** (scale factor 1000 → m); nodata **−9999**; snapshot valid **06 UTC** of the file date. The 1044 "snowmelt runoff" grid is
a free check on our own melt model. NSIDC has downgraded G02158 to "Basic" level of service ([NSIDC](https://nsidc.org/data/g02158/versions/1)), so cache the four storm dates.

```python
import tarfile, gzip, io, numpy as np, requests
d = pd.Timestamp('2023-12-17')
u = f'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{d:%Y}/{d:%m_%b}/SNODAS_{d:%Y%m%d}.tar'
t = tarfile.open(fileobj=io.BytesIO(requests.get(u, timeout=300).content))
def grid(code):                       # 1034 = SWE, 1036 = depth
    n = next(m for m in t.getnames() if f'ssmv1{code}tS' in m and m.endswith('.dat.gz'))
    a = np.frombuffer(gzip.decompress(t.extractfile(n).read()), '>i2').reshape(3351, 6935)
    return np.where(a == -9999, np.nan, a.astype(np.float32))[1190:1408, 6141:6587]   # mm, MA window
lat = 52.87083333334 - np.arange(1190, 1408) * 0.00833333333       # cell centres
lon = -124.72916666667 + np.arange(6141, 6587) * 0.00833333333
swe_mm, depth_mm = grid('1034'), grid('1036')
```
Read the header (`.txt.gz`/`.hdr`) from the same tar and assert the numbers above before trusting the hard-coded window.

### 1.4 HRRR 2 m temperature (recommended for all four storms — one source, 2014 →)
Use the `.idx` sidecar to download only the needed GRIB messages (a few MB instead of the whole file):
```python
base = f'https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.{d:%Y%m%d}/conus/hrrr.t{d:%H}z.wrfsfcf00.grib2'
idx = requests.get(base + '.idx').text.splitlines()          # lines "n:start:d=YYYYMMDDHH:VAR:LEVEL:anl:"
want = [':TMP:2 m above ground:', ':DPT:2 m above ground:', ':PRES:surface:', ':UGRD:10 m above ground:', ':VGRD:10 m above ground:', ':HGT:surface:']
buf = b''
for i, line in enumerate(idx):
    if any(w in line for w in want):
        a = int(line.split(':')[1]); b = int(idx[i + 1].split(':')[1]) - 1 if i + 1 < len(idx) else ''
        buf += requests.get(base, headers={'Range': f'bytes={a}-{b}'}).content
open('/tmp/h.grib2', 'wb').write(buf); g = pygrib.open('/tmp/h.grib2')
t2 = g.select(name='2 metre temperature')[0]; T2 = t2.values - 273.15; la, lo = t2.latlons()   # then RegularGridInterpolator is NOT valid (Lambert grid):
# use scipy.interpolate.griddata once to build a (ny, nx) index map from the engine grid to the nearest HRRR cell, reuse every hour
```
- HRRR terrain (`HGT:surface`) is 3 km-smoothed; correct T to the 10–30 m DEM with a lapse rate of **−6.5 °C/km** [bg] (`T_cell = T2 − 0.0065 (z_DEM − z_HRRR)`).
  On Berkshire/Worcester-hill slopes this moves cells across the 0–2 °C phase band — that is where the snow line matters.
- Also in `wrfsfc` [bg, not re-checked]: `CSNOW / CRAIN / CFRZR / CICEP:surface` (categorical type; use `f01` — at `f00` they may be empty), `WEASD:surface` (SWE, kg m⁻²) and `SNOD:surface` — a fallback snowpack if SNODAS is unreachable.
- RTMA/URMA (3b/3c) are better 2 m analyses (2.5 km, obs-corrected) but start in 2019; use them only as a check on Sep/Jul/Dec 2023.

### 1.5 Frozen-ground products
No free, no-login **gridded** soil-frost product for Massachusetts was found. SMAP freeze/thaw (NSIDC) is 9–36 km and needs Earthdata login [bg]; CRREL frost-tube and
NWS co-op frost-depth observations are point data [bg]. Standard practice is an **air-temperature index** (§3.4).

### 1.6 First Colab cell (verification, 30 s)
```python
for u in [
  'https://noaa-mrms-pds.s3.amazonaws.com/?list-type=2&prefix=CONUS/PrecipFlag_00.00/20231218/&max-keys=3',
  'https://noaa-mrms-pds.s3.amazonaws.com/?list-type=2&prefix=CONUS/MultiSensor_QPE_01H_Pass2_00.00/20180104/&max-keys=3',   # expect KeyCount 0
  'https://mtarchive.geol.iastate.edu/2018/01/04/mrms/ncep/PrecipFlag/',
  'https://mtarchive.geol.iastate.edu/2018/01/04/mrms/ncep/GaugeCorr_QPE_01H/',
  'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/2023/12_Dec/',
  'https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.20180104/conus/hrrr.t00z.wrfsfcf00.grib2.idx']:
    r = requests.get(u, timeout=60); print(r.status_code, u, r.text[:300].replace('\n', ' '))
```

---

## 2. Snowpack before each storm (what to expect from SNODAS)

| storm | expected state (sources) | engine consequence |
|---|---|---|
| **Jan 4 2018** | Blizzard: 13.4 in Boston (daily record), 16.8 in Worcester, 17.6 in Taunton, 12.5 in Fitchburg ([NRCC](https://www.nrcc.cornell.edu/services/blog/2018/01/05/index.html), [WHDH](https://whdh.com/weather-blog/bomb-cyclone-a-year-ago-today/)) [vendor/news]; preceded by ~2 weeks of severe late-Dec cold and followed by single-digit highs (NRCC) — ground almost certainly frozen; MA WRC: Jan 2018 river flooding came "later during rain-on-snow events" (the Jan 12–13 thaw) ([MA hydrologic conditions Jan 2018](https://www.mass.gov/doc/january-2018-hydrologic-conditions/download)). | Inland precip ≈ all snow → **no pluvial flood inland**; coast run (tide) unaffected. Cape/Islands may have mixed — **not verified**. A Jan 12–14 2018 rain-on-snow run would be the real winter test (frozen ground + deep pack + rain). |
| **Dec 17–19 2023** | MA: no snowfall expected and highs near 61 °F (Boston Globe); NWS Boston coordination message mentions no snow cover or frozen ground ([wx1box](https://wx1box.org/?p=3867)). Vermont: "existing snowpack below 1,500 feet was rapidly melted off", snowmelt added **2–3 in** of runoff on top of 2–4 in of rain within 12–18 h, temperatures and dew points in the 40s–50s °F ([NWS Burlington](https://weather.gov/media/btv/events/The%20Major%20Snowmelt%20and%20Flooding%20Event%20of%20December%2018.pdf)); Maine: snowmelt 1.5–2.5 in, 3.5–4.5 in in mountains ([USGS NE WSC](https://usgs.gov/centers/new-england-water-science-center/science/december-2023-flood-maine)) [vendor]. **No source found on MA snowpack** — likely bare in the east and patchy at most on Berkshire/Hoosac/Worcester-hill tops. | Pull SNODAS 2023-12-17 for the MA window: if SWE ≈ 0 south/east of the Berkshires, the `wet_start_mm=120` comment in `sim/water_sim.py` ("after a very wet fall and snowmelt") has no snowmelt basis in MA. |
| Jul / Sep 2023 | no snow | module off (`SNOW=0` or SWE=0 and T > 2 °C everywhere) |

---

## 3. Recommended engine design (hourly, per cell, all GPU arrays)

State per cell: `SWE` (ice + liquid, mm), `WL` (liquid held in pack, mm), `F` (frozen-ground index, °C·d; computed before the run).
Inputs per hour: `P` (MRMS mm/h), `T` (HRRR 2 m, lapse-corrected, °C), `Td` or RH, wind `u` (10 m), `Pa` (mb), snow fraction from PrecipFlag where available.
Output: `Q_snow` (mm/h of water leaving the pack base) **replaces** `P` as the water input to the existing infiltration / surface-water step on snow cells; non-snow cells keep rain.

### 3.1 Phase
- If PrecipFlag available (2020+ AWS; 2018 IEM if the hourly check passes): `fs = frac(flag == 3)` per hour (§1.2); cells with no flag or flag 0 use temperature.
- Temperature rule (fallback and for consistency checks): linear ramp `fs = clip((T_hi − T)/(T_hi − T_lo), 0, 1)` with **T_lo = 0 °C, T_hi = 2 °C**.
  Snow-17: rain and snow equally likely between 0 and 2 °C; single-threshold default **PXTEMP = 1 °C** ([Anderson, SNOW-17 calibration, NWS HL 4.2.2](https://www.weather.gov/media/owp/oh/hrl/docs/422snow17.pdf)) [vendor].
  Jennings et al. (2018, *Nat. Commun.* 9, [doi:10.1038/s41467-018-03629-7](https://doi.org/10.1038/s41467-018-03629-7)) [paper]: the 50 % threshold varies in space and is a large error source;
  hemispheric mean ≈ 1.0 °C and lower (near 0 °C) in humid regions such as the US Northeast [bg — abstract checked, numbers not]. A wet-bulb rule (snow if Tw < ~0.5–1 °C [bg]) is better in
  humid nor'easters; HRRR gives Td so Tw is cheap (Stull 2011 formula [bg]).
- `snowfall = fs·P` → `SWE += snowfall`; `R = (1 − fs)·P`.

### 3.2 Melt (Snow-17, Anderson 2006 — [NWS HL "SNOW-17"](https://www.weather.gov/media/owp/oh/hrl/docs/22snow17.pdf)) [vendor]
**Non-rain hours** (R < 0.25 mm/h):
`M = Mf · max(T − MBASE, 0) · Δt/6 + 0.0125 · R · T`, MBASE = 0 °C, Mf in mm/°C/6 h with a seasonal sine between MFMIN (21 Dec) and MFMAX (21 Jun):
`Mf = (MFMAX + MFMIN)/2 + (MFMAX − MFMIN)/2 · sin(2π N/366)`, N = days since 21 Mar (form reconstructed from the garbled PDF extract — re-check eq. 7).
In December/January Mf ≈ MFMIN. Ranges (mm/°C/6 h) by forest cover, from the Snow-17 calibration guide (HL 4.2.2) [vendor]; the per-day value is ×4:

| NLCD class | MFMAX | MFMIN | **Dec–Jan Mf, mm/°C/day** |
|---|---|---|---|
| Open, developed, crops/pasture (21–24, 81–82) | 1.3–2.0 | 0.5–0.9 | **2.0–3.6 (use 2.8)** |
| Deciduous (41) | 1.0–1.3 | 0.35–0.5 | **1.4–2.0 (1.7)** |
| Mixed (43) | 0.8–1.0 | 0.25–0.4 | **1.0–1.6 (1.3)** |
| Conifer, dense (42) | 0.5–0.8 | 0.2–0.3 | **0.8–1.2 (1.0)** |

NWS a-priori ranges (Anderson 2002, in [Snow-17 a-priori parameters](https://www.weather.gov/media/owp/oh/rfcdev/docs/Snow-17_A_priori_parm_estimates.pdf)) are similar (open flat MFMAX 1.5–2.2, MFMIN 0.2–0.6); raise for south aspects, lower for north.
No New-England-specific calibrated table was found; NERFC's calibrated Snow-17 values are not public [unverified].

**Rain-on-snow hours** (R ≥ 0.25 mm/h; "greater than 0.25 mm per hour (1.5 mm per 6 hours)", Snow-17) — assumes saturated air and overcast sky:
```
M = σ·Δt·[(T+273)^4 − 273^4]                       longwave,  σ = 6.12e-10 mm K^-4 h^-1
  + 0.0125·R·T                                       heat in rain
  + 8.5·UADJ·(Δt/6)·[(0.9·e_sat − 6.11) + 0.00057·Pa·T]   turbulent (condensation + sensible)
e_sat (mb) = 2.7489e8 · exp(−4278.63/(T + 242.792));  Pa in mb;  T in °C;  Δt in h
UADJ = 0.002 · (6-h wind run at 1 m, km)  — typical 0.03–0.19 mm/mb (HL 4.2.2); default 0.10, or compute from HRRR 10 m wind (log-profile to 1 m).
```
Same form in the CNRFC rain-on-snow note ([CNRFC](https://www.cnrfc.noaa.gov/publications/Rain_on_snow.pdf)) [vendor], which also states the practical point: melt is a modest
fraction of the rain (6 h, 2 in of rain: ≈ 6 % at 35 °F, 15 % at 40 °F, 25 % at 45 °F) and turbulent transfer usually dominates.
Hourly values computed here (R = 5 mm/h, UADJ 0.10, Pa 1000 mb): **T = 2 °C → 0.4 mm/h; 5 °C → 1.2; 10 °C → 2.7; 15 °C → 4.3 mm/h** (≈ 30 mm in 12 h at 10 °C,
same order as the 50–75 mm reported in Vermont on 18 Dec 2023 with stronger wind). `M = min(M, SWE)`.

### 3.3 Liquid water and outflow
`WL += M + R_on_snow`; capacity `Wmax = PLWHC · (SWE − WL)`, **PLWHC = 0.05** (ripe snow holds 2–5 %; up to 0.2–0.3 for shallow snow on flat ground; Snow-17 maximum 0.4) [vendor].
`Q_snow = max(WL − Wmax, 0)`; `WL −= Q_snow`; `SWE −= Q_snow`. For storm-length runs skip cold content (or use Snow-17 NMF = 0.15 mm/°C/6 h with TIPM 0.1–0.5) — a cold January pack
(Jan 2018) will hold the first ~10–20 mm of rain; omitting cold content makes the model *wetter*, i.e. conservative for warnings.
Optional lag (Snow-17 LAG/attenuation) is unnecessary at 1 h steps for a 1–2 day event.

### 3.4 Frozen ground (CFGI; Molnau & Bissell 1983, as described by Follum et al. 2018, *HESS* 22, 2669, [doi:10.5194/hess-22-2669-2018](https://hess.copernicus.org/articles/22/2669/2018/hess-22-2669-2018.html)) [paper]
`F_t = A·F_{t−1} − T_d · exp(−0.4·K·D)`, F ≥ 0 [bg], T_d daily mean air T (°C), D snow depth (cm, from SNODAS depth or HRRR SNOD).
**Frozen when F > 83 °C·d, thawed when F < 56 °C·d** (Follum quoting Molnau & Bissell) — VERIFIED. **A = 0.97**, **K = 0.5 cm⁻¹ when T_d < 0 °C and 0.08 cm⁻¹ when T_d ≥ 0 °C** [bg — the
numbers were lost in the page extract]. Spin up from 1 Nov using gridMET or HRRR daily means.
Effect in the engine: Follum notes "frozen and impermeable" is an oversimplification (frozen forest soils often still infiltrate). Recommend
`Fk_frozen = Fk · FROZEN_FACTOR` with FROZEN_FACTOR ≈ 0.1 on open/developed/agricultural cells and 0.5 under forest, exposed as an env knob like `FC_SCALE`; ramp linearly between F = 56 and 83.
Expected: Jan 2018 frozen nearly everywhere; Dec 2023 thawed (mild late fall [news]; confirm by computing F).

### 3.5 Where it plugs into `w4_flood_gpu.py`
- New block after the `RAIN` loop: `PHASE[ts]`, `T2[ts]`, `UADJ[ts]` arrays on the engine grid (same interpolation map reused each hour); `SWE0` from SNODAS of the storm-start date (06 UTC snapshot — for `t0` 00 UTC use the previous day's file).
- In the hourly forcing step: `rain_in = R (bare cells) | Q_snow (snow cells)` replaces `RAIN[ts]`; snowfall never reaches the surface-water depth.
- Write `snow=dict(source=..., swe0_mean_mm, melt_total_mean_mm, snowfall_mean_mm, frozen_frac)` into `meta`, beside `rain=RAIN_META`.
- Knob `SNOW=0/1` so July/Sep runs are bit-identical.
- Check: SNODAS daily SWE change and product 1044 (melt runoff) vs our melt, at 1 km, for Dec 17→19 2023 over southern VT/western MA.

---

## 4. What this implies for the Dec 2023 over-wet result
1. **Phase**: all rain in MA → the PrecipFlag mask changes nothing. (Expect flags 1/10/6, a few 3 at the very start on high terrain at most.)
2. **Snowpack**: can only add water. If SNODAS shows SWE ≈ 0–20 mm on the hill towns, melt adds ≤ ~20 mm at the cells that have snow — it makes the roads *wetter*, never drier.
   So snow is **not** the explanation for over-wet roads; it removes a justification for one current parameter instead.
3. **Frozen ground**: unlikely in a mild December → no infiltration change.
4. **What it does test**: `wet_start_mm = 120` was justified by "very wet fall and snowmelt". If SNODAS confirms no MA snowpack, rerun Dec 2023 with WET_START from the
   antecedent-store spin-up (rain-only) and with A11 re-scoring (road sampling: max over vertices picks up channel water). A11 remains the leading hypothesis (`ideas.md`).
5. For **Jan 2018**: first confirm whether the inland run had zero rain (§0). If so, the snow module plus IEM QPE is required *before* any inland Jan 2018 result is reported.
6. A better winter validation storm for the snow module itself is **12–13 Jan 2018** (rain on a deep, cold pack over frozen ground; MA WRC reports rain-on-snow flooding) — candidate for `ideas.md` A12.

---

## 5. Snow on roads — hazard layer (later)
### 5.1 Physics
- Road-cell snow depth `Hs` = snowfall since the last plow pass, converted with fresh-snow density ~100 kg m⁻³ (10:1, [bg]; nor'easters often 8–12:1) minus melt (§3.2) on paved cells (pavement heat: add +1–2 °C to T on road cells [bg]).
  Plow cycles are not public (§5.3); assume a reset every 2–3 h on interstates/primary and 4–8 h elsewhere [bg] and show it as a scenario.
- **Traffic** (FHWA *Empirical Studies on Traffic Flow in Inclement Weather*, sect. 5 — [FHWA](https://ops.fhwa.dot.gov/publications/weatherempirical/sect5.htm)) [vendor], intensity *i* in cm/h liquid equivalent, visibility *v* in km:
  light snow (0.01 cm/h): free-flow speed and speed-at-capacity −5 to −16 %, capacity −12 to −20 % (independent of intensity); maximum reductions at ≈ 0.3 cm/h.
  Weather adjustment factors (aggregate): **free-flow speed F = 0.838 − 0.0908·i + 0.00597·v²**; speed-at-capacity F = 0.816 + 0.0308·v; **capacity F = 0.792 + 0.00480·v²** (cap F at 1).
  Rain for comparison: capacity F = 0.892 constant.
- FHWA Road Weather Management ([roadimpact](https://ops.fhwa.dot.gov/weather/roadimpact.htm)) [vendor]: freeways in **heavy snow** — average speed −5 to −40 %, free-flow speed −5 to −64 %, volume −30 to −44 %, capacity −12 to −27 %;
  light rain/snow — capacity −4 to −11 %; arterials with snowy/slushy pavement — speed −30 to −40 %.
- **Friction** (peak µ, typical ranges used in winter-maintenance literature, e.g. Wallman & Åström 2001, VTI Meddelande 911 [bg — tables not opened]): dry 0.8–1.0, wet 0.5–0.8,
  slush/loose snow 0.2–0.5, packed snow 0.2–0.3, black ice 0.15–0.3, wet ice 0.05–0.1. Sweden targets µ ≥ 0.20–0.35 and Norway ≥ 0.4 on high-volume roads after treatment
  (PIARC 2006, quoted in [TAC 2009](https://www.tac-atc.ca/wp-content/uploads/ptm-friction-finalpub.pdf)) [vendor]. Peak friction occurs near 30 % slip on winter-contaminated surfaces vs 18–20 % dry/wet ([Wambold et al., PIARC 2002](https://proceedings-sapporo2002.piarc.org/en/pdf/doc_pdf/communications/VI100e.pdf)).
- **Immobilisation**: Japan NILIM — vehicles start having difficulty driving or starting when hourly snowfall exceeds **10 cm/h** (Ikehara et al., [NILIM annual report 2018](https://www.nilim.go.jp/english/annual/annual2018/pdf_file/1_019.pdf)) [vendor].
  No authoritative depth threshold found; passenger-car ground clearance 13–20 cm implies unplowed depth ≳ 15 cm immobilises most cars [bg]. Suggested classes: Hs < 2.5 cm "slow", 2.5–15 cm "hazardous", > 15 cm or snowfall > 10 cm/h "impassable for cars".

### 5.2 Hazard index (proposal)
`H_road = max(class(Hs), class(µ_est))` with µ_est from surface state (snow / slush when T ∈ [−1, 2] °C and liquid present / ice when refreezing after melt: T drops below 0 °C with WL > 0 or ponded depth > 0).
The refreeze case is where the flood and snow layers meet: ponded water from the flood engine at T < 0 °C → ice → the Jan 2018 and Dec 2023 (flash freeze after the front, 19 Dec [unverified]) cases.

### 5.3 Validation data
- **MassDOT crash points** (§1.1 #5): Crash layer fields `WEATH_COND_DESCR` ("Weather Condition"), `ROAD_SURF_COND_DESCR` ("Road Surface Condition"), `AMBNT_LIGHT_DESCR`, `CRASH_DATETIME`, `CRASH_HOUR`, `LAT`, `LON`, `RDWY`, `STREETNAME` — **VERIFIED** on the 2025 service.
  Query (not executed): `.../MASSDOT_ODP_OPEN_2023v/FeatureServer/0/query?where=ROAD_SURF_COND_DESCR LIKE '%Snow%' OR ROAD_SURF_COND_DESCR LIKE '%Ice%' OR ROAD_SURF_COND_DESCR LIKE '%Slush%'&time=<epoch ms range>&outFields=*&f=geojson&resultOffset=0` (page by 2000).
  Exact category strings of `ROAD_SURF_COND_DESCR` were not listed — run `returnDistinctValues=true&outFields=ROAD_SURF_COND_DESCR&returnGeometry=false` first. Use: share of snow/ice crashes per hour vs modelled `H_road`; also flooded-road crashes ("Water (standing, moving)" [bg]) as an extra L2 label for rain storms.
- **2018 crashes**: not in the public REST folder; IMPACT Open Data Portal (Data Extract → VIEW → search year → download, [IMPACT help](https://apps.impact.dot.state.ma.us/helpcdp/topics/idh-topic110.htm)) — formats and login **not verified**; may need Mo to download in a browser.
- **MassDOT plow / AVL tracks or storm reports**: no public archive found. Ask MassDOT Snow & Ice (Mo's decision; agent will not email).
- Other free checks [bg]: CoCoRaHS daily snowfall/snow depth reports; NOHRSC station observations; HRRR `CSNOW` hours.

---

## 6. Not verified / blocked this pass
- Direct S3 listing of `noaa-mrms-pds` (index.html and `?list-type=2` URLs blocked to the agent); the Jan 2018 absence is from two independent text sources (IEM, planetary-datasets), not a listing.
- IEM `2018/01/04/.../PrecipFlag/` directory and its file cadence (2-min vs reduced); NSIDC `noaadata.apps.nsidc.org` directory listing; NSIDC SNODAS binary→GeoTIFF help page.
- SNODAS product codes, scale factor, nodata and 06 UTC timing [bg]; CFGI A and K values [bg]; Snow-17 seasonal Mf equation (reconstructed); friction table [bg]; Jennings threshold numbers [bg].
- MA snowpack on 17 Dec 2023 — no report found; SNODAS check is the answer.
