"""Slide images for the advisor meeting (16:9, 3840 x 2160): static GIS maps from the committed ArcGIS layer and cascade output, and
screenshots of the live site. Real data only. Runs on GitHub Actions (.github/workflows/slide_shots.yml), which can reach the basemap tiles.
  python tools/slide_shots.py maps   -> shots/1_*.png 2_*.png 5_*.png 6_*.png
  python tools/slide_shots.py site   -> shots/3_*.png 4_*.png
"""
import json, os, sys, datetime as dt
OUT = 'shots'; os.makedirs(OUT, exist_ok=True)
W, H, DPI = 16, 9, 240
COL = {'High': '#C62828', 'Medium': '#F08C00', 'Low': '#9AA5AE'}
LW = {'High': 2.2, 'Medium': 1.3, 'Low': 0.35}


def maps():
    import numpy as np, geopandas as gpd, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt, contextily as ctx
    from matplotlib.lines import Line2D
    from shapely.geometry import Point, box
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 15})
    G = gpd.read_file('zip://docs/proto/arcgis/d3_road_flood_vulnerability_shp.zip').to_crs(3857)
    POS = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'; REF = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}'   # no API key (CartoDB now needs one)

    def north(ax, x=0.965, y=0.86):
        ax.annotate('N', xy=(x, y + 0.07), xytext=(x, y), xycoords='axes fraction', ha='center', va='center', fontsize=20, fontweight='bold',
                    arrowprops=dict(facecolor='#1B2A33', edgecolor='#1B2A33', width=6, headwidth=18, headlength=16))

    def scalebar(ax, km):
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); lat = 42.4
        m = km * 1000 / np.cos(np.radians(lat))   # web-mercator metres per ground metre at District 3's latitude
        sx = x0 + (x1 - x0) * 0.04; sy = y0 + (y1 - y0) * 0.05
        ax.plot([sx, sx + m], [sy, sy], color='#1B2A33', lw=5, solid_capstyle='butt', zorder=20)
        ax.plot([sx, sx + m / 2], [sy, sy], color='white', lw=2.4, solid_capstyle='butt', zorder=21)
        ax.text(sx + m / 2, sy + (y1 - y0) * 0.015, f'{km:g} km', ha='center', va='bottom', fontsize=15, zorder=22,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1.5))

    def draw(ax, g, scale=1.0):
        for v in ('Low', 'Medium', 'High'):
            s = g[g.vuln == v]
            if len(s): s.plot(ax=ax, color=COL[v], linewidth=LW[v] * scale, zorder={'Low': 3, 'Medium': 4, 'High': 5}[v])

    def legend(ax, g, title, loc='lower right'):
        n = g.vuln.value_counts()
        h = [Line2D([0], [0], color=COL[v], lw=LW[v] * 2 + 1, label=f'{v}  ({n.get(v, 0):,} segment{"" if n.get(v, 0) == 1 else "s"})') for v in ('High', 'Medium', 'Low')]
        L = ax.legend(handles=h, title=title, loc=loc, fontsize=15, title_fontsize=16, frameon=True, framealpha=0.95, borderpad=0.9)
        L.get_frame().set_edgecolor('#C9D2D8')

    def finish(fig, ax, name):
        ax.set_axis_off(); fig.subplots_adjust(0, 0, 1, 1); fig.savefig(f'{OUT}/{name}', dpi=DPI); plt.close(fig); print('wrote', name)

    def frame(ax, cx, cy, half_w):
        half_h = half_w * H / W; ax.set_xlim(cx - half_w, cx + half_w); ax.set_ylim(cy - half_h, cy + half_h)

    def card(ax, x, y, title, rows, ha='left'):
        txt = title + '\n' + '\n'.join(f'{k}:  {v}' for k, v in rows)
        ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va='top', fontsize=15, linespacing=1.55, zorder=30, family='DejaVu Sans',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='white', edgecolor='#C9D2D8', alpha=0.97))

    # 1. all of District 3
    fig, ax = plt.subplots(figsize=(W, H)); cc = G.geometry.centroid; b = [cc.x.quantile(.002), cc.y.quantile(.002), cc.x.quantile(.998), cc.y.quantile(.998)]
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; hw = max((b[2] - b[0]) / 2, (b[3] - b[1]) / 2 * W / H) * 1.12
    frame(ax, cx, cy, hw); draw(ax, G)
    ctx.add_basemap(ax, source=POS, zoom=10, attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors', attribution_size=9); ctx.add_basemap(ax, source=REF, zoom=10, attribution=False, zorder=10)
    legend(ax, G, 'Flood vulnerability, MassDOT District 3'); north(ax); scalebar(ax, 20)
    finish(fig, ax, '1_district3_vulnerability.png')

    def zoom_map(name, lon, lat, half_w_m, title, sid=None, card_rows=None, marker=None, zoom=16):
        p = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(3857)[0]
        fig, ax = plt.subplots(figsize=(W, H)); frame(ax, p.x, p.y, half_w_m)
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); sub = G[G.intersects(box(x0, y0, x1, y1))]
        draw(ax, sub, 2.4)
        if sid is not None:
            s = G[G.seg_id == sid]
            s.plot(ax=ax, color='#1B2A33', linewidth=16, zorder=8); s.plot(ax=ax, color=COL[s.vuln.iloc[0]], linewidth=9, zorder=9)
            e = s.geometry.iloc[0].interpolate(0.5, normalized=True)
            ax.annotate('this segment', (e.x, e.y), xytext=(60, 40), textcoords='offset points', fontsize=16, fontweight='bold', color='#1B2A33', zorder=14,
                        arrowprops=dict(arrowstyle='->', color='#1B2A33', lw=2.5), bbox=dict(facecolor='white', edgecolor='#1B2A33', pad=3))
        if marker:
            m = gpd.GeoSeries([Point(*marker[0])], crs=4326).to_crs(3857)[0]
            ax.scatter([m.x], [m.y], s=650, marker='*', color='#1F4E79', edgecolor='white', linewidth=2, zorder=12)
            ax.annotate(marker[1], (m.x, m.y), xytext=(18, -34), textcoords='offset points', fontsize=15, color='#1F4E79', fontweight='bold', zorder=13,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, pad=2))
        ctx.add_basemap(ax, source=POS, zoom=min(zoom, 16), attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors', attribution_size=9); ctx.add_basemap(ax, source=REF, zoom=min(zoom, 16), attribution=False, zorder=10)
        legend(ax, sub, title); north(ax); scalebar(ax, 0.2 if half_w_m < 1500 else 0.5)
        if card_rows: card(ax, 0.02, 0.97, card_rows[0], card_rows[1])
        finish(fig, ax, name)

    def rows_for(sid):
        r = G[G.seg_id == sid].iloc[0]
        def num(v, nd=2, u=''):
            try: v = float(v)
            except (TypeError, ValueError): return '–'
            return '–' if np.isnan(v) else f'{round(v, nd):g}{u}'
        strm = (r.flag_strm or '').replace(';', ', ')
        dly = 'not on a detour-modelled segment' if num(r.vh_delay) == '–' else f'{num(r.det_min, 1, " min")} added trip time, {num(r.vh_delay, 0, " veh-h")}'
        return (f'{r.road or "Unnamed road"}, {r.town}', [
            ('Vulnerability class', r.vuln), ('Storms flagged (p_close >= 0.5)', f'{num(r.n_flag, 0)} of {num(r.n_cov, 0)} modelled' + (f'  ({strm})' if strm else '')),
            ('Peak modelled depth, 25 storms', num(r.cat_dep_m, 2, ' m')),
            ('Sept 2023 District 3 run: peak depth', num(r.d3_dep_m, 2, ' m')),
            ('Detour delay (Sept 2023 run)', dly),
            ('Documented flood reports on segment', num(r.n_rpt, 0))])

    # 2. Leominster, street level, one segment's attributes (Litchfield Street: High, flagged in 3 storms, 3 reports)
    L = G[(G.town == 'Leominster') & (G.road == 'Litchfield Street') & (G.vuln == 'High')].sort_values('vh_delay', ascending=False).iloc[0]
    c = gpd.GeoSeries([L.geometry.centroid], crs=3857).to_crs(4326)[0]
    zoom_map('2_leominster_street_level_attributes.png', c.x, c.y, 900, 'Flood vulnerability', sid=L.seg_id, card_rows=rows_for(L.seg_id), zoom=17)

    # 6. Worcester, Route 20 @ Grafton St (MassDOT repeat site #24) and the flagged Route 20 segment just east
    zoom_map('6_worcester_route20_grafton.png', -71.7480, 42.2354, 650, 'Flood vulnerability', sid=52654, card_rows=rows_for(52654),
             marker=((-71.74868, 42.23545), 'MassDOT repeat-flood site #24\nRoute 20 @ Grafton St'), zoom=17)

    # 5. residents who lose emergency access at the Leominster peak (cascade output, 2020 Census blocks)
    C = json.loads(open('docs/site/data/leominster_sep2023/cascade.json').read().replace('NaN', 'null'))
    th = C['t_h']; pk = C['totals']['peak']; k = min(range(len(th)), key=lambda i: abs(th[i] - pk['pop_lost_h']))
    rows = [r for r in C['areas']['rows'] if any(a <= k <= b for a, b in r[5])]
    import pandas as pd
    A = pd.DataFrame(rows, columns=['lon', 'lat', 'pop', 'mask', 'h', 'iv'])
    A = gpd.GeoDataFrame(A, geometry=gpd.points_from_xy(A.lon, A.lat), crs=4326).to_crs(3857)
    A['cat'] = np.where(A['mask'] & 8, 'Isolated: no open road to any service', np.where((A['mask'] & 7) == 7, 'Lose hospital, fire and police reach',
                np.where(A['mask'] & 2, 'Lose fire-station reach (8 min)', 'Lose hospital (30 min) or police (10 min) reach')))
    CC = {'Isolated: no open road to any service': '#7B1E1E', 'Lose hospital, fire and police reach': '#C62828', 'Lose fire-station reach (8 min)': '#F08C00',
          'Lose hospital (30 min) or police (10 min) reach': '#E8B33A'}
    R = json.load(open('docs/site/data/leominster_sep2023/roads.json'))['features']
    vf = int(round(th[k] * 60 / 5)); closed = [f for f in R if len(f['properties'].get('d', [])) > vf and f['properties']['d'][vf] >= 30]
    CL = gpd.GeoDataFrame.from_features(closed, crs=4326).to_crs(3857) if closed else None
    bx = C['box_epsg26986']; BB = gpd.GeoSeries([box(*bx)], crs=26986).to_crs(3857).total_bounds
    fig, ax = plt.subplots(figsize=(W, H)); frame(ax, (BB[0] + BB[2]) / 2, (BB[1] + BB[3]) / 2, (BB[2] - BB[0]) / 2 * W / H * 0.62)
    if CL is not None: CL.plot(ax=ax, color='#1B2A33', linewidth=3.2, zorder=6)
    for cat in CC:
        s = A[A.cat == cat]
        if len(s): ax.scatter(s.geometry.x, s.geometry.y, s=np.clip(s['pop'] / 3, 12, 400), color=CC[cat], alpha=0.85, edgecolor='white', linewidth=0.6, zorder=7)
    ctx.add_basemap(ax, source=POS, zoom=13, attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors', attribution_size=9); ctx.add_basemap(ax, source=REF, zoom=13, attribution=False, zorder=10)
    t_loc = (dt.datetime.strptime(C['storm_start'], '%Y-%m-%dT%H:%MZ') + dt.timedelta(hours=th[k]) - dt.timedelta(hours=4))
    h = [Line2D([0], [0], marker='o', color='w', markerfacecolor=CC[c_], markersize=14, label=f'{c_}  ({int(A[A.cat == c_]["pop"].sum()):,} people)') for c_ in CC if (A.cat == c_).any()]
    h.append(Line2D([0], [0], color='#1B2A33', lw=4, label=f'Road closed, 30 cm or more ({len(closed)} segments)'))
    Lg = ax.legend(handles=h, loc='lower right', fontsize=14, title=f'At the peak, {t_loc:%b %-d %-I:%M %p} EDT: {int(A["pop"].sum()):,} residents lose access',
                   title_fontsize=15, framealpha=0.95, borderpad=0.9); Lg.get_frame().set_edgecolor('#C9D2D8')
    north(ax); scalebar(ax, 2)
    finish(fig, ax, '5_leominster_lost_access_peak.png')
    print('lost-access check: map sum', int(A['pop'].sum()), 'cascade peak', pk['pop_lost_any'], 'output frame', k, 't_h', th[k])


def site():
    import asyncio
    from playwright.async_api import async_playwright
    BASE = 'https://horus331.github.io/mass-flood-watch/'
    async def run():
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            async def shot(url, name, rain_off=True, wait=25000, scroll=None, el=None):
                pg = await b.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
                await pg.goto(BASE + url, wait_until='load'); await pg.wait_for_timeout(9000)
                if rain_off: await pg.evaluate("var r=document.getElementById('lyRain'); if(r&&r.checked) r.click()")
                await pg.mouse.move(1919, 1079); await pg.wait_for_timeout(wait)
                if scroll: await pg.evaluate(scroll); await pg.wait_for_timeout(3000)
                if el: await (await pg.query_selector(el)).screenshot(path=f'{OUT}/{name}')
                else: await pg.screenshot(path=f'{OUT}/{name}')
                print('wrote', name); await pg.close()
            await shot('viewer.html?run=leominster_sep2023&c=-71.7620,42.5200&z=14.3&t=91', '3_replay_leominster_sep2023_peak.png')
            await shot('viewer.html?run=leominster_sep2023&c=-71.7600,42.5250&z=16.2&t=91', '3b_replay_leominster_street_level.png')
            await shot('viewer.html?run=whatif', '4a_whatif_leominster.png')
            await shot('viewer.html?run=forecast', '4b_forecast_week.png', rain_off=False)
            await shot('viewer.html?run=d3_sep2023&t=54', '3c_replay_district3.png', wait=35000)
            await b.close()
    asyncio.run(run())


if __name__ == '__main__':
    {'maps': maps, 'site': site}[sys.argv[1]]()
