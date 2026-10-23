"""Label expansion for MassDOT District 3 storms (docs/proto/obs/LABELS_EXPANSION.md).

Every site below is a road-level report copied from a public source (NWS Local Storm Report through IEM, NOAA NCEI Storm Events, or a
news story), with the source URL and a short verbatim quote.  Coordinates are placed afterwards:
  1. `queries`  writes docs/proto/obs/labels_geocode_queries.json for proto/label_geocode.py (OSM Overpass / Nominatim, run on Actions);
  2. `build`    reads docs/proto/obs/labels_geocode_osm.json, falls back to the MassGIS-derived docs/graph_segments.json road network,
               and writes proto/data/labels_<storm>_<area>.csv (same columns as the catalogue label files) plus
               docs/proto/obs/labels_expansion_sites.json (per-site geocode audit trail).

    python proto/labels_expand.py queries
    python proto/labels_expand.py build

Geocode modes (g):  pair  = closest approach of road a and feature b (intersection, rail underpass, river crossing): exact when the gap is
                            under 80 m and the report names that intersection/crossing, else approx
                    near  = vertex of road a nearest the NWS point `near` (Storm Events points have 4 decimals and are often the reported
                            place; LSR points are usually town centroids at 0.01 deg): approx
                    cent  = vertex nearest the road centroid (no location along the road given): approx
                    addr  = Nominatim street address, snapped to road a: approx
Coordinates are never invented: a site the geocoders cannot place keeps coord_quality `town` at the NWS point.
"""
import os, sys, csv, json, argparse, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
Q_PATH = os.path.join(ROOT, 'docs', 'proto', 'obs', 'labels_geocode_queries.json')
OSM_PATH = os.path.join(ROOT, 'docs', 'proto', 'obs', 'labels_geocode_osm.json')
AUDIT_PATH = os.path.join(ROOT, 'docs', 'proto', 'obs', 'labels_expansion_sites.json')
COLS = ['id', 'name', 'road', 'town', 'type', 'time_local', 'time_quality', 'lon', 'lat', 'coord_quality', 'source_url', 'quote', 'source']


def SE(i): return f'https://www.ncdc.noaa.gov/stormevents/eventdetails.jsp?id={i}'


def LSR(t):
    t = dt.datetime.strptime(t, '%Y-%m-%dT%H:%MZ'); a = t - dt.timedelta(hours=1); b = t + dt.timedelta(hours=1)
    return f'https://mesonet.agron.iastate.edu/lsr/#BOX/{a:%Y%m%d%H%M}/{b:%Y%m%d%H%M}'


CBS_FITCH = 'https://www.cbsnews.com/boston/news/fitchburg-massachusetts-flash-flooding/'
B25_AUG26 = 'https://www.boston25news.com/news/local/flooding-leaves-massachusetts-roads-impassable-severe-storms-move-through/OO2KJN6FTNH6XI7HSTHMGA5AVA/'
CBS_AUG26 = 'https://www.cbsnews.com/boston/news/leominster-shirley-storm-damage-rain-wind/'
B25_JUL18 = 'https://www.boston25news.com/news/severe-weather-leaves-several-roads-flooded-throughout-worcester-county/792274888'
WHDH_AUG21 = 'https://whdh.com/news/flash-flooding-leaves-dozens-of-motorists-stranded-in-submerged-cars-in-worcester/'

# Storm files.  `new`: storm added to the catalogue in this expansion; otherwise rows are appended to the existing label file.
FILES = {'may2018': 'labels_may2018_shrewsbury.csv', 'aug2018b': 'labels_aug2018b_holden.csv', 'sep2018': 'labels_sep2018_fitchburg.csv',
         'sep2018w': 'labels_sep2018w_shrewsbury.csv', 'sep2018b': 'labels_sep2018b_gardner.csv', 'jul2019': 'labels_jul2019_spencer.csv',
         'aug2019': 'labels_aug2019_oxford.csv', 'sep2019': 'labels_sep2019_northbridge.csv', 'jun2020': 'labels_jun2020_northbridge.csv',
         'jun2020b': 'labels_jun2020b_gardner.csv', 'aug2020b': 'labels_aug2020b_worcester.csv', 'jul2021b': 'labels_jul2021b_worcester.csv',
         'jul2023b': 'labels_jul2023b_worcester.csv', 'jul2023c': 'labels_jul2023c_fitchburg.csv', 'jul2023d': 'labels_jul2023d_hubbardston.csv',
         # existing storms: news-sourced additions appended with N-numbered ids
         'jul2018': 'labels_jul2018_worcester.csv', 'aug2020': 'labels_aug2020_worcester.csv', 'aug2021': 'labels_aug2021_worcester.csv',
         'aug2026': 'labels_aug2026_leominster.csv', 'sep2018m': 'labels_sep2018m_milford.csv'}

