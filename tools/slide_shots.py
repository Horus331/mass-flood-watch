"""Slide images for the advisor meeting (16:9, 3840 x 2160): static GIS maps from the committed ArcGIS layer and cascade output, and
screenshots of the live site. Real data only. Runs on GitHub Actions (.github/workflows/slide_shots.yml), which can reach the basemap tiles.
  python tools/slide_shots.py maps   -> shots/1_*.png 2_*.png 5_*.png 6_*.png
  python tools/slide_shots.py site   -> shots/3_*.png 4_*.png
"""
import json, os, sys, datetime as dt
OUT = 'shots'; os.makedirs(OUT, exist_ok=True)
EBASE = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}'
EREF = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}'
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


def dpw():
    """Leominster Sept 11 2023 at the replay peak (frame 91, 7:35 PM EDT): live-site depth pack, closed / at-risk roads, impassable
    stretches, and the 4 DPW-confirmed closures. Everything from docs/site/data/leominster_sep2023 (the pack the live site shows)."""
    import numpy as np, geopandas as gpd, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt, contextily as ctx
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from PIL import Image
    from pyproj import Transformer
    from shapely.geometry import shape
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    D = 'docs/site/data/leominster_sep2023/'; F = 91
    m = json.load(open(D + 'meta.json')); assert m['frame_min'] == 5
    T = Transformer.from_crs(4326, 26986, always_xy=True)
    cx, cy = zip(*[T.transform(*c) for c in m['corners']]); x0, x1, y0, y1 = min(cx), max(cx), min(cy), max(cy)
    a = np.asarray(Image.open(D + m['depthc']['sheets'][F // 3]).convert('RGB'))[..., F % 3].astype(float)
    h = 3 * (a / 255) ** 2                                   # metres (pack encoding)
    stops = [(0.05, (158, 202, 225, .78)), (0.15, (107, 174, 214, .82)), (0.30, (33, 113, 181, .86)), (1.00, (8, 48, 107, .90))]
    rgba = np.zeros(h.shape + (4,))
    for i, (lo, c) in enumerate(stops):
        hi = stops[i + 1][0] if i + 1 < len(stops) else 99
        k = (h >= lo) & (h < hi); rgba[k] = [c[0] / 255, c[1] / 255, c[2] / 255, c[3]]
    R = json.load(open(D + 'roads.json'))['features']
    G = gpd.GeoDataFrame([{'id': f['id'], 'n': f['properties'].get('n'), 'd': f['properties']['d'][F] if len(f['properties'].get('d', [])) > F else 0,
                           'geometry': shape(f['geometry'])} for f in R], crs=4326).to_crs(26986)
    PC = json.load(open(D + 'pieces.json')); from shapely.geometry import LineString
    imp = [LineString(PC['lines'][i]) for i in range(len(PC['seg'])) if any(a_ <= F <= b_ for a_, b_ in PC['w30'][i])]
    IMP = gpd.GeoDataFrame(geometry=imp, crs=4326).to_crs(26986) if imp else None
    fig, ax = plt.subplots(figsize=(W, H))
    ccx, ccy = T.transform(-71.7530, 42.5245); hy = 2350; hx = hy * W / H
    ax.set_xlim(ccx - hx, ccx + hx); ax.set_ylim(ccy - hy, ccy + hy)
    ax.imshow(rgba, extent=(x0, x1, y0, y1), origin='upper', zorder=5, interpolation='bilinear')
    risk = G[(G.d >= 15) & (G.d < 30)]; shut = G[G.d >= 30]
    for g_, col, lw in ((risk, '#F0A202', 3.2), (shut, '#E8590C', 3.6)):
        if len(g_): g_.plot(ax=ax, color='white', linewidth=lw + 2.6, zorder=6); g_.plot(ax=ax, color=col, linewidth=lw, zorder=7)
    if IMP is not None: IMP.plot(ax=ax, color='#C62828', linewidth=4.6, zorder=8)
    ctx.add_basemap(ax, crs='EPSG:26986', source=EBASE, zoom=15, attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors', attribution_size=10)
    ctx.add_basemap(ax, crs='EPSG:26986', source=EREF, zoom=15, attribution=False, zorder=9)
    S = [('1', 'Pleasant St @ Colburn St', -71.76727, 42.52065, 'Caught: 0.79 m peak, over 30 cm for 3.7 h\nDPW: closed 2 weeks', (0.015, 0.40)),
         ('2', 'Lancaster St (Rte 117) @ Malburn St', -71.73814, 42.51078, 'Caught: 1.07 m peak, over 30 cm for 9.3 h\nDPW: closed 1 week', (0.665, 0.42)),
         ('3', 'Mechanic St @ Manning Ave', -71.75831, 42.52616, 'Mechanic St itself: 0.07 m (miss)\nWater St, 44 m away: 1.55 m (flagged)\nDPW: closed 1 week', (0.015, 0.82)),
         ('4', 'Hamilton St near Main St', -71.74024, 42.54048, 'Missed: 0.13 m; blocked by debris from a\nrailroad-embankment washout, not water\nDPW: closed 1 week', (0.665, 0.82))]
    for n, nm, lon, lat, txt, off in S:
        x, y = T.transform(lon, lat)
        ok = n in '12'
        ax.scatter([x], [y], s=1500, color='#1B2A33' if ok else ('#5B6770' if n == '3' else '#8A1C1C'), edgecolor='white', linewidth=3, zorder=20)
        ax.text(x, y, n, color='white', fontsize=22, fontweight='bold', ha='center', va='center', zorder=21)
        ax.annotate(f'{n}  {nm}\n{txt}', (x, y), xytext=off, textcoords='axes fraction', va='top', fontsize=17, zorder=22, linespacing=1.35,
                    bbox=dict(boxstyle='round,pad=0.55', facecolor='white', edgecolor='#1B2A33', linewidth=1.4, alpha=0.96),
                    arrowprops=dict(arrowstyle='-', color='#1B2A33', lw=1.8))
    ax.text(0.012, 0.985, 'Leominster, Sept 11, 2023, 7:35 PM — model vs. DPW-confirmed closures', transform=ax.transAxes, fontsize=26, fontweight='bold',
            va='top', ha='left', zorder=30, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#C9D2D8', alpha=0.97))
    hnd = [Patch(facecolor=(158/255, 202/255, 225/255), label='Water 5–15 cm'), Patch(facecolor=(107/255, 174/255, 214/255), label='15–30 cm'),
           Patch(facecolor=(33/255, 113/255, 181/255), label='30–100 cm'), Patch(facecolor=(8/255, 48/255, 107/255), label='100 cm +'),
           Line2D([0], [0], color='#E8590C', lw=5, label='Road closed (30 cm +)'), Line2D([0], [0], color='#F0A202', lw=5, label='Road at risk (15–30 cm)'),
           Line2D([0], [0], color='#C62828', lw=5, label='Impassable stretch'),
           Line2D([0], [0], marker='o', color='w', markerfacecolor='#1B2A33', markersize=20, label='DPW-confirmed closure (numbered)')]
    L = ax.legend(handles=hnd, loc='lower left', bbox_to_anchor=(0.004, 0.035), fontsize=16, ncol=2, framealpha=0.96, borderpad=0.8, columnspacing=1.4); L.get_frame().set_edgecolor('#C9D2D8')
    ax.set_axis_off(); fig.subplots_adjust(0, 0, 1, 1); fig.savefig(f'{OUT}/7_leominster_model_vs_dpw_closures.png', dpi=DPI); plt.close(fig)
    print('wrote 7; closed', len(shut), 'at risk', len(risk), 'impassable pieces', len(imp))


def _depth_rgba(D, F, faint=1.0):
    import numpy as np
    from PIL import Image
    from pyproj import Transformer
    m = json.load(open(D + 'meta.json')); T = Transformer.from_crs(4326, 26986, always_xy=True)
    cx, cy = zip(*[T.transform(*c) for c in m['corners']])
    a = np.asarray(Image.open(D + m['depthc']['sheets'][F // 3]).convert('RGB'))[..., F % 3].astype(float); h = 3 * (a / 255) ** 2
    stops = [(0.05, (158, 202, 225, .78)), (0.15, (107, 174, 214, .82)), (0.30, (33, 113, 181, .86)), (1.00, (8, 48, 107, .90))]
    rgba = np.zeros(h.shape + (4,))
    for i, (lo, c) in enumerate(stops):
        hi = stops[i + 1][0] if i + 1 < len(stops) else 99; k = (h >= lo) & (h < hi)
        rgba[k] = [c[0] / 255, c[1] / 255, c[2] / 255, c[3] * faint]
    return rgba, (min(cx), max(cx), min(cy), max(cy))


def detour():
    """Exchange St / Kingman Dr / Constitution Dr / Granite St closure, Leominster Sept 11 2023 at 7:35 PM: the model's detour (proto/resilience.py
    closure_detours on the live pack, computed into tools/slide_detour_exchange.json)."""
    import numpy as np, geopandas as gpd, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt, contextily as ctx
    from matplotlib.lines import Line2D
    from shapely.geometry import MultiLineString
    plt.rcParams.update({'font.family': 'DejaVu Sans'})
    J = json.load(open('tools/slide_detour_exchange.json'))
    def gdf(parts_list): return gpd.GeoDataFrame(geometry=[MultiLineString(p) for p in parts_list], crs=4326).to_crs(26986)
    DRY, WET, CLS, U, V = gdf(J['dry']), gdf(J['wet']), gdf(J['closed']), gdf([J['u_geo']]), gdf([J['v_geo']])
    b = np.array([DRY.total_bounds, WET.total_bounds, CLS.total_bounds]); x0, y0 = b[:, 0].min(), b[:, 1].min(); x1, y1 = b[:, 2].max(), b[:, 3].max()
    cx, cy = (x0 + x1) / 2 + 0.25 * (x1 - x0), (y0 + y1) / 2 + 0.16 * (y1 - y0); hw = max((x1 - x0) / 2 * 2.2, (y1 - y0) / 2 * 2.4 * W / H, 900); hh = hw * H / W
    fig, ax = plt.subplots(figsize=(W, H)); ax.set_xlim(cx - hw, cx + hw); ax.set_ylim(cy - hh, cy + hh)
    rgba, ext = _depth_rgba('docs/site/data/leominster_sep2023/', 91); ax.imshow(rgba, extent=ext, origin='upper', zorder=5, interpolation='bilinear')
    CLS.plot(ax=ax, color='#1B2A33', linewidth=16, zorder=7); CLS.plot(ax=ax, color='#C62828', linewidth=12, zorder=8)
    WET.plot(ax=ax, color='white', linewidth=10, zorder=9); WET.plot(ax=ax, color='#E8590C', linewidth=6, linestyle=(0, (2.2, 1.4)), zorder=10)
    DRY.plot(ax=ax, color='white', linewidth=7, zorder=11); DRY.plot(ax=ax, color='#1F5FA8', linewidth=4.5, zorder=12)
    ctx.add_basemap(ax, crs='EPSG:26986', source=EBASE, zoom=16, attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors', attribution_size=10)
    ctx.add_basemap(ax, crs='EPSG:26986', source=EREF, zoom=16, attribution=False, zorder=13)
    for G_, lab, col in ((U, 'A', '#1B2A33'), (V, 'B', '#1B2A33')):
        pt = G_.geometry.iloc[0].interpolate(0.5, normalized=True)
        ax.scatter([pt.x], [pt.y], s=1300, color=col, edgecolor='white', linewidth=3, zorder=20); ax.text(pt.x, pt.y, lab, color='white', fontsize=22, fontweight='bold', ha='center', va='center', zorder=21)
    def lab_line(G_, text, col, frac, off):
        geom = G_.geometry.union_all() if hasattr(G_.geometry, 'union_all') else G_.unary_union
        from shapely.ops import linemerge
        L = linemerge(geom) if geom.geom_type == 'MultiLineString' else geom
        L = max(L.geoms, key=lambda g: g.length) if L.geom_type == 'MultiLineString' else L
        pt = L.interpolate(frac, normalized=True)
        ax.annotate(text, (pt.x, pt.y), xytext=off, textcoords='offset points', fontsize=20, fontweight='bold', color=col, zorder=25,
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=col, linewidth=2), arrowprops=dict(arrowstyle='-', color=col, lw=2))
    lab_line(DRY, f"Normal (dry day): {J['dry_min']:.1f} min", '#1F5FA8', 0.5, (-430, -110))
    lab_line(WET, f"Detour: {J['wet_min']:.1f} min", '#E8590C', 0.5, (110, 30))
    ex = J['wet_min'] - J['dry_min']; vph = J['aadt'] / 24
    box = (f"Extra time per trip:  {ex:.1f} min\n"
           f"Daily traffic on the closed stretch:  {J['aadt']:,.0f} vehicles/day\n(MassDOT AADT, busiest segment = Kingman Dr)\n"
           f"Vehicles per hour (flat daily profile):  {vph:,.0f}\n"
           f"Delay:  {vph:,.0f} veh/h x {ex:.1f} min / 60 = {vph * ex / 60:,.1f} vehicle-hours per hour closed\n"
           f"Stretch closed {J['hours_closed']:.1f} h in this run")
    ax.text(0.012, 0.975, box, transform=ax.transAxes, fontsize=17, va='top', ha='left', zorder=30, linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.7', facecolor='white', edgecolor='#C9D2D8', alpha=0.97))
    h = [Line2D([0], [0], color='#C62828', lw=7, label='Closed stretch (30 cm or more): Exchange St, Kingman Dr, Constitution Dr, Granite St'),
         Line2D([0], [0], color='#1F5FA8', lw=6, label='Normal route A to B (through the now-closed streets)'), Line2D([0], [0], color='#E8590C', lw=6, ls=(0, (2.2, 1.4)), label='Detour the model finds with roads over 30 cm closed'),
         Line2D([0], [0], marker='s', color='w', markerfacecolor=(33/255, 113/255, 181/255), markersize=16, label='Modelled water depth, 7:35 PM')]
    Lg = ax.legend(handles=h, loc='lower right', bbox_to_anchor=(0.996, 0.035), fontsize=16, framealpha=0.96, borderpad=0.8); Lg.get_frame().set_edgecolor('#C9D2D8')
    ax.set_axis_off(); fig.subplots_adjust(0, 0, 1, 1); fig.savefig(f'{OUT}/8_detour_exchange_st_leominster.png', dpi=DPI); plt.close(fig); print('wrote 8')


def services():
    """All of District 3: road network, hospitals / fire / police the lost-access step uses (docs/network/facilities.json, OpenStreetMap),
    faint Leominster Sept 2023 peak depth. No title (background image)."""
    import numpy as np, geopandas as gpd, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt, contextily as ctx
    from matplotlib.lines import Line2D
    G = gpd.read_file('zip://docs/proto/arcgis/d3_road_flood_vulnerability_shp.zip')
    hull = (G.geometry.union_all() if hasattr(G.geometry, 'union_all') else G.unary_union).convex_hull
    F = json.load(open('docs/network/facilities.json'))['facilities']
    pts = {}
    for k in ('hospital', 'fire_station', 'police'):
        P = gpd.GeoDataFrame(geometry=gpd.points_from_xy([r[0] for r in F[k]], [r[1] for r in F[k]]), crs=4326).to_crs(26986)
        keep = [len(G.sindex.query(p.buffer(300), predicate='intersects')) > 0 for p in P.geometry]; pts[k] = P[keep]
    fig, ax = plt.subplots(figsize=(W, H)); x0, y0, x1, y1 = G.total_bounds
    cc = G.geometry.centroid; bx = [cc.x.quantile(.002), cc.y.quantile(.002), cc.x.quantile(.998), cc.y.quantile(.998)]
    cx, cy = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2; hw = max((bx[2] - bx[0]) / 2, (bx[3] - bx[1]) / 2 * W / H) * 1.1; hh = hw * H / W
    ax.set_xlim(cx - hw, cx + hw); ax.set_ylim(cy - hh, cy + hh)
    G.plot(ax=ax, color='#9AA3AB', linewidth=0.35, zorder=4)
    rgba, ext = _depth_rgba('docs/site/data/leominster_sep2023/', 91, faint=0.55); ax.imshow(rgba, extent=ext, origin='upper', zorder=5, interpolation='bilinear')
    st = {'hospital': ('#C62828', 'Hospitals', 95), 'fire_station': ('#F08C00', 'Fire stations', 32), 'police': ('#1F5FA8', 'Police stations', 32)}
    for k in ('fire_station', 'police', 'hospital'):
        c, _, sz = st[k]; ax.scatter(pts[k].geometry.x, pts[k].geometry.y, s=sz, color=c, edgecolor='white', linewidth=0.8, zorder=7 + (k == 'hospital'))
    ctx.add_basemap(ax, crs='EPSG:26986', source=EBASE, zoom=10, attribution='Basemap: Esri, HERE, Garmin, OpenStreetMap contributors · facilities: OpenStreetMap', attribution_size=10)
    h = [Line2D([0], [0], marker='o', color='w', markerfacecolor=st[k][0], markersize=14 if k == 'hospital' else 11, label=f'{st[k][1]} ({len(pts[k])})') for k in ('hospital', 'fire_station', 'police')]
    h.append(Line2D([0], [0], color='#9AA3AB', lw=2, label='District 3 roads (48,945 segments)'))
    Lg = ax.legend(handles=h, loc='lower left', bbox_to_anchor=(0.004, 0.035), fontsize=16, framealpha=0.95, borderpad=0.8); Lg.get_frame().set_edgecolor('#C9D2D8')
    ax.set_axis_off(); fig.subplots_adjust(0, 0, 1, 1); fig.savefig(f'{OUT}/9_district3_services_background.png', dpi=DPI); plt.close(fig)
    print('wrote 9; counts', {k: len(v) for k, v in pts.items()})


if __name__ == '__main__':
    {'maps': maps, 'site': site, 'dpw': dpw, 'detour': detour, 'services': services}[sys.argv[1]]()
