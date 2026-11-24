"""District 3 road segments (docs/graph_segments.json, the network the model evaluates) as GeoJSONSeq for tippecanoe: one feature per
segment, c = class (0 local/collector, 1 arterial, 2 highway). No feature id: the street layer is not coloured per segment (flood
colours come from the separate road layers), so tippecanoe can merge segments of the same class (--coalesce), which makes the zoomed-out
tiles 5-7 times smaller (map speed plan, 24 Nov 2026). Local streets (c = 0, 165,000 of 188,000 segments) start at zoom 10: below it they
are under half a pixel wide, and leaving them out makes the zoom 8-9 tiles about 10 times lighter (arterials and highways stay).
    python proto/tiles/build_streets_seq.py OUT.geojsonl
Run by .github/workflows/tiles.yml, which turns it into docs/site/tiles/d3_streets.pmtiles."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM
S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']; n = 0
with open(sys.argv[1], 'w') as f:
    for seg, lo, la in IM.decode_segments(S):
        if len(lo) < 2: continue
        c = int(P['cls'][seg])
        f.write(json.dumps({'type': 'Feature', 'properties': {'c': c}, **({'tippecanoe': {'minzoom': 10}} if c == 0 else {}),
                            'geometry': {'type': 'LineString', 'coordinates': [[round(a, 6), round(b, 6)] for a, b in zip(lo, la)]}},
                           separators=(',', ':')) + '\n'); n += 1
print(n, 'segments')