# (storm, town, road, name, type, t_utc | date, quote, url, source, geocode)
#   t_utc 'YYYY-MM-DDTHH:MMZ' -> time_quality report;  'YYYY-MM-DD' -> day
S = [
 # ---- may2018: 15 May 2018 thunderstorms, Worcester / Shrewsbury (LSR only; Storm Events has no rows here) ----
 ('may2018', 'Shrewsbury', 'Route 9', 'Route 9 westbound at Lake Street: closed', 'closed', '2018-05-15T21:10Z',
  'RTE 9 WESTBOUND AT LAKE STREET CLOSEWD DUE TO FLOODING', LSR('2018-05-15T21:10Z'), 'LSR', dict(g='pair', a='ref:MA 9|Route 9|Boston Turnpike', b='Lake Street', near=(-71.72, 42.30))),
 ('may2018', 'Shrewsbury', 'Maple Avenue', 'Maple Avenue: impassable', 'impassable', '2018-05-15T21:10Z',
  'ROUTE 9 WESTBOUND AT LAKE STREET CLOSED DUE TO FLOODING_ MAPLE AVENUE AT SALON PLAZA FLOODED AND IMPASSABLE', LSR('2018-05-15T21:10Z'), 'LSR', dict(g='cent', a='Maple Avenue', near=(-71.72, 42.30))),
 ('may2018', 'Worcester', 'I-290', 'I-290 westbound at Route 146 southbound: flooded', 'flooded', '2018-05-15T21:10Z',
  'ONE FOOT OF STREET FLOODING ON ROUTE 290 WEST AT ROUTE 146 SOUTH', LSR('2018-05-15T21:10Z'), 'LSR', dict(g='pair', a='ref:I 290', b='ref:MA 146', near=(-71.81, 42.27))),
 ('may2018', 'Millville', 'Central Street', 'Central Street near the bike path: impassable', 'impassable', '2018-05-15T22:20Z',
  'At 5:20 PM EST in Millville, a car was trapped in flood waters on Central Street near the Bike Path.', SE(748721), 'StormEvents', dict(g='near', a='Central Street', near=(-71.5826, 42.0235))),
 ('may2018', 'Blackstone', 'Main Street', 'Main Street: impassable', 'impassable', '2018-05-15T22:23Z',
  'At 5:23 PM EST, Main Street in Blackstone was flooded and impassable.  A car was trapped in the floodwaters and towed out.', SE(748722), 'StormEvents', dict(g='near', a='Main Street', near=(-71.5448, 42.018))),
 # ---- aug2018b: 11 Aug 2018 thunderstorms, Holden / Spencer / West Boylston ----
 ('aug2018b', 'Holden', 'Main Street', 'Main Street: flooded', 'flooded', '2018-08-11T15:00Z',
  'ON MAIN STREET 6 INCHES OF STREET FLOODING FROM CURB TO CURB', LSR('2018-08-11T15:00Z'), 'LSR', dict(g='near', a='Main Street|ref:MA 122A', near=(-71.85, 42.35))),
 ('aug2018b', 'Spencer', 'Donnelly Road', 'Donnelly Road: flooded', 'flooded', '2018-08-11T15:10Z',
  'SIGNIFICANT STREET FLOODING ON DONNELLY ROAD', LSR('2018-08-11T15:10Z'), 'LSR', dict(g='cent', a='Donnelly Road', near=(-71.99, 42.24))),
 ('aug2018b', 'West Boylston', 'Crescent Street', 'Crescent Street: impassable', 'impassable', '2018-08-11T23:03Z',
  'At 6:03 PM EST, Crescent Street was flooded and impassable.', SE(780608), 'StormEvents', dict(g='near', a='Crescent Street', near=(-71.7908, 42.3745))),
 ('aug2018b', 'Lancaster', 'Main Street', 'Main Street at the railroad underpass: flooded', 'flooded', '2018-08-12T00:27Z',
  'FLOODING ON MAIN STREET IN THE AREA OF THE UNDERPASS AT THE MAIN STREET BRIDGE. WATER DEPTH IS 2 AND A HALF FEET', LSR('2018-08-12T00:27Z'), 'LSR',
  dict(g='pair', a='Main Street|ref:MA 70', b='rail', near=(-71.67, 42.45), q='approx')),     # two Main St rail crossings in Lancaster
 # ---- sep2018: 18 Sep 2018, remnants of Florence, north Worcester County ----
 ('sep2018', 'Gardner', 'Walnut Street', 'Walnut Street: flooded', 'flooded', '2018-09-18T13:58Z',
  'At 8:58 AM EST, Walnut Street in Gardner was flooded.', SE(783711), 'StormEvents', dict(g='near', a='Walnut Street', near=(-71.9864, 42.5779))),
 ('sep2018', 'Fitchburg', 'Princeton Road', 'Princeton Road (Route 31) railroad underpass: flooded', 'flooded', '2018-09-18T14:16Z',
  'MODERATE FLOODING UNDER SEVERAL RAILROAD UNDERPASSES INCLUDING AT PRINCETON RD (RT 31) AND ROUTE 2A.', LSR('2018-09-18T14:16Z'), 'LSR',
  dict(g='pair', a='Princeton Road|ref:MA 31', b='rail', towns=['Fitchburg', 'Westminster'], near=(-71.8457, 42.5518))),
 ('sep2018', 'Fitchburg', 'Route 2A', 'Route 2A railroad underpass: flooded', 'flooded', '2018-09-18T14:16Z',
  'At 9:16 AM EST, moderate flooding was reported under several railroad underpasses southwest of Fitchburg. This included Princeton Road and State Route 2A.', SE(783714), 'StormEvents',
  dict(g='pair', a='ref:MA 2A', b='rail', towns=['Fitchburg', 'Westminster'], near=(-71.8756, 42.5583), q='approx')),
 ('sep2018', 'Hubbardston', 'Brigham Street', 'Brigham Street at the West Branch Ware River: flooded', 'flooded', '2018-09-18T14:30Z',
  'At 9:30 AM EST, the West Branch of the Ware River in Hubbardston overflowed its banks and flooded Brigham Street.', SE(783719), 'StormEvents',
  dict(g='pair', a='Brigham Street', b='water:West Branch Ware River', near=(-71.9978, 42.4781))),
 ('sep2018', 'Ashburnham', 'Route 12', 'Route 12 by Jewell Hill Road: flooded', 'flooded', '2018-09-18T15:49Z',
  'ROUTE 12 BY JEWELL HILL ROAD FLOODED', LSR('2018-09-18T15:49Z'), 'LSR', dict(g='pair', a='ref:MA 12', b='Jewell Hill Road', near=(-71.90, 42.63))),
 # ---- sep2018w: the same storm (Florence), Worcester / Shrewsbury ----
 ('sep2018w', 'Worcester', 'Route 20', 'Route 20 at the Grafton Street (Route 122) overpass: flooded', 'flooded', '2018-09-18T14:23Z',
  'At 9:23 AM EST, U.S. Route 20 in Worcester was flooded at the Grafton Street overpass.', SE(783716), 'StormEvents',
  dict(g='pair', a='ref:US 20', b='ref:MA 122|Grafton Street', towns=['Worcester', 'Millbury'], near=(-71.7498, 42.2366))),
 ('sep2018w', 'Shrewsbury', 'Maple Avenue', 'Maple Avenue at Route 9: impassable', 'impassable', '2018-09-18T14:32Z',
  'At 9:32 AM EST, the intersection of Maple Avenue and State Route 9 in Shrewsbury was flooded and impassable.', SE(783721), 'StormEvents',
  dict(g='pair', a='Maple Avenue', b='ref:MA 9|Route 9|Boston Turnpike', near=(-71.74, 42.275))),
 ('sep2018w', 'Shrewsbury', 'Floral Street', 'Floral Street: impassable', 'impassable', '2018-09-18T17:36Z',
  'At 12:36 PM EST, Floral Street in Shrewsbury was flooded and impassable.', SE(786796), 'StormEvents', dict(g='near', a='Floral Street', near=(-71.6967, 42.2829))),
 ('sep2018w', 'Marlborough', 'Farm Road', 'Farm Road near Clarke Drive: impassable', 'impassable', '2018-09-18T14:53Z',
  'At 9:53 AM EST, a car was trapped in floodwaters on Farm Road near Clarke Drive in Marlborough.', SE(783727), 'StormEvents',
  dict(g='pair', a='Farm Road', b='Clarke Drive|Clark Drive', near=(-71.5176, 42.3427))),
 # ---- sep2018b: 26 Sep 2018 evening downpours, Gardner / Templeton / Westminster ----
 ('sep2018b', 'Templeton', 'Baldwinville Road', 'Baldwinville Road: flooded', 'flooded', '2018-09-27T01:10Z',
  'SECTION OF BALDWINVILLE ROAD IS FLOODED', LSR('2018-09-27T01:10Z'), 'LSR', dict(g='near', a='Baldwinville Road', near=(-72.07, 42.56))),
 ('sep2018b', 'Gardner', 'West Broadway', 'West Broadway (Route 2A): impassable', 'impassable', '2018-09-27T01:22Z',
  'CAR STUCK IN FLOOD WATERS ON WEST BROADWAY (ROUTE 2A)', LSR('2018-09-27T01:22Z'), 'LSR', dict(g='cent', a='West Broadway', near=(-71.99, 42.58))),
 ('sep2018b', 'Templeton', 'South Main Street', 'South Main Street: flooded', 'flooded', '2018-09-27T01:34Z',
  'SECTION OF SOUTH MAIN STREET FLOODED', LSR('2018-09-27T01:34Z'), 'LSR', dict(g='near', a='South Main Street', near=(-72.07, 42.55))),
 ('sep2018b', 'Gardner', 'Risley Street', 'Risley Street at John Street: impassable', 'impassable', '2018-09-27T01:46Z',
  'At 8:46 PM EST, a car was trapped in flood waters on Risley Street and John Street in Gardner.', SE(786829), 'StormEvents',
  dict(g='pair', a='Risley Street', b='John Street', near=(-71.9962, 42.564))),
 ('sep2018b', 'Gardner', 'Leo Drive', 'Leo Drive: impassable', 'impassable', '2018-09-27T02:05Z',
  'At 9:05 PM EST, Leo Drive in Gardner was flooded and impassable.', SE(786831), 'StormEvents', dict(g='near', a='Leo Drive', near=(-72.016, 42.596))),
 ('sep2018b', 'Westminster', 'Oakmont Avenue', 'South Avenue at Oakmont Avenue: flooded', 'flooded', '2018-09-27T02:06Z',
  'SIGNIFICANT FLOODING AT THE INTERSECTION OF SOUTH AVE AND OAKMOUNT AVE', LSR('2018-09-27T02:06Z'), 'LSR',
  dict(g='near', a='Oakmont Avenue', towns=['Westminster'], near=(-71.90, 42.55), osm=False)),    # OSM has no South Avenue there (it matched South Street)
 ('sep2018b', 'Templeton', 'Boulder Drive', 'Boulder Drive: flooded (manhole covers lifting)', 'flooded', '2018-09-27T02:12Z',
  'MANHOLE COVERS STARTING TO COME OFF THE GROUND FROM FLOODING ON BOULDER DRIVE', LSR('2018-09-27T02:12Z'), 'LSR', dict(g='cent', a='Boulder Drive', near=(-72.07, 42.55))),
 # ---- jul2019: 6 Jul 2019 thunderstorms, Spencer / Worcester / Oxford ----
 ('jul2019', 'Worcester', 'Armory Street', 'Armory Street: flooded', 'flooded', '2019-07-06T21:25Z',
  'Flooding was reported on Armory Street in South Worcester with water flowing over the curb.', SE(837555), 'StormEvents', dict(g='near', a='Armory Street', near=(-71.8157, 42.2466))),
 ('jul2019', 'Spencer', 'Pleasant Street', 'Pleasant Street: impassable', 'impassable', '2019-07-06T21:26Z',
  'Pleasant Street in Spencer was flooded an impassable, with manhole covers popped off.', SE(837556), 'StormEvents', dict(g='near', a='Pleasant Street|ref:MA 31', near=(-71.9992, 42.2488))),
 ('jul2019', 'Spencer', 'South Spencer Road', 'South Spencer Road at the railroad overpass near Lyford Cross Road: impassable', 'impassable', '2019-07-06T21:30Z',
  'More than three feet of street flooding occurred on South Spencer Road near the railroad overpass at Lyford Cross Road in Spencer, MA.  The road was impassable.', SE(836176), 'StormEvents',
  dict(g='pair', a='South Spencer Road', b='rail', near=(-72.014, 42.218))),
 ('jul2019', 'Worcester', 'Route 20', 'Route 20 at Route 122A: flooded', 'flooded', '2019-07-06T21:54Z',
  'Several feet of street flooding was reported near the intersection of Routes 20 and 122A on the border of Worcester and Millbury.', SE(838478), 'StormEvents',
  dict(g='pair', a='ref:US 20', b='ref:MA 122A', towns=['Worcester', 'Millbury'], near=(-71.7826, 42.2171))),
 ('jul2019', 'Oxford', 'Sutton Avenue', 'Sutton Avenue: flooded', 'flooded', '2019-07-06T21:56Z',
  'Flooding was reported on Sutton Ave in Oxford.', SE(837571), 'StormEvents', dict(g='near', a='Sutton Avenue', near=(-71.8596, 42.1167))),
 # ---- aug2019: 7 Aug 2019 evening storms, Oxford / Worcester (small) ----
 ('aug2019', 'Oxford', 'Sutton Avenue', 'I-395 exit 4B ramp at Sutton Avenue: impassable', 'impassable', '2019-08-08T02:01Z',
  'In Oxford, the Sutton Avenue Exit (4B) off of I-395 was flooded with one foot of water and impassable.', SE(850621), 'StormEvents',
  dict(g='pair', a='Sutton Avenue', b='ref:I 395', near=(-71.85, 42.12), q='approx')),
 ('aug2019', 'Worcester', 'Southbridge Street', 'I-290 eastbound exit ramp at Southbridge Street: flooded', 'flooded', '2019-08-08T02:40Z',
  'In the southern portion of Worcester, the Southbridge Street exit ramp off of I-290 eastbound had substantial flooding at the bottom of the ramp.', SE(850623), 'StormEvents',
  dict(g='net', a='Ramp-Rt 290 Eb To Southbridge St Nb', b='Southbridge Street', near=(-71.81, 42.24))),
 # ---- sep2019: 2 Sep 2019 storms, Oxford / Whitinsville (small) ----
 ('sep2019', 'Oxford', 'Sutton Avenue', 'Sutton Avenue: closed', 'closed', '2019-09-02T21:36Z',
  'In Oxford, a portion of Sutton Avenue was closed due to flooding.', SE(852468), 'StormEvents', dict(g='near', a='Sutton Avenue', near=(-71.8332, 42.1104))),
 ('sep2019', 'Northbridge', 'Park Street', 'Park Street at Cottage Street: impassable', 'impassable', '2019-09-02T21:48Z',
  'In the Whitinsville section of Northbridge, Park Street at Cottage Street was flooded and impassable for a time.', SE(852469), 'StormEvents',
  dict(g='pair', a='Park Street', b='Cottage Street', near=(-71.6636, 42.1122))),
 ('sep2019', 'Milford', 'Central Street', 'Central Street at North and South Bow Streets: closed', 'closed', '2019-09-02T21:55Z',
  'In Milford, Central Street at South Bow and North Bow Street was closed for a time due to flooding.', SE(852470), 'StormEvents',
  dict(g='pair', a='Central Street', b='North Bow Street|South Bow Street', near=(-71.516, 42.1398))),
 ('sep2019', 'Marlborough', 'Prospect Street', 'Prospect Street at Main Street: flooded', 'flooded', '2019-09-02T21:36Z',
  'In Marlborough, Prospect Street at Main Street was flooded.', SE(852467), 'StormEvents', dict(g='pair', a='Prospect Street', b='Main Street', near=(-71.5518, 42.3469))),
 # ---- jun2020: 28 Jun 2020 flash flooding, Blackstone Valley ----
 ('jun2020', 'Northbridge', 'Cross Street', 'Cross Street near East Street: flooded (3 ft)', 'flooded', '2020-06-28T21:31Z',
  'In the Whitinsville section of Northbridge, flash flooding occurred, with 3 feet of water on Cross Street near East Street.', SE(897825), 'StormEvents',
  dict(g='pair', a='Cross Street', b='East Street', near=(-71.6598, 42.1111))),
 ('jun2020', 'Northbridge', 'Church Street', 'Church Street: impassable', 'impassable', '2020-06-28T21:49Z',
  'In Northbridge, there was flooding on Church Street with road impassable.', SE(899290), 'StormEvents', dict(g='near', a='Church Street', near=(-71.6532, 42.1163))),
 ('jun2020', 'Hopedale', 'Adin Street', 'Adin Street at Mendon Street (Route 16): flooded', 'flooded', '2020-06-28T21:51Z',
  'In Hopedale, flooding was reported at the intersection of Adin Street and Mendon Street (Route 16).', SE(899292), 'StormEvents',
  dict(g='pair', a='Adin Street', b='Mendon Street|ref:MA 16', near=(-71.5288, 42.1314))),
 ('jun2020', 'Blackstone', 'Rathbun Street', 'Rathbun Street: impassable', 'impassable', '2020-06-28T22:19Z',
  'In Blackstone, two cars were stuck in flood waters on Rathbun Street. Roadway was impassable.', SE(899322), 'StormEvents', dict(g='near', a='Rathbun Street', near=(-71.5013, 42.0214))),
 ('jun2020', 'Uxbridge', 'Quaker Highway', 'Quaker Highway (Route 146A): flooded with debris', 'flooded', '2020-06-28T22:36Z',
  'In Uxbridge, many sections of Quaker Highway (Route 146A) were flooded, with debris across the road.', SE(899325), 'StormEvents', dict(g='near', a='Quaker Highway|ref:MA 146A', near=(-71.6047, 42.0389))),
 ('jun2020', 'Uxbridge', 'Route 122', 'Route 122: flooded with rocks in the road', 'flooded', '2020-06-28T22:36Z',
  'Also, Route 122 was flooded, with rocks in the road.', SE(899325), 'StormEvents', dict(g='near', a='ref:MA 122', near=(-71.6047, 42.0389))),
 ('jun2020', 'Franklin', 'Brook Street', 'Brook Street: impassable', 'impassable', '2020-06-28T22:18Z',
  'In Franklin, a portion of Brook Street was flooded and impassable.', SE(899316), 'StormEvents', dict(g='near', a='Brook Street', near=(-71.3898, 42.1078))),
 ('jun2020', 'Franklin', 'Sargent Lane', 'Sargent Lane at Dartmouth Road: flooded', 'flooded', '2020-06-28T22:45Z',
  'Street flooding was reported on Sargent Lane at Dartmouth Road.', SE(899331), 'StormEvents', dict(g='pair', a='Sargent Lane', b='Dartmouth Road', near=(-71.3917, 42.0977))),
 # ---- jun2020b: same evening, Gardner / Fitchburg (and one Worcester report) ----
 ('jun2020b', 'Gardner', 'Route 2A', 'Route 2A: flooded (1 ft)', 'flooded', '2020-06-28T23:18Z',
  'There was one foot of water on a section of Route 2A at 618 PM EST.', SE(899348), 'StormEvents', dict(g='near', a='ref:MA 2A', near=(-72.0034, 42.5774))),
 ('jun2020b', 'Gardner', 'Timpany Boulevard', 'Timpany Boulevard: impassable', 'impassable', '2020-06-28T23:43Z',
  'A car was stuck in flooding on Timpany Blvd. at 643 PM EST.', SE(899348), 'StormEvents', dict(g='cent', a='Timpany Boulevard', near=(-71.99, 42.58))),
 ('jun2020b', 'Gardner', 'Chestnut Street', 'Chestnut Street at Union Square: impassable', 'impassable', '2020-06-28T23:48Z',
  'Chestnut Street at Union Square was flooded and impassable at 648 PM EST.', SE(899348), 'StormEvents',
  dict(g='pair', a='Chestnut Street', b='Union Square|Union Street', near=(-71.99, 42.575))),
 ('jun2020b', 'Gardner', 'Jean Street', 'Jean Street: flooded (1 ft)', 'flooded', '2020-06-29T00:15Z',
  'ON JEAN STREET_ THERE WAS ONE FOOT OF STREET FLOODING_ THE GREENWOOD PLAYGROUND WAS FLOODED_ AND THERE WERE FLOODED BASEMENTS.', LSR('2020-06-29T00:15Z'), 'LSR',
  dict(g='cent', a='Jean Street', near=(-71.99, 42.58))),
 ('jun2020b', 'Fitchburg', 'Princeton Road', 'Princeton Road bridge: impassable', 'impassable', '2020-06-28T23:53Z',
  'A car was stuck in flooding on Princeton Road on the Princeton Road Bridge.', SE(899733), 'StormEvents',
  dict(g='near', a='Princeton Road|ref:MA 31', towns=['Fitchburg', 'Westminster'], near=(-71.8457, 42.5518))),
 ('jun2020b', 'Worcester', 'West Boylston Street', 'West Boylston Street: impassable (3 ft)', 'impassable', '2020-06-29T00:30Z',
  'A car was stuck in flood waters three feet deep on West Boylston Street, in an area that typically receives flooding.', SE(899734), 'StormEvents',
  dict(g='near', a='West Boylston Street|ref:MA 12', near=(-71.7977, 42.3137))),
 # ---- aug2020b: 27 Aug 2020, Worcester ----
 ('aug2020b', 'Worcester', 'Whipple Street', 'Whipple Street at Blackstone River Road: flooded', 'flooded', '2020-08-27T18:18Z',
  'In Worcester, flooding was reported on Whipple Street at Blackstone River Road with manhole covers floating.', SE(916702), 'StormEvents',
  dict(g='pair', a='Whipple Street', b='Blackstone River Road', near=(-71.7947, 42.2326))),
 ('aug2020b', 'Worcester', 'College Street', 'College Street at Southbridge Street: flooded', 'flooded', '2020-08-27T18:18Z',
  'Also, flooding was reported on College Street at Southbridge Street.', SE(916702), 'StormEvents', dict(g='pair', a='College Street', b='Southbridge Street', near=(-71.81, 42.245))),
 ('aug2020b', 'Worcester', 'Route 20', 'Route 20 (Southwest Cutoff) near 86 Southwest Cutoff: impassable, rescues', 'impassable', '2020-08-27T18:30Z',
  'In the southeast part of Worcester, law enforcement reported that several cars were stuck in flooding on Route 20 at the 86 Cutoff. A few rescues of people were being conducted.', SE(916713), 'StormEvents',
  dict(g='addr', a='ref:US 20', addr='86 Southwest Cutoff, Worcester, MA', near=(-71.7495, 42.2354))),
 # ---- jul2021b: 17-18 Jul 2021, Worcester / Leicester (MRMS Pass2 on AWS) ----
 ('jul2021b', 'Worcester', 'Millbury Street', 'Millbury Street at McKeon Road: impassable', 'impassable', '2021-07-17T21:21Z',
  'In the southern part of Worcester, cars were stuck in flood waters at Millbury Street and McKeon Road.', SE(974621), 'StormEvents',
  dict(g='pair', a='Millbury Street', b='McKeon Road', near=(-71.7932, 42.2367))),
 ('jul2021b', 'Worcester', 'Dale Street', 'Dale Street: flooded to car windshields', 'flooded', '2021-07-17T21:24Z',
  'In Worcester, flash flood waters were up to car windshields on Dale Street.', SE(974625), 'StormEvents', dict(g='near', a='Dale Street', near=(-71.8103, 42.2584))),
 ('jul2021b', 'Worcester', 'Dewey Street', 'Dewey Street at Parker Street: impassable (five cars stuck)', 'impassable', '2021-07-17T22:07Z',
  'In Worcester, five cars were stuck in flood waters at Dewey Street and Parker Street.', SE(974628), 'StormEvents',
  dict(g='pair', a='Dewey Street', b='Parker Street', near=(-71.8216, 42.2587))),
 ('jul2021b', 'Leicester', 'Route 56', 'Route 56 at Marshall Street: flooded with debris', 'flooded', '2021-07-18T08:46Z',
  'In Leicester, Route 56 at Marshall Street was flooded, with debris in the roadway.  May be because of the Kettle Brook.', SE(974704), 'StormEvents',
  dict(g='pair', a='ref:MA 56', b='Marshall Street', near=(-71.9065, 42.2771))),
 # ---- jul2023b: 10 Jul 2023 (the Vermont-flood day), Worcester / Rutland (small) ----
 ('jul2023b', 'Worcester', 'Route 20', 'Route 20 (Southwest Cutoff) near 86 Southwest Cutoff: impassable (4 cars stuck)', 'impassable', '2023-07-10T15:58Z',
  'Area of 86 southwest cutoff flooded with 4 cars stuck in flood waters.', LSR('2023-07-10T15:58Z'), 'LSR',
  dict(g='addr', a='ref:US 20', addr='86 Southwest Cutoff, Worcester, MA', near=(-71.7495, 42.2354))),
 ('jul2023b', 'Rutland', 'Route 56', 'Route 56 at Vista Circle: flooded', 'flooded', '2023-07-10T20:43Z',
  'Route 56 at Vista Circle is heavily flooded. Relayed amateur radio.', LSR('2023-07-10T20:43Z'), 'LSR', dict(g='pair', a='ref:MA 56', b='Vista Circle', near=(-71.9596, 42.3876))),
 ('jul2023b', 'Gardner', 'Ripley Street', 'Ripley Street: closed (car stuck)', 'closed', '2023-07-10T20:45Z',
  'Ripley Street flooded and impassable_ car stuck in flooding - road is closed. Relayed by amateur radio.', LSR('2023-07-10T20:45Z'), 'LSR', dict(g='cent', a='Ripley Street', near=(-72.00, 42.56))),
 ('jul2023b', 'Douglas', 'Gilboa Road', 'Gilboa Road: flooded', 'flooded', '2023-07-10T14:17Z',
  'In Douglas, Gilboa Rd has significant street flooding.', SE(1117592), 'StormEvents', dict(g='near', a='Gilboa Road', near=(-71.7062, 42.08))),
 # ---- jul2023c: 16 Jul 2023, Fitchburg ----
 ('jul2023c', 'Fitchburg', 'Franklin Road', 'Franklin Road at Royalston Street: impassable (waist deep)', 'impassable', '2023-07-16T14:05Z',
  'Franklin Road at Royalston Street ca stuck in street flooding that was waist deep. Relayed by Amateur Radio.', LSR('2023-07-16T14:05Z'), 'LSR',
  dict(g='pair', a='Franklin Road', b='Royalston Street|Royalston Road', near=(-71.8248, 42.5689))),
 ('jul2023c', 'Fitchburg', 'Birch Street', 'Birch Street: pavement destroyed, asphalt in the road', 'washout', '2023-07-16T15:44Z',
  'In Fitchburg there was structural damage to Birch St. Large sections of asphalt were lying on the road with rushing water.', SE(1118097), 'StormEvents', dict(g='near', a='Birch Street', near=(-71.7926, 42.5741))),
 ('jul2023c', 'Fitchburg', 'John Fitch Highway', 'John Fitch Highway: flooded', 'flooded', '2023-07-16',
  'Flooding was also reported around John Fitch Highway and Lunenburg Street.', CBS_FITCH, 'news', dict(g='cent', a='John Fitch Highway', near=(-71.78, 42.59))),
 ('jul2023c', 'Fitchburg', 'Lunenburg Street', 'Lunenburg Street: flooded', 'flooded', '2023-07-16',
  'Flooding was also reported around John Fitch Highway and Lunenburg Street.', CBS_FITCH, 'news', dict(g='near', a='Lunenburg Street', near=(-71.783, 42.5889))),
 ('jul2023c', 'Rutland', 'Pleasantdale Road', 'Pleasantdale Road: impassable', 'impassable', '2023-07-16T15:25Z',
  'In Rutland, Pleasantdale Road was flooded and impassable.', SE(1118096), 'StormEvents', dict(g='near', a='Pleasantdale Road', near=(-71.9813, 42.3508))),
 # ---- jul2023d: 21 Jul 2023, Leominster / Hubbardston ----
 ('jul2023d', 'Leominster', 'Route 2', 'Route 2 near mile marker 98: closed both directions', 'closed', '2023-07-21T22:05Z',
  'MassDOT social media account reports that both eastbound and westbound sides of Route 2 near mile marker 98 in Leominster are closed due to flooding.', LSR('2023-07-21T22:05Z'), 'LSR',
  dict(g='near', a='ref:MA 2', towns=['Leominster', 'Fitchburg'], near=(-71.7621, 42.5467))),
 ('jul2023d', 'Hubbardston', 'Route 68', 'Route 68 in the town centre: impassable (car in floodwaters)', 'impassable', '2023-07-21T22:00Z',
  'Social media photo of urban flooding on route 68 in the center of Hubbardston_ with a car in floodwaters.', LSR('2023-07-21T22:00Z'), 'LSR',
  dict(g='near', a='ref:MA 68', near=(-72.0062, 42.4737))),
 ('jul2023d', 'Hubbardston', 'Williamsville Road', 'Williamsville Road: flooded', 'flooded', '2023-07-21T22:30Z',
  'Williamsville Rd flooded in Hubbardston with DPW assistance requested. relayed by amateur radio.', LSR('2023-07-21T22:30Z'), 'LSR', dict(g='near', a='Williamsville Road', near=(-72.01, 42.48))),
 # ---- additions to existing storms (news) ----
 ('jul2018', 'Worcester', 'Quinsigamond Avenue', 'Quinsigamond Avenue: cars stranded, towed', 'impassable', '2018-07-17',
  'On Quinsigamond Avenue, there were more victims of flash flooding', B25_JUL18, 'news', dict(g='cent', a='Quinsigamond Avenue', near=(-71.80, 42.25))),
 ('aug2020', 'Worcester', 'Washington Square', 'Washington Square: flooded', 'flooded', '2020-08-23T21:41Z',
  'In Worcester, Washington Square was flooded to an unknown depth.', SE(916327), 'StormEvents', dict(g='near', a='Washington Square', near=(-71.795, 42.2615))),
 ('aug2021', 'Worcester', 'Sever Street', 'Sever Street: flooded (kayaker in the street)', 'flooded', '2021-08-19',
  'a kayaker paddling down a flooded Seaver Street in Worcester', WHDH_AUG21, 'news', dict(g='cent', a='Sever Street', near=(-71.81, 42.27))),
 ('aug2026', 'Leominster', 'Merriam Avenue', 'Merriam Avenue at the Route 2 interchange: closed', 'closed', '2026-08-03',
  'Merriam Avenue at the Route 2 interchange was closed for roadway flooding', B25_AUG26, 'news',
  dict(g='pair', a='Merriam Avenue', b='ref:MA 2', towns=['Leominster', 'Fitchburg'], near=(-71.78, 42.55), q='approx')),
 ('aug2026', 'Fitchburg', 'Route 2', 'Route 2 westbound: vehicles stranded', 'impassable', '2026-08-03',
  "Monday morning's heavy rain led to flash flooding on Route 2 in Fitchburg.", CBS_AUG26, 'news', dict(g='cent', a='ref:MA 2', towns=['Fitchburg'], near=(-71.80, 42.55))),
 ('aug2026', 'Leominster', 'Granite Street', 'Granite Street: pavement buckled, road shut', 'other_damage', '2026-08-03',
  'Parts of Granite and Helena streets buckled, shutting down the road.', CBS_AUG26, 'news', dict(g='pair', a='Granite Street', b='Helena Street', near=(-71.76, 42.52), q='approx')),
 # ---- sep2018m: Florence 18 Sep 2018, third cluster (Milford / Bellingham / Uxbridge); appended last so earlier geocode keys stay stable ----
 ('sep2018m', 'Uxbridge', 'Route 122', 'Route 122 at Hazel Street: flooded', 'flooded', '2018-09-18T15:40Z',
  'ROUTE 122 AT HAZEL STREET FLOODED', LSR('2018-09-18T15:40Z'), 'LSR', dict(g='pair', a='ref:MA 122', b='Hazel Street', near=(-71.60, 42.08))),
 ('sep2018m', 'Bellingham', 'Monique Drive', 'Monique Drive: impassable', 'impassable', '2018-09-18T15:44Z',
  'At 10:44 AM EST, Monique Drive in Bellingham was reported flooded and impassable.', SE(786780), 'StormEvents', dict(g='near', a='Monique Drive', near=(-71.4804, 42.112))),
 ('sep2018m', 'Milford', 'North Bow Street', 'North Bow Street: impassable', 'impassable', '2018-09-18T15:44Z',
  'At 10:44 AM EST, North Bow Street in Milford was reported flooded and impassable.', SE(786782), 'StormEvents', dict(g='near', a='North Bow Street', near=(-71.5164, 42.1429))),
 ('sep2018m', 'Bellingham', 'Caroline Drive', 'Caroline Drive: impassable (water to car bumper)', 'impassable', '2018-09-18T16:35Z',
  'At 11:35 AM EST, Caroline Drive in Bellingham was reported flooded and impassable.', SE(786787), 'StormEvents', dict(g='near', a='Caroline Drive', near=(-71.4797, 42.1014))),
]

