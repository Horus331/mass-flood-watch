"""Shared header and footer of the site pages (between <!--sh:start-->...<!--sh:end--> and <!--sf:start-->...<!--sf:end-->).
Four tabs (Mo, 21 Nov 2026): Map · How it works · Research · About. Data now lives in About (#data), Progress in Research (#progress);
data.html and progress.html redirect there.
    python proto/site_shell.py"""
import os, re
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
TABS = [('./', 'Map'), ('how-it-works.html', 'How it works'), ('research.html', 'Research'), ('about.html', 'About')]
CUR = {'index.html': './', 'viewer.html': './', 'how-it-works.html': 'how-it-works.html', 'research.html': 'research.html', 'about.html': 'about.html'}
MARK = ('<svg class="sh-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3c4.6 6 8.5 10.6 8.5 15.2A8.5 8.5 0 0 1 7.5 18.2C7.5 13.6 11.4 9 16 3z" '
        'fill="#1a73e8"/><path d="M8.6 20.6c2.4 1.5 4.7 1.5 7 0s4.7-1.5 7.4 0" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>')


def header(cur):
    nav = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == cur else '', t) for h, t in TABS)
    return ('<!--sh:start--><header class="sh"><div class="sh-in"><a class="sh-brand" href="./">%s<span><b>Mass Flood</b> Watch</span></a>'
            '<nav class="sh-nav" aria-label="Site">%s</nav><span class="sh-grow"></span><span class="sh-tag">Research prototype · WPI</span></div></header><!--sh:end-->' % (MARK, nav))


EXPLORE = ('<h4>Explore</h4><ul><li><a href="./">The model map</a></li><li><a href="how-it-works.html">How it works</a></li>'
           '<li><a href="how-it-works.html#s-tree">The model, part by part</a></li><li><a href="research.html">Research</a></li>'
           '<li><a href="research.html#progress">Progress</a></li></ul>')
ABOUT = ('<h4>About</h4><ul><li><a href="about.html">About the project</a></li><li><a href="about.html#team">Team</a></li>'
         '<li><a href="about.html#data">Data sources</a></li><li><a href="model-tree-print.html">The model in text</a></li>'
         '<li><a href="https://www.wpi.edu/academics/departments/civil-environmental-architectural-engineering">WPI Civil, Environmental &amp; Architectural Engineering</a></li></ul>')


def redirect(to, title):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s · Mass Flood Watch</title><meta http-equiv="refresh" content="0; url=%s"><link rel="canonical" href="%s">'
            '<style>body{font:16px/1.5 Roboto,system-ui,sans-serif;margin:48px;color:#202124;background:#fff}</style></head>'
            '<body><p>%s has moved: <a href="%s">continue</a>.</p><script>location.replace(%r)</script></body></html>\n') % (title, to, to, title, to, to)


def main():
    for f in sorted(os.listdir(D)):
        if not f.endswith('.html'): continue
        p = os.path.join(D, f); s = open(p).read(); o = s
        if '<!--sh:start-->' in s: s = re.sub(r'<!--sh:start-->.*?<!--sh:end-->', lambda m: header(CUR.get(f, '')), s, flags=re.S)
        if '<!--sf:start-->' in s:
            s = re.sub(r'<h4>Explore</h4><ul>.*?</ul>', lambda m: EXPLORE, s, count=1, flags=re.S)
            s = re.sub(r'<h4>About</h4><ul>.*?</ul>', lambda m: ABOUT, s, count=1, flags=re.S)
            s = s.replace('<a href="data.html">Data credits</a>', '<a href="about.html#data">Data credits</a>')
        if s != o: open(p, 'w').write(s); print('updated', f)
    open(os.path.join(D, 'data.html'), 'w').write(redirect('about.html#data', 'Data'))
    open(os.path.join(D, 'progress.html'), 'w').write(redirect('research.html#progress', 'Progress'))
    print('redirects: data.html, progress.html')


if __name__ == '__main__':
    main()
