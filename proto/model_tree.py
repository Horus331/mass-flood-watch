"""Interactive model tree: content + build + check (docs/model-tree/).

    python proto/model_tree.py build     # -> docs/model-tree/tree.json (parameter values read from the code / live workflow, never typed)
    python proto/model_tree.py check     # re-reads every parameter from the code and diffs it with tree.json -> docs/model-tree/CHECK.md (exit 1 on any difference)

Parameter values carry a `ref` that says where the deployed value lives:
  yml:KEY                       the live forecast workflow's env (.github/workflows/forecast.yml)
  const:path:NAME               a module-level constant (ast, literal values only)
  env:path:KEY                  the default of os.environ.get('KEY', 'default') in that file (used when the live workflow does not set KEY)
  dict:path:NAME:key            one entry of a module-level dict constant
Positions: a fixed layered grid (LAYOUT below), column = step along the main chain, so the picture reads left to right.
"""
import ast, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'docs', 'model-tree')
GH = 'https://github.com/Horus331/mass-flood-watch/blob/main/'
YML = '.github/workflows/forecast.yml'
W9 = 'sim/colab/w9_lisflood.py'; PT = 'proto/prototype.py'; FC = 'proto/forecast.py'; RS = 'proto/resilience.py'; CS = 'proto/cascade.py'

# ------------------------------------------------------------------------------------------------ sources (all real, linked)
SRC = {
    'mrms': ('NOAA NSSL / NCEP, MRMS MultiSensor QPE 01H Pass2 (AWS noaa-mrms-pds)', 'https://www.nssl.noaa.gov/projects/mrms/'),
    'zhang2016': ('Zhang J. et al. (2016) Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation. BAMS 97(4)', 'https://doi.org/10.1175/BAMS-D-14-00174.1'),
    'hrrr': ('NOAA GSL / NCEP, High-Resolution Rapid Refresh (HRRR) v4 (AWS noaa-hrrr-bdp-pds)', 'https://rapidrefresh.noaa.gov/hrrr/'),
    'dowell2022': ('Dowell D.C. et al. (2022) The High-Resolution Rapid Refresh (HRRR): an hourly updating convection-allowing forecast model. Part I. Weather and Forecasting 37(8)', 'https://doi.org/10.1175/WAF-D-21-0151.1'),
    '3dep': ('USGS 3D Elevation Program (3DEP), 1/3 arc-second and lidar-derived 10 m DEM', 'https://www.usgs.gov/3d-elevation-program'),
    'lidarspec': ('USGS Lidar Base Specification (quality level 2: RMSEz ≤ 10 cm)', 'https://www.usgs.gov/ngp-standards-and-specifications/lidar-base-specification-online'),
    'nhd': ('USGS NHDPlus High Resolution', 'https://www.usgs.gov/national-hydrography/nhdplus-high-resolution'),
    'bieger2015': ('Bieger K., Rathjens H., Allen P.M., Arnold J.G. (2015) Development and evaluation of bankfull hydraulic geometry relationships for the physiographic regions of the United States. JAWRA 51(3)', 'https://doi.org/10.1111/jawr.12282'),
    'ssurgo': ('USDA NRCS Soil Survey Geographic Database (SSURGO), hydrologic soil group', 'https://www.nrcs.usda.gov/resources/data-and-reports/soil-survey-geographic-database-ssurgo'),
    'nlcd': ('MRLC National Land Cover Database 2021 (land cover + fractional impervious surface)', 'https://www.mrlc.gov/'),
    'massdot': ('MassDOT Road Inventory (segments, functional class, AADT) via the MassDOT open-data portal', 'https://geo-massdot.opendata.arcgis.com/'),
    'naacc': ('North Atlantic Aquatic Connectivity Collaborative (NAACC) road-stream crossing surveys', 'https://naacc.org/'),
    'macross': ('Massachusetts Stream Crossings / UMass Stream Continuity Project', 'https://streamcontinuity.org/'),
    'nbi': ('FHWA National Bridge Inventory', 'https://www.fhwa.dot.gov/bridge/nbi.cfm'),
    'census': ('US Census Bureau, 2020 Census blocks (TIGER/Line + P1 population)', 'https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html'),
    'osm': ('OpenStreetMap contributors (hospitals, fire and police stations, via Overpass)', 'https://www.openstreetmap.org/'),
    'tr55': ('USDA SCS (1986) Urban Hydrology for Small Watersheds, Technical Release 55', 'https://www.govinfo.gov/content/pkg/CZIC-gb980-u73-1986/html/CZIC-gb980-u73-1986.htm'),
    'neh630': ('USDA NRCS National Engineering Handbook Part 630 Hydrology, Chapter 10 (2004): Estimation of direct runoff from storm rainfall', 'https://directives.nrcs.usda.gov//sites/default/files2/1712930634/Part%20630%20-%20Hydrology.pdf'),
    'chow1988': ('Chow V.T., Maidment D.R., Mays L.W. (1988) Applied Hydrology. McGraw-Hill (antecedent-moisture CN conversions)', None),
    'chow1959': ('Chow V.T. (1959) Open-Channel Hydraulics. McGraw-Hill (Manning n tables; permissible velocities)', None),
    'barnes2014': ('Barnes R., Lehman C., Mulla D. (2014) Priority-flood: an optimal depression-filling and watershed-labeling algorithm for digital elevation models. Computers & Geosciences 62', 'https://doi.org/10.1016/j.cageo.2013.04.024'),
    'bates2010': ('Bates P.D., Horritt M.S., Fewtrell T.J. (2010) A simple inertial formulation of the shallow water equations for efficient two-dimensional flood inundation modelling. J. Hydrology 387', 'https://doi.org/10.1016/j.jhydrol.2010.03.027'),
    'dealmeida2012': ('de Almeida G.A.M., Bates P., Freer J.E., Souvignet M. (2012) Improving the stability of a simple formulation of the shallow water equations for 2-D flood modeling. Water Resources Research 48', 'https://doi.org/10.1029/2011WR011570'),
    'shaw2021': ('Shaw J. et al. (2021) LISFLOOD-FP 8.0: the new discontinuous Galerkin shallow-water solver for multi-core CPUs and GPUs. Geosci. Model Dev. 14', 'https://doi.org/10.5194/gmd-14-3577-2021'),
    'lfzenodo': ('LISFLOOD-FP 8.2 source code (Zenodo)', 'https://doi.org/10.5281/zenodo.13121102'),
    'hds5': ('Schall J.D. et al. (2012) Hydraulic Design of Highway Culverts, 3rd ed. FHWA-HIF-12-026 (HDS-5)', 'https://trid.trb.org/View/1144118'),
    'hec15': ('Kilgore R.T., Cotton G.K. (2005) Design of Roadside Channels with Flexible Linings. FHWA-IF-05-114 (HEC-15)', 'https://www.fhwa.dot.gov/engineering/hydraulics/pubs/05114/05114.pdf'),
    'arr': ('Ball J. et al. (eds) (2019) Australian Rainfall and Runoff: A Guide to Flood Estimation, Book 6 (blockage ch. 6; safety design criteria ch. 7)', 'https://arr.ga.gov.au/'),
    'shand2011': ('Shand T.D. et al. (2011) Australian Rainfall and Runoff Project 10: Appropriate Safety Criteria for Vehicles. Stage 2 report P10/S2/020', 'https://arr.ga.gov.au/'),
    'pregnolato2017': ('Pregnolato M., Ford A., Wilkinson S.M., Dawson R.J. (2017) The impact of flooding on road transport: a depth-disruption function. Transportation Research Part D 55', 'https://doi.org/10.1016/j.trd.2017.06.020'),
    'ganin2017': ('Ganin A.A. et al. (2017) Resilience and efficiency in transportation networks. Science Advances 3(12) e1701079', 'https://doi.org/10.1126/sciadv.1701079'),
    'latora2001': ('Latora V., Marchiori M. (2001) Efficient behavior of small-world networks. Physical Review Letters 87', 'https://doi.org/10.1103/PhysRevLett.87.198701'),
    'dijkstra1959': ('Dijkstra E.W. (1959) A note on two problems in connexion with graphs. Numerische Mathematik 1', 'https://doi.org/10.1007/BF01386390'),
    'nfpa1710': ('NFPA 1710 (2020) Standard for the Organization and Deployment of Fire Suppression Operations… (§4.1.2.1.1: 480 s travel, full first alarm)', 'https://www.nfpa.org/codes-and-standards/nfpa-1710-standard-development/1710'),
    'carr2009': ('Carr B.G. et al. (2009) Access to emergency care in the United States. Annals of Emergency Medicine 54(2)', 'https://doi.org/10.1016/j.annemergmed.2009.01.025'),
    'schwartz2017': ('Schwartz C.S., Sobash R.A. (2017) Generating probabilistic forecasts from convection-allowing ensembles using neighborhood approaches: a review and recommendations. Monthly Weather Review 145', 'https://doi.org/10.1175/MWR-D-16-0400.1'),
    'knisel1980': ('Knisel W.G. (ed.) (1980) CREAMS: A Field-Scale Model for Chemicals, Runoff and Erosion from Agricultural Management Systems. USDA Conservation Research Report 26 (frozen-soil curve number)', None),
    'roberts2008': ('Roberts N.M., Lean H.W. (2008) Scale-selective verification of rainfall accumulations from high-resolution forecasts of convective events. Monthly Weather Review 136', 'https://doi.org/10.1175/2007MWR2123.1'),
    'bekker2020': ('Bekker J., Davis J. (2020) Learning from positive and unlabeled data: a survey. Machine Learning 109', 'https://doi.org/10.1007/s10994-020-05877-5'),
    'lsr': ('NWS Local Storm Reports (Iowa Environmental Mesonet archive)', 'https://mesonet.agron.iastate.edu/lsr/'),
    'stormevents': ('NOAA NCEI Storm Events Database', 'https://www.ncdc.noaa.gov/stormevents/'),
    'usgsnwis': ('USGS Water Data for the Nation (stream stage, 15-min)', 'https://waterdata.usgs.gov/'),
    'mass511': ('MassDOT / Mass511 traveler information (roadway events)', 'https://mass511.com/'),
    'leomdpw': ('City of Leominster DPW, Sept 2023 flash-flood damage points (shared with the project, Oct 2026)', None),
    'fema_nfhl': ('FEMA National Flood Hazard Layer (100-year zone)', 'https://www.fema.gov/flood-maps/national-flood-hazard-layer'),
    'nws_ffw': ('NWS flash-flood warnings (IEM VTEC archive)', 'https://mesonet.agron.iastate.edu/vtec/'),
}

