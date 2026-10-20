"""Culvert hydraulics for road-stream crossings: FHWA HDS-5 inlet control + a full-flow outlet-control check.

    python sim/infra/culvert.py --selftest
    from culvert import headwater, q_at_headwater, assess_crossing

Inlet control (FHWA HDS-5, 3rd ed. 2012, Appendix A; Normann et al. 1985), in US customary units with Ku = 1:
    unsubmerged, form 1:  HWi/D = Hc/D + K (Q / (A D^0.5))^M + Ks S          Hc = dc + Vc^2 / 2g (specific head at critical depth)
    unsubmerged, form 2:  HWi/D = K (Q / (A D^0.5))^M
    submerged:            HWi/D = c (Q / (A D^0.5))^2 + Y + Ks S
    Ks = -0.5 (0.7 for mitered inlets); unsubmerged for Q/(A D^0.5) <= 3.5, submerged >= 4.0, linear blend between (HDS-5 draws a
    tangent curve; the gap is < 2 % of HW for the tabled shapes).  D = rise, A = full barrel area, Q per barrel.
    (SI: Ku = 1.811 and the limits become 1.93 / 2.21; computing in US units avoids carrying two sets of constants.)
Outlet control (HDS-5 eq. 4, full barrel), SI:
    H = [1 + ke + 2 g n^2 L / R^(4/3)] V^2 / 2g ;  HWo = H + ho - S L ;  ho = max(TW, (dc + D) / 2)
Governing headwater = max(HWi, HWo).  q_at_headwater inverts it by bisection: the flow the barrel(s) pass at a given headwater.

Status at a crossing (assess_crossing): headwater HW (m above the inlet invert) from the flood run,
    overtopped   HW >= crest (road crest above the invert: deck - invert, else rise + fill)
    surcharged   HW / rise > 1.0 (inlet submerged; HDS-5 / most DOT design limits are HW/D 1.0-1.5)
    ok           otherwise;  unknown when there is no geometry and no crest.
These are hydraulic states (L2 in docs/validation/protocol.md), not structural failure predictions.
"""
import math, sys

G_US, G_SI, FT = 32.174, 9.80665, 0.3048
CFS = FT ** 3

# HDS-5 Table A.1/A.2/A.4 inlet-control constants: (form, K, M, c, Y, Ks).  Key: (shape, material, inlet edge) in canonical words
# (shape: circular / elliptical / pipe_arch / box / arch_open; material: concrete / metal / plastic / stone / wood; inlet: projecting /
# headwall / wingwall / headwall_wingwall / mitered / groove_headwall / groove_projecting / chamfer_headwall).
COEF = {
    ('circular', 'concrete', 'headwall'):          (1, 0.0098, 2.0, 0.0398, 0.67, -0.5),   # Chart 1 scale 1, square edge with headwall
    ('circular', 'concrete', 'groove_headwall'):   (1, 0.0018, 2.0, 0.0292, 0.74, -0.5),   # scale 2, groove end with headwall
    ('circular', 'concrete', 'groove_projecting'): (1, 0.0045, 2.0, 0.0317, 0.69, -0.5),   # scale 3, groove end projecting
    ('circular', 'metal', 'headwall'):             (1, 0.0078, 2.0, 0.0379, 0.69, -0.5),   # Chart 2 scale 1
    ('circular', 'metal', 'mitered'):              (1, 0.0210, 1.33, 0.0463, 0.75, 0.7),   # scale 2, mitered to conform to slope
    ('circular', 'metal', 'projecting'):           (1, 0.0340, 1.50, 0.0553, 0.54, -0.5),  # scale 3, projecting
    ('box', 'concrete', 'wingwall'):               (1, 0.026, 1.0, 0.0347, 0.81, -0.5),    # Chart 8, 30-75 deg wingwall flares
    ('box', 'concrete', 'headwall_wingwall'):      (1, 0.061, 0.75, 0.0400, 0.80, -0.5),   # 90 and 15 deg wingwall flares
    ('box', 'concrete', 'projecting'):             (1, 0.061, 0.75, 0.0423, 0.82, -0.5),   # 0 deg wingwall flares (extensions of sides)
    ('box', 'concrete', 'chamfer_headwall'):       (2, 0.515, 0.667, 0.0375, 0.79, -0.5),  # Chart 9/10, 90 deg headwall with 3/4" chamfers
    ('elliptical', 'concrete', 'headwall'):        (1, 0.0100, 2.0, 0.0398, 0.67, -0.5),   # Chart 29, square edge with headwall
    ('pipe_arch', 'metal', 'headwall'):            (1, 0.0083, 2.0, 0.0379, 0.69, -0.5),   # Chart 34, 90 deg headwall
    ('pipe_arch', 'metal', 'mitered'):             (1, 0.0300, 1.0, 0.0463, 0.75, 0.7),
    ('pipe_arch', 'metal', 'projecting'):          (1, 0.0340, 1.5, 0.0496, 0.57, -0.5),
    ('arch_closed', 'metal', 'headwall'):          (1, 0.0083, 2.0, 0.0379, 0.69, -0.5),   # CM arch (structural plate)
    ('arch_closed', 'metal', 'mitered'):           (1, 0.0300, 1.0, 0.0473, 0.75, 0.7),
    ('arch_closed', 'metal', 'projecting'):        (1, 0.0340, 1.5, 0.0496, 0.57, -0.5),
    ('arch_open', 'concrete', 'mitered'):          (2, 0.44, 0.74, 0.040, 0.48, 0.7),      # Table A.4 concrete open-bottom arch, 2:1 span:rise, 0 deg flare
    ('arch_open', 'concrete', 'headwall_wingwall'): (2, 0.47, 0.68, 0.04, 0.62, -0.5),    # 45 deg flare
    ('arch_open', 'concrete', 'headwall'):         (2, 0.48, 0.65, 0.041, 0.57, -0.5),     # 90 deg headwall
}
# entrance-loss coefficient ke (HDS-5 Table C.2) and Manning n (HDS-5 Table B.1, typical values) for the outlet-control check
KE = {('concrete', 'projecting'): 0.5, ('concrete', 'headwall'): 0.5, ('concrete', 'groove_headwall'): 0.2, ('concrete', 'groove_projecting'): 0.2,
      ('concrete', 'mitered'): 0.7, ('concrete', 'wingwall'): 0.4, ('concrete', 'headwall_wingwall'): 0.5, ('concrete', 'chamfer_headwall'): 0.2,
      ('metal', 'projecting'): 0.9, ('metal', 'headwall'): 0.5, ('metal', 'mitered'): 0.7, ('metal', 'wingwall'): 0.5, ('metal', 'headwall_wingwall'): 0.5}