# Coordinate / name fixes to existing catalogue labels (item 4 of the expansion; changelog in LABELS_EXPANSION.md).
#   (file, id, town, geocode, field overrides).  Coordinates change only when OSM places the named intersection within 80 m (-> exact) or,
#   for rows that were town-level, when the named road is found (-> approx).
FIX = [
 ('labels_aug2015_natick.csv', 'AUG2015-02', 'Natick', dict(g='pair', a='Speen Street', b='Timer Street', near=(-71.3754, 42.2837)), {}),
 ('labels_aug2018_natick.csv', 'AUG2018-05', 'Maynard', dict(g='pair', a='Thompson Street', b='Sudbury Street', near=(-71.46, 42.43)),
  dict(name='Thompson Street at Sudbury Street: flooded (3 ft)', road='Sudbury Street')),
 ('labels_aug2018_natick.csv', 'AUG2018-08', 'Hudson', dict(g='pair', a='Marlboro Road|Marlborough Road', b='Reed Street', near=(-71.5879, 42.3822)), {}),
 ('labels_aug2018_natick.csv', 'AUG2018-21', 'Natick', dict(g='pair', a='Terrace Avenue', b='Wethersfield Road', near=(-71.35, 42.28)),
  dict(name='Terrace Avenue at Wethersfield Road: flooded (3 ft)', road='Wethersfield Road')),
 ('labels_aug2021_worcester.csv', 'W011', 'Worcester', dict(g='pair', a='Enid Street', b='Commonwealth Avenue', near=(-71.7619, 42.2507)), {}),
 ('labels_aug2023_metrowest.csv', 'AUG2023-04', 'Holliston', dict(g='pair', a='Concord Street|ref:MA 126', b='Ashland Street', near=(-71.4316, 42.2261)), {}),
 ('labels_aug2023b_millbury.csv', 'AUG2023b-02', 'Oxford', dict(g='pair', a='Orchard Hill Road', b='Sutton Avenue', near=(-71.8435, 42.1141)), {}),
 ('labels_aug2023b_millbury.csv', 'AUG2023b-04', 'Shrewsbury', dict(g='near', a='Municipal Drive', near=(-71.7128, 42.2959)),
  dict(name='Municipal Drive: flooded', road='Municipal Drive')),
 ('labels_aug2026_leominster.csv', 'AUG2026-04', 'Fitchburg', dict(g='pair', a='Wanoosnoc Road', b='North Main Street', near=(-71.7816, 42.5636)), {}),
 ('labels_jul2018_worcester.csv', 'JUL2018-01', 'Worcester', dict(g='pair', a='Chandler Street', b='Murray Avenue', near=(-71.8052, 42.2601)),
  dict(name='Chandler Street at Murray Avenue: flooded (1 ft)')),
 ('labels_jul2018_worcester.csv', 'JUL2018-02', 'Auburn', dict(g='cent', a='Auburn Street', near=(-71.83, 42.20)),
  dict(name='Auburn Street: flooded', road='Auburn Street')),
 ('labels_jul2021_worcester.csv', 'JUL2021-05', 'Millbury', dict(g='pair', a='ref:MA 146', b='ref:MA 122A', near=(-71.7652, 42.1867)), {}),
 ('labels_jul2023_worcester.csv', 'JUL2023-03', 'Worcester', dict(g='pair', a='Franklin Street', b='rail', near=(-71.7834, 42.2635)),
  dict(name='Franklin Street by the railroad tracks: flooded')),
 ('labels_oct2016_worcester.csv', 'OCT2016-08', 'Worcester', dict(g='cent', a='Bridge Street', near=(-71.81, 42.27)), dict(name='Bridge Street: impassable', road='Bridge Street')),
 ('labels_oct2016_worcester.csv', 'OCT2016-09', 'Worcester', dict(g='pair', a='Bancroft Street', b='Chandler Street', near=(-71.8176, 42.2607)), {}),
 ('labels_oct2016_worcester.csv', 'OCT2016-13', 'Worcester', dict(g='pair', a='Major Taylor Boulevard', b='Summer Street', near=(-71.797, 42.2699)),
  dict(name='Major Taylor Boulevard, Summer Street: closed', road='Major Taylor Boulevard')),
 ('labels_oct2016_worcester.csv', 'OCT2016-17', 'Worcester', dict(g='pair', a='Harding Street', b='Pond Street', near=(-71.7954, 42.2585)), {}),
 ('labels_oct2016_worcester.csv', 'OCT2016-18', 'Worcester', dict(g='pair', a='Highland Street', b='Park Avenue', near=(-71.8147, 42.2544)), {}),
 ('labels_oct2016_worcester.csv', 'OCT2016-20', 'Worcester', dict(g='pair', a='Highland Street', b='Park Avenue', near=(-71.8164, 42.2703)), {}),
 ('labels_oct2016_worcester.csv', 'OCT2016-29', 'Worcester', dict(g='pair', a='Martin Luther King Jr Boulevard|Martin Luther King Junior Boulevard', b='rail', near=(-71.81, 42.26)),
  dict(name='MLK Boulevard at the railroad underpass: flooded', road='Martin Luther King Jr Boulevard')),
 ('labels_sep2021_worcester.csv', 'SEP2021-05', 'Worcester', dict(g='pair', a='ref:US 20', b='ref:MA 122', towns=['Worcester', 'Millbury'], near=(-71.75, 42.23)),
  dict(name='Southwest Cutoff (Route 20) at Grafton Street (Route 122): impassable')),
 ('labels_sep2021_worcester.csv', 'SEP2021-07', 'West Boylston', None, dict(name='Unknown road: washout (exact street unknown)', road='')),
 ('labels_sep2022_webster.csv', 'SEP2022-03', 'Webster', dict(g='pair', a='West Main Street|ref:MA 197', b='Mason Lane', near=(-71.8688, 42.0746)),
  dict(name='West Main Street (Route 197) at Mason Lane: closed', road='West Main Street')),
]

