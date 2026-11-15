"""Shared site header and footer: writes the same markup into every page between its markers.

    python tools/site_shell.py          # updates docs/{how-it-works,progress,about}.html and docs/viewer.html in place

Markers: <!--sh:start--><!--sh:end--> (header) and <!--sf:start--><!--sf:end--> (footer). The tab of the page itself gets aria-current.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABS = [('./', 'Model', 'index'), ('how-it-works.html', 'How it works', 'how-it-works'), ('progress.html', 'Progress', 'progress'), ('about.html', 'About', 'about')]
PAGES = {'how-it-works.html': 'how-it-works', 'progress.html': 'progress', 'about.html': 'about', 'viewer.html': 'index'}
MARK = ('<svg class="sh-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3c4.6 6 8.5 10.6 8.5 15.2A8.5 8.5 0 0 1 7.5 18.2C7.5 13.6 11.4 9 16 3z" fill="#1a73e8"/>'
        '<path d="M8.6 20.6c2.4 1.5 4.7 1.5 7 0s4.7-1.5 7.4 0" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>')
GH = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.2-.4-1.3.1-2.7 0 0 .8-.3 2.7 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.5.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></svg>')


def header(cur):
    cur_attr = ' aria-current="page"'
    nav = ''.join(f'<a href="{h}"{cur_attr if k == cur else ""}>{t}</a>' for h, t, k in TABS)
    return ('<header class="sh"><div class="sh-in">'
            f'<a class="sh-brand" href="./">{MARK}<span><b>Mass Flood</b> Watch</span></a>'
            f'<nav class="sh-nav" aria-label="Site">{nav}</nav><span class="sh-grow"></span>'
            '<span class="sh-tag">Research prototype · WPI</span>'
            f'<a class="sh-icon" href="https://github.com/Horus331/mass-flood-watch" title="Code and data on GitHub" aria-label="Code and data on GitHub">{GH}</a>'
            '</div></header>')


FOOTER = ('<footer class="sf"><div class="sf-in">'
          '<div><b>Mass Flood Watch</b>Forecasting which roads flash floods will close, and who loses access to emergency services. '
          'PhD research by Mohab Eldokla, Department of Civil, Environmental and Architectural Engineering, Worcester Polytechnic Institute. '
          'Advisors: Prof. Mingjiang Tao, Prof. Leonard Albano and Prof. Lindsay Graff.</div>'
          '<div><b>Site</b><ul><li><a href="./">Model</a></li><li><a href="how-it-works.html">How it works</a></li><li><a href="progress.html">Progress</a></li><li><a href="about.html">About</a></li></ul></div>'
          '<div><b>More</b><ul><li><a href="model-tree-print.html">The model in text</a></li><li><a href="https://github.com/Horus331/mass-flood-watch">Code and data</a></li><li><a href="mailto:mgeldokla@wpi.edu">Contact</a></li></ul></div>'
          '<div class="sf-note">A research prototype, not an official warning service. For emergencies call 911; for official flood warnings see the National Weather Service.</div>'
          '</div></footer>')


def main():
    for f, cur in PAGES.items():
        p = os.path.join(ROOT, 'docs', f)
        if not os.path.exists(p): continue
        s = open(p, encoding='utf-8').read(); s0 = s
        s = re.sub(r'<!--sh:start-->.*?<!--sh:end-->', lambda m: '<!--sh:start-->' + header(cur) + '<!--sh:end-->', s, flags=re.S)
        s = re.sub(r'<!--sf:start-->.*?<!--sf:end-->', lambda m: '<!--sf:start-->' + FOOTER + '<!--sf:end-->', s, flags=re.S)
        if s != s0: open(p, 'w', encoding='utf-8').write(s); print('updated', f)


if __name__ == '__main__':
    main()
