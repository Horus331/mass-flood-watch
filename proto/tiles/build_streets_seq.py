"""District 3 road segments (docs/graph_segments.json, the network the model evaluates) as GeoJSONSeq for tippecanoe: one feature per
segment, feature id = segment id (so the map can colour it with feature-state), c = class (0 local/collector, 1 arterial, 2 highway).
    python proto/tiles/build_streets_seq.py OUT.geojsonl
Run by .github/workflows/tiles.yml, which turns it into docs/site/tiles/d3_streets.pmtiles."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM
S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']; n = 0
with open(sys.argv[1], 'w') as f:
    for seg, lo, la in IM.decode_segments(S):
        if len(lo) < 2: continue
        f.write(json.dumps({'type': 'Feature', 'id': int(seg), 'properties': {'c': int(P['cls'][seg])},
                            'geometry': {'type': 'LineString', 'coordinates': [[round(a, 6), round(b, 6)] for a, b in zip(lo, la)]}},
                           separators=(',', ':')) + '\n'); n += 1
print(n, 'segments')
