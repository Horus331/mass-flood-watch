"""Record MassDOT's public roadway-events feed (http://events.massdot.evbg.net/) so every closure gets a timestamped history.
Runs every 15 min from .github/workflows/events_log.yml; appends new/changed events to docs/proto/obs/massdot_events/YYYY-MM.jsonl."""
import os, sys, json, hashlib, datetime as dt, requests, xml.etree.ElementTree as ET
URL = os.environ.get('EVENTS_URL', 'http://events.massdot.evbg.net/')
OUT = 'docs/proto/obs/massdot_events'
def flat(e):
    d = {}
    for c in e.iter():
        if c is e: continue
        if c.text and c.text.strip() and len(list(c)) == 0: d[c.tag.split('}')[-1]] = c.text.strip()
    return d
r = requests.get(URL, timeout=60); r.raise_for_status()
now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); os.makedirs(OUT, exist_ok=True)
try: root = ET.fromstring(r.content); items = [flat(e) for e in root if len(list(e))]
except ET.ParseError: items = []; open(f'{OUT}/last_raw.txt', 'w').write(r.text[:200000])
seen_p = f'{OUT}/seen.json'; seen = json.load(open(seen_p)) if os.path.exists(seen_p) else {}
new = 0
with open(f'{OUT}/{now[:7]}.jsonl', 'a') as f:
    for it in items:
        h = hashlib.sha1(json.dumps(it, sort_keys=True).encode()).hexdigest()
        if h in seen: continue
        seen[h] = now; f.write(json.dumps(dict(logged=now, **it)) + '\n'); new += 1
json.dump(seen, open(seen_p, 'w'))
open(f'{OUT}/last_poll.txt', 'w').write(f'{now} items={len(items)} new={new} bytes={len(r.content)}\n')
print(now, 'items', len(items), 'new', new)