# ------------------------------------------------------------------------------------------------ stages
STAGES = [
    (1, 'Inputs', 'What the model is given'), (2, 'Grids', 'Turning data into 20 m cells'), (3, 'Flood engine', 'Water moves'),
    (4, 'Water on each road', 'Depth on every road segment'), (5, 'How the road fails', 'Failure checks'),
    (6, 'Who loses access', 'Consequences on the network'), (7, 'Forecast', 'Before the storm'), (8, 'Checked against reality', 'Validation'),
    (9, 'What-if only', 'Scenarios, not live'), (10, "Can't capture yet", 'Named limitations'),
]


def P(name, ref=None, value=None, unit='', origin=''):
    return dict(name=name, ref=ref, value=value, unit=unit, origin=origin)


def code(path, fn=''):
    return dict(path=path, fn=fn, url=GH + path)


# Each node: id, stage, type, title, plain, what, source [keys], units, resolution, period, how_used, formula (TeX), symbols, formula_text,
# parameters, output, code, limits, status.  Edges are listed separately with labels.
N = []


def node(**k):
    k.setdefault('type', 'process'); k.setdefault('status', 'live'); k.setdefault('source', []); k.setdefault('parameters', [])
    k.setdefault('code', []); k.setdefault('symbols', []); N.append(k)


# ---------------- 1 inputs
node(id='mrms', stage=1, type='input', title='Observed rain (radar + gauges)',
     plain='Radar plus rain gauges tell us how much rain fell on every 1 km square, every hour.',
     what='NOAA MRMS MultiSensor QPE 01H Pass2: radar precipitation bias-corrected with rain gauges. Before 14 Oct 2020 the gauge-corrected GaugeCorr QPE (IEM archive); RadarOnly only as a last resort, recorded per hour.',
     source=['mrms', 'zhang2016'], units='mm per hour', resolution='0.01° (~1 km), hourly', period='Oct 2020 → today (GaugeCorr before)',
     how_used='Bilinear interpolation onto the 20 m cell centres; drives storm replays and the 12 h spin-up of every forecast.',
     output='rain r(x, y, t), mm per hour on 20 m cells', code=[code(W9, 'mrms_sources / mrms_sample')],
     limits='Radar under-reads in the heaviest convective cores and far from the radar; gauges are sparse.')
node(id='hrrr', stage=1, type='input', title='Forecast rain + 2 m temperature (HRRR)',
     plain='A weather-forecast model says how much rain will fall in the next two days, every hour, on 3 km squares.',
     what='NOAA HRRR v4 hourly precipitation buckets (APCP) and 2 m air temperature; 48 h cycles at 00/06/12/18 UTC, 18 h cycles every hour.',
     source=['hrrr', 'dowell2022'], units='mm per hour; °C', resolution='3 km, hourly', period='live, each cycle',
     how_used='Forecast rain on the 20 m grid after neighbourhood spreading; the temperature splits rain from snow.',
     output='forecast rain and temperature fields per forecast hour', code=[code('sim/colab/hrrr_rain.py', 'hourly / nbhd'), code('sim/colab/lf_phase.py', 'tmp2m')],
     limits='A 3 km forecast cannot place a thunderstorm to the street; storms are often displaced by tens of km.')
node(id='lidar', stage=1, type='input', title='Ground height (lidar)',
     plain='Laser scans from aircraft measured the height of the ground everywhere, so we know which way water runs.',
     what='USGS 3DEP lidar-derived bare-earth DEM at 10 m (tiles), quality level 2.', source=['3dep', 'lidarspec'],
     units='m (NAVD88)', resolution='10 m', period='static', how_used='Averaged to the 20 m model grid; its highest 10 m cell per 20 m cell is kept as the road crest.',
     output='terrain z (m) at 10 m', code=[code(W9, 'inputs (dem10)')], limits='Bare earth hides pipes and culverts under roads; bridges and decks are removed.')
node(id='nhd', stage=1, type='input', title='Streams (NHDPlus HR)',
     plain='A national map of every stream and river tells us where water channels already exist.',
     what='USGS NHDPlus HR flowlines with drainage area; bankfull width and depth from regional curves.', source=['nhd', 'bieger2015'],
     units='m (width, depth); km² (drainage area)', resolution='flowlines rasterised to 30 m (channels30)', period='static',
     how_used='Flowline cells are carved to bankfull depth so rivers carry their water in the model.', output='channel mask, bankfull width / depth',
     code=[code(W9, 'channels30 burn')], limits='Small ditches and piped streams are missing or misplaced.')
node(id='ssurgo', stage=1, type='input', title='Soils (SSURGO)',
     plain='Soil maps say how quickly the ground can soak up rain: sandy soil drinks fast, clay slowly.',
     what='USDA NRCS SSURGO hydrologic soil group A–D (and shallow water table → D).', source=['ssurgo'], units='class A–D',
     resolution='rasterised to 30 m', period='static', how_used='Sets the curve number of every cell together with land cover.',
     output='hydrologic soil group per cell', code=[code(W9, "LF_LOSS=cn (hf_grid soils30)")], limits='Map units are coarse; soil changes within a few metres are not resolved.')
node(id='nlcd', stage=1, type='input', title='Land cover + pavement (NLCD 2021)',
     plain='Satellite maps say which ground is forest, grass or pavement; pavement makes almost all rain run off.',
     what='MRLC NLCD 2021 land-cover classes and fractional impervious surface.', source=['nlcd'], units='class; % impervious',
     resolution='30 m', period='2021', how_used='Impervious share → curve number and Manning roughness.', output='impervious fraction per cell',
     code=[code(W9, 'manning_map')], limits='30 m pixels blur narrow streets and parking lots.')
node(id='roads', stage=1, type='input', title='Roads (MassDOT Road Inventory)',
     plain='The state road list gives every road piece, how big it is and how many cars use it per day.',
     what='MassDOT Road Inventory: District 3 road graph (segments, functional class, speed, AADT, connectivity).', source=['massdot'],
     units='segments; vehicles/day', resolution='segment geometry (metres)', period='current inventory',
     how_used='Road points every 10 m are sampled on the depth grid; the graph carries detours and access.',
     output='road segments + graph links (docs/graph_segments.json)', code=[code('sim/infra/impacts.py', 'road_points')],
     limits='Some AADT values are defaults; private roads and driveways are not in the inventory.')
node(id='crossings', stage=1, type='input', title='Culverts and stream crossings',
     plain='A list of every place where a road crosses a stream, with the pipe size and condition where it was surveyed.',
     what='Road–stream crossings from the MA Stream Crossings Project / NAACC surveys (size, shape, condition, inlet blockage), USGS/TIGER road–stream intersections, MassDOT structures and the NBI (bridges).',
     source=['naacc', 'macross', 'nbi'], units='m (span, rise); class', resolution='points', period='surveys 2010s–2025',
     how_used='Opens a notch through the road fill at each crossing; sizes the HDS-5 culvert check; bridges stay open.',
     output='crossing list (docs/network/crossings_all.json)', code=[code(W9, 'open_crossings / is_bridge')],
     limits='Only part of the crossings have a surveyed size or condition.')
node(id='census', stage=1, type='input', title='People (2020 Census blocks)',
     plain='The Census tells us how many people live on each block, so we can count who gets cut off.',
     what='2020 Census blocks, population at each block internal point.', source=['census'], units='persons', resolution='block',
     period='2020', how_used='Each block is attached to its nearest road segment.', output='population per segment',
     code=[code('proto/census_blocks.py', '')], limits='Night-time (home) population only.')
node(id='facilities', stage=1, type='input', title='Hospitals, fire, police',
     plain='Where the hospitals, fire stations and police stations are, so we can check who can still reach them.',
     what='OpenStreetMap hospitals, fire stations, police (Overpass extract, Oct 2026).', source=['osm'], units='points', resolution='points',
     period='Oct 2026 extract', how_used='Sources of the shortest-path searches for emergency access.', output='facility points (docs/network/facilities.json)',
     code=[code(RS, 'access')], limits='OSM completeness varies; no staffing or capacity data.')

