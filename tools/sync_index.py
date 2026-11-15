"""docs/index.html = docs/viewer.html (the site opens on the model; Mo, 15 Nov 2026).  Run after any change to viewer.html:
    python tools/sync_index.py           # writes docs/index.html
    python tools/sync_index.py --check   # exit 1 when index.html is out of date (CI: .github/workflows/site_index.yml)
Only the <title> differs."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'docs', 'viewer.html')).read()
out = src.replace('<title>Storm Replay · Mass Flood Watch</title>', '<title>Mass Flood Watch · Road flood model, central Massachusetts</title>', 1)
out = out.replace('<html lang="en">', '<html lang="en">\n<!-- generated from docs/viewer.html by tools/sync_index.py: edit viewer.html, then run the script -->', 1)
p = os.path.join(ROOT, 'docs', 'index.html')
if '--check' in sys.argv:
    ok = os.path.exists(p) and open(p).read() == out; print('index.html', 'up to date' if ok else 'OUT OF DATE'); sys.exit(0 if ok else 1)
open(p, 'w').write(out); print('wrote', p)