PREFIX = {'may2018': 'MAY2018', 'aug2018b': 'AUG2018b', 'sep2018': 'SEP2018', 'sep2018w': 'SEP2018w', 'sep2018b': 'SEP2018b', 'jul2019': 'JUL2019',
          'aug2019': 'AUG2019', 'sep2019': 'SEP2019', 'jun2020': 'JUN2020', 'jun2020b': 'JUN2020b', 'aug2020b': 'AUG2020b', 'jul2021b': 'JUL2021b',
          'jul2023b': 'JUL2023b', 'jul2023c': 'JUL2023c', 'jul2023d': 'JUL2023d', 'jul2018': 'JUL2018-N', 'aug2020': 'AUG2020-N', 'aug2021': 'W1', 'aug2026': 'AUG2026-N', 'sep2018m': 'SEP2018m'}
EXISTING = {'jul2018', 'aug2020', 'aug2021', 'aug2026'}


def key(i, s): return f'{s[0]}:{i:03d}'


def queries():
    Q = []
    for i, s in enumerate(S):
        g = s[9]
        if g['g'] == 'net': continue
        q = dict(key=key(i, s), town=s[1], towns=g.get('towns'), a=g['a'], b=g.get('b') if g['g'] == 'pair' else None, near=list(g['near']) if g.get('near') else None,
                 addr=g.get('addr'))
        Q.append(q)
    for f, rid, town, g, _ in FIX:
        if g is None: continue
        Q.append(dict(key=f'fix:{rid}', town=town, towns=g.get('towns'), a=g['a'], b=g.get('b') if g['g'] == 'pair' else None, near=list(g['near']), addr=None))
    json.dump(Q, open(Q_PATH, 'w'), indent=1); print(len(Q), 'queries ->', Q_PATH)