N_MANNING = dict(concrete=0.012, metal=0.024, plastic=0.012, stone=0.025, wood=0.016, other=0.015)
INLET_FALLBACK = dict(wingwall='headwall', headwall_wingwall='headwall', chamfer_headwall='headwall', groove_headwall='headwall',
                      groove_projecting='projecting', none='projecting', other='headwall', unknown='headwall')

def coef_for(shape, material, inlet):
    """HDS-5 constants for a crossing described in canonical words; falls back to the nearest tabled case and says so.
    Returns (key_used, (form, K, M, c, Y, Ks), exact: bool)."""
    shape = shape or 'circular'; material = material or 'concrete'; inlet = inlet or 'headwall'
    key = (shape, material, inlet)
    if key in COEF: return key, COEF[key], True
    # materials without tables: smooth plastic ~ concrete, corrugated/other ~ metal; stone/wood boxes ~ concrete box
    thin = inlet in ('projecting', 'mitered', 'none')                      # thin-wall plastic ends behave like CMP ends (as HY-8 treats them)
    mat = {'plastic': 'metal' if thin else 'concrete', 'stone': 'concrete', 'wood': 'concrete', 'other': 'concrete'}.get(material, material)
    shp = {'arch_open': 'arch_open'}.get(shape, shape)
    if shp == 'box': mat = 'concrete'
    if shp in ('pipe_arch', 'arch_closed'): mat = 'metal'
    if shp == 'elliptical': mat = 'concrete'
    if shp == 'arch_open': mat = 'concrete'
    fb = 'groove_projecting' if (shp, mat, inlet) == ('circular', 'concrete', 'projecting') else INLET_FALLBACK.get(inlet, 'headwall')
    for inl in (inlet, fb, 'headwall', 'projecting', 'wingwall', 'mitered'):
        if (shp, mat, inl) in COEF: return (shp, mat, inl), COEF[(shp, mat, inl)], False
    return ('circular', 'concrete', 'headwall'), COEF[('circular', 'concrete', 'headwall')], False