# ---------------- 2 grids
node(id='dem20', stage=2, title='20 m terrain grid', plain='The ground heights are averaged into 20 m squares, a 1000 × 1000 grid for each 20 km box.',
     what='10 m DEM tiles averaged to RES = 20 m; each run covers a 20 × 20 km box in EPSG:26986 (MA State Plane, m).', source=['3dep'],
     units='m', resolution='20 m', how_used='The surface water flows over.', parameters=[P('grid cell size', 'yml:RES', unit='m', origin='set by us (speed vs detail)')],
     output='z(x, y), m on 20 m cells', code=[code(W9, 'main (inputs)')], limits='A 20 m cell cannot hold a gutter or curb line (< 1 m wide).')
node(id='channels', stage=2, title='Rivers carved to bankfull', plain='Rivers are dug into the grid so they can carry water the way real channels do.',
     what='NHDPlus HR flowline cells lowered by a volume-equivalent bankfull burn; with the live terrain fix, flowlines (incl. buried conduits) are enforced as continuous downhill conveyance.',
     source=['nhd', 'bieger2015'], units='m', how_used='Modifies z on channel cells.', parameters=[P('flowline enforcement (live terrain fix T2)', 'yml:LF_CHAN_ENFORCE', origin='pre-registered terrain test, live 5 Nov 2026'),
     P('maximum enforcement cut', f'env:{W9}:LF_CHAN_ENFORCE_MAX', unit='m', origin='set by us (cap against DEM artefacts)')],
     output='z with channels', code=[code(W9, 'enforce_channels')], limits='Bankfull geometry from regional curves, not surveyed.')
node(id='notch', stage=2, title='Road–stream crossing notch (3 × 3 cells)', plain='Where a stream goes under a road, we cut a small gap in the road so the water can pass, like the real pipe.',
     what='At every mapped crossing a 3 × 3-cell notch is cut through the road fill to the lowest ground within 40 m; with the live fix, levels are read from the un-notched DEM and the notch is joined to its outlet.',
     source=['naacc', 'macross'], units='m', how_used='Stands in for the culvert barrel (the model has no pipes).',
     parameters=[P('search radius for the notch level', f'env:{W9}:LF_BREACH_M', unit='m', origin='set by us (two cells each side)'),
                 P('notch fix (live terrain fix T2)', 'yml:LF_NOTCH_FIX', origin='pre-registered terrain test, live 5 Nov 2026')],
     output='z with crossings opened', code=[code(W9, 'open_crossings')], limits='A notch passes far more water than a small or blocked pipe; stream water in the notch can read as road depth (handled by the rain-onset rule).')
node(id='breach', stage=2, title='Pit breaching (ponds kept)', plain='Fake holes in the ground map are opened so water can drain; real ponds deeper than 4 m are kept.',
     what='Least-cost breaching of every closed depression to the box edge (Barnes et al. 2014 priority-flood with carving), 4-connected (the solver exchanges water across cell faces).',
     source=['barnes2014'], units='m', how_used='Final model DEM.', parameters=[P('maximum cut', f'env:{W9}:LF_BREACH_MAX', unit='m', origin='set by us (deeper basins are real ponds / quarries)'),
     P('4-connected carving', f'env:{W9}:LF_BREACH_D4', origin='set by us (LISFLOOD-FP exchanges water across faces only)')],
     output='model DEM z (m)', code=[code(W9, 'breach_depressions')], limits='A carved one-cell path is a stand-in for an unknown pipe.')
node(id='crest', stage=2, title='Road-crest height', plain='We remember the highest point of the ground in each square, which is usually the road top.',
     what='Highest 10 m lidar cell inside each 20 m cell (z_raw_max10), before any hydraulic edit; bridge decks read depth from their approaches.',
     source=['3dep'], units='m', how_used='Freeboard and overtopping checks, crest-relative depth near crossings.', output='z_crest (m)',
     code=[code(W9, 'z_raw.npz'), code(PT, 'deck / approach rules')], limits='Lidar RMSEz ≈ 0.10 m.')
node(id='cn', stage=2, title='Runoff: curve number (TR-55)', plain='For each square we work out how much of the rain runs off instead of soaking in.',
     what='NRCS curve number from hydrologic soil group × NLCD land cover/impervious share, AMC II, scaled and clipped; cumulative SCS-CN rain excess per cell; then a steady loss is taken out of each hour of excess.',
     source=['tr55', 'neh630', 'ssurgo', 'nlcd'], units='mm', resolution='per cell, hourly',
     formula=r"Q=\frac{(P-0.2S)^2}{P+0.8S}\;(P>0.2S),\qquad S=\frac{25400}{CN_{\mathrm{eff}}}-254,\qquad CN_{\mathrm{eff}}=\mathrm{clip}(c\cdot CN_{II},30,98)",
     formula_text='Q = (P−0.2S)²/(P+0.8S),  S = 25400/CN − 254,  CN = clip(c·CN_II, 30, 98)',
     symbols=[('P', 'cumulative rain since the start, mm'), ('Q', 'cumulative runoff (rain excess), mm'), ('S', 'potential retention, mm'), ('CN_{II}', 'curve number, average antecedent moisture'), ('c', 'calibration scale')],
     parameters=[P('antecedent moisture class', 'yml:LF_CN_AMC', origin='TR-55 average condition'),
                 P('curve-number scale c', 'yml:LF_CN_SCALE', origin='calibrated on Leominster Sep 2023 (two USGS gauges, pre-set rule; docs/proto/parity/BASELINE.md)'),
                 P('steady loss after runoff', 'yml:LF_INFIL_MMH', unit='mm/h', origin='set by us (soak-in of ponded water and minor storm drains)'),
                 P('loss taken from the hourly excess (parity mode)', 'yml:LF_PARITY', origin='CPU/GPU parity audit (docs/proto/parity/PARITY.md)')],
     output='effective rain r_eff, mm per hour per cell', code=[code(W9, 'LF_LOSS=cn / rain_minus_infil')], limits='One global scale; the scale is below 1 although Sept 2023 was wet: it stands in for losses the model lacks.')
node(id='manning', stage=2, title='Surface roughness (Manning n)', plain='Rough ground (forest) slows water down; smooth pavement and rivers let it move fast.',
     what='Manning n per cell: channels and open water, dense pavement (> 30 % impervious), everything else.', source=['chow1959'], units='s m^-1/3',
     parameters=[P('channel / water n', f'env:{W9}:LF_N_CHAN', origin='Chow 1959'), P('floodplain n', f'env:{W9}:LF_N_FP', origin='Chow 1959 flood plains (set by us within the table range)')],
     output='n(x, y)', code=[code(W9, 'manning_map')], limits='One value per class; not calibrated.')
node(id='rain_grid', stage=2, title='Rain on every cell', plain='Each 20 m square gets its own rain for every hour: measured rain for a past storm, forecast rain for the next two days.',
     what='Replay: MRMS on every cell. Forecast: 12 h of observed MRMS spin-up, then HRRR (neighbourhood-spread), radar nowcast in the first hours of the issue member, snow held out. Rain minus losses → the solver’s dynamic rain file (NetCDF).',
     source=['mrms', 'hrrr'], units='mm/h → m/s', resolution='20 m, hourly', output='effective rain r_eff(x, y, t)', code=[code(W9, 'RAIN / write_rain_nc')],
     limits='Hourly steps smooth out 5–15 min bursts.')

# ---------------- 3 engine
node(id='lisflood', stage=3, type='engine', title='LISFLOOD-FP 8.2 flood engine',
     plain='The engine moves the water downhill across the 20 m squares, a tiny step at a time, and records how deep it gets everywhere.',
     what='LISFLOOD-FP 8.2 (University of Bristol), 2-D local-inertial ("acceleration") solver: momentum on cell faces with Manning friction, mass continuity per cell, adaptive time step capped at 1 s; free (outflow) boundaries; CPU (OpenMP) build on GitHub Actions, CUDA build on WPI Turing (same results under the parity settings).',
     source=['bates2010', 'dealmeida2012', 'shaw2021', 'lfzenodo'], units='m, m³/s, s', resolution='20 m; time step ≤ 1 s; snapshots every 5 min',
     formula=r"\begin{gathered}q^{t+\Delta t}=\frac{q^{t}-g\,h_f\,\Delta t\,\partial(h+z)/\partial x}{1+g\,\Delta t\,n^{2}\,|q^{t}|\,/\,h_f^{7/3}}\\[6pt]\frac{h^{t+\Delta t}-h^{t}}{\Delta t}=\frac{\sum q_{\mathrm{in}}-\sum q_{\mathrm{out}}}{\Delta x}+r_{\mathrm{eff}}\\[6pt]\Delta t=\min\!\Big(\alpha\,\frac{\Delta x}{\sqrt{g\,h_{\max}}},\;\Delta t_{\max}\Big)\end{gathered}",
     formula_text='q⁺ = (q − g h_f Δt ∂(h+z)/∂x) / (1 + g Δt n² |q| / h_f^7/3);  Δh/Δt = Σq/Δx + r_eff;  Δt = min(α Δx/√(g h), Δt_max)',
     symbols=[('q', 'flow per unit width across a cell face, m²/s'), ('h_f', 'flow depth at the face, m'), ('h', 'water depth, m'), ('z', 'ground height, m'), ('g', '9.81 m/s²'), ('n', 'Manning roughness'), ('\\Delta x', 'cell size, m'), ('r_{eff}', 'effective rain, m/s'), ('\\alpha', 'Courant number'), ('\\Delta t_{max}', 'time-step cap, s')],
     parameters=[P('parity settings: time-step cap Δt_max = 1 s, soil loss taken from the rain', 'yml:LF_PARITY', origin='CPU/GPU parity audit: 1 s is converged (0.5 s gives the same result); docs/proto/parity/PARITY.md'),
                 P('Courant number α', None, 0.7, '', 'LISFLOOD-FP default (cfl 0.7), not changed'),
                 P('default floodplain friction (fpfric)', None, 0.08, '', 'overridden cell by cell by the Manning map'),
                 P('snapshot interval', 'yml:LF_SAVEINT', unit='s', origin='set by us (5-min depth frames)')],
     output='water depth h(x, y, t) every 5 min; peak depth h_max; speeds; face flows', code=[code(W9, 'write_par / run'), code('sim/colab/w9_lisflood.py', 'get_lisflood')],
     limits='No pipes, no infiltration of standing water, no sediment or debris.')
