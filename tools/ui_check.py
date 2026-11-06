"""Screenshots of the LIVE Forecast tab for checking the user interface while a storm is forecast (run on GitHub Actions by
.github/workflows/ui_check.yml; images go to the orphan branch ui-check).  Desktop and phone views, the side panel scrolled to the
forecast-by-forecast card, and the map zoomed on the top 'likely' roads at their peak frame.  Also writes ui_check.json with what the page
showed (headline, card text, console errors) so a check can be read without opening the images."""
import asyncio, json, os, urllib.request
from pyproj import Transformer
BASE = 'https://horus331.github.io/mass-flood-watch/'
OUT = 'shots'; os.makedirs(OUT, exist_ok=True)
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']


def main():
    from playwright.async_api import async_playwright
    S = json.load(urllib.request.urlopen(BASE + 'site/data/forecast_status.json?m=' + str(int(__import__('time').time()))))
    tr = Transformer.from_crs(26986, 4326, always_xy=True)
    segs = [s for s in (S.get('k_of_n') or {}).get('segments', []) if s.get('class') == 'likely'][:3]
    report = dict(issued=S.get('issued'), built=S.get('built'), headline=S.get('headline'), shots=[], errors=[])
    async def run():
        async with async_playwright() as p:
            b = await p.chromium.launch(args=ARGS)
            async def shot(url, name, vp=(1600, 1000), wait=20000, el=None, js=None, phone=False):
                ctx = await (b.new_context(**p.devices['iPhone 13']) if phone else b.new_context(viewport={'width': vp[0], 'height': vp[1]}, device_scale_factor=1.5))
                pg = await ctx.new_page(); errs = []
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
                await pg.goto(BASE + url, wait_until='load'); await pg.wait_for_timeout(wait)
                if js: await pg.evaluate(js); await pg.wait_for_timeout(4000)
                if el and await pg.query_selector(el): await (await pg.query_selector(el)).screenshot(path=f'{OUT}/{name}')
                else: await pg.screenshot(path=f'{OUT}/{name}')
                txt = await pg.evaluate("(()=>{var h=document.getElementById('fhist');return {fhist:h&&!h.hidden?h.innerText.slice(0,1500):null, rank:[...document.querySelectorAll('.rank li, #rankList li')].slice(0,8).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200))}})()")
                report['shots'].append(dict(name=name, url=url, **txt)); report['errors'] += [e[:200] for e in errs if '404' not in e][:5]
                print('wrote', name); await ctx.close()
            await shot('viewer.html?run=forecast', 'fc_desktop.png')
            await shot('viewer.html?run=forecast', 'fc_panel_history.png', js="var h=document.getElementById('fhist'); if(h) h.scrollIntoView({block:'start'})", el='#card')
            await shot('viewer.html?run=forecast', 'fc_phone.png', phone=True)
            for i, s in enumerate(segs):
                lon, lat = tr.transform(s['x'], s['y'])
                await shot(f'viewer.html?run=forecast&c={lon:.5f},{lat:.5f}&z=16', f'fc_road{i + 1}.png')
                report['shots'][-1]['road'] = f"{s.get('road') or 'unnamed'} ({s.get('town')}) {s.get('k')}/8"
            await b.close()
    asyncio.run(run())
    json.dump(report, open(f'{OUT}/ui_check.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