# ---- barrel geometry (any unit, consistent) ----
def top_width(shape, B, D, y):
    """Free-surface width at depth y for a barrel of span B and rise D."""
    if y <= 0: return B if shape in ('box', 'arch_open') else 0.0
    if y >= D: return 0.0 if shape not in ('box',) else B
    if shape == 'box': return B
    if shape == 'arch_open':                                     # vertical walls to mid-rise, semi-ellipse crown above (Con/Span-like)
        h = 0.5 * D
        return B if y <= h else B * math.sqrt(max(0.0, 1 - ((y - h) / (D - h)) ** 2))
    if shape == 'circular': B = D                                # circle, ellipse, pipe-arch, closed arch: ellipse of span B and rise D
    return B * math.sqrt(max(0.0, 1 - (1 - 2 * y / D) ** 2))

def flow_area(shape, B, D, y, n=200):
    """Flow area below depth y (midpoint integration of the top width; exact closed forms agree to < 0.1 %)."""
    y = min(max(y, 0.0), D)
    if y <= 0: return 0.0
    if shape == 'box': return B * y
    if shape == 'circular':
        th = 2 * math.acos(1 - 2 * y / D); return D * D / 8 * (th - math.sin(th))
    dy = y / n; return sum(top_width(shape, B, D, (k + 0.5) * dy) for k in range(n)) * dy

def full_area(shape, B, D): return flow_area(shape, B, D, D)

def wetted_perimeter_full(shape, B, D):
    if shape == 'box': return 2 * (B + D)
    if shape == 'circular': return math.pi * D
    if shape == 'arch_open': h = 0.5 * D; a, b = B / 2, D - h; return B + 2 * h + math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b))) / 2   # bed + walls + half-ellipse crown (Ramanujan)
    a, b = B / 2, D / 2; return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))

def critical_depth(Q, shape, B, D, g=G_SI):
    """Critical depth: Q^2/g = A^3/T, bisection on y in (0, D); capped at D (closed conduits flowing full have no free surface)."""
    if Q <= 0: return 0.0
    f = lambda y: flow_area(shape, B, D, y) ** 3 / max(top_width(shape, B, D, y), 1e-9) - Q * Q / g
    lo, hi = 1e-6 * D, D * (1 - 1e-6)
    if f(hi) < 0: return D
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if f(m) < 0: lo = m
        else: hi = m
    return 0.5 * (lo + hi)

# ---- inlet / outlet control ----
def hw_inlet(Q, shape, span, rise, material='concrete', inlet='headwall', S=0.01, nb=1):
    """Inlet-control headwater (m above the inlet invert) for total flow Q (m3/s) through nb identical barrels of span x rise (m)."""
    if Q <= 0: return 0.0
    key, (form, K, M, c, Y, Ks), _ = coef_for(shape, material, inlet)
    q = Q / nb / CFS; B, D = (rise if shape == 'circular' else span) / FT, rise / FT
    A = full_area(shape, B, D); x = q / (A * math.sqrt(D))
    def unsub():
        if form == 1:
            dc = critical_depth(q, shape, B, D, G_US); Hc = dc + (q / max(flow_area(shape, B, D, dc), 1e-9)) ** 2 / (2 * G_US)
            return Hc / D + K * x ** M + Ks * S
        return K * x ** M
    sub = lambda: c * x * x + Y + Ks * S
    if x <= 3.5: r = unsub()
    elif x >= 4.0: r = sub()
    else:                                                        # transition: blend the two forms evaluated at the zone limits
        w = (x - 3.5) / 0.5; r = (1 - w) * unsub() + w * sub()
    return max(r, 0.0) * rise

def hw_outlet(Q, shape, span, rise, length=20.0, material='concrete', inlet='headwall', S=0.01, tw=0.0, nb=1, n=None, ke=None, full=None):
    """Outlet-control headwater (m above the inlet invert), full-barrel energy equation (HDS-5 eq. 4), per barrel.
    ho = max(TW, (dc + D)/2) is HDS-5's approximation for a barrel flowing full or nearly full at the outlet; when the barrel is not
    full (full=None: inlet unsubmerged and TW < D) ho = max(TW, dc) instead, otherwise a trickle would read as HW = D/2."""
    if Q <= 0: return 0.0
    q = Q / nb; B = rise if shape == 'circular' else span; D = rise
    A = full_area(shape, B, D); R = A / wetted_perimeter_full(shape, B, D); V = q / A
    n = n or N_MANNING.get(material, 0.015); ke = KE.get((material, inlet), 0.5) if ke is None else ke
    H = (1 + ke + 2 * G_SI * n * n * length / R ** (4 / 3)) * V * V / (2 * G_SI)
    dc = critical_depth(q, shape, B, D)
    if full is None: full = tw >= D or hw_inlet(Q, shape, span, rise, material, inlet, S, nb) >= D
    ho = max(tw, (dc + D) / 2) if full else max(tw, dc)
    return max(H + ho - S * length, 0.0)