node(id='depth', stage=3, type='output', title='Water depth every 5 minutes', plain='The engine’s main answer: how deep the water is on every square, every 5 minutes.',
     what='Depth snapshots (.wd), peak depth (.max) and the snapshot peak; stored as cm grids.', units='m', resolution='20 m, 5 min',
     output='h(x, y, t), m', code=[code(W9, 'frames / hmax')], limits='A flash peak between snapshots is caught by h_max, not by the frames.')
node(id='velocity', stage=3, type='output', title='Water speed and flows', plain='How fast the water moves and how much flows through each road crossing.',
     what='Face velocities (.Vx/.Vy) → cell speed, peak depth × speed; face fluxes → flow through crossings.', units='m/s; m²/s; m³/s', resolution='20 m, 5 min',
     parameters=[P('velocity output', 'yml:LF_VOUT', origin='needed by the fast-water and washout checks')], output='V(x, y), d·V, Q at crossings',
     code=[code(W9, 'velocity_peaks / cell_speed')], limits='Speeds on 20 m cells over steep verges can be numerical (capped at 5 m/s in the edge check).')

# ---------------- 4 roads
node(id='roadpts', stage=4, title='Road sampled every 10 m', plain='We put a dot every 10 m along every road and read the water depth under each dot.',
     what='Road points densified every RES/2 = 10 m along each segment, mapped to the 20 m depth cell; cells lowered by hydraulic edits (notch, channel, breach) are waterway cells, not road.',
     units='m', parameters=[P('edited-cell tolerance', f'const:{PT}:EDIT_TOL_M', unit='m', origin='set by us')], output='depth at each road point',
     code=[code('sim/infra/impacts.py', 'road_points')], limits='Lane-level position is not resolved inside a 20 m cell.')
node(id='segdepth', stage=4, title='Road depth d (second-highest point)', plain='For each road piece we take the second-deepest dot, so one odd dot cannot close a road on its own.',
     what='Segment depth d = the second-highest depth over the segment’s road points (the highest when it has one point).',
     formula=r"d=\mathrm{top}_2\{h(p)\,:\,p\in\text{road points of the segment}\}", formula_text='d = 2nd-highest h over the segment’s road points',
     symbols=[('h(p)', 'depth at road point p, m')], output='d per segment, m', code=[code(PT, 'seg_top2')], limits='A short dip shorter than 20 m of road is not counted.')
node(id='onset', stage=4, title='Only water the storm added', plain='Water that was already there before the rain (a stream in a culvert gap) is not counted as flooding.',
     what='Depth is measured above what stood on the road when the rain began (box-mean rain since start ≥ 1 mm); in forecasts a closure also needs a rise of ≥ 30 cm after onset (P1 rise rule).',
     parameters=[P('rain-onset threshold', f'const:{PT}:RC_RAIN_ONSET_MM', unit='mm', origin='set by us'), P('rise needed after onset', f'const:{FC}:RISE_CM', unit='cm', origin='pre-registered P1 rule, adopted 8 Nov 2026')],
     output='storm-added depth per segment', code=[code(PT, 'PROTO_RES_CONSISTENT'), code(FC, 'rises')], limits='A road already under water before the storm is not flagged even if it gets deeper by less than 30 cm.')

# ---------------- 5 failure
node(id='pclose', stage=5, type='check', title='Ponding → chance of closure', plain='If the water on a road is about 30 cm deep (above a car’s door sill), the road is likely closed.',
     what='Closure probability from segment depth with a normal uncertainty; a segment is flagged closed when p ≥ 0.5 (i.e. d ≥ 30 cm).',
     formula=r"p_{\mathrm{close}}=\Phi\!\left(\frac{d-d_0}{\sigma}\right)", formula_text='p = Φ((d − 0.30)/0.10)',
     symbols=[('\\Phi', 'standard normal CDF'), ('d', 'segment depth, m'), ('d_0', 'closure depth, m'), ('\\sigma', 'depth uncertainty, m')],
     parameters=[P('closure depth d₀', f'const:{PT}:FAIL_M', unit='m', origin='ordinary car stalls / floats around 0.3 m (Shand et al. 2011; Pregnolato et al. 2017: speed 0 at 300 mm)'),
                 P('uncertainty σ', f'const:{PT}:SIGMA_M', unit='m', origin='set by us (lidar + model depth error)'), P('flag threshold', f'const:{FC}:CLOSE_P', origin='p ≥ 0.5 ⇔ d ≥ d₀')],
     source=['shand2011', 'pregnolato2017'], output='p_close per segment; closed segments', code=[code(PT, 'main (p_close)')],
     limits='Depth only: a road can fail by erosion with little ponded water.')
node(id='culvert', stage=5, type='check', title='Culvert capacity (HDS-5)', plain='For surveyed pipes we check whether the stream flow is bigger than the pipe can carry before water goes over the road.',
     what='FHWA HDS-5 inlet/outlet-control headwater for surveyed culverts (size, shape, inlet); capacity at road-crest headwater vs the modelled flow, flow uncertain by a lognormal factor; NAACC inlet blockage reduces capacity (Poor 25 %, Critical 50 %). Map layer; not part of p_close by default.',
     formula=r"P_c=\Phi\!\left(\frac{\ln(Q/Q_{\mathrm{crest}})}{\sigma_{\ln Q}}\right),\qquad Q_{\mathrm{crest}}^{\mathrm{blocked}}=(1-B)\,Q_{\mathrm{crest}}",
     formula_text='P_c = Φ(ln(Q/Q_crest)/σ),  Q_crest,blocked = (1 − B) Q_crest',
     symbols=[('Q', 'modelled peak flow at the crossing, m³/s'), ('Q_{crest}', 'culvert capacity at road-crest headwater, m³/s'), ('\\sigma_{\\ln Q}', 'flow uncertainty'), ('B', 'blockage share')],
     parameters=[P('flow uncertainty σ_lnQ', f'const:{PT}:Q_SIGMA_LN', origin='set by us (± ~35 % peak flow)'), P('blockage, NAACC "Poor"', f'dict:{PT}:BLOCKAGE:Poor', origin='ARR 2019 Book 6 ch. 6 design blockage range'),
                 P('blockage, NAACC "Critical"', f'dict:{PT}:BLOCKAGE:Critical', origin='ARR 2019 Book 6 ch. 6'), P('crossing → road distance', f'const:{PT}:XING_SEG_M', unit='m', origin='set by us')],
     source=['hds5', 'arr', 'naacc'], output='P_culvert per crossing (map layer)', code=[code(PT, 'culvert_probability'), code('sim/infra/culvert.py', '')],
     limits='Only surveyed culverts; debris during the storm is not predicted.', status='live (map layer, not in p_close)')
node(id='freeboard', stage=5, type='check', title='Freeboard (water beside the road)', plain='If the water next to the road comes within 30 cm of the road top, the road edge is at risk.',
     what='Freeboard f = road crest − highest water surface within 30 m; design practice keeps 1 ft (0.30 m) of freeboard; σ combines lidar and model height errors.',
     formula=r"P_{fb}=\Phi\!\left(\frac{m-f}{\sigma_{fb}}\right),\quad f=z_{\mathrm{crest}}-\max(z+h)_{30\,\mathrm{m}}", formula_text='P = Φ((0.30 − f)/0.15)',
     parameters=[P('design freeboard m', f'const:{PT}:FB_MARGIN_M', unit='m', origin='1 ft freeboard of DOT culvert/ditch criteria under HDS-5'), P('σ_fb', f'const:{PT}:FB_SIGMA_M', unit='m', origin='√(0.10² + 0.10²): lidar RMSEz and model depth'),
                 P('search radius', f'const:{PT}:FB_RADIUS_M', unit='m', origin='set by us (3 × 3 cells)')],
     source=['hds5', 'lidarspec'], output='P_freeboard per segment', code=[code(PT, 'p_freeboard')], status='candidate layer (opt-in, not in p_close)',
     limits='Uses peak water surface, not duration.')