# ---------------------------------------------------------------------------------------------------------------------------- build
def _net():
    sys.path.insert(0, HERE)
    from pyproj import Transformer
    G = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    return G, Transformer.from_crs(4326, 26986, always_xy=True), Transformer.from_crs(26986, 4326, always_xy=True)


def _decode(g):
    out = []
    for part in g:
        x, y = part[0], part[1]; P = [(x, y)]
        for k in range(2, len(part), 2): x += part[k]; y += part[k + 1]; P.append((x, y))
        out.append([(a / 1e5, b / 1e5) for a, b in P])
    return out


def _netnames(spec):
    out = []
    for v in spec.split('|'):
        v = v.strip()
        if v == 'rail' or v.startswith('water:'): continue
        if v.startswith('ref:'):
            r = v[4:].split()[-1]; out += ['I-' + r if v[4:].startswith('I ') else 'Route ' + r]
        else: out.append(v)
    return out


def _netpts(G, T, spec, towns, near, rad=6000.0):
    names = set(_netnames(spec)); P = []
    idx = [i for i, r in enumerate(G['props']['road']) if r in names]
    inn = [i for i in idx if G['props']['town'][i] in towns]
    for i in (inn or idx): P += [p for part in _decode(G['geo'][i]) for p in part]
    if not P: return None
    x, y = T.transform([p[0] for p in P], [p[1] for p in P]); P = np.column_stack([x, y])
    if near: nx, ny = T.transform(*near); P = P[np.hypot(P[:, 0] - nx, P[:, 1] - ny) < rad]
    return P if len(P) else None


