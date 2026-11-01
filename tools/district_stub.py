"""Split a whole-district replay pack (docs/site/build_data.py build_tiled) between the data site and the main site.

    python3 tools/district_stub.py <pack dir> <data-site storm dir> <main-site stub dir> <data base URL> <site key> [--index <data-site index.json>]

  data-site storm dir  everything (depth / overview / tile / flow sheets and the JSON), served by GitHub Pages of Horus331/mfw-data-d3
  main-site stub dir   docs/site/data/<key>/: the JSON only (meta with data_base = the data-site URL, roads, pieces, refs, network, flow.json,
                       cascade), plus the radar-rain loop already there (rain.json / rain.png are kept and copied to the data site too)
The viewer reads JSON from the run folder and every image sheet from meta.data_base (viewer.js dbase()).
Used by tools/publish_district.sh (pack on the district-data branch -> data site + stub)."""
import argparse, json, os, shutil


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pack'); ap.add_argument('data_dir'); ap.add_argument('stub_dir'); ap.add_argument('base'); ap.add_argument('key')
    ap.add_argument('--index'); ap.add_argument('--title')
    a = ap.parse_args()
    if os.path.exists(a.data_dir): shutil.rmtree(a.data_dir)
    shutil.copytree(a.pack, a.data_dir)
    m = json.load(open(os.path.join(a.pack, 'meta.json'))); m['key'] = a.key; m['data_base'] = a.base.rstrip('/') + '/'
    json.dump(m, open(os.path.join(a.data_dir, 'meta.json'), 'w'), separators=(',', ':'))
    os.makedirs(a.stub_dir, exist_ok=True)
    keep = {'rain.json', 'rain.png'}
    for f in os.listdir(a.stub_dir):
        if f in keep: continue
        p = os.path.join(a.stub_dir, f); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    for f in os.listdir(a.pack):
        if f.endswith('.json'): shutil.copy(os.path.join(a.pack, f), a.stub_dir)
    json.dump(m, open(os.path.join(a.stub_dir, 'meta.json'), 'w'), separators=(',', ':'))
    for f in keep:
        if os.path.exists(os.path.join(a.stub_dir, f)) and not os.path.exists(os.path.join(a.data_dir, f)): shutil.copy(os.path.join(a.stub_dir, f), a.data_dir)
    if a.index:
        I = json.load(open(a.index)) if os.path.exists(a.index) else {'storms': []}
        size = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(a.data_dir) for x in fs)
        e = dict(key=a.key, title=a.title or a.key, storm_start=m.get('storm_start'), frame_min=m.get('frame_min'), nf=m.get('nf'),
                 resolution_m=m.get('resolution_m'), tiles=len(((m.get('depthc') or {}).get('tiles') or {}).get('list', [])), mb=round(size / 1e6, 1),
                 viewer='https://horus331.github.io/mass-flood-watch/viewer.html?run=' + a.key)
        I['storms'] = [s for s in I.get('storms', []) if s.get('key') != a.key] + [e]
        json.dump(I, open(a.index, 'w'), indent=1)
    sz = lambda d: sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(d) for x in fs) / 1e6
    print('data site %.1f MB, main-site stub %.1f MB: %s' % (sz(a.data_dir), sz(a.stub_dir), ', '.join(sorted(os.listdir(a.stub_dir)))))


if __name__ == '__main__':
    main()