node(id='fastwater', stage=5, type='check', title='Depth × speed (vehicle stability)', plain='Even shallow water can push a car off the road if it moves fast enough.',
     what='Peak depth × speed against the small-car stability limit of the ARR vehicle-safety criteria.', formula=r"P_{dv}=\Phi\!\left(\frac{\ln(dV/0.30)}{0.35}\right)",
     formula_text='P = Φ(ln(d·V/0.30)/0.35)', parameters=[P('small-car limit d·V', f'const:{PT}:DV0_M2S', unit='m²/s', origin='Shand et al. 2011 / ARR 2019 Book 6 ch. 7 (H1/H2)'),
     P('σ (log)', f'const:{PT}:DV_SIGMA_LN', origin='half the log-range of the vehicle classes')], source=['shand2011', 'arr'],
     output='P_dv per segment', code=[code(PT, 'p_fastwater')], status='candidate layer (opt-in, not in p_close)', limits='Snapshot speeds every 5 min can miss short spikes.')
node(id='washout', stage=5, type='check', title='Embankment washout at crossings', plain='When water pours over a road at a stream crossing fast enough, it can wash the road fill away.',
     what='Overtopping speed on unedited road cells near a crossing vs the permissible velocity of grass on easily eroded soil.', formula=r"P_{w}=\Phi\!\left(\frac{\ln(V/1.5)}{0.30}\right)",
     formula_text='P = Φ(ln(V/1.5)/0.30)', parameters=[P('permissible velocity', f'const:{PT}:V_ERODE_MS', unit='m/s', origin='SCS TP-61 / Chow 1959 Table 7-6'), P('σ (log)', f'const:{PT}:V_SIGMA_LN', origin='spans 1.2–2.1 m/s'),
     P('minimum depth over the road', f'const:{PT}:ERODE_MIN_H_M', unit='m', origin='set by us')], source=['chow1959'], output='P_washout per segment',
     code=[code(PT, 'p_fastwater (washout term)')], status='candidate layer (opt-in, not in p_close)', limits='No soil or embankment data; one permissible velocity for all fills.')
node(id='edge', stage=5, type='check', title='Edge erosion along the road', plain='Fast, shallow water running along a road can wash out the gravel shoulder even without a deep puddle.',
     what='Both a speed and a shear criterion must be exceeded beside the road (HEC-15 τ = γ h S vs gravel permissible shear), weighted by time above 1 m/s.',
     formula=r"P_{\mathrm{edge}}=\min\big(\Phi(\tfrac{\ln(V/1.0)}{0.46}),\,\Phi(\tfrac{\ln(\gamma h S/11\,\mathrm{Pa})}{0.61})\big)\cdot\min(1,t_{V\ge1}/1\,\mathrm{h})",
     formula_text='P = min(Φ(ln(V/1.0)/0.46), Φ(ln(τ/11 Pa)/0.61)) × min(1, t/1 h)',
     parameters=[P('permissible speed', f'const:{PT}:EDGE_V_MS', unit='m/s', origin='Chow 1959 Tables 7-3 / 7-6 (gravel, loam, thin grass)'), P('permissible shear', f'const:{PT}:EDGE_TAU_PA', unit='Pa', origin='HEC-15 Table 2.3 (gravel)'),
                 P('reference duration', f'const:{PT}:EDGE_T_REF_H', unit='h', origin='CIRIA R116 (Hewlett et al. 1987) duration curves')],
     source=['hec15', 'chow1959'], output='P_edge per segment', code=[code(PT, 'edge washout layer')], status='candidate layer (opt-in; adds +0 Leominster DPW sites)',
     limits='A 20 m grid cannot hold the curb-line flow that causes most edge washouts.')

# ---------------- 6 access
node(id='graph', stage=6, title='Road network graph', plain='All road pieces joined at junctions, so we can find routes like a GPS does.',
     what='District 3 MassDOT graph; free-flow travel time per segment by class; a closed segment is removed, a wet one slowed.', source=['massdot'],
     output='graph with travel times', code=[code(RS, 'graph'), code(CS, '')], limits='Daily traffic only (flat profile); no traffic assignment.')
node(id='pregnolato', stage=6, title='Slower on wet roads (Pregnolato curve)', plain='Cars drive slower through water; at 30 cm they stop.',
     what='Speed reduction by depth (5–30 cm) from the depth–disruption function.', source=['pregnolato2017'],
     formula=r"f(d)=\frac{0.0009\,d^{2}-0.5529\,d+86.94}{86.94}\quad(d\ \text{in mm})", formula_text='f(d) = (0.0009 d² − 0.5529 d + 86.94)/86.94, d in mm',
     parameters=[P('no effect below', f'const:{CS}:SLOW_CM', unit='cm', origin='Pregnolato et al. 2017'), P('closed at', f'const:{CS}:CLOSE_CM', unit='cm', origin='= closure depth')],
     output='speed factor per segment and frame', code=[code(CS, 'cascade')], limits='Fitted on UK data.')
node(id='dijkstra', stage=6, title='Shortest routes and detours', plain='The computer finds the quickest way around closed roads, like a navigation app.',
     what='Dijkstra shortest paths on the wet graph (node-weighted by travel time); detours capped at 30 min; vehicle-hours from AADT.', source=['dijkstra1959'],
     output='detour minutes, vehicle-hours of delay', code=[code(CS, 'cascade'), code(RS, 'closure_detours')], limits='No congestion feedback (no equilibrium assignment).')
node(id='access', stage=6, title='Emergency access standards', plain='We count people who can no longer reach a hospital in 30 min, a fire station in 8 min or police in 10 min.',
     what='Residents within the standard of an open facility, now vs dry; isolated = no route to any open hospital, fire or police station.',
     parameters=[P('hospital', f'dict:{RS}:ACCESS_MIN:hospital', unit='min', origin='Carr et al. 2009 (share within 30 min of an emergency department)'),
                 P('fire station', f'dict:{RS}:ACCESS_MIN:fire_station', unit='min', origin='NFPA 1710 (2020) §4.1.2.1.1: 480 s travel'),
                 P('police', f'dict:{RS}:ACCESS_MIN:police', unit='min', origin='set by us (no national standard; planning assumption)')],
     source=['carr2009', 'nfpa1710', 'census', 'osm'], output='people losing access (per service), person-hours', code=[code(RS, 'access'), code(CS, 'connectivity')],
     limits='Night-time population; facilities from OSM.')
node(id='efficiency', stage=6, title='Network resilience (efficiency)', plain='One number for how well the whole road network still moves people during the storm.',
     what='Global efficiency of the network over time, as used for road-network resilience by Ganin et al. 2017.', source=['latora2001', 'ganin2017'],
     formula=r"E(t)=\frac{1}{N(N-1)}\sum_{i\neq j}\frac{1}{\tau_{ij}(t)},\qquad Q_{\mathrm{eff}}(t)=100\,\frac{E(t)}{E_{\mathrm{dry}}}",
     formula_text='E = Σ 1/τ_ij / (N(N−1));  Q = 100 E/E_dry', symbols=[('\\tau_{ij}', 'shortest travel time from i to j'), ('N', 'segments in the box')],
     output='functionality curve Q(t), %', code=[code(RS, 'Q_eff')], status='live in replays (skipped in the forecast for speed)', limits='All trips weighted equally.')

# ---------------- 7 forecast
node(id='gate', stage=7, title='Rain gate', plain='The flood model only runs for real when the forecast shows heavy rain somewhere in the district.',
     what='Any District 3 town with forecast 6 h maximum ≥ 25 mm or 24 h maximum ≥ 40 mm (HRRR); then up to 4 boxes of 20 × 20 km on the wettest towns. Below that, rain ≥ 8 mm still runs one box ("water mode", never a warning).',
     formula=r"\max_{6h}\ge G_6\;\lor\;\max_{24h}\ge G_{24}", formula_text='max6h ≥ 25 mm or max24h ≥ 40 mm',
     parameters=[P('6 h threshold G₆', f'env:{FC}:GATE_6H_MM', unit='mm', origin='every catalogue closure storm must fire it (docs/proto/forecast/GATE.md)'),
                 P('24 h threshold G₂₄', f'env:{FC}:GATE_24H_MM', unit='mm', origin='as above'), P('water-mode threshold', f'env:{FC}:WATER_MM', unit='mm', origin='set by us'),
                 P('box size', f'const:{FC}:BOX_KM', unit='km', origin='set by us')],
     output='boxes to run', code=[code(FC, 'evaluate')], limits='HRRR intensity errors pass straight into the gate.')
node(id='nbhd', stage=7, title='Spreading the forecast (20 km / 90th percentile)', plain='Because forecasts often put the storm a little off, each spot takes the heavier rain forecast near it.',
     what='Each HRRR value replaced by the 90th percentile within 20 km, every hour (neighbourhood approach).', source=['schwartz2017'],
     parameters=[P('radius, percentile', 'yml:LF_HRRR_NBHD', unit='km, %', origin='best hindcast set-up (docs/proto/forecast/HINDCAST.md)')],
     output='spread forecast rain', code=[code('sim/colab/hrrr_rain.py', 'nbhd')], limits='Adds rain volume (deliberate: catches displaced cores).')
