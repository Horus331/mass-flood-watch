"""Model coverage for the public map (docs/site/data/coverage.json), run from the repo root: python3 proto/build_coverage.py

forecast : MassDOT District 3, dissolved from its 73 towns (docs/towns.json, as the live forecast gate uses them, proto/forecast.py).
           The live forecast runs the flood model here.
tested   : the 20 x 20 km storm boxes of the District 4-6 transfer test (docs/proto/transfer/r1/*/config.json, kind 'test'), dissolved.
           Historical storms only, frozen District 3 settings: tested, not forecast.
Polygons are simplified to ~30 m and written in lon/lat."""
import glob, json, os, sys
import numpy as np
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union, transform
from pyproj import Transformer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'proto'))
from forecast import d3_towns

tr = Transformer.from_crs(26986, 4326, always_xy=True).transform
d3 = unary_union([Polygon(r) for _, _, rings in d3_towns() for r in rings if len(r) >= 4]).buffer(0)
# towns are lon/lat already (d3_towns converts); clean slivers in metres
to_m = Transformer.from_crs(4326, 26986, always_xy=True).transform
d3m = transform(to_m, d3).buffer(50).buffer(-50)
# fill interior gaps (towns missing from the polygon file are enclosed by the district): keep exterior rings only
d3m = unary_union([Polygon(p.exterior) for p in (d3m.geoms if d3m.geom_type == 'MultiPolygon' else [d3m])]).simplify(30)
boxes = []
for f in sorted(glob.glob(os.path.join(ROOT, 'docs/proto/transfer/r1/*/config.json'))):
    c = json.load(open(f))
    if c.get('kind') != 'test': continue
    x0, y0, x1, y1 = [float(v) for v in c['box'].split(',')]; boxes.append(box(x0, y0, x1, y1))
tested = unary_union(boxes).difference(d3m).simplify(30)
r = lambda g: json.loads(json.dumps(mapping(transform(tr, g))), parse_float=lambda v: round(float(v), 5))
out = dict(type='FeatureCollection', made_by='proto/build_coverage.py', features=[
    dict(type='Feature', properties=dict(k='forecast', name='Forecast area: MassDOT District 3', n_towns=len(d3_towns())), geometry=r(d3m)),
    dict(type='Feature', properties=dict(k='tested', name='Tested on past storms only: Districts 4-6', n_boxes=len(boxes)), geometry=r(tested))])
p = os.path.join(ROOT, 'docs/site/data/coverage.json'); json.dump(out, open(p, 'w'), separators=(',', ':'))
print(p, os.path.getsize(p), 'bytes;', len(boxes), 'test boxes; District 3 area %.0f km2' % (d3m.area / 1e6))
