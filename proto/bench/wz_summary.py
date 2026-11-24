"""Summary of the MassDOT work-zone feed (CWZ GeoJSON) for the key check: is it real data, and how much is in District 3."""
import json, sys, collections
d = json.load(open(sys.argv[1])); f = d.get('features', [])
print('work zones:', len(f))
def pt(g):
    c = (g or {}).get('coordinates')
    while isinstance(c, list) and c and isinstance(c[0], list): c = c[0]
    return c
def core(x):
    p = x.get('properties', {}); return p.get('core_details', p)
roads = collections.Counter(); starts = []; d3 = 0; types = collections.Counter(); upd = []
for x in f:
    c = core(x); p = x.get('properties', {})
    roads.update(c.get('road_names') or ['?']); types[c.get('event_type', '?')] += 1
    if p.get('start_date'): starts.append(p['start_date'][:10])
    if c.get('update_date'): upd.append(c['update_date'][:10])
    q = pt(x.get('geometry'))
    if q and -72.15 < q[0] < -71.30 and 42.0 < q[1] < 42.72: d3 += 1
print('in District 3 forecast box:', d3)
print('event types:', dict(types))
print('top roads:', roads.most_common(8))
if starts: print('start dates:', min(starts), 'to', max(starts))
if upd: print('last updated:', min(upd), 'to', max(upd))
info = d.get('feed_info') or {}
print('publisher:', info.get('publisher'), '| update_date:', info.get('update_date'), '| contact:', bool(info.get('contact_email')))
if f: print('property keys:', sorted(f[0].get('properties', {}).keys())[:20])