node(id='spinup', stage=7, title='Radar spin-up + nowcast', plain='The forecast starts from the rain that has already fallen, and uses radar for the first hours.',
     what='12 h of observed MRMS before the cycle; for the issue member the first hours are observed / radar-advected nowcast, blended into HRRR.',
     parameters=[P('spin-up', 'yml:LF_SPINUP_H', unit='h', origin='set by us (8 Nov 2026)')], source=['mrms'], output='rain series for the member',
     code=[code(W9, 'LF_SPINUP_H / LF_NOWCAST'), code('proto/nowcast_hindcast.py', '')], limits='Nowcast skill fades after ~2 h.')
node(id='phase', stage=7, title='Rain or snow', plain='When it is cold, part of the precipitation falls as snow and does not run off right away.',
     what='Liquid fraction from HRRR 2 m temperature, linear between 0 and 2 °C; frozen part kept as snow (no melt within the run).',
     formula=r"f_{\mathrm{liq}}=\mathrm{clip}\!\left(\frac{T-T_{lo}}{T_{hi}-T_{lo}},0,1\right)", formula_text='f = clip((T − 0)/(2 − 0), 0, 1)',
     parameters=[P('T_lo', 'const:sim/colab/lf_phase.py:T_LO', unit='°C', origin='set by us (common rain/snow transition)'), P('T_hi', 'const:sim/colab/lf_phase.py:T_HI', unit='°C', origin='set by us'),
                 P('switch', 'yml:LF_PHASE', origin='artifact fix, live 13 Nov 2026')], output='liquid rain', code=[code('sim/colab/lf_phase.py', 'liquid_fraction')],
     limits='No snowmelt; no rain-on-snow.')
node(id='members', stage=7, title='8 time-lagged HRRR members', plain='We run the flood model with the newest forecast and 7 slightly older ones, to see how much they agree.',
     what='Members T, T−6, T−12, T−18 h (48 h cycles) plus the hourly cycles before T; each is its own flood run per box; older members reused from cache.',
     output='8 flood runs per box', code=[code('proto/forecast_kofn.py', 'members')], limits='Lagged members share the same model errors.')
node(id='kofn', stage=7, title='"k of 8": likely / possible', plain='A road is "likely closed" if at least 2 of the 8 runs close it, "possible" if 1 does.',
     what='k = number of members with p_close ≥ 0.5 on the segment; likely k ≥ 2, possible k = 1. Shown as "k of 8", not as a percentage.',
     formula=r"k=\sum_{m=1}^{8}\mathbb{1}\left[p_{\mathrm{close}}^{(m)}\ge0.5\right]", formula_text='k = Σ_m 1[p_close,m ≥ 0.5]',
     output='likely / possible road lists', code=[code('proto/forecast_kofn.py', 'closures')], limits='Members can agree on a wrong storm position.')
node(id='pirank', stage=7, title='Ranking by chance of flooding (π)', plain='Roads in the list are ordered by how likely they are to really flood, using depth and a few road and rain facts.',
     what='π from a fitted logistic model on the deployed depth probit plus hazard terms (hours > 15 cm, HAND, slope, culvert/overtop/sag/edge layers, peak 1 h rain, stream distance, length); used for order only. Not shown as a %: used for order only until its calibration is proven.',
     formula=r"\mathrm{logit}\,\pi=b_o\,o+b_0+\mathbf b\cdot\mathbf h,\qquad o=1.7\,\mathrm{clip}\!\left(\frac{d-0.30}{0.10},-6,6\right)",
     formula_text='logit π = b_o·o + b₀ + b·h,  o = 1.7·clip((d−0.30)/0.10, −6, 6)', source=['bekker2020'], output='order of the road list',
     code=[code('proto/latent_label.py', ''), code(FC, 'pi order')], limits='Fitted on reports, which favour busy roads.', status='live (order only)')

# ---------------- 8 validation
node(id='labels', stage=8, type='label', title='Flood reports (labels, never inputs)', plain='Real reports of flooded roads are kept aside and used only to check the model, never to feed it.',
     what='NWS Local Storm Reports, NOAA Storm Events, MassDOT roadway events, news / WX1BOX, Leominster DPW damage points, (opt-in) SeeClickFix and crash records. Positive-unlabelled: a road with no report is not a dry road.',
     source=['lsr', 'stormevents', 'mass511', 'leomdpw', 'bekker2020'], output='labelled sites per storm', code=[code('proto/data/', 'labels_*.csv')], limits='Reports cluster on busy roads; most flooded roads are never reported.')
node(id='matching', stage=8, type='label', title='Matching reports to roads', plain='A report counts for a road if it is within 30 m of it; reports close together count once.',
     what='Strict match within 30 m of a road point; labels clustered single-link within 150 m into sites; approximate locations carry a position uncertainty.',
     parameters=[P('match distance', None, 30, 'm', 'docs/proto/PROTOCOL.md'), P('site clustering', None, 150, 'm', 'docs/proto/PROTOCOL.md')],
     output='sites', code=[code('proto/score_v2.py', '')], limits='Approximate coordinates (~500 m) limit what can be matched.')
node(id='metrics', stage=8, type='label', title='Scores', plain='We ask: of the real flooded places, how many were on the model’s short list, compared with picking roads at random?',
     what='Site recall at the closure rule and at fixed shares (top 1–10 % of segments); chance recall (exact hypergeometric) and lift; CSI; FSS at 100/300/1000 m; storm-clustered bootstrap CIs; paired tests with pre-registered adoption rules.',
     source=['roberts2008'], formula=r"\mathrm{recall}@k\%=\frac{\#\,\text{sites hit in top }k\%}{\#\,\text{sites}},\quad \mathrm{lift}=\frac{\mathrm{recall}}{\mathrm{recall}_{\mathrm{chance}}},\quad \mathrm{CSI}=\frac{H}{H+M+F}",
     formula_text='recall@k% = sites hit / sites;  lift = recall / chance;  CSI = H/(H+M+F)', output='skill (reported elsewhere, not on this tree)', code=[code('proto/score_v2.py', ''), code('proto/bench_v3.py', '')],
     limits='Few sites per storm; wide intervals.')
node(id='baselines', stage=8, type='label', title='Six named baselines', plain='The model must beat simple alternatives an office could use today.',
     what='NWS flash-flood warnings; FEMA 100-yr zone; MassDOT repeat flood points; radar rain threshold; terrain only (HAND); static hazard × vulnerability × consequence.',
     source=['nws_ffw', 'fema_nfhl'], output='benchmark (docs/proto/scoring/BENCHMARK_v3.md)', code=[code('proto/bench_v3.py', '')], limits='Some baselines are undated (used for every storm).')
node(id='split', stage=8, type='label', title='Calibration vs test storms', plain='One storm was used to set the model; all the others are tests it never saw.',
     what='Calibration: Leominster Sep 2023 (and Worcester Aug 2021 for design choices). Tests: 23 held-out District 3 storms, 81 District 4–6 storms (frozen settings), the live forward test from 3 Nov 2026. 5 locked storms never opened.',
     output='which storms decide what', code=[code('docs/proto/PROTOCOL_v3.md', '')], limits='The test set is small in District 3.')
node(id='gauges', stage=8, type='label', title='River gauges', plain='River-level gauges show whether the model’s rivers rise as much and as early as the real ones.',
     what='USGS 15-min stage; modelled rise at the nearest channel cell vs observed rise and peak time.', source=['usgsnwis'], output='rise and timing errors', code=[code('proto/score.py', '')],
     limits='Few gauges per box; small streams ungauged.')

# ---------------- 9 what-if
node(id='wi_culvert', stage=9, type='process', status='what-if only', title='Culverts blocked 0–100 %', plain='What if the pipes under the roads were partly or fully clogged with debris?',
     what='Culvert notch floor raised by a fraction f of the opening (f = 1: solid fill); bridges stay open; optionally only the smallest third of surveyed culverts.',
     formula=r"z_{\mathrm{notch}}'=z_{\mathrm{cut}}+f\,(z_{\mathrm{crest}}-z_{\mathrm{cut}})", formula_text="z' = z_cut + f (z_crest − z_cut)", source=['arr'],
     output='flood with blocked culverts', code=[code(W9, 'partial_block / block_crossings')], limits='Geometric proxy for an inlet-area reduction.')
node(id='wi_amc', stage=9, type='process', status='what-if only', title='Dry / wet soil (AMC I / III)', plain='What if the ground was already soaked (or bone dry) before the storm?',
     what='Curve number converted to antecedent class I or III (Chow et al. 1988), calibration scale kept.', source=['neh630', 'chow1988'],
     formula=r"CN_I=\frac{4.2\,CN_{II}}{10-0.058\,CN_{II}},\qquad CN_{III}=\frac{23\,CN_{II}}{10+0.13\,CN_{II}}", formula_text='CN_I = 4.2CN/(10−0.058CN);  CN_III = 23CN/(10+0.13CN)',
     output='flood with wetter / drier ground', code=[code(W9, 'LF_CN_AMC')], limits='One class for the whole box.')
node(id='wi_frozen', stage=9, type='process', status='what-if only', title='Frozen ground', plain='What if the same storm hit frozen ground in early spring, when water cannot soak in?',
     what='Knisel (CREAMS) rule: CN 95 where the unfrozen CN ≤ 80, else 98; no steady soak-in.', source=['knisel1980'], output='flood on frozen ground',
     code=[code(W9, 'LF_CN_FROZEN')], limits='Real frost varies with snow cover and depth.')
