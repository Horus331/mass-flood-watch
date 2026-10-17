"""One-time helper: copy the WPI logo from wpi.edu's page header into docs/wpi-logo.svg.
The letters 'WPI' are drawn white on wpi.edu's dark header; they get class "wm" so the map page can colour them to match its theme."""
import os, re, requests
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, 'docs', 'wpi-logo.svg')
if os.path.exists(OUT): raise SystemExit('logo already present')
html = requests.get('https://www.wpi.edu/', headers={'User-Agent': 'Mozilla/5.0 (student research map)'}, timeout=60).text
svgs = re.findall(r'<svg[^>]*viewBox="0 0 300\.06 97\.03"[^>]*>.*?</svg>', html, re.S) or [s for s in re.findall(r'<svg.*?</svg>', html, re.S) if 'ac2b37' in s.lower() and len(s) > 10000]
if not svgs: raise SystemExit('logo not found on wpi.edu')
svg = svgs[0]
svg = re.sub(r'(d="(?:m299\.62 16\.6|M257\.08 16\.49)[^"]*"\s+)class="cls-4"', r'\1class="wm"', svg)       # the I and the WP letters
svg = re.sub(r'\sid="[^"]*"', '', svg); svg = svg.replace('<svg ', '<svg aria-hidden="true" ', 1)
svg = re.sub(r'\.cls-(\d)', r'.wpi\1', svg).replace('class="cls-', 'class="wpi')                        # avoid clashing with page CSS
open(OUT, 'w').write(svg); print('saved', OUT, len(svg), 'bytes; letters recoloured:', svg.count('class="wm"'))