def headwater(Q, shape, span, rise, material='concrete', inlet='headwall', S=0.01, length=20.0, tw=0.0, nb=1):
    hi = hw_inlet(Q, shape, span, rise, material, inlet, S, nb); ho = hw_outlet(Q, shape, span, rise, length, material, inlet, S, tw, nb)
    return dict(hw_inlet=hi, hw_outlet=ho, hw=max(hi, ho), control='inlet' if hi >= ho else 'outlet')

def q_at_headwater(HW, shape, span, rise, material='concrete', inlet='headwall', S=0.01, length=20.0, tw=0.0, nb=1):
    """Flow (m3/s) that the barrel(s) pass at headwater HW (m above invert): invert max(HWi, HWo)(Q) = HW by bisection."""
    if HW <= 0: return 0.0
    f = lambda Q: headwater(Q, shape, span, rise, material, inlet, S, length, tw, nb)['hw'] - HW
    lo, hi = 0.0, 1.0
    while f(hi) < 0 and hi < 1e5: hi *= 2
    for _ in range(50):
        m = 0.5 * (lo + hi)
        if f(m) < 0: lo = m
        else: hi = m
    return 0.5 * (lo + hi)

def assess_crossing(hw_m, shape=None, span=None, rise=None, material=None, inlet=None, nb=1, crest_m=None, slope=0.01, length=None, q_model=None,
                    surcharge_ratio=1.0):
    """Hydraulic state of one crossing at headwater hw_m (m above the inlet invert).
    crest_m: road crest above the invert (deck - invert, or rise + fill).  Returns a dict (status, hw_rise, q_pass, q_cap_crest, basis...)."""
    out = dict(hw_m=None if hw_m is None else round(float(hw_m), 3), hw_rise=None, status='unknown', basis=None, q_pass_m3s=None, q_cap_crest_m3s=None,
               coef=None, coef_exact=None, control=None)
    if hw_m is None: return out
    geom = bool(rise and rise > 0 and (shape == 'circular' or (span and span > 0)))
    if geom:
        span = span or rise; L = length or max(10.0, 2 * (crest_m or rise + 1.0) + 8.0)     # unknown barrel length: road width ~8 m + 2:1 fill slopes
        out['hw_rise'] = round(hw_m / rise, 3); key, _, exact = coef_for(shape, material, inlet); out.update(coef='/'.join(key), coef_exact=exact)
        qp = q_at_headwater(min(hw_m, crest_m) if crest_m else hw_m, shape, span, rise, material or 'concrete', inlet or 'headwall', slope, L, 0.0, nb or 1)
        out['q_pass_m3s'] = round(qp, 3); out['control'] = headwater(qp, shape, span, rise, material or 'concrete', inlet or 'headwall', slope, L, 0.0, nb or 1)['control'] if qp > 0 else None
        if crest_m: out['q_cap_crest_m3s'] = round(q_at_headwater(crest_m, shape, span, rise, material or 'concrete', inlet or 'headwall', slope, L, 0.0, nb or 1), 3)
        if q_model is not None and out['q_cap_crest_m3s']: out['q_ratio'] = round(q_model / out['q_cap_crest_m3s'], 3)
    if crest_m is not None and hw_m >= crest_m: out.update(status='overtopped', basis='crest')
    elif geom and hw_m / rise > surcharge_ratio: out.update(status='surcharged', basis='rise')
    elif geom or crest_m is not None: out.update(status='ok', basis='rise' if geom else 'crest')
    return out