node(id='wi_rain', stage=9, type='process', status='what-if only', title='More or less rain', plain='What if the same storm had been half as strong, or a quarter stronger?',
     what='Every hour of the observed radar rain multiplied (× 0.5 to × 1.25), same timing and place.', output='flood under scaled rain', code=[code(W9, 'LF_RAIN_SCALE')],
     limits='Scaling keeps the storm’s shape.')

# ---------------- 10 can't capture
node(id='cc_edge', stage=10, type='limit', status="can't capture yet", title='Edge erosion without ponding', plain='Roads that wash out at the edge with almost no standing water are missed.',
     what='Most missed Leominster damage (Sep 2023) is edge washout with ~2 cm of modelled water, mostly along one street; curb-line flow is narrower than a 20 m cell.',
     output='—', code=[code('docs/proto/phase1/LEOMINSTER_MISSES.md', '')], limits='Needs curb-line flow and damage inventories from more towns.')
node(id='cc_debris', stage=10, type='limit', status="can't capture yet", title='Debris blockage during the storm', plain='Branches and trash that clog a pipe during the storm are not predicted.',
     what='Blockage can be imposed as a what-if, not forecast.', output='—', limits='No debris-supply data.')
node(id='cc_drains', stage=10, type='limit', status="can't capture yet", title='Storm drains (pipes)', plain='City storm-drain pipes are not in the model yet.',
     what='Street inlets and pipes carry part of the runoff in built-up areas; the model has no pipe network.',
     output='—', limits='Pipe network data (sizes, inverts, condition) are held by each city.')
node(id='cc_gw', stage=10, type='limit', status="can't capture yet", title='Groundwater', plain='Rising groundwater under roads and foundations is not modelled.',
     what='No subsurface flow; antecedent wetness only through the curve number.', output='—', limits='Needs groundwater observations.')

# ------------------------------------------------------------------------------------------------ edges (from, to, label, kind)
E = [
    ('mrms', 'rain_grid', 'observed rain, mm/h (1 km)', 'data'), ('hrrr', 'nbhd', 'forecast rain, mm/h (3 km)', 'data'), ('hrrr', 'phase', '2 m temperature, °C', 'data'),
    ('mrms', 'spinup', '12 h observed rain', 'data'), ('nbhd', 'rain_grid', 'spread forecast rain, mm/h', 'data'), ('spinup', 'rain_grid', 'spin-up + nowcast hours', 'data'),
    ('phase', 'rain_grid', 'liquid share 0–1', 'data'), ('lidar', 'dem20', 'z at 10 m', 'data'), ('lidar', 'crest', 'highest 10 m cell', 'data'),
    ('nhd', 'channels', 'flowlines, bankfull width/depth', 'data'), ('dem20', 'channels', 'z, 20 m', 'process'), ('crossings', 'notch', 'crossing points', 'data'),
    ('channels', 'notch', 'z with channels', 'process'), ('notch', 'breach', 'z with notches', 'process'), ('ssurgo', 'cn', 'soil group A–D', 'data'),
    ('nlcd', 'cn', 'impervious %', 'data'), ('nlcd', 'manning', 'impervious %', 'data'), ('nhd', 'manning', 'channel mask', 'data'), ('rain_grid', 'cn', 'rain P, mm', 'data'),
    ('breach', 'lisflood', 'model DEM z, m', 'data'), ('cn', 'lisflood', 'effective rain r_eff, m/s', 'data'), ('manning', 'lisflood', 'roughness n', 'data'),
    ('lisflood', 'depth', 'h(x,y,t), m every 5 min', 'data'), ('lisflood', 'velocity', 'face velocities, flows', 'data'),
    ('roads', 'roadpts', 'segments', 'data'), ('depth', 'roadpts', 'h at road points', 'data'), ('roadpts', 'segdepth', 'depth per point, m', 'process'),
    ('segdepth', 'onset', 'd, m', 'process'), ('onset', 'pclose', 'storm-added d, m', 'process'), ('crest', 'freeboard', 'z_crest, m', 'data'), ('depth', 'freeboard', 'water surface, m', 'data'),
    ('velocity', 'culvert', 'flow at crossing Q, m³/s', 'data'), ('crossings', 'culvert', 'size, shape, blockage', 'data'), ('velocity', 'fastwater', 'peak d·V, m²/s', 'data'),
    ('velocity', 'washout', 'speed over the road, m/s', 'data'), ('velocity', 'edge', 'speed beside the road, m/s', 'data'),
    ('pclose', 'graph', 'closed segments → removed', 'process'), ('segdepth', 'pregnolato', 'depth 5–30 cm', 'data'), ('roads', 'graph', 'graph links, class, AADT', 'data'),
    ('pregnolato', 'graph', 'speed factor', 'process'), ('graph', 'dijkstra', 'wet graph', 'process'), ('dijkstra', 'access', 'travel times', 'process'),
    ('census', 'access', 'people per block', 'data'), ('facilities', 'access', 'facility points', 'data'), ('dijkstra', 'efficiency', 'all-pairs travel times', 'process'),
    ('hrrr', 'gate', 'town 6 h / 24 h maxima', 'data'), ('gate', 'members', 'boxes to run', 'process'), ('members', 'rain_grid', 'one rain series per member', 'process'),
    ('pclose', 'kofn', 'p_close per member', 'process'), ('kofn', 'pirank', 'likely / possible list', 'process'), ('segdepth', 'pirank', 'depth, hours > 15 cm', 'data'),
    ('labels', 'matching', 'report points', 'label'), ('pclose', 'metrics', 'flags and ranking (replays)', 'label'), ('matching', 'metrics', 'sites', 'label'),
    ('baselines', 'metrics', 'baseline rankings', 'label'), ('split', 'metrics', 'which storms', 'label'), ('depth', 'gauges', 'modelled stage rise', 'label'),
    ('kofn', 'metrics', 'forecast lists (forward test)', 'label'),
    ('wi_culvert', 'notch', 'raised notch floor', 'whatif'), ('wi_amc', 'cn', 'CN_I / CN_III', 'whatif'), ('wi_frozen', 'cn', 'frozen CN', 'whatif'), ('wi_rain', 'rain_grid', 'rain × factor', 'whatif'),
    ('cc_edge', 'edge', 'missing mechanism', 'limit'), ('cc_debris', 'culvert', 'not predicted', 'limit'), ('cc_drains', 'lisflood', 'no pipes', 'limit'), ('cc_gw', 'cn', 'no subsurface', 'limit'),
]

# fixed layered layout: column = step along the main chain (inputs → grids → engine → outputs → roads → failure → access → validation),
# row inside the column; the forecast band sits above the inputs and grids it feeds, the what-if and limitation bands below.
LAYOUT = {
    'mrms': (0, 0), 'hrrr': (0, 1), 'lidar': (0, 2), 'nhd': (0, 3), 'crossings': (0, 4), 'ssurgo': (0, 5), 'nlcd': (0, 6), 'roads': (0, 7), 'census': (0, 8), 'facilities': (0, 9),
    'rain_grid': (1, 0), 'cn': (1, 1), 'dem20': (1, 2), 'channels': (1, 3), 'notch': (1, 4), 'breach': (1, 5), 'manning': (1, 6), 'crest': (1, 7),
    'lisflood': (2, 3), 'depth': (3, 2), 'velocity': (3, 5),
    'roadpts': (4, 1), 'segdepth': (4, 2), 'onset': (4, 3),
    'pclose': (5, 2), 'culvert': (5, 4), 'freeboard': (5, 5), 'fastwater': (5, 6), 'washout': (5, 7), 'edge': (5, 8),
    'pregnolato': (6, 1), 'graph': (6, 2), 'dijkstra': (6, 3), 'access': (6, 4), 'efficiency': (6, 5),
    'labels': (7, 0), 'matching': (7, 1), 'split': (7, 2), 'baselines': (7, 3), 'metrics': (7, 4.5), 'gauges': (7, 6),
    'gate': (0, -3), 'nbhd': (0, -2), 'members': (1, -3), 'spinup': (1, -2), 'phase': (1, -1.1), 'kofn': (5, -2), 'pirank': (6, -2),
    'wi_rain': (0, 11), 'wi_amc': (1, 11), 'wi_frozen': (2, 11), 'wi_culvert': (3, 11),
    'cc_gw': (1, 13), 'cc_drains': (2, 13), 'cc_debris': (4, 13), 'cc_edge': (5, 13),
}
COLS = ['Inputs', 'Grids', 'Flood engine', 'Engine outputs', 'Water on each road', 'How the road fails', 'Who loses access', 'Checked against reality']

FOLLOW = ['mrms', 'rain_grid', 'cn', 'lisflood', 'depth', 'roadpts', 'segdepth', 'onset', 'pclose', 'graph', 'dijkstra', 'access', 'labels', 'metrics']


# ------------------------------------------------------------------------------------------------ resolving refs
def _read(path): return open(os.path.join(ROOT, path)).read()


def _yml_env():
    env = {}
    for m in re.finditer(r"^\s+(LF_[A-Z0-9_]+|RES):\s*'?([^'#\n$]+?)'?\s*(#.*)?$", _read(YML), re.M):
        env.setdefault(m.group(1), m.group(2).strip())
    return env