def net_geocode(G, T, TI, s):
    """Fallback on docs/graph_segments.json (MassGIS road names) when OSM gave nothing."""
    from scipy.spatial import cKDTree
    g = s[9]; near = g.get('near'); tw = g.get('towns') or [s[1]]; A = _netpts(G, T, g['a'], tw, near)
    if A is None: return None
    if g.get('b') and g['g'] in ('pair', 'net'):
        B = _netpts(G, T, g['b'], tw, near)
        d = cKDTree(B).query(A)[0] if B is not None else None
        if B is not None and d.min() <= 400:
            d, j = cKDTree(B).query(A); k = d.argmin(); p = (A[k] + B[j[k]]) / 2; lo, la = TI.transform(*p)
            q = 'exact' if d[k] <= 80 and g.get('q') != 'approx' else 'approx'
            return round(lo, 6), round(la, 6), q, f'graph_segments pair gap {d[k]:.0f} m'
    if g['g'] == 'cent':
        c = A.mean(0); k = np.hypot(*(A - c).T).argmin(); lo, la = TI.transform(*A[k]); return round(lo, 6), round(la, 6), 'approx', 'graph_segments road centroid vertex'
    nx, ny = T.transform(*near); d = np.hypot(A[:, 0] - nx, A[:, 1] - ny); k = d.argmin(); lo, la = TI.transform(*A[k])
    return round(lo, 6), round(la, 6), 'approx', f'graph_segments road vertex {d[k]:.0f} m from NWS point'


def pick(s, R):
    """lon, lat, coord_quality, how  (R = OSM result for this site)."""
    g = s[9]; near = g.get('near'); qmax = g.get('q'); c = None
    if g.get('osm') is False: return None
    if R and R.get('pair') and R['pair']['candidates']:
        C = R['pair']['candidates']
        c = min(C, key=lambda c: c.get('to_near_m', 0) + 2 * c['gap_m']) if near else C[0]
        if c.get('to_near_m', 0) > 4000 or c['gap_m'] > 400: c = None          # implausibly far from the NWS point: fall through
    if R and R.get('pair') and R['pair']['candidates'] and c is not None:
        q = 'exact' if c['gap_m'] <= 80 else 'approx'
        if qmax == 'approx': q = 'approx'
        return c['lonlat'][0], c['lonlat'][1], q, f"osm pair gap {c['gap_m']} m" + (f", {c.get('to_near_m')} m from NWS point" if near else '') + f", {len(C)} candidate(s)"
    if R and g['g'] == 'addr' and isinstance(R.get('addr'), list) and R['addr']:
        a = R['addr'][0]; return round(a['lonlat'][0], 6), round(a['lonlat'][1], 6), 'approx', f"nominatim: {str(a['name'])[:80]}"
    if R and R.get('single'):
        sg = R['single']
        if g['g'] in ('near', 'pair', 'addr') and sg.get('nearest_vertex') and sg.get('nearest_m', 1e9) < 1500:
            return sg['nearest_vertex'][0], sg['nearest_vertex'][1], 'approx', f"osm road vertex {sg['nearest_m']} m from NWS point (road {sg['length_m']} m)"
        return sg['centroid_vertex'][0], sg['centroid_vertex'][1], 'approx', f"osm road centroid vertex (road {sg['length_m']} m)"
    return None


def load_osm():
    import glob
    R = {}
    for f in [OSM_PATH] + sorted(glob.glob(OSM_PATH.replace('.json', '_*.json'))):
        for k, v in json.load(open(f)).items():
            if k not in R or (v.get('pair') or v.get('single') or v.get('addr')): R[k] = v
    return R


