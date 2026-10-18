"""Post a progress update to docs/progress.json (and optionally set a stage's status/note).
usage: python tools/progress.py "update text" [--stage N --status "in progress" --note "..."]
"""
import json, sys, time, argparse, os
from zoneinfo import ZoneInfo
ap = argparse.ArgumentParser(); ap.add_argument('text'); ap.add_argument('--stage', type=int); ap.add_argument('--status'); ap.add_argument('--note'); a = ap.parse_args()
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'progress.json'); P = json.load(open(p))
now = time.strftime('%a %b %d, %-I:%M %p', time.localtime()) if os.environ.get('TZ') else __import__('datetime').datetime.now(ZoneInfo('America/New_York')).strftime('%a %b %d, %-I:%M %p')
P['updates'].insert(0, dict(t=now, text=a.text)); P['updates'] = P['updates'][:40]
if a.stage:
    for s in P['stages']:
        if s['n'] == a.stage:
            if a.status: s['status'] = a.status
            if a.note is not None: s['note'] = a.note
json.dump(P, open(p, 'w'), indent=1, ensure_ascii=False); print('progress updated', now)