def _consts(path):
    T = ast.parse(_read(path)); out = {}
    for st in T.body:
        if isinstance(st, ast.Assign):
            for t in st.targets:
                if isinstance(t, ast.Name):
                    try: out[t.id] = ast.literal_eval(st.value)
                    except Exception: pass
                elif isinstance(t, ast.Tuple) and isinstance(st.value, ast.Tuple):
                    for a, b in zip(t.elts, st.value.elts):
                        try: out[a.id] = ast.literal_eval(b)
                        except Exception: pass
    return out


def _num(v):
    try:
        f = float(v); return int(f) if f.is_integer() and '.' not in str(v) else f
    except Exception: return v


def resolve(ref):
    kind, rest = ref.split(':', 1)
    if kind == 'yml':
        v = _yml_env().get(rest)
        if v is None: raise KeyError(f'{rest} not in {YML}')
        return _num(v), f'{YML} env {rest}'
    if kind == 'const':
        path, name = rest.rsplit(':', 1); C = _consts(path)
        if name not in C: raise KeyError(f'{name} not a literal constant in {path}')
        return C[name], f'{path} {name}'
    if kind == 'dict':
        path, name, key = rest.split(':'); return _consts(path)[name][key], f'{path} {name}[{key!r}]'
    if kind == 'env':
        path, key = rest.rsplit(':', 1)
        m = re.search(r"os\.environ\.get\('" + re.escape(key) + r"',\s*'([^']*)'\)", _read(path))
        if not m: raise KeyError(f'no default for {key} in {path}')
        return _num(m.group(1)), f'{path} default of {key}'
    raise ValueError(ref)


def build_tree():
    nodes = []
    for n in N:
        n = json.loads(json.dumps(n))
        for p in n['parameters']:
            if p['ref']: p['value'], p['where'] = resolve(p['ref'])
            else: p['where'] = 'stated (not a code setting)'
        n['source'] = [dict(key=k, text=SRC[k][0], url=SRC[k][1]) for k in n['source']]
        n['next'] = [dict(to=b, what=l) for a, b, l, _ in E if a == n['id']]
        n['from'] = [dict(frm=a, what=l) for a, b, l, _ in E if b == n['id']]
        nodes.append(n)
    ids = {n['id'] for n in nodes}
    for a, b, _, _ in E: assert a in ids and b in ids, (a, b)
    assert set(LAYOUT) == ids, (ids ^ set(LAYOUT))
    for n in nodes: n['col'], n['row'] = LAYOUT[n['id']]
    return dict(title='Mass Flood Watch: model tree', made_by='proto/model_tree.py', stages=[dict(id=s, title=t, sub=u) for s, t, u in STAGES], columns=COLS,
                nodes=nodes, edges=[dict(source=a, target=b, label=l, kind=k) for a, b, l, k in E], follow=FOLLOW)


def cmd_build():
    os.makedirs(OUT, exist_ok=True); T = build_tree(); p = os.path.join(OUT, 'tree.json')
    json.dump(T, open(p, 'w'), indent=1, ensure_ascii=False); print('wrote', p, len(T['nodes']), 'nodes', len(T['edges']), 'edges')


def cmd_check():
    T = json.load(open(os.path.join(OUT, 'tree.json'))); rows = []; bad = 0
    for n in T['nodes']:
        for p in n['parameters']:
            if not p.get('ref'): rows.append((n['id'], p['name'], p['value'], '(stated)', 'n/a')); continue
            try: v, where = resolve(p['ref'])
            except Exception as e: v, where = None, f'ERROR {e}'
            ok = v == p['value']; bad += not ok
            rows.append((n['id'], p['name'], p['value'], f'{v} ({where})', 'OK' if ok else 'DIFFERENT'))
    links = [s['url'] for n in T['nodes'] for s in n['source'] if s['url']]
    missing_code = [c['path'] for n in T['nodes'] for c in n['code'] if not os.path.exists(os.path.join(ROOT, c['path'].rstrip('/')))]
    bad += len(missing_code)
    from datetime import datetime, timezone
    L = [f'# Model tree check ({datetime.now(timezone.utc):%Y-%m-%d %H:%MZ})', '',
         f'`python proto/model_tree.py check`: every parameter on the tree re-read from the code and the live forecast workflow '
         f'(`{YML}`) and compared with `docs/model-tree/tree.json`.', '',
         f'**Result: {"PASS" if not bad else "FAIL"}** — {sum(1 for r in rows if r[4] == "OK")} parameters match the code, {sum(1 for r in rows if r[4] == "n/a")} are stated values '
         f'(not code settings), {sum(1 for r in rows if r[4] == "DIFFERENT")} differ; {len(missing_code)} code links point to missing files; {len(set(links))} source links listed.', '',
         '| node | parameter | on the tree | in the code (where) | |', '|---|---|---|---|---|']
    L += [f'| {a} | {b} | {c} | {d} | {e} |' for a, b, c, d, e in rows]
    if missing_code: L += ['', 'Missing code paths: ' + ', '.join(missing_code)]
    open(os.path.join(OUT, 'CHECK.md'), 'w').write('\n'.join(L) + '\n'); print('\n'.join(L[:6])); return 0 if not bad else 1


def cmd_print():
    """docs/model-tree-print.html: the same content as one static, printable page (stage by stage), the backup of the interactive tree."""
    import html
    T = json.load(open(os.path.join(OUT, 'tree.json'))); e = html.escape; by = {n['id']: n for n in T['nodes']}; H = []
    for st in T['stages']:
        ns = [n for n in T['nodes'] if n['stage'] == st['id']]
        if not ns: continue
        H.append(f"<h2>{st['id']}. {e(st['title'])}</h2>")
        for n in ns:
            H.append(f"<section id='{n['id']}'><h3>{e(n['title'])} <span class='st'>{e(n['status'])}</span></h3><p class='plain'>{e(n['plain'])}</p><p>{e(n.get('what', ''))}</p>")
            meta = ' · '.join(x for x in (n.get('units'), n.get('resolution'), n.get('period')) if x)
            if meta: H.append(f"<p class='meta'>{e(meta)}</p>")
            if n.get('formula'): H.append(f"<div class='tex' data-tex='{e(n['formula'], quote=True)}'></div>")
            if n['parameters']:
                H.append('<table>' + ''.join(f"<tr><td>{e(p['name'])}<br><small>{e(p['origin'])} · {e(p['where'])}</small></td><td><b>{e(str(p['value']))} {e(p['unit'])}</b></td></tr>" for p in n['parameters']) + '</table>')
            if n.get('output'): H.append(f"<p><b>Out:</b> {e(n['output'])}</p>")
            if n['next']: H.append('<p><b>Goes to:</b> ' + '; '.join(f"<a href='#{x['to']}'>{e(by[x['to']]['title'])}</a> ({e(x['what'])})" for x in n['next']) + '</p>')
            if n.get('limits'): H.append(f"<p><b>Cannot capture:</b> {e(n['limits'])}</p>")
            if n['source']: H.append('<p class="src"><b>Sources:</b> ' + '; '.join((f"<a href='{e(s_['url'])}'>{e(s_['text'])}</a>" if s_['url'] else e(s_['text'])) for s_ in n['source']) + '</p>')
            if n['code']: H.append('<p class="src"><b>Code:</b> ' + '; '.join(f"<a href='{e(c['url'])}'><code>{e(c['path'])}</code></a> {e(c['fn'])}" for c in n['code']) + '</p>')
            H.append('</section>')
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Model Tree (printable) · Mass Flood Watch</title>'
            '<link rel="icon" href="wpi-logo.svg"><link rel="stylesheet" href="model-tree/lib/katex.min.css"><style>:root{--bg:#fff;--ink:#1f2328;--muted:#5d6670;--line:#ddd}'
            '@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14171b;--ink:#e8eaed;--muted:#a3abb4;--line:#33393f}}'
            'body{margin:0 auto;max-width:980px;padding:24px 16px 60px;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}'
            'h2{border-bottom:2px solid var(--line);padding-bottom:4px;margin-top:36px}section{break-inside:avoid;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:10px 0}'
            'h3{margin:0 0 4px}.st{font-size:12px;font-weight:400;color:var(--muted);border:1px solid var(--line);border-radius:99px;padding:1px 8px}.plain{font-size:16px}'
            '.meta,.src,small{color:var(--muted)}table{border-collapse:collapse;width:100%}td{border-top:1px solid var(--line);padding:4px;vertical-align:top}.tex{overflow-x:auto}a{color:#1f5f99}</style></head><body>'
            '<h1>Model tree (printable)</h1><p>The content of the <a href="model-tree.html">interactive model tree</a> as one page. Parameter values are read from the code '
            '(<code>proto/model_tree.py</code>, check: <a href="model-tree/CHECK.md">CHECK.md</a>).</p>' + '\n'.join(H) +
            '<script src="model-tree/lib/katex.min.js"></script><script>document.querySelectorAll(".tex").forEach(function(d){try{katex.render(d.dataset.tex,d,{displayMode:true,throwOnError:false})}catch(e){d.textContent=d.dataset.tex}})</script></body></html>')
    open(os.path.join(ROOT, 'docs', 'model-tree-print.html'), 'w').write(page); print('wrote docs/model-tree-print.html')


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else 'build'
    sys.exit({'build': cmd_build, 'check': cmd_check, 'print': cmd_print}[c]() or 0)
