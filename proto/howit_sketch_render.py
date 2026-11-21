"""Draw the How it works sketch from docs/how-it-works/sketch/ (proto/howit_sketch_data.py + proto/howit_dem.py outputs).

Writes into docs/how-it-works/sketch/:
  L_rain.png, L_ground.png, L_water.png, L_roads.png, L_access_fire.png, L_access_hospital.png, L_access_police.png, L_check.png
      flat top-down layers, 1200 x 1080 px (5 m per pixel) over the 6.0 x 5.4 km box
  stack.png       the five layers as tilted slabs (rain on top, access at the bottom), 2x pixels
  z_road.png      close-up of one road with its 10 m sample dots and the 20 m depth cells
  anchors.json    every label position, in % of the image it belongs to, plus the numbers shown in the text
No label text is drawn into the images: the page puts HTML labels at these anchors, so text stays sharp and translatable.
    python proto/howit_sketch_render.py
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = f'{ROOT}/docs/how-it-works/sketch'
W, H, MPP = 1200, 1080, 5.0                     # layer pixels, metres per pixel
J = json.load(open(f'{D}/sketch.json'))
X0, Y0, X1, Y1 = J['box_epsg26986']

RAIN = [(0.5, (158, 224, 140)), (2.5, (62, 179, 78)), (10, (247, 211, 32)), (25, (255, 140, 0)), (50, (222, 30, 45))]   # map classes, mm/h
DEPTH = [(0.01, (198, 219, 239)), (0.05, (158, 202, 225)), (0.15, (107, 174, 214)), (0.30, (33, 113, 181)), (1.00, (8, 48, 107))]
ST = {'wet': (242, 193, 78), 'risk': (240, 162, 2), 'closed': (232, 89, 12)}
LOST = (124, 92, 196); FAC = {'hospital': (197, 34, 51), 'fire': (232, 89, 12), 'police': (26, 95, 180)}
PAPER = (246, 247, 244)


def px(x, y): return (x / MPP, y / MPP)


def hillshade():
    Z = np.load(f'{D}/dem20.npz'); z = Z['z'].astype(float); c0 = int((X0 - int(Z['x0'])) / 20); r0 = int((int(Z['y1']) - Y1) / 20)
    z = z[r0:r0 + 270, c0:c0 + 300]; z = np.where(np.isfinite(z), z, np.nanmean(z))
    gy, gx = np.gradient(z, 20.0); slope = np.arctan(np.hypot(gx, gy) * 1.6); asp = np.arctan2(-gx, gy)
    az, alt = math.radians(315), math.radians(42)
    hs = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - asp)
    return z, np.clip(hs, 0, 1)


def up(a, mode=Image.BILINEAR):
    return np.asarray(Image.fromarray(a).resize((W, H), mode))


def ground_rgb(z, hs, tint=True, light=0.0):
    zn = (z - np.percentile(z, 2)) / max(np.percentile(z, 98) - np.percentile(z, 2), 1); zn = np.clip(zn, 0, 1)
    lo, mid, hi = np.array([214, 229, 196]), np.array([233, 228, 197]), np.array([214, 196, 168])
    base = np.where(zn[..., None] < 0.5, lo + (mid - lo) * (zn[..., None] / 0.5), mid + (hi - mid) * ((zn[..., None] - 0.5) / 0.5))
    if not tint: base = np.full_like(base, 236.0)
    shade = 0.55 + 0.55 * hs[..., None]
    rgb = np.clip(base * shade, 0, 255)
    if light: rgb = rgb * (1 - light) + 250 * light
    return up(rgb.astype(np.uint8))


def lerp_ramp(v, ramp):
    out = np.zeros(v.shape + (3,)); a = np.zeros(v.shape)
    for (t0, c0), (t1, c1) in zip(ramp[:-1], ramp[1:]):
        m = (v >= t0) & (v < t1); f = ((v - t0) / (t1 - t0))[m][:, None]; out[m] = np.array(c0) + (np.array(c1) - np.array(c0)) * f
    m = v >= ramp[-1][0]; out[m] = ramp[-1][1]
    return out


def water_overlay(rgb, dep):
    d = up(dep.astype(np.float32), Image.BILINEAR)
    col = lerp_ramp(d, DEPTH); al = np.clip((d - 0.01) / 0.06, 0, 1) * np.where(d < 0.05, 0.55, 0.92)
    return (rgb * (1 - al[..., None]) + col * al[..., None]).astype(np.uint8)


def road_lines(draw, roads, color_fn, width_fn, scale=1.0):
    for r in roads:
        c = color_fn(r)
        if c is None: continue
        w = max(1, int(round(width_fn(r) * scale)))
        for part in r['parts']:
            pts = [(x / MPP * scale, y / MPP * scale) for x, y in part]
            if len(pts) > 1: draw.line(pts, fill=c, width=w, joint='curve')


def base_w(r): return {0: 2, 1: 3, 2: 4}.get(min(r['cls'], 2), 2)


def layer_roads(rgb, roads, mode='status', service=None, ss=2):
    """Roads drawn at ss x then reduced (anti-aliasing). mode: 'grey' all grey; 'status' grey + coloured status; 'access' lost coverage."""
    im = Image.fromarray(rgb).resize((W * ss, H * ss), Image.BILINEAR); dr = ImageDraw.Draw(im)
    grey = (150, 158, 166) if mode != 'grey' else (120, 128, 136)
    road_lines(dr, roads, lambda r: grey, base_w, ss)
    if mode == 'status':
        for st in ('wet', 'risk', 'closed'):
            road_lines(dr, [r for r in roads if r['st'] == st], lambda r: ST[r['st']], lambda r: {'wet': 4, 'risk': 5, 'closed': 7}[r['st']], ss)
    if mode == 'access':
        road_lines(dr, [r for r in roads if service in r['lost'] and r['st'] != 'closed'], lambda r: LOST, lambda r: 5, ss)
        road_lines(dr, [r for r in roads if r['st'] == 'closed'], lambda r: ST['closed'], lambda r: 7, ss)
    if mode == 'check':
        road_lines(dr, [r for r in roads if r['st'] == 'closed'], lambda r: ST['closed'], lambda r: 7, ss)
    return np.asarray(im.resize((W, H), Image.LANCZOS))


def rain_layer(z, hs):
    g = ground_rgb(z, hs, tint=False, light=0.55).astype(float)
    R = np.load(f'{D}/rain.npy'); rr = np.asarray(Image.fromarray(R).resize((W, H), Image.NEAREST))
    col = np.zeros(rr.shape + (3,)); al = np.zeros(rr.shape)
    for t, c in RAIN:
        m = rr >= t; col[m] = c; al[m] = 0.66
    return (g * (1 - al[..., None]) + col * al[..., None]).astype(np.uint8), R


def save(a, name):
    name = name.replace('.png', '.jpg'); Image.fromarray(a).save(f'{D}/{name}', quality=86, optimize=True, progressive=True); return name


def pct(x, y, w=W * MPP, h=H * MPP): return [round(100 * x / w, 2), round(100 * y / h, 2)]


def seg_mid(r):
    best = None
    for part in r['parts']:
        P = np.array(part); L = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        if best is None or L[-1] > best[0]:
            m = L[-1] / 2; i = max(1, int(np.searchsorted(L, m))); f = (m - L[i - 1]) / max(L[i] - L[i - 1], 1e-6)
            best = (L[-1], P[i - 1] + (P[i] - P[i - 1]) * f)
    return best[1], best[0]


# ---------------------------------------------------------------- the tilted stack
SX, SHX, SY, SS = 0.62, 0.30, 0.25, 2          # u scale, shear per v, v scale, output pixel scale


def stack(layers, gap=0.95, thick=12):
    sw, sh = W * SX + H * SHX, H * SY                       # slab footprint (1x)
    step = sh * gap; mx, my = 30, 24
    CW = int((sw + 2 * mx) * SS); CH = int((sh + step * (len(layers) - 1) + thick + 2 * my + 16) * SS)
    can = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); geo = []
    for k in range(len(layers) - 1, -1, -1):                 # bottom slab first: upper slabs cover the back of lower ones
        ox, oy = mx * SS, (my + step * k) * SS
        sx, shx, sy = SX * SS, SHX * SS, SY * SS
        a, b, c = 1 / sx, -shx / (sx * sy), -ox / sx + shx * oy / (sx * sy); d, e, f = 0, 1 / sy, -oy / sy
        src = Image.fromarray(layers[k]).convert('RGBA')
        P = lambda u, v: (ox + sx * u + shx * v, oy + sy * v)
        # shadow and edge first, then the face
        sh_ = Image.new('RGBA', can.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh_)
        q = [P(0, 0), P(W, 0), P(W, H), P(0, H)]
        ds.polygon([(x + 6 * SS, y + (thick + 10) * SS) for x, y in q], fill=(20, 40, 60, 70))
        can.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(9 * SS)))
        de = ImageDraw.Draw(can)
        de.polygon([P(0, H), P(W, H), (P(W, H)[0], P(W, H)[1] + thick * SS), (P(0, H)[0], P(0, H)[1] + thick * SS)], fill=(150, 160, 170, 255))
        de.polygon([P(0, 0), P(0, H), (P(0, H)[0], P(0, H)[1] + thick * SS), (P(0, 0)[0], P(0, 0)[1] + thick * SS)], fill=(176, 184, 192, 255))
        face = src.transform(can.size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
        can.alpha_composite(face)
        de.line(q + [q[0]], fill=(255, 255, 255, 200), width=2 * SS)
        geo.append(dict(k=k, ox=ox, oy=oy))
    geo.sort(key=lambda g: g['k'])
    def proj(k, xm, ym):          # metres in the box -> % of the stack image
        g = geo[k]; u, v = xm / MPP, ym / MPP
        return [round(100 * (g['ox'] + SX * SS * u + SHX * SS * v) / CW, 2), round(100 * (g['oy'] + SY * SS * v) / CH, 2)]
    return can, proj, (CW, CH)


def closeup(dep, r, z, hs, pad=170, out=900):
    """Close-up of road r: 20 m depth cells as squares, the road, and its 10 m sample dots coloured by depth class."""
    P = np.vstack([np.array(p) for p in r['parts']]); cx, cy = P[:, 0].mean(), P[:, 1].mean()
    half = max(np.ptp(P[:, 0]), np.ptp(P[:, 1])) / 2 + pad
    bx0, by0 = cx - half, cy - half; s = out / (2 * half)          # px per metre
    im = Image.new('RGB', (out, out), PAPER); dr = ImageDraw.Draw(im)
    c0, c1 = int(bx0 // 20), int((bx0 + 2 * half) // 20) + 1; r0, r1 = int(by0 // 20), int((by0 + 2 * half) // 20) + 1
    for rr in range(max(r0, 0), min(r1, dep.shape[0])):
        for cc in range(max(c0, 0), min(c1, dep.shape[1])):
            v = float(dep[rr, cc]); x = (cc * 20 - bx0) * s; y = (rr * 20 - by0) * s
            g = int(228 + 22 * hs[min(rr, hs.shape[0] - 1), min(cc, hs.shape[1] - 1)] - 12)
            col = tuple(int(t) for t in lerp_ramp(np.array([v]), DEPTH)[0]) if v >= 0.01 else (g, g, g - 6)
            dr.rectangle([x, y, x + 20 * s, y + 20 * s], fill=col, outline=(255, 255, 255), width=1)
    for q in J['roads']:
        for part in q['parts']:
            pts = [((x - bx0) * s, (y - by0) * s) for x, y in part]
            if len(pts) > 1: dr.line(pts, fill=(90, 98, 106), width=3 if q['id'] != r['id'] else 10)
    dots = []
    for part in r['parts']:
        Pp = np.array(part)
        for a_, b_ in zip(Pp[:-1], Pp[1:]):
            L = np.hypot(*(b_ - a_))
            for t in np.arange(0, L, 10.0):
                qq = a_ + (b_ - a_) * t / max(L, 1e-6); cc, rr = int(qq[0] // 20), int(qq[1] // 20)
                v = float(dep[rr, cc]) if 0 <= rr < dep.shape[0] and 0 <= cc < dep.shape[1] else 0.0
                dots.append((qq, v))
    for qq, v in dots:
        x, y = (qq[0] - bx0) * s, (qq[1] - by0) * s
        if v < 0.01: dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255), outline=(80, 90, 100), width=2)
        else: dr.ellipse([x - 7, y - 7, x + 7, y + 7], fill=tuple(int(t) for t in lerp_ramp(np.array([v]), DEPTH)[0]), outline=(255, 255, 255), width=3)
    top = sorted(dots, key=lambda q: -q[1])[:2]
    pos = [[round(100 * (q[0][0] - bx0) * s / out, 2), round(100 * (q[0][1] - by0) * s / out, 2)] for q in top]
    dry = sum(v < 0.05 for _, v in dots)
    return im, (bx0, by0, s), dict(n=len(dots), dry=int(dry), top=pos)


def main():
    z, hs = hillshade(); dep = np.load(f'{D}/depth.npy').astype(np.float32); roads = J['roads']
    A = dict(made_by='proto/howit_sketch_render.py', time=J['time_local'], layers={}, counts=J['counts'])
    meta = json.load(open(f'{ROOT}/docs/site/data/leominster_sep2023/meta.json'))
    rain, R = rain_layer(z, hs); save(rain, 'L_rain.png')
    ground = ground_rgb(z, hs); g_roads = layer_roads(ground, roads, 'grey'); save(g_roads, 'L_ground.png')
    pale = ground_rgb(z, hs, light=0.35)
    water = water_overlay(pale, dep); save(water, 'L_water.png')
    st = layer_roads(ground_rgb(z, hs, tint=False, light=0.45), roads, 'status'); save(st, 'L_roads.png')
    acc = {}
    for s in ('fire_station', 'hospital', 'police'):
        acc[s] = layer_roads(ground_rgb(z, hs, tint=False, light=0.5), roads, 'access', s); save(acc[s], f'L_access_{s}.png')
    chk = layer_roads(ground_rgb(z, hs, tint=False, light=0.5), roads, 'check'); save(chk, 'L_check.png')

    # ---- anchors (metres in the box)
    km = lambda rs: round(sum(sum(np.hypot(*np.diff(np.array(p), axis=0).T).sum() for p in r['parts']) for r in rs) / 1000, 1)
    closed = sorted([r for r in roads if r['st'] == 'closed' and r['name']], key=lambda r: -r['d'])
    named = {}
    for r in closed:                                   # one label per street name, at its deepest piece
        if r['name'] not in named: named[r['name']] = r
    streets = []
    for r in list(named.values())[:8]:
        m, L = seg_mid(r); streets.append(dict(name=r['name'], d=r['d'], pos=pct(*m), id=r['id']))
    # rain: the wettest 100 m cell
    ri = np.unravel_index(np.argmax(R), R.shape); rain_max = float(R.max())
    rain_pos = pct(ri[1] * 100 + 50, ri[0] * 100 + 50)
    # ground: high and low points
    zi = np.unravel_index(np.nanargmax(z), z.shape); zl = np.unravel_index(np.nanargmin(z), z.shape)
    # deepest water on a road and in the box
    di = np.unravel_index(np.argmax(dep), dep.shape)
    fac = []
    seen = set()
    for f in J['facilities']:
        key = (f['kind'], round(f['x'] / 60), round(f['y'] / 60))
        if key in seen: continue
        seen.add(key); fac.append(dict(kind=f['kind'], name=f['name'] or {'fire': 'Fire station', 'police': 'Police', 'hospital': 'Hospital'}[f['kind']], pos=pct(f['x'], f['y']), m=[f['x'], f['y']]))
    reps = [dict(pos=pct(r['x'], r['y']), src=r['src'], text=r['text'], t=r['t']) for r in J['reports'] if r['src'] in ('LSR', 'StormEvents')]
    streams = {}
    refs = json.load(open(f'{ROOT}/docs/site/data/leominster_sep2023/refs.json'))
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    for row in refs['crossings']['rows']:
        x, y = tr.transform(row[0], row[1])
        if X0 <= x <= X1 and Y0 <= y <= Y1 and row[3] and 'nnamed' not in row[3] and 'namedl' not in row[3]:
            nm = row[3].replace('The ', '')
            streams.setdefault(nm, []).append((x - X0, Y1 - y))
    stream_lbl = [dict(name=k, pos=pct(*np.mean(v, axis=0))) for k, v in streams.items() if k in ('North Nashua River', 'Monoosnoc Brook', 'Fall Brook', 'Reservoir Brook')]
    A['rain'] = dict(max_mmh=round(rain_max), pos=rain_pos, frame_time='6:48 PM', source=J['rain_grid']['source'],
                     box_mean_mmh=round(float(R.mean()), 1),
                     so_far_mm=round(sum(meta['rain_hourly_mean_mm'][:6]) + meta['rain_hourly_mean_mm'][6] * 50 / 60), hourly_mm=meta['rain_hourly_mean_mm'][:13])
    A['ground'] = dict(high_m=round(float(np.nanmax(z))), high_pos=pct(zi[1] * 20 + 10, zi[0] * 20 + 10), low_m=round(float(np.nanmin(z))),
                       low_pos=pct(zl[1] * 20 + 10, zl[0] * 20 + 10), streams=stream_lbl)
    A['water'] = dict(max_cm=round(float(dep.max()) * 100), max_pos=pct(di[1] * 20 + 10, di[0] * 20 + 10),
                      wet_km2=round(float((dep >= 0.05).sum()) * 400 / 1e6, 2), deep_km2=round(float((dep >= 0.30).sum()) * 400 / 1e6, 2))
    A['roads'] = dict(streets=streets, closed=J['counts']['closed'], risk=J['counts']['risk'],
                      closed_km=km([r for r in roads if r['st'] == 'closed']), risk_km=km([r for r in roads if r['st'] == 'risk']),
                      wet_km=km([r for r in roads if r['st'] == 'wet']), total_km=km(roads))
    A['access'] = dict(facilities=fac, minutes=J['access_min'],
                       lost_km={s: km([r for r in roads if s in r['lost'] and r['st'] != 'closed']) for s in ('fire_station', 'hospital', 'police')})
    A['check'] = dict(reports=reps)

    # ---- close-up road: Exchange Street (closed; reported by the National Weather Service at 5:10 PM)
    ex = next(r for r in roads if r['name'] == 'Exchange Street' and r['st'] == 'closed')
    zi_, (bx0, by0, s), nd = closeup(dep, ex, z, hs)
    zi_.save(f'{D}/z_road.png', optimize=True)
    m, L = seg_mid(ex)
    A['closeup'] = dict(name=ex['name'], d=ex['d'], length_m=round(L), dots=nd['n'], dry_dots=nd['dry'], top=nd['top'], pos=[round(100 * (m[0] - bx0) * s / 900, 2), round(100 * (m[1] - by0) * s / 900, 2)],
                        m_per_px=round(1 / s, 3))

    # ---- the stack (top to bottom: rain, ground, water, roads, access)
    can, proj, size = stack([rain, g_roads, water, st, acc['fire_station']])
    can.save(f'{D}/stack.webp', quality=90, method=6)
    def P(k, pos): return proj(k, pos[0] / 100 * W * MPP, pos[1] / 100 * H * MPP)
    A['stack'] = dict(size=size, corners=[[proj(k, 0, 0), proj(k, W * MPP, 0), proj(k, W * MPP, H * MPP), proj(k, 0, H * MPP)] for k in range(5)],
                      rain=P(0, rain_pos), stream=P(1, stream_lbl[0]['pos']) if stream_lbl else None, water=P(2, A['water']['max_pos']),
                      streets=[dict(name=t['name'], d=t['d'], p=P(3, t['pos'])) for t in streets[:3]],
                      facilities=[dict(kind=f['kind'], name=f['name'], p=P(4, f['pos'])) for f in fac])
    json.dump(A, open(f'{D}/anchors.json', 'w'), indent=1)
    print(json.dumps({k: A[k] for k in ('rain', 'water', 'counts')}, indent=0)[:900]); print('roads', A['roads']['closed'], A['roads']['closed_km'], 'access', A['access']['lost_km'])


if __name__ == '__main__':
    main()