def build():
    R = load_osm()
    G, T, TI = _net(); rows = {}; audit = []
    for i, s in enumerate(S):
        storm, town, road, name, typ, t, quote, url, src, g = s
        r = pick(s, R.get(key(i, s)))
        if r is None or (g['g'] == 'pair' and r[2] != 'exact' and g.get('q') != 'approx'):
            n = net_geocode(G, T, TI, s)
            if n and (r is None or n[2] == 'exact'): r = n
        if r is None:
            nr = g.get('near'); r = (nr[0], nr[1], 'town', 'not placed: NWS point kept')
        lon, lat, q, how = r
        if len(t) == 10: tl, tq = f'{t}T12:00', 'day'
        else:
            tu = dt.datetime.strptime(t, '%Y-%m-%dT%H:%MZ'); tl, tq = (tu - dt.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M'), 'report'   # all storms are in EDT (May-Sep)
        rows.setdefault(storm, []).append(dict(name=name, road=road, town=town, type=typ, time_local=tl, time_quality=tq, lon=f'{float(lon):.5f}', lat=f'{float(lat):.5f}',
                                               coord_quality=q, source_url=url, quote=quote, source=src))
        audit.append(dict(key=key(i, s), storm=storm, town=town, road=road, coord_quality=q, how=how, lon=float(lon), lat=float(lat)))
    for storm, L in rows.items():
        path = os.path.join(HERE, 'data', FILES[storm])
        if storm in EXISTING:
            old = list(csv.DictReader(open(path))); hdr = list(old[0].keys())
            old = [o for o in old if not o['id'].startswith(PREFIX[storm])]          # idempotent: drop previous additions
            for k, r in enumerate(L): r['id'] = f'{PREFIX[storm]}{k + 1:02d}'
            out = old + L
        else:
            hdr = COLS
            for k, r in enumerate(L): r['id'] = f'{PREFIX[storm]}-{k + 1:02d}'
            out = L
        with open(path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=hdr, extrasaction='ignore'); w.writeheader(); w.writerows(out)
        print(f'{storm:9s} {len(L):3d} rows -> {os.path.relpath(path, ROOT)}')
    json.dump(audit, open(AUDIT_PATH, 'w'), indent=1)
    fix(R, (G, T, TI))


def fix(R, NET):
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True); log = []
    LP = os.path.join(ROOT, 'docs', 'proto', 'obs', 'labels_fix_changelog.json')
    prev = {e['id']: e for e in json.load(open(LP))} if os.path.exists(LP) else {}     # re-runs keep the original (pre-fix) values
    for f, rid, town, g, over in FIX:
        path = os.path.join(HERE, 'data', f); rows = list(csv.DictReader(open(path))); hdr = list(rows[0].keys())
        r = next(x for x in rows if x['id'] == rid); before = dict(lon=r['lon'], lat=r['lat'], coord_quality=r['coord_quality'], name=r['name'], road=r['road'])
        how = None; res = R.get(f'fix:{rid}') or {}
        if g and g['g'] == 'pair' and (res.get('pair') or {}).get('candidates'):
            C = res['pair']['candidates']; c = min(C, key=lambda c: c.get('to_near_m', 0) + 2 * c['gap_m'])
            if c['gap_m'] <= 80 and c.get('to_near_m', 0) <= 1500:
                r['lon'], r['lat'] = f"{c['lonlat'][0]:.5f}", f"{c['lonlat'][1]:.5f}"; r['coord_quality'] = 'exact'
                how = f"OSM intersection, gap {c['gap_m']} m, {c.get('to_near_m')} m from the old point"
        elif g and res.get('single') and r['coord_quality'] in ('town',) or (g and g['g'] == 'near' and res.get('single')):
            sg = res['single']; v = sg.get('nearest_vertex') if g['g'] == 'near' and sg.get('nearest_m', 1e9) < 1500 else sg['centroid_vertex']
            r['lon'], r['lat'] = f'{v[0]:.5f}', f'{v[1]:.5f}'; r['coord_quality'] = 'approx'; how = f"OSM road vertex (road {sg['length_m']} m)"
        if how is None and g:
            n = net_geocode(*NET, ('', town, '', '', '', '', '', '', '', g))
            if n:
                x0, y0 = T.transform(float(r['lon']), float(r['lat'])); x1, y1 = T.transform(n[0], n[1])
                if (g['g'] == 'pair' and n[2] == 'exact' and np.hypot(x1 - x0, y1 - y0) <= 1500) or (g['g'] != 'pair' and r['coord_quality'] == 'town') \
                        or (g['g'] == 'pair' and r['coord_quality'] == 'town'):
                    r['lon'], r['lat'] = f'{n[0]:.5f}', f'{n[1]:.5f}'; r['coord_quality'] = n[2]; how = n[3]
        for k, v in over.items(): r[k] = v
        if g is None: how = 'name/road corrected only'
        after = dict(lon=r['lon'], lat=r['lat'], coord_quality=r['coord_quality'], name=r['name'], road=r['road'])
        if rid in prev:
            before = prev[rid]['before']
            if after == dict(prev[rid]['after']): how = prev[rid]['how']
        if after != before:
            x0, y0 = T.transform(float(before['lon']), float(before['lat'])); x1, y1 = T.transform(float(after['lon']), float(after['lat']))
            log.append(dict(file=f, id=rid, before=before, after=after, moved_m=round(float(np.hypot(x1 - x0, y1 - y0))), how=how or 'names only (OSM did not confirm the point)'))
        with open(path, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=hdr); w.writeheader(); w.writerows(rows)
    json.dump(log, open(LP, 'w'), indent=1)
    for e in log: print('fix', e['id'], e['moved_m'], 'm', e['before']['coord_quality'], '->', e['after']['coord_quality'], '|', e['how'])


# ---------------------------------------------------------------------------------------------------------------------------- catalogue
NEW = {  # id: (area, note)
 'may2018': ('shrewsbury', 'Thunderstorms 15 May 2018: Route 9 / Lake St closed in Shrewsbury, I-290 at Route 146 flooded. LSR only (no Storm Events rows in the box). Small.'),
 'aug2018b': ('holden', 'Thunderstorms 11 Aug 2018: Holden Main St, Spencer Donnelly Rd, West Boylston Crescent St (evening cell). Small.'),
 'sep2018': ('fitchburg', 'Remnants of Florence 18 Sep 2018, north Worcester County: Gardner, Fitchburg/Westminster railroad underpasses, Hubbardston, Ashburnham.'),
 'sep2018w': ('shrewsbury', 'Remnants of Florence 18 Sep 2018, Worcester/Shrewsbury: Route 20 at the Route 122 overpass, Maple Ave at Route 9, Floral St. Small.'),
 'sep2018m': ('milford', 'Remnants of Florence 18 Sep 2018, third cluster: Uxbridge Route 122 at Hazel St, Milford North Bow St, Bellingham Monique Dr and Caroline Dr.'),
 'sep2018b': ('gardner', 'Evening downpours 26 Sep 2018 (27 Sep UTC): Gardner, Templeton, Westminster.'),
 'jul2019': ('spencer', 'Thunderstorms 6 Jul 2019: Spencer, South Worcester, Route 20/122A, Oxford.'),
 'aug2019': ('oxford', 'Evening storms 7 Aug 2019 (8 Aug UTC): I-395 exit 4B in Oxford and the I-290 EB ramp to Southbridge St in Worcester. Small.'),
 'sep2019': ('northbridge', 'Storms 2 Sep 2019: Sutton Ave closed in Oxford, Park St at Cottage St in Whitinsville. Small (Milford and Marlborough sites outside the box).'),
 'jun2020': ('northbridge', 'Flash flooding 28 Jun 2020, Blackstone Valley: Northbridge/Whitinsville, Hopedale, Uxbridge, Blackstone.'),
 'jun2020b': ('gardner', 'Same evening as jun2020 (28 Jun 2020), Gardner and the Princeton Road bridge in Fitchburg.'),
 'aug2020b': ('worcester', 'Thunderstorm 27 Aug 2020, south Worcester: Whipple St, College St, Route 20 rescues. Small.'),
 'jul2021b': ('worcester', 'Storms 17-18 Jul 2021: Worcester (Millbury St/McKeon Rd, Dale St, Dewey St/Parker St) and Leicester Route 56 next morning.'),
 'jul2023b': ('worcester', '10 Jul 2023 (day of the Vermont flood): Route 20 at 86 Southwest Cutoff (4 cars stuck), Rutland Route 56. Small.'),
 'jul2023c': ('fitchburg', 'Storm 16 Jul 2023, Fitchburg: Franklin Rd at Royalston St, Birch St pavement destroyed, John Fitch Hwy, Lunenburg St.'),
 'jul2023d': ('hubbardston', 'Storms 21 Jul 2023: Route 2 closed both ways in Leominster (MassDOT), Hubbardston Route 68 and Williamsville Rd.'),
}
D3_BOX = (128000.0, 856000.0, 206000.0, 946000.0)