def selftest():
    ok = True
    def check(name, cond, detail=''):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name, detail)
    # 1. HDS-5 Chart 1 example (concrete pipe, inlet control): D = 42 in, Q = 120 cfs -> HW/D 2.5 / 2.1 / 2.2 for scales 1 / 2 / 3 (nomograph)
    D = 42 * 0.0254; Q = 120 * CFS
    for inl, pub in (('headwall', 2.5), ('groove_headwall', 2.1), ('groove_projecting', 2.2)):
        r = hw_inlet(Q, 'circular', D, D, 'concrete', inl, S=0.0) / D
        check(f'Chart 1 concrete {inl}', abs(r - pub) <= 0.12, f'HW/D {r:.2f} vs nomograph {pub}')
    # 2. HDS-5 Chart 2 example (CMP): D = 36 in, Q = 66 cfs -> HW/D 1.8 / 2.1 / 2.2 (headwall / mitered / projecting)
    D = 36 * 0.0254; Q = 66 * CFS
    for inl, pub in (('headwall', 1.8), ('mitered', 2.1), ('projecting', 2.2)):
        r = hw_inlet(Q, 'circular', D, D, 'metal', inl, S=0.0) / D
        check(f'Chart 2 CMP {inl}', abs(r - pub) <= 0.12, f'HW/D {r:.2f} vs nomograph {pub}')
    # 3. HDS-5 critical-depth chart example (circular): D = 66 in, Q = 100 cfs -> dc/D = 0.50
    D = 66 * 0.0254; dc = critical_depth(100 * CFS, 'circular', D, D)
    check('critical depth chart', abs(dc / D - 0.50) <= 0.03, f'dc/D {dc / D:.3f} vs 0.50')
    # 4. closed-form checks: circle area by integration vs exact; box critical depth = (q^2/g)^(1/3)
    check('ellipse(B=D) area = circle', abs(flow_area('elliptical', 1.0, 1.0, 0.3) - flow_area('circular', 1.0, 1.0, 0.3)) < 1e-3)
    dcb = critical_depth(3.0, 'box', 2.0, 2.0); check('box critical depth', abs(dcb - (1.5 ** 2 / G_SI) ** (1 / 3)) < 1e-4, f'{dcb:.4f}')
    # 5. outlet control, hand calculation: concrete pipe D = 1 m, n 0.012, L 30 m, ke 0.5, S 0.01, Q 1.5 m3/s, TW 0
    #    H = (1 + 0.5 + 19.63*0.012^2*30/0.25^(4/3)) * 1.910^2/19.61 = 0.379; dc = 0.707 -> ho = 0.854; HWo = 0.379 + 0.854 - 0.30 = 0.933
    hwo = hw_outlet(1.5, 'circular', 1.0, 1.0, 30.0, 'concrete', 'headwall', 0.01, 0.0, full=True)
    check('outlet control hand calc', abs(hwo - 0.933) < 0.01, f'{hwo:.3f} vs 0.933')
    # 6. continuity at the transition zone and monotonic headwater; inversion round trip
    hs = [hw_inlet(q, 'box', 2.0, 1.5, 'concrete', 'wingwall', 0.01) for q in [0.5 * k for k in range(1, 60)]]
    check('inlet HW monotonic in Q (box)', all(b > a for a, b in zip(hs, hs[1:])))
    hw = headwater(4.0, 'circular', 1.2, 1.2, 'metal', 'projecting', 0.02, 25.0)['hw']; qb = q_at_headwater(hw, 'circular', 1.2, 1.2, 'metal', 'projecting', 0.02, 25.0)
    check('q_at_headwater inverts headwater', abs(qb - 4.0) < 1e-3, f'{qb:.4f}')
    check('two barrels pass twice the flow', abs(q_at_headwater(1.5, 'box', 2, 1.5, nb=2) - 2 * q_at_headwater(1.5, 'box', 2, 1.5)) < 1e-3)
    # 7. coefficient fallbacks and status
    k, c_, ex = coef_for('circular', 'plastic', 'projecting'); check('plastic projecting -> CMP projecting table', k == ('circular', 'metal', 'projecting') and not ex, k)
    check('concrete projecting -> groove end projecting', coef_for('circular', 'concrete', 'projecting')[0] == ('circular', 'concrete', 'groove_projecting'))
    check('exact key', coef_for('box', 'concrete', 'wingwall')[2])
    a = assess_crossing(2.5, 'circular', 1.0, 1.0, 'concrete', 'headwall', crest_m=2.0); check('overtopped', a['status'] == 'overtopped' and a['hw_rise'] == 2.5, a)
    a = assess_crossing(1.4, 'circular', 1.0, 1.0, 'concrete', 'headwall', crest_m=2.0); check('surcharged', a['status'] == 'surcharged' and 0 < a['q_pass_m3s'] < a['q_cap_crest_m3s'], a)
    a = assess_crossing(0.6, 'box', 2.0, 1.5, 'concrete', 'wingwall', crest_m=2.5); check('ok', a['status'] == 'ok' and a['hw_rise'] == 0.4 and a['q_pass_m3s'] > 0, a)
    check('unknown without geometry', assess_crossing(1.0)['status'] == 'unknown' and assess_crossing(3.0, crest_m=2.0)['status'] == 'overtopped')
    print('culvert selftest', 'OK' if ok else 'FAILED'); return ok

if __name__ == '__main__':
    if '--selftest' in sys.argv: sys.exit(0 if selftest() else 1)
    print(__doc__)