def catalog():
    from pyproj import Transformer
    T = Transformer.from_crs(4326, 26986, always_xy=True); TI = Transformer.from_crs(26986, 4326, always_xy=True)
    CP = os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json'); C = json.load(open(CP))
    lsr = list(csv.DictReader(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog', 'lsr_ma_flood_2014_2026.csv'))))
    se = list(csv.DictReader(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog', 'stormevents_ma_flood_2014_2026.csv'))))
    mrms = {}
    try: mrms = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog', 'mrms_check.json')))
    except Exception: pass
    have = {e['id'] for e in C['events']}; out = []
    for sid, (area, note) in NEW.items():
        L = list(csv.DictReader(open(os.path.join(HERE, 'data', FILES[sid]))))
        P = [(T.transform(float(r['lon']), float(r['lat'])), r) for r in L if r['coord_quality'] != 'town']
        best = None
        for x0 in range(int(D3_BOX[0] / 1000) - 5, int(D3_BOX[2] / 1000) - 14):
            for y0 in range(int(D3_BOX[1] / 1000) - 4, int(D3_BOX[3] / 1000) - 19):
                inb = [r for (x, y), r in P if x0 * 1000 <= x < x0 * 1000 + 20000 and y0 * 1000 <= y < y0 * 1000 + 20000]
                if not inb: continue
                xs = [x for (x, y), r in P if x0 * 1000 <= x < x0 * 1000 + 20000 and y0 * 1000 <= y < y0 * 1000 + 20000]
                ys = [y for (x, y), r in P if x0 * 1000 <= x < x0 * 1000 + 20000 and y0 * 1000 <= y < y0 * 1000 + 20000]
                cen = abs(np.mean(xs) - (x0 * 1000 + 10000)) + abs(np.mean(ys) - (y0 * 1000 + 10000))      # centre the cluster in the box
                sc = (len(inb), -cen)
                if best is None or sc > best[0]: best = (sc, x0 * 1000, y0 * 1000, inb)
        _, bx, by, inb = best; box = [bx, by, bx + 20000, by + 20000]
        tt = sorted(dt.datetime.strptime(r['time_local'], '%Y-%m-%dT%H:%M') + dt.timedelta(hours=4) for r in inb if r['time_quality'] == 'report')
        first, last = tt[0], tt[-1]
        t0 = (first - dt.timedelta(hours=7)).replace(minute=0); hours = max(18, int(np.ceil(((last - t0).total_seconds() / 3600 + 5))))
        lo0, la0 = TI.transform(box[0], box[1]); lo1, la1 = TI.transform(box[2], box[3])
        # raw NWS rows in the box and window (as in the catalogue counts)
        def inbox(lon, lat): x, y = T.transform(lon, lat); return box[0] <= x < box[2] and box[1] <= y < box[3]
        w0, w1 = t0, t0 + dt.timedelta(hours=hours)
        nl = sum(1 for r in lsr if r['TYPETEXT'].upper() in ('FLOOD', 'FLASH FLOOD') and w0 <= dt.datetime.strptime(r['VALID'], '%Y%m%d%H%M') <= w1 and inbox(float(r['LON']), float(r['LAT'])))
        ns = 0
        for r in se:
            if r['EVENT_TYPE'] not in ('Flood', 'Flash Flood') or not r['BEGIN_LAT']: continue
            t = dt.datetime.strptime(r['BEGIN_DATE_TIME'], '%d-%b-%y %H:%M:%S') + dt.timedelta(hours=int(r['CZ_TIMEZONE'][-1]))
            if w0 <= t <= w1 and inbox(float(r['BEGIN_LON']), float(r['BEGIN_LAT'])): ns += 1
        era = 'aws' if t0 >= dt.datetime(2020, 10, 14) else 'iem'
        q = {}
        for r in inb: q[r['coord_quality']] = q.get(r['coord_quality'], 0) + 1
        dl = (first - dt.timedelta(hours=4)).strftime('%Y-%m-%d')
        e = dict(id=sid, area=area, date_local=dl, t0=t0.strftime('%Y-%m-%dT%H:00Z'), hours=hours, first_report_utc=first.strftime('%Y-%m-%dT%H:%MZ'),
                 last_report_utc=last.strftime('%Y-%m-%dT%H:%MZ'), box_26986=box, bbox_lonlat=[round(lo0, 3), round(la0, 3), round(lo1, 3), round(la1, 3)],
                 start=(first - dt.timedelta(days=1)).strftime('%Y-%m-%d'), end=(last + dt.timedelta(days=1)).strftime('%Y-%m-%d'),
                 towns=sorted({r['town'] for r in inb}),
                 counts=dict(lsr_flood=nl, stormevents_flood=ns, road_sites_named=len(inb), label_rows=len(L), label_rows_outside_box=len(L) - len(inb)),
                 max_rain_lsr_in=None,
                 mrms=('AWS noaa-mrms-pds MultiSensor_QPE_01H_Pass2 (w9 as is)' if era == 'aws' else
                       'IEM mtarchive GaugeCorr_QPE_01H (MRMS v11, gauge-corrected; MultiSensor Pass2 does not exist before 14 Oct 2020); w9 needs an IEM reader'),
                 era=era, existing=False, note=note, labels=f'proto/data/{FILES[sid]}',
                 sources=sorted({dict(LSR='IEM LSR (NWS BOX)', StormEvents='NOAA Storm Events', news='news')[r['source']] for r in L}),
                 label_coord_quality=q, selected=True, expansion='2026-10-23 LABELS_EXPANSION.md',
                 group='A: MRMS Pass2 on AWS (w9 as is)' if era == 'aws' else 'B: before Oct 2020 (IEM MRMS only)')
        if sid in mrms: e['mrms_check'] = {k: v for k, v in mrms[sid].items()}
        gp = os.path.join(ROOT, 'docs', 'proto', 'obs', f'gauges_{sid}.json')
        if os.path.exists(gp):
            e['gauges'] = []
            for g in json.load(open(gp))['gauges']:
                if not inbox(g['lon'], g['lat']): continue
                pq, ps = g.get('peak_q_cfs'), g.get('peak_stage_ft')
                e['gauges'].append(dict(site=g['site'], name=g['name'], drain_mi2=g.get('drain_mi2'), peak_q_cfs=pq[1] if pq else None,
                                        peak_q_time_local=pq[0] if pq else None, peak_stage_ft=ps[1] if ps else None))
        out.append(e); print(sid, era, e['t0'], hours, box, len(inb), '/', len(L), q, e['towns'])
    C['events'] = [x for x in C['events'] if x['id'] not in NEW] + out
    json.dump(C, open(CP, 'w'), indent=1)


def report():
    """Markdown tables for LABELS_EXPANSION.md (per-storm counts from catalog.json and the label files)."""
    from collections import Counter
    C = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    print('| id | date (local) | era | box EPSG:26986 | t0 UTC / h | label rows | in box | exact / approx / town (in box) | types (in box) | sources (all rows) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    tot = Counter()
    for sid in NEW:
        e = C[sid]; L = list(csv.DictReader(open(os.path.join(HERE, 'data', FILES[sid])))); bx = e['box_26986']
        from pyproj import Transformer
        T = Transformer.from_crs(4326, 26986, always_xy=True)
        inb = [r for r in L if (lambda p: bx[0] <= p[0] < bx[2] and bx[1] <= p[1] < bx[3])(T.transform(float(r['lon']), float(r['lat'])))]
        q = Counter(r['coord_quality'] for r in inb); ty = Counter(r['type'] for r in inb); so = Counter(r['source'] for r in L)
        tot['rows'] += len(L); tot['inb'] += len(inb); tot['inb_road'] += sum(1 for r in inb if r['coord_quality'] != 'town')
        tot['aws_inb'] += len(inb) if e['era'] == 'aws' else 0
        print(f"| {sid} | {e['date_local']} | {e['era']} | {','.join(map(str, bx))} | {e['t0']} / {e['hours']} | {len(L)} | {len(inb)} | "
              f"{q['exact']} / {q['approx']} / {q['town']} | {', '.join(f'{k} {v}' for k, v in ty.most_common())} | {', '.join(f'{k} {v}' for k, v in so.most_common())} |")
    print(dict(tot))
    print()
    print('| existing storm | rows added | added rows inside the catalogue box | exact / approx / town |')
    print('|---|---|---|---|')
    for sid in sorted(EXISTING):
        e = C[sid]; bx = e['box_26986']; L = [r for r in csv.DictReader(open(os.path.join(HERE, 'data', FILES[sid]))) if r['id'].startswith(PREFIX[sid])]
        inb = [r for r in L if (lambda p: bx[0] <= p[0] < bx[2] and bx[1] <= p[1] < bx[3])(T.transform(float(r['lon']), float(r['lat'])))]
        q = Counter(r['coord_quality'] for r in inb)
        print(f"| {sid} | {len(L)} ({', '.join(r['road'] for r in L)}) | {len(inb)} | {q['exact']} / {q['approx']} / {q['town']} |")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['queries', 'build', 'catalog', 'report']); a = ap.parse_args()
    dict(queries=queries, build=build, catalog=catalog, report=report)[a.cmd]()
