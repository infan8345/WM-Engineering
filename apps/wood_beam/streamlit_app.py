import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math, re, os, datetime, subprocess, tempfile, io, ast
import numpy as np

# ── Wood / Steel databases ────────────────────────────────────────────
wood_sections_raw = [
    ("2x8 Douglas Fir-Larch No.1",  "sawn", 1.5,  7.25,  2.6, 1200, 1600),
    ("2x10 Douglas Fir-Larch No.1", "sawn", 1.5,  9.25,  3.4, 1200, 1600),
    ("2x12 Douglas Fir-Larch No.1", "sawn", 1.5, 11.25,  4.1, 1200, 1600),
    ("4x8 Douglas Fir-Larch No.1",  "sawn", 3.5,  7.25,  5.2, 1200, 1600),
    ("4x10 Douglas Fir-Larch No.1", "sawn", 3.5,  9.25,  6.8, 1200, 1600),
    ("4x12 Douglas Fir-Larch No.1", "sawn", 3.5, 11.25,  8.2, 1200, 1600),
    ("6x8 Douglas Fir-Larch No.1",  "sawn", 5.5,  7.25,  7.8, 1200, 1600),
    ("6x10 Douglas Fir-Larch No.1", "sawn", 5.5,  9.25, 10.2, 1200, 1600),
    ("6x12 Douglas Fir-Larch No.1", "sawn", 5.5, 11.25, 12.3, 1200, 1600),
    ("6x14 Douglas Fir-Larch No.1", "sawn", 5.5, 13.25, 14.4, 1200, 1600),
    ("6x16 Douglas Fir-Larch No.1", "sawn", 5.5, 15.25, 16.5, 1200, 1600),
    ("6x18 Douglas Fir-Larch No.1", "sawn", 5.5, 17.25, 18.6, 1200, 1600),
    ("8x12 Douglas Fir-Larch No.1", "sawn", 7.25, 11.25, 16.4, 1200, 1600),
    ("8x14 Douglas Fir-Larch No.1", "sawn", 7.25, 13.25, 19.2, 1200, 1600),
    ("8x16 Douglas Fir-Larch No.1", "sawn", 7.25, 15.25, 22.0, 1200, 1600),
    ("8x18 Douglas Fir-Larch No.1", "sawn", 7.25, 17.25, 24.8, 1200, 1600),
    ("3.5\" x 11.875\" PSL",  "psl", 3.5,  11.875, 12.7, 2900, 2000),
    ("3.5\" x 14\" PSL",      "psl", 3.5,  14.0,   15.0, 2900, 2000),
    ("3.5\" x 16\" PSL",      "psl", 3.5,  16.0,   17.2, 2900, 2000),
    ("3.5\" x 18\" PSL",      "psl", 3.5,  18.0,   19.3, 2900, 2000),
    ("4x12 PSL (nominal)",    "psl", 3.5,  11.5,   12.5, 2900, 2000),
    ("5.25\" x 11.875\" PSL", "psl", 5.25, 11.875, 19.0, 2900, 2000),
    ("5.25\" x 14\" PSL",     "psl", 5.25, 14.0,   22.5, 2900, 2000),
    ("5.25\" x 16\" PSL",     "psl", 5.25, 16.0,   25.8, 2900, 2000),
    ("5.25\" x 18\" PSL",     "psl", 5.25, 18.0,   29.0, 2900, 2000),
    ("6x12 PSL (nominal)",    "psl", 5.5,  11.5,   18.5, 2900, 2000),
    ("7\" x 11.875\" PSL",    "psl", 7.0,  11.875, 25.3, 2900, 2000),
    ("7\" x 14\" PSL",        "psl", 7.0,  14.0,   30.0, 2900, 2000),
    ("7\" x 16\" PSL",        "psl", 7.0,  16.0,   34.4, 2900, 2000),
    ("7\" x 18\" PSL",        "psl", 7.0,  18.0,   38.7, 2900, 2000),
]

# LVL database: common depths through 18 inches, 1–4 plies.
# Generic design values match the original app assumptions. Verify the
# selected product against the manufacturer's current evaluation report.
LVL_DEPTHS = [5.5, 7.25, 9.25, 9.5, 11.25, 11.875, 14.0, 16.0, 18.0]
LVL_PLY_COUNTS = [1, 2, 3, 4]
LVL_PLY_WIDTH = 1.75       # in per ply
LVL_DENSITY_PCF = 36.0     # used only to estimate self-weight
LVL_FB = 2600              # psi; generic app assumption
LVL_E = 1900               # ksi; generic app assumption

for plies in LVL_PLY_COUNTS:
    width = plies * LVL_PLY_WIDTH
    for depth in LVL_DEPTHS:
        plf = round(width * depth / 144.0 * LVL_DENSITY_PCF, 1)
        depth_label = f"{depth:g}"
        desc = f'{plies}-ply {LVL_PLY_WIDTH:g}" x {depth_label}" LVL'
        wood_sections_raw.append(
            (desc, "lvl", width, depth, plf, LVL_FB, LVL_E)
        )

wood_list = []
for _e in wood_sections_raw:
    desc, mat, w, d, plf, fb, e = _e
    wood_list.append((desc, mat, w, d, plf, fb, e, w*d**3/12.0, w*d**2/6.0))

steel_sections = [
    ("W10 X 12",  53.8,  13.9, 12, 30000, 29000),
    ("W12 X 14",  88.6,  17.4, 14, 30000, 29000),
    ("W12 X 16", 103.0,  20.1, 16, 30000, 29000),
    ("W12 X 19", 130.0,  24.3, 19, 30000, 29000),
    ("W12 X 22", 156.0,  29.3, 22, 30000, 29000),
    ("W14 X 22", 199.0,  33.2, 22, 30000, 29000),
    ("W12 X 26", 204.0,  39.4, 26, 30000, 29000),
    ("W14 X 26", 245.0,  39.5, 26, 30000, 29000),
    ("W16 X 26", 301.0,  45.0, 26, 30000, 29000),
    ("W14 X 30", 291.0,  45.6, 30, 30000, 29000),
    ("W16 X 31", 375.0,  51.5, 31, 30000, 29000),
    ("W14 X 34", 340.0,  53.0, 34, 30000, 29000),
    ("W16 X 36", 448.0,  63.0, 36, 30000, 29000),
]

# ── Global overhanging-beam analysis ─────────────────────────────────
def build_global_loads(all_pl, all_dl, main_len):
    """Map local span inputs to one global coordinate system.

    Support A is x=0. Support B is x=main_len. The left cantilever has
    negative x coordinates; the right cantilever is beyond x=main_len.
    """
    span_names = {1: "Left cantilever", 2: "Main span", 3: "Right cantilever"}
    point_loads, dist_loads = [], []

    for bid in (1, 2, 3):
        for i, item in enumerate(all_pl.get(bid, []), start=1):
            # New UI stores the evaluated value together with the original
            # expression. Tuple support is retained for compatibility.
            if isinstance(item, dict):
                a = float(item['x'])
                P = float(item['P'])
                P_expr = str(item.get('P_expr', f'{P:g}'))
                d_expr = str(item.get('d_expr', f'{a:g}'))
            else:
                a, P = item[:2]
                P_expr = str(item[2]) if len(item) > 2 else f'{P:g}'
                d_expr = str(item[3]) if len(item) > 3 else f'{a:g}'

            if bid == 1:
                x = -a
            elif bid == 2:
                x = a
            else:
                x = main_len + a
            point_loads.append({
                'label': f'{span_names[bid]} P{i}', 'region': bid,
                'local_x': a, 'x': x, 'P': P,
                'P_expr': P_expr, 'd_expr': d_expr,
            })

        for i, item in enumerate(all_dl.get(bid, []), start=1):
            if isinstance(item, dict):
                x1 = float(item['x1'])
                x2 = float(item['x2'])
                w = float(item['w'])
                w_expr = str(item.get('w_expr', f'{w:g}'))
            else:
                x1, x2, w = item[:3]
                w_expr = str(item[3]) if len(item) > 3 else f'{w:g}'

            if bid == 1:
                gx1, gx2 = -x2, -x1
            elif bid == 2:
                gx1, gx2 = x1, x2
            else:
                gx1, gx2 = main_len + x1, main_len + x2
            dist_loads.append({
                'label': f'{span_names[bid]} w{i}', 'region': bid,
                'local_x1': x1, 'local_x2': x2,
                'x1': gx1, 'x2': gx2, 'w': w,
                'w_expr': w_expr,
            })

    point_loads.sort(key=lambda r: r['x'])
    dist_loads.sort(key=lambda r: r['x1'])
    return point_loads, dist_loads


def _moment_at_x(x, RA, RB, support_B, point_loads, dist_loads):
    """Bending moment in kip-ft using Macaulay brackets."""
    m = RA * max(x, 0.0) + RB * max(x - support_B, 0.0)
    for p in point_loads:
        m -= p['P'] * max(x - p['x'], 0.0)
    for d in dist_loads:
        m -= d['w'] / 2.0 * (
            max(x - d['x1'], 0.0) ** 2 - max(x - d['x2'], 0.0) ** 2
        )
    return m


def _shear_at_x(x, RA, RB, support_B, point_loads, dist_loads):
    """Shear immediately to the right of x in kips."""
    v = (RA if x >= 0.0 else 0.0) + (RB if x >= support_B else 0.0)
    for p in point_loads:
        if x >= p['x']:
            v -= p['P']
    for d in dist_loads:
        v -= d['w'] * (
            max(x - d['x1'], 0.0) - max(x - d['x2'], 0.0)
        )
    return v


def analyze_overhanging_beam(left_len, main_len, right_len, all_pl, all_dl):
    """Analyze the entire beam as one overhanging simply-supported member."""
    if main_len <= 0:
        raise ValueError("Main span must be greater than zero.")

    point_loads, dist_loads = build_global_loads(all_pl, all_dl, main_len)
    load_rows = []
    total_load = 0.0
    moment_about_A = 0.0

    for p in point_loads:
        W = p['P']
        total_load += W
        moment_about_A += W * p['x']
        expr = p.get('P_expr', f'{W:g}')
        load_rows.append({
            'Load': p['label'], 'Type': 'Point',
            'Input expression': expr,
            'Magnitude': f"{expr} = {W:.4g} k",
            'Range / position': f"x = {p['x']:.3f} ft",
            'Resultant W (k)': W, 'Centroid x (ft)': p['x'],
            'W x (kip-ft)': W * p['x'],
        })

    for d in dist_loads:
        length = d['x2'] - d['x1']
        W = d['w'] * length
        xc = (d['x1'] + d['x2']) / 2.0
        total_load += W
        moment_about_A += W * xc
        expr = d.get('w_expr', f"{d['w']:g}")
        load_rows.append({
            'Load': d['label'], 'Type': 'UDL',
            'Input expression': expr,
            'Magnitude': f"{expr} = {d['w']:.4g} k/ft",
            'Range / position': f"{d['x1']:.3f} to {d['x2']:.3f} ft",
            'Resultant W (k)': W, 'Centroid x (ft)': xc,
            'W x (kip-ft)': W * xc,
        })

    RB = moment_about_A / main_len
    RA = total_load - RB

    x_min = -left_len
    x_max = main_len + right_len
    base = np.linspace(x_min, x_max, 6001)
    special = [x_min, 0.0, main_len, x_max]
    special += [p['x'] for p in point_loads]
    special += [z for d in dist_loads for z in (d['x1'], d['x2'])]

    # Add every interior V=0 location so moment extrema are evaluated at the
    # actual critical point rather than only at a plotting-grid station.
    boundaries = sorted(set(float(v) for v in special))
    shear_roots = []
    for xL, xR in zip(boundaries[:-1], boundaries[1:]):
        if xR - xL <= 1e-10:
            continue
        eps = min(1e-8, (xR - xL) / 1000.0)
        vL = _shear_at_x(xL + eps, RA, RB, main_len, point_loads, dist_loads)
        vR = _shear_at_x(xR - eps, RA, RB, main_len, point_loads, dist_loads)
        if abs(vL) < 1e-10:
            shear_roots.append(xL + eps)
        elif abs(vR) < 1e-10:
            shear_roots.append(xR - eps)
        elif vL * vR < 0:
            lo, hi = xL + eps, xR - eps
            for _ in range(60):
                mid = (lo + hi) / 2.0
                vm = _shear_at_x(mid, RA, RB, main_len, point_loads, dist_loads)
                if vL * vm <= 0:
                    hi = mid
                    vR = vm
                else:
                    lo = mid
                    vL = vm
            shear_roots.append((lo + hi) / 2.0)

    special += shear_roots
    x = np.unique(np.concatenate((base, np.array(special, dtype=float))))
    x.sort()

    M = np.array([
        _moment_at_x(xi, RA, RB, main_len, point_loads, dist_loads)
        for xi in x
    ])
    V = np.array([
        _shear_at_x(xi + 1e-9, RA, RB, main_len, point_loads, dist_loads)
        for xi in x
    ])

    regions = {
        1: ('Left Cantilever', x <= 0.0 + 1e-9, left_len),
        2: ('Main Span', (x >= -1e-9) & (x <= main_len + 1e-9), main_len),
        3: ('Right Cantilever', x >= main_len - 1e-9, right_len),
    }
    span_extrema = {}
    for bid, (name, mask, length) in regions.items():
        if length <= 0:
            continue
        xr, mr = x[mask], M[mask]
        i_max = int(np.argmax(mr))
        i_min = int(np.argmin(mr))
        i_abs = int(np.argmax(np.abs(mr)))
        span_extrema[bid] = {
            'name': name, 'length': length,
            'M_pos': float(mr[i_max]), 'x_pos': float(xr[i_max]),
            'M_neg': float(mr[i_min]), 'x_neg': float(xr[i_min]),
            'M_abs': float(abs(mr[i_abs])), 'M_governing': float(mr[i_abs]),
            'x_governing': float(xr[i_abs]),
        }

    i_gov = int(np.argmax(np.abs(M)))
    return {
        'left_len': left_len, 'main_len': main_len, 'right_len': right_len,
        'point_loads': point_loads, 'dist_loads': dist_loads,
        'load_rows': load_rows, 'total_load': total_load,
        'moment_about_A': moment_about_A, 'RA': RA, 'RB': RB,
        'x': x, 'V': V, 'M': M, 'span_extrema': span_extrema,
        'M_abs_max': float(abs(M[i_gov])), 'M_governing': float(M[i_gov]),
        'x_M_governing': float(x[i_gov]),
    }


# ── Deflection and section selection ─────────────────────────────────
def equivalent_moment_deflection(analysis, E_ksi, I_in4, defl_limit):
    """Equivalent-UDL deflection comparison based on the real regional moment.

    For each active beam region, take the absolute governing moment from the
    same global analysis used for reactions, diagrams, and strength design:

        w_eq = 8 |M_real| / L_eq^2
        delta_eq = 5 w_eq L_eq^4 / (384 E I)

    The equivalent model is a simply supported span under uniform load.  For a
    cantilever, L_eq = 2 Lc; for the main span, L_eq = L.  This is reported as a
    comparison/screening method only.  The exact full-beam elastic-curve method
    remains the governing serviceability check for member selection.
    """
    if E_ksi <= 0 or I_in4 <= 0:
        return None

    spans = {}
    passes = True
    for bid in (1, 2, 3):
        ext = analysis.get('span_extrema', {}).get(bid)
        if not ext or ext.get('length', 0.0) <= 0:
            continue

        actual_length_ft = float(ext['length'])
        equivalent_span_ft = (
            2.0 * actual_length_ft if bid in (1, 3) else actual_length_ft
        )
        real_moment_kip_ft = abs(float(ext['M_governing']))
        w_eq_k_per_ft = (
            8.0 * real_moment_kip_ft / equivalent_span_ft ** 2
            if equivalent_span_ft > 0 else 0.0
        )

        # Consistent inch-kip units: E [kip/in^2], I [in^4],
        # w [kip/in], and equivalent span [in].
        span_in = equivalent_span_ft * 12.0
        w_eq_k_per_in = w_eq_k_per_ft / 12.0
        delta_eq_in = (
            5.0 * w_eq_k_per_in * span_in ** 4 / (384.0 * E_ksi * I_in4)
        )
        allow_in = span_in / defl_limit
        ratio = delta_eq_in / allow_in if allow_in > 0 else 0.0
        ok = delta_eq_in <= allow_in + 1e-9
        passes = passes and ok

        spans[bid] = {
            'name': ext['name'],
            'actual_length': actual_length_ft,
            'equivalent_span': equivalent_span_ft,
            'real_moment': real_moment_kip_ft,
            'signed_real_moment': float(ext['M_governing']),
            'moment_location': float(ext['x_governing']),
            'w_eq': w_eq_k_per_ft,
            'delta': delta_eq_in,
            'allow': allow_in,
            'ratio': ratio,
            'passes': ok,
        }

    worst = max(spans.values(), key=lambda r: r['ratio']) if spans else None
    return {
        'method': 'Equivalent UDL from real regional moment',
        'formula': 'w_eq = 8|M_real|/L_eq^2',
        'spans': spans,
        'passes': passes,
        'worst_region': worst['name'] if worst else 'Unavailable',
        'worst_ratio': worst['ratio'] if worst else float('nan'),
        'worst_delta': worst['delta'] if worst else float('nan'),
        'worst_allow': worst['allow'] if worst else float('nan'),
        'comparison_only': True,
    }


def beam_deflection(analysis, E_ksi, I_in4, defl_limit):
    """Numerically integrate EI*y''=M with y(A)=y(B)=0."""
    x_ft = analysis['x']
    x_in = x_ft * 12.0
    M_kip_in = analysis['M'] * 12.0
    if E_ksi <= 0 or I_in4 <= 0:
        return None

    curvature = M_kip_in / (E_ksi * I_in4)
    theta0 = np.zeros_like(x_in)
    y0 = np.zeros_like(x_in)
    for i in range(1, len(x_in)):
        dx = x_in[i] - x_in[i - 1]
        theta0[i] = theta0[i - 1] + 0.5 * (curvature[i] + curvature[i - 1]) * dx
        y0[i] = y0[i - 1] + 0.5 * (theta0[i] + theta0[i - 1]) * dx

    ia = int(np.argmin(np.abs(x_ft - 0.0)))
    ib = int(np.argmin(np.abs(x_ft - analysis['main_len'])))
    xa, xb = x_in[ia], x_in[ib]
    c1 = -(y0[ib] - y0[ia]) / (xb - xa)
    c2 = -y0[ia] - c1 * (xa - x_in[0])
    y = y0 + c1 * (x_in - x_in[0]) + c2
    theta = theta0 + c1

    # Cantilever-tip deflection decomposition.  The total tip displacement is
    # separated into (1) rigid-line displacement caused by support rotation
    # and (2) local cantilever bending relative to the tangent at the support.
    # For a determinate overhanging beam, the local bending component is caused
    # by the overhang curvature, while the support-rotation component captures
    # the influence of the main-span loading on the overhang tip.
    cantilever_breakdown = {}
    if analysis['left_len'] > 0:
        itip = int(np.argmin(np.abs(x_ft + analysis['left_len'])))
        dx_tip = x_in[itip] - x_in[ia]
        rotation_component = float(theta[ia] * dx_tip)
        total_tip = float(y[itip])
        local_component = total_tip - rotation_component
        cantilever_breakdown[1] = {
            'name': 'Left Cantilever', 'support': 'A',
            'support_x_ft': 0.0, 'tip_x_ft': float(x_ft[itip]),
            'support_rotation_rad': float(theta[ia]),
            'lever_arm_in': float(dx_tip),
            'rotation_component_signed': rotation_component,
            'local_bending_signed': float(local_component),
            'total_tip_signed': total_tip,
            'rotation_component': abs(rotation_component),
            'local_bending': abs(float(local_component)),
            'total_tip': abs(total_tip),
            'sum_error': float(total_tip - (local_component + rotation_component)),
        }
    if analysis['right_len'] > 0:
        right_tip_x = analysis['main_len'] + analysis['right_len']
        itip = int(np.argmin(np.abs(x_ft - right_tip_x)))
        dx_tip = x_in[itip] - x_in[ib]
        rotation_component = float(theta[ib] * dx_tip)
        total_tip = float(y[itip])
        local_component = total_tip - rotation_component
        cantilever_breakdown[3] = {
            'name': 'Right Cantilever', 'support': 'B',
            'support_x_ft': float(analysis['main_len']),
            'tip_x_ft': float(x_ft[itip]),
            'support_rotation_rad': float(theta[ib]),
            'lever_arm_in': float(dx_tip),
            'rotation_component_signed': rotation_component,
            'local_bending_signed': float(local_component),
            'total_tip_signed': total_tip,
            'rotation_component': abs(rotation_component),
            'local_bending': abs(float(local_component)),
            'total_tip': abs(total_tip),
            'sum_error': float(total_tip - (local_component + rotation_component)),
        }

    span_defs = {}
    region_masks = {
        1: (x_ft <= 0.0 + 1e-9, analysis['left_len'], 'Left Cantilever'),
        2: ((x_ft >= -1e-9) & (x_ft <= analysis['main_len'] + 1e-9),
            analysis['main_len'], 'Main Span'),
        3: (x_ft >= analysis['main_len'] - 1e-9,
            analysis['right_len'], 'Right Cantilever'),
    }
    passes = True
    for bid, (mask, length, name) in region_masks.items():
        if length <= 0:
            continue
        yr, xr, xri = y[mask], x_ft[mask], x_in[mask]

        # Cantilever serviceability is checked independently as local bending
        # relative to the tangent at the adjacent support.  This removes the
        # rigid-line displacement caused by rotation of the main-span support.
        # The global elastic curve is retained for the main span and for the
        # separate absolute-tip-displacement diagnostic below.
        if bid == 1:
            y_check = yr - y[ia] - theta[ia] * (xri - x_in[ia])
            basis = 'Local bending relative to tangent at support A'
        elif bid == 3:
            y_check = yr - y[ib] - theta[ib] * (xri - x_in[ib])
            basis = 'Local bending relative to tangent at support B'
        else:
            y_check = yr
            basis = 'Global deflection relative to the support chord'

        idx = int(np.argmax(np.abs(y_check)))
        delta = float(abs(y_check[idx]))

        # For code deflection limits, a cantilever's effective check span is
        # twice its actual length.  Only the allowable limit uses 2Lc; the
        # local elastic bending calculation uses the actual cantilever length.
        check_length = 2.0 * length if bid in (1, 3) else length
        allow = check_length * 12.0 / defl_limit
        ok = delta <= allow + 1e-9
        passes = passes and ok
        span_defs[bid] = {
            'name': name, 'delta': delta,
            'signed_delta': float(y_check[idx]),
            'global_signed_delta_at_check': float(yr[idx]),
            'x': float(xr[idx]), 'actual_length': float(length),
            'check_length': float(check_length),
            'basis': basis,
            'allow': allow, 'ratio': delta / allow if allow else 0.0,
            'passes': ok,
        }

    equivalent = equivalent_moment_deflection(
        analysis, E_ksi, I_in4, defl_limit
    )

    i_max = int(np.argmax(np.abs(y)))
    worst_checked = max(span_defs.values(), key=lambda d: d['ratio'])
    max_checked = max(span_defs.values(), key=lambda d: d['delta'])
    return {
        'x': x_ft, 'y': y, 'theta': theta,
        # Global absolute movement is retained as a diagnostic only.
        'max_abs': float(abs(y[i_max])),
        'x_max': float(x_ft[i_max]), 'signed_max': float(y[i_max]),
        # Regional serviceability uses local cantilever bending and main-span
        # chord-relative deflection, as stored in spans.
        'max_check_abs': float(max_checked['delta']),
        'max_check_region': max_checked['name'],
        'max_check_x': float(max_checked['x']),
        'governing_check_region': worst_checked['name'],
        'support_rotations': {
            'A': float(theta[ia]),
            'B': float(theta[ib]),
        },
        'cantilever_breakdown': cantilever_breakdown,
        'spans': span_defs, 'passes': passes,
        'equivalent_moment': equivalent,
    }


def cantilever_moment_deflection_note(analysis, deflection):
    """Explain independent local cantilever checks and absolute tip movement.

    The cantilever design check is based on bending relative to the tangent at
    the adjacent support.  Main-span support rotation is therefore excluded
    from the local cantilever demand.  For an absolute-position diagnostic,
    the signed rotation and local components are still added algebraically.
    """
    if not deflection:
        return None
    spans = deflection.get('spans', {})
    breakdown = deflection.get('cantilever_breakdown', {})
    extrema = analysis.get('span_extrema', {})
    if not all(k in spans and k in extrema for k in (1, 3)):
        return None

    left_m = float(extrema[1]['M_abs'])
    right_m = float(extrema[3]['M_abs'])
    left_d = spans[1]
    right_d = spans[3]
    moment_side = 'Right' if right_m > left_m + 1e-9 else ('Left' if left_m > right_m + 1e-9 else 'Neither')
    deflection_side = (
        'Left' if left_d['ratio'] > right_d['ratio'] + 1e-9
        else ('Right' if right_d['ratio'] > left_d['ratio'] + 1e-9 else 'Neither')
    )

    note = (
        f"Cantilever deflection is checked independently as local bending relative "
        f"to the tangent at its support. Left |M|max = {left_m:.3f} kip-ft and "
        f"right |M|max = {right_m:.3f} kip-ft; {moment_side.lower()} cantilever has "
        f"the larger regional moment. The local-deflection ratios are left = "
        f"{left_d['ratio']:.3f} and right = {right_d['ratio']:.3f}; "
        f"{deflection_side.lower()} cantilever governs the independent cantilever check."
    )

    def rotation_effect(b):
        rotation = float(b['rotation_component_signed'])
        local = float(b['local_bending_signed'])
        tol = 1e-10
        if abs(rotation) <= tol or abs(local) <= tol:
            return 'has no material interaction with'
        if rotation * local < 0.0:
            return 'opposes (partially cancels)'
        return 'reinforces'

    if 1 in breakdown and 3 in breakdown:
        lb = breakdown[1]
        rb = breakdown[3]
        note += (
            f" Main-span rotation does not reduce the local bending itself; it only "
            f"changes the absolute tip position. Algebraically, left tip = "
            f"{lb['rotation_component_signed']:.4f} + ({lb['local_bending_signed']:.4f}) "
            f"= {lb['total_tip_signed']:.4f} in and right tip = "
            f"{rb['rotation_component_signed']:.4f} + ({rb['local_bending_signed']:.4f}) "
            f"= {rb['total_tip_signed']:.4f} in. In this load case, support rotation "
            f"{rotation_effect(lb)} the left local-bending component and "
            f"{rotation_effect(rb)} the right local-bending component."
        )
    return note


def regional_deflection_summary(deflection):
    """Return compact text for every active regional deflection check."""
    if not deflection:
        return 'Deflection results unavailable.'
    parts = []
    for bid in (1, 2, 3):
        if bid not in deflection.get('spans', {}):
            continue
        d = deflection['spans'][bid]
        parts.append(
            f"{d['name']}: {d['delta']:.4f}/{d['allow']:.4f} = "
            f"{d['ratio']:.3f} ({'PASS' if d['passes'] else 'FAIL'})"
        )
    return ' | '.join(parts)


def equivalent_deflection_summary(deflection):
    """Return compact equivalent-moment UDL comparison for active regions."""
    if not deflection:
        return 'Equivalent-moment comparison unavailable.'
    equivalent = deflection.get('equivalent_moment')
    if not equivalent:
        return 'Equivalent-moment comparison unavailable.'
    parts = []
    for bid in (1, 2, 3):
        if bid not in equivalent.get('spans', {}):
            continue
        d = equivalent['spans'][bid]
        parts.append(
            f"{d['name']}: M={d['real_moment']:.3f} kip-ft, "
            f"w_eq={d['w_eq']:.4f} k/ft, "
            f"delta_eq/allow={d['delta']:.4f}/{d['allow']:.4f}"
            f"={d['ratio']:.3f} ({'PASS' if d['passes'] else 'FAIL'})"
        )
    return ' | '.join(parts)


def section_equivalent_fields(deflection):
    """Extract governing equivalent-method values for a section row."""
    equivalent = deflection.get('equivalent_moment') if deflection else None
    spans = equivalent.get('spans', {}) if equivalent else {}
    if not spans:
        return {
            'equiv_defl_ratio': float('inf'), 'equiv_defl_ok': False,
            'equiv_worst_region': 'Unavailable',
            'equiv_worst_delta': float('nan'),
            'equiv_worst_allow': float('nan'),
        }
    worst = max(spans.values(), key=lambda r: r['ratio'])
    return {
        'equiv_defl_ratio': float(worst['ratio']),
        'equiv_defl_ok': bool(equivalent['passes']),
        'equiv_worst_region': worst['name'],
        'equiv_worst_delta': float(worst['delta']),
        'equiv_worst_allow': float(worst['allow']),
    }


def select_wood_beam_global(analysis, defl_limit, const_dim, const_value,
                            mat_filter=None):
    cands = []
    for desc, mat, w, d, plf, fb, e, Ix, Sx in wood_list:
        if mat_filter and mat != mat_filter:
            continue
        if const_dim == 'D' and d > const_value:
            continue
        if const_dim == 'B' and w > const_value:
            continue
        S_req = analysis['M_abs_max'] * 12000.0 / fb
        if Sx + 1e-9 < S_req:
            continue
        defl = beam_deflection(analysis, e, Ix, defl_limit)
        if defl and defl['passes']:
            capacity = fb * Sx / 12000.0
            cands.append({
                'type': 'wood', 'desc': desc, 'mat': mat, 'width': w, 'depth': d,
                'plf': plf, 'fb': fb, 'E': e, 'I_prov': Ix, 'S_prov': Sx,
                'S_req': S_req, 'capacity': capacity, 'deflection': defl,
            })
    if not cands:
        return None
    cands.sort(key=lambda r: (r['plf'], r['depth'], r['width']))
    return cands[0]


def select_steel_beam_global(analysis, defl_limit):
    cands = []
    for desc, Ix, Sx, plf, fb, e in steel_sections:
        S_req = analysis['M_abs_max'] * 12000.0 / fb
        if Sx + 1e-9 < S_req:
            continue
        defl = beam_deflection(analysis, e, Ix, defl_limit)
        if defl and defl['passes']:
            capacity = fb * Sx / 12000.0
            cands.append({
                'type': 'steel', 'desc': desc, 'mat': 'steel', 'plf': plf,
                'fb': fb, 'E': e, 'I_prov': Ix, 'S_prov': Sx,
                'S_req': S_req, 'capacity': capacity, 'deflection': defl,
            })
    if not cands:
        return None
    cands.sort(key=lambda r: r['plf'])
    return cands[0]



def evaluate_wood_sections_global(analysis, defl_limit, const_dim, const_value,
                                  mat_filter=None):
    """Evaluate every eligible wood section and retain PASS/FAIL reasons.

    A member may be present in the database but still fail strength, deflection,
    or both. This diagnostic list makes that distinction explicit.
    """
    rows = []
    for desc, mat, w, d, plf, fb, e, Ix, Sx in wood_list:
        if mat_filter and mat != mat_filter:
            continue
        if const_dim == 'D' and d > const_value:
            continue
        if const_dim == 'B' and w > const_value:
            continue

        S_req = analysis['M_abs_max'] * 12000.0 / fb
        capacity = fb * Sx / 12000.0
        strength_ratio = analysis['M_abs_max'] / capacity if capacity > 0 else float('inf')
        strength_ok = strength_ratio <= 1.0 + 1e-9

        defl = beam_deflection(analysis, e, Ix, defl_limit)
        if defl and defl['spans']:
            worst = max(defl['spans'].values(), key=lambda r: r['ratio'])
            defl_ratio = worst['ratio']
            defl_ok = defl['passes']
            worst_region = worst['name']
            worst_delta = worst['delta']
            worst_allow = worst['allow']
        else:
            defl_ratio = float('inf')
            defl_ok = False
            worst_region = 'Unavailable'
            worst_delta = float('nan')
            worst_allow = float('nan')

        equiv = section_equivalent_fields(defl)
        row = {
            'desc': desc, 'mat': mat, 'width': w, 'depth': d, 'plf': plf,
            'fb': fb, 'E': e, 'I_prov': Ix, 'S_prov': Sx,
            'S_req': S_req, 'capacity': capacity,
            'strength_ratio': strength_ratio, 'strength_ok': strength_ok,
            'deflection': defl, 'defl_ratio': defl_ratio,
            'defl_ok': defl_ok, 'worst_region': worst_region,
            'worst_delta': worst_delta, 'worst_allow': worst_allow,
            'overall_ok': strength_ok and defl_ok,
        }
        row.update(equiv)
        rows.append(row)
    return rows


def evaluate_steel_sections_global(analysis, defl_limit):
    """Evaluate every listed steel section with exact and equivalent checks."""
    rows = []
    for desc, Ix, Sx, plf, fb, e in steel_sections:
        S_req = analysis['M_abs_max'] * 12000.0 / fb
        capacity = fb * Sx / 12000.0
        strength_ratio = (
            analysis['M_abs_max'] / capacity if capacity > 0 else float('inf')
        )
        strength_ok = strength_ratio <= 1.0 + 1e-9
        defl = beam_deflection(analysis, e, Ix, defl_limit)
        if defl and defl['spans']:
            worst = max(defl['spans'].values(), key=lambda r: r['ratio'])
            defl_ratio = worst['ratio']
            defl_ok = defl['passes']
            worst_region = worst['name']
            worst_delta = worst['delta']
            worst_allow = worst['allow']
        else:
            defl_ratio = float('inf')
            defl_ok = False
            worst_region = 'Unavailable'
            worst_delta = float('nan')
            worst_allow = float('nan')
        row = {
            'desc': desc, 'mat': 'steel', 'plf': plf,
            'fb': fb, 'E': e, 'I_prov': Ix, 'S_prov': Sx,
            'S_req': S_req, 'capacity': capacity,
            'strength_ratio': strength_ratio, 'strength_ok': strength_ok,
            'deflection': defl, 'defl_ratio': defl_ratio,
            'defl_ok': defl_ok, 'worst_region': worst_region,
            'worst_delta': worst_delta, 'worst_allow': worst_allow,
            'overall_ok': strength_ok and defl_ok,
        }
        row.update(section_equivalent_fields(defl))
        rows.append(row)
    return rows


def diagnostic_rank(row):
    """Rank near-passing candidates first; lower is better."""
    return (max(row['strength_ratio'], row['defl_ratio']),
            row['strength_ratio'] + row['defl_ratio'], row['plf'])


def strongest_candidate(rows):
    return max(rows, key=lambda r: (r['capacity'], r['I_prov'])) if rows else None


def serviceability_guidance(row):
    """Return the stiffness needed for a reference candidate to meet deflection.

    For the same load case and elastic modulus, deflection varies inversely with I.
    This is a screening calculation only, not a product or connection design.
    """
    if not row or not math.isfinite(row.get('defl_ratio', float('inf'))):
        return None
    ratio = max(float(row['defl_ratio']), 1.0)
    I_req = float(row['I_prov']) * ratio
    result = {
        'ratio': ratio,
        'I_current': float(row['I_prov']),
        'I_required': I_req,
        'EI_required': float(row['E']) * I_req,
    }
    if row.get('mat') == 'lvl':
        current_plies = float(row['width']) / LVL_PLY_WIDTH
        equivalent_plies = current_plies * ratio
        result.update({
            'current_plies': current_plies,
            'equivalent_plies': equivalent_plies,
            'whole_plies': int(math.ceil(equivalent_plies - 1e-12)),
            'equivalent_width': equivalent_plies * LVL_PLY_WIDTH,
        })
    return result


def psl_7x18_exclusion_reason(mat_filter, const_dim, const_value):
    reasons = []
    if mat_filter and mat_filter != 'psl':
        reasons.append(f"active material filter is {mat_filter.upper()}, not PSL")
    if const_dim == 'D' and const_value is not None and 18.0 > const_value:
        reasons.append(f"18.0 in depth exceeds the {const_value:.3f} in maximum depth")
    if const_dim == 'B' and const_value is not None and 7.0 > const_value:
        reasons.append(f"7.0 in width exceeds the {const_value:.3f} in maximum width")
    return '; '.join(reasons)


# ── Diagrams ──────────────────────────────────────────────────────────
def plot_beam(analysis, loc, beam_label, selection, defl_limit):
    left_len = analysis['left_len']
    main_len = analysis['main_len']
    right_len = analysis['right_len']
    fig, ax = plt.subplots(figsize=(11, 5.8))

    ax.plot([-left_len, main_len + right_len], [0, 0], 'k-', linewidth=3, zorder=5)
    for sx in (0, main_len):
        ax.plot([sx, sx], [-0.36, 0.10], 'g-', linewidth=3, zorder=4)

    all_p = [abs(p['P']) for p in analysis['point_loads'] if p['P'] != 0]
    all_w = [abs(d['w']) for d in analysis['dist_loads'] if d['w'] != 0]
    max_p = max(all_p) if all_p else 1.0
    max_w = max(all_w) if all_w else 1.0

    for d in analysis['dist_loads']:
        if d['w'] == 0:
            continue
        h = 0.42 * (abs(d['w']) / max_w) + 0.08
        ax.add_patch(patches.Rectangle(
            (d['x1'], 0), d['x2'] - d['x1'], h,
            linewidth=1.5, edgecolor='blue', facecolor='lightblue', alpha=0.45
        ))
        xv = float(math.ceil(d['x1'] + 1e-6))
        while xv < d['x2'] - 1e-6:
            ax.plot([xv, xv], [0, h], 'b-', linewidth=0.8, alpha=0.7, zorder=3)
            xv += 1.0
        ax.plot([d['x1'], d['x2']], [h, h], 'b-', linewidth=1.5)
        ax.text((d['x1'] + d['x2']) / 2, h + 0.07, f"{d['w']:.3g} k/ft",
                ha='center', color='blue', fontsize=10)

    for p in analysis['point_loads']:
        if p['P'] == 0:
            continue
        h = 0.65 * (abs(p['P']) / max_p) + 0.1
        ax.annotate('', xy=(p['x'], 0), xytext=(p['x'], h),
                    arrowprops=dict(arrowstyle='-|>', color='red', lw=2.5))
        ax.text(p['x'], h + 0.07, f"{p['P']:.3g} k",
                ha='center', color='red', fontsize=10)

    mids = {1: -left_len / 2.0, 2: main_len / 2.0,
            3: main_len + right_len / 2.0}
    for bid, ext in analysis['span_extrema'].items():
        ax.text(mids[bid], -0.28,
                f"Max |M| = {ext['M_abs']:.2f} kip-ft\nM = {ext['M_governing']:.2f} at x={ext['x_governing']:.2f} ft",
                ha='center', va='top', color='purple', fontsize=9)

    ax.text(0, -0.56, f"RA = {analysis['RA']:.2f} k",
            ha='center', color='green', fontsize=10)
    ax.text(main_len, -0.56, f"RB = {analysis['RB']:.2f} k",
            ha='center', color='green', fontsize=10)

    if selection:
        ax.text((main_len - left_len + right_len) / 2.0, -0.78,
                f"Selected: {selection['desc']}  |  Moment capacity = {selection['capacity']:.2f} kip-ft",
                ha='center', fontsize=10, color='black')

    ax.set_title(f"Beam Loading — {loc}", fontsize=13)
    ax.set_xlim(-left_len - 0.8, main_len + right_len + 0.8)
    ax.set_ylim(-1.00, 1.05)
    ax.set_xlabel("Global position x (ft); Support A = 0", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    fig.text(
        0.01, 0.01,
        f"Governing |M| = {analysis['M_abs_max']:.2f} kip-ft "
        f"(M = {analysis['M_governing']:.2f} kip-ft at x = {analysis['x_M_governing']:.2f} ft)    "
        f"Deflection criterion: L/{defl_limit}    Grade: "
        f"{selection['mat'].upper() if selection else beam_label}",
        fontsize=9, color='white', backgroundcolor='black', va='bottom'
    )
    plt.tight_layout(rect=[0, 0.07, 1, 1])
    return fig


def plot_shear_moment(analysis, loc):
    x, V, M = analysis['x'], analysis['V'], analysis['M']
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    ax1, ax2 = axes
    ax1.plot(x, V, linewidth=1.8)
    ax1.axhline(0, linewidth=0.8)
    ax1.axvline(0, linestyle='--', linewidth=0.9)
    ax1.axvline(analysis['main_len'], linestyle='--', linewidth=0.9)
    ax1.fill_between(x, 0, V, alpha=0.18)
    ax1.set_ylabel('Shear V (kips)')
    ax1.set_title(f'Shear and Bending-Moment Diagrams — {loc}')
    ax1.grid(alpha=0.25)

    ax2.plot(x, M, linewidth=1.8)
    ax2.axhline(0, linewidth=0.8)
    ax2.axvline(0, linestyle='--', linewidth=0.9)
    ax2.axvline(analysis['main_len'], linestyle='--', linewidth=0.9)
    ax2.fill_between(x, 0, M, alpha=0.18)
    ax2.plot(analysis['x_M_governing'], analysis['M_governing'], 'o')
    ax2.annotate(
        f"M = {analysis['M_governing']:.2f} kip-ft\nx = {analysis['x_M_governing']:.2f} ft",
        xy=(analysis['x_M_governing'], analysis['M_governing']),
        xytext=(8, 12), textcoords='offset points', fontsize=9
    )
    ax2.set_xlabel('Global position x (ft); Support A = 0')
    ax2.set_ylabel('Moment M (kip-ft)')
    ax2.grid(alpha=0.25)
    plt.tight_layout()
    return fig


# ── LaTeX helpers ─────────────────────────────────────────────────────
def tex_esc(s):
    s = str(s)
    for old, new in [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'),
                     ('$', r'\$'), ('#', r'\#'), ('^', r'\^{}'), ('_', r'\_'),
                     ('{', r'\{'), ('}', r'\}'), ('~', r'\~{}')]:
        s = s.replace(old, new)
    return s


def generate_latex_content(loc, beam_label, defl_limit, L0, analysis, selection, wood_diagnostics=None, steel_alternative=None, section_diagnostics=None):
    left_len, main_len, right_len = L0[1], L0[2], L0[3]
    date_str = datetime.date.today().strftime('%B %d, %Y')
    # Always show a usable beam mark in the LaTeX output.
    beam_mark = str(loc).strip() or 'UNSPECIFIED'
    diagnostic_pool = section_diagnostics or wood_diagnostics or []
    reference_candidate = (
        strongest_candidate(diagnostic_pool) if diagnostic_pool else None
    )
    deflection_reference = (
        selection['deflection'] if selection
        else (reference_candidate['deflection'] if reference_candidate else None)
    )
    deflection_member_label = (
        selection['desc'] if selection
        else (reference_candidate['desc'] if reference_candidate else 'No member')
    )
    lines = [
        r'\documentclass[10pt]{article}',
        # Reserve exactly 3.00 inches for the repeating top header.
        r'\usepackage[letterpaper,left=0.8in,right=0.8in,top=3in,bottom=0.85in,headheight=2.30in,headsep=0.20in,includehead]{geometry}',
        r'\usepackage{graphicx}', r'\usepackage{booktabs}',
        r'\usepackage{longtable}', r'\usepackage{array}',
        r'\usepackage{amsmath}', r'\usepackage{fancyhdr}', r'\usepackage{xcolor}',
        r'\setlength{\parindent}{0pt}',
        r'\pagestyle{fancy}', r'\fancyhf{}',
        r'\fancyhead[C]{%',
        r'\begin{minipage}[b][2.25in][c]{\textwidth}',
        r'\centering',
        r'{\LARGE\bfseries BEAM DESIGN REPORT}\\[10pt]',
        r'{\large\bfseries Beam Location / Mark: '
        r'\fbox{\parbox{0.62\textwidth}{\centering\strut ' + tex_esc(beam_mark) + r'}}}\\[7pt]',
        r'{\large\bfseries Beam Type: ' + tex_esc(beam_label) + r'}\\[5pt]',
        r'{\normalsize Deflection Criterion: L/' + str(defl_limit)
        + r'\qquad Date: ' + date_str + r'}',
        r'\end{minipage}}',
        r'\lfoot{Prepared: ' + date_str + r'}', r'\rfoot{Page \thepage}',
        r'\renewcommand{\headrulewidth}{0.8pt}',
        r'\renewcommand{\footrulewidth}{0.4pt}',
        r'\begin{document}',
        r'\thispagestyle{fancy}',
        r'\textbf{Beam Location / Mark:} ' + tex_esc(beam_mark) + r'\\[4pt]',
        r'\textbf{Analysis model.} One continuous overhanging beam with simple supports at '
        r'$A: x=0$ and $B: x=L$. Downward loads are positive input values. '
        r'All reported moments are generated from the same global moment function.',
        r'\begin{figure}[htbp]\centering',
        r'\includegraphics[width=\textwidth]{beam_diagram}',
        r'\caption{Loading diagram with span and governing moments.}', r'\end{figure}',
        r'\begin{figure}[htbp]\centering',
        r'\includegraphics[width=\textwidth]{shear_moment_diagram}',
        r'\caption{Shear-force and bending-moment diagrams.}', r'\end{figure}',
        r'\clearpage',
        r'\section*{1. Geometry and Coordinate System}',
        r'\textbf{Beam Location / Mark:} ' + tex_esc(beam_mark) + r'\\[3pt]',
        f'Left cantilever $= {left_len:.3f}$ ft, main support span $L = {main_len:.3f}$ ft, '
        f'right cantilever $= {right_len:.3f}$ ft.\\',
        f'Global beam limits: $x={-left_len:.3f}$ ft to $x={main_len+right_len:.3f}$ ft.',
        r'\section*{2. Applied Loads and Resultants}',
        r'For each distributed load, $W=w(x_2-x_1)$ and '
        r'$\bar{x}=(x_1+x_2)/2$.',
        r'\begin{longtable}{p{0.23\textwidth}p{0.10\textwidth}p{0.15\textwidth}rrrr}',
        r'\toprule Load & Type & Magnitude & $W$ (k) & $\bar{x}$ (ft) & $W\bar{x}$ (kip-ft) \\ \midrule',
        r'\endhead',
    ]
    if analysis['load_rows']:
        for row in analysis['load_rows']:
            lines.append(
                f"{tex_esc(row['Load'])} & {row['Type']} & {tex_esc(row['Magnitude'])} & "
                f"{row['Resultant W (k)']:.3f} & {row['Centroid x (ft)']:.3f} & "
                f"{row['W x (kip-ft)']:.3f} \\\\"
            )
    else:
        lines.append(r'No applied loads & -- & -- & 0.000 & -- & 0.000 \\')
    lines += [
        r'\midrule',
        rf"\multicolumn{{3}}{{r}}{{Totals:}} & {analysis['total_load']:.3f} & -- & {analysis['moment_about_A']:.3f} \\\\ ",
        r'\bottomrule\end{longtable}',
        r'\section*{3. Support Reactions}',
        r'\[\sum F_y=0:\qquad R_A+R_B=\sum W\]',
        r'\[\sum M_A=0:\qquad R_B L=\sum(W\bar{x})\]',
        rf"\[R_B=\frac{{{analysis['moment_about_A']:.3f}}}{{{main_len:.3f}}}={analysis['RB']:.3f}\ \text{{kips}}\]",
        rf"\[R_A={analysis['total_load']:.3f}-{analysis['RB']:.3f}={analysis['RA']:.3f}\ \text{{kips}}\]",
        r'\section*{4. Shear and Moment Calculation}',
        r'Using Macaulay brackets $\langle z\rangle=0$ for $z<0$ and '
        r'$\langle z\rangle=z$ for $z\ge 0$:',
        r'\[V(x)=R_AH(x)+R_BH(x-L)-\sum P_iH(x-x_i)'
        r'-\sum w_j\left[\langle x-x_{1j}\rangle-\langle x-x_{2j}\rangle\right]\]',
        r'\[M(x)=R_A\langle x\rangle+R_B\langle x-L\rangle'
        r'-\sum P_i\langle x-x_i\rangle'
        r'-\sum \frac{w_j}{2}\left[\langle x-x_{1j}\rangle^2-\langle x-x_{2j}\rangle^2\right]\]',
        r'\begin{center}\begin{tabular}{lrrrr}',
        r'\toprule Region & $M_{max+}$ & $M_{min-}$ & Governing $M$ & Location $x$ \\',
        r' & (kip-ft) & (kip-ft) & (kip-ft) & (ft) \\ \midrule',
    ]
    for bid in (1, 2, 3):
        if bid not in analysis['span_extrema']:
            continue
        ext = analysis['span_extrema'][bid]
        lines.append(
            f"{ext['name']} & {ext['M_pos']:.3f} & {ext['M_neg']:.3f} & "
            f"{ext['M_governing']:.3f} & {ext['x_governing']:.3f} \\\\"
        )
    lines += [
        r'\midrule',
        f"Global & -- & -- & {analysis['M_governing']:.3f} & {analysis['x_M_governing']:.3f} \\\\ ",
        r'\bottomrule\end{tabular}\end{center}',
        f"Governing absolute moment: $|M|_{{max}}={analysis['M_abs_max']:.3f}$ kip-ft.",
        r'\section*{5. Member Strength Selection}',
    ]

    if selection:
        lines += [
            r'\[S_{req}=\frac{|M|_{max}(12{,}000)}{F_b}\]',
            rf"\[S_{{req}}=\frac{{{analysis['M_abs_max']:.3f}(12{{,}}000)}}{{{selection['fb']:.0f}}}"
            rf"={selection['S_req']:.3f}\ \text{{in}}^3\]",
            r'\begin{center}\begin{tabular}{ll}', r'\toprule',
            r'Selected member & \textbf{' + tex_esc(selection['desc']) + r'} \\',
            r'Material & ' + selection['mat'].upper() + r' \\',
            f"$F_b$ & {selection['fb']:.0f} psi \\\\ ",
            f"$E$ & {selection['E']:.0f} ksi \\\\ ",
            f"$S_{{required}}$ & {selection['S_req']:.3f} in$^3$ \\\\ ",
            f"$S_{{provided}}$ & {selection['S_prov']:.3f} in$^3$ \\\\ ",
            f"$I_{{provided}}$ & {selection['I_prov']:.3f} in$^4$ \\\\ ",
            f"Moment capacity & {selection['capacity']:.3f} kip-ft \\\\ ",
        ]
        if selection['type'] == 'wood':
            lines += [
                f"Dimensions & {selection['width']:.3f} in $\\times$ {selection['depth']:.3f} in \\\\ ",
                f"Listed self-weight & {selection['plf']:.1f} lb/ft \\\\ ",
            ]
        lines += [r'\bottomrule\end{tabular}\end{center}',
                  r'Check: $S_{provided}\ge S_{required}$ and moment capacity '
                  r'$\ge |M|_{max}$.']
    else:
        lines.append(r'\textcolor{red}{No eligible listed section passes both strength and deflection checks.}')
        if wood_diagnostics:
            strongest = reference_candidate
            ranked = sorted(wood_diagnostics, key=diagnostic_rank)[:8]
            lines += [
                r'\subsection*{Why the listed sections did not pass}',
                r'Being listed in the database means the section was evaluated; it does not mean the section is adequate.',
            ]
            if strongest:
                guide = serviceability_guidance(strongest)
                lines += [
                    r'\textbf{Reference candidate only---NOT SELECTED:} ' + tex_esc(strongest['desc']) + r'\\',
                    f"Moment demand/capacity = {analysis['M_abs_max']:.3f}/{strongest['capacity']:.3f} "
                    f"= {strongest['strength_ratio']:.3f} "
                    f"({'PASS' if strongest['strength_ok'] else 'FAIL'}).\\",
                    f"Governing regional deflection check: {tex_esc(strongest['worst_region'])}, "
                    f"{strongest['worst_delta']:.4f}/{strongest['worst_allow']:.4f} in "
                    f"= {strongest['defl_ratio']:.3f} "
                    f"({'PASS' if strongest['defl_ok'] else 'FAIL'}).\\",
                    r'\begin{center}\begin{tabular}{lrrrrl}',
                    r'\toprule Region & Max $|\delta|$ (in) & Allowable (in) & Ratio & Location $x$ (ft) & Check \\ \midrule',
                ]
                for bid in (1, 2, 3):
                    if bid not in strongest['deflection']['spans']:
                        continue
                    d = strongest['deflection']['spans'][bid]
                    lines.append(
                        f"{tex_esc(d['name'])} & {d['delta']:.4f} & {d['allow']:.4f} & "
                        f"{d['ratio']:.3f} & {d['x']:.3f} & "
                        f"{'PASS' if d['passes'] else 'FAIL'} \\\\"
                    )
                lines += [r'\bottomrule\end{tabular}\end{center}']
                moment_deflection_note = cantilever_moment_deflection_note(
                    analysis, strongest['deflection']
                )
                if moment_deflection_note:
                    lines += [tex_esc(moment_deflection_note) + r'\\[4pt]']
                if guide and strongest['defl_ratio'] > 1.0:
                    lines += [
                        f"Required stiffness: $I_{{req}}={guide['I_current']:.1f}"
                        f"({guide['ratio']:.3f})={guide['I_required']:.1f}$ in$^4$.\\",
                    ]
                    if 'equivalent_plies' in guide:
                        lines += [
                            f"At the same depth and assumed $E$, this equals {guide['equivalent_plies']:.2f} "
                            f"equivalent LVL plies; the next whole number is {guide['whole_plies']} plies "
                            f"({guide['equivalent_width']:.2f} in total width), outside the listed 1--4 ply catalog. "
                            r'This is a stiffness equivalence, not a design recommendation.\[4pt]',
                        ]
                if steel_alternative:
                    lines += [
                        r'\textbf{First listed steel alternative passing both checks:} '
                        + tex_esc(steel_alternative['desc']) + r'\\',
                        f"Steel capacity = {steel_alternative['capacity']:.3f} kip-ft; "
                        f"$I={steel_alternative['I_prov']:.1f}$ in$^4$; "
                        f"maximum checked deflection = {steel_alternative['deflection']['max_check_abs']:.4f} in.\\[4pt]",
                    ]
            lines += [
                r'\begin{center}\begin{tabular}{p{0.29\textwidth}rrrrll}',
                r'\toprule Section & Capacity & $M/Cap.$ & $\delta/\delta_{allow}$ & Worst region & Strength & Deflection \\',
                r' & (kip-ft) & & & & & \\ \midrule',
            ]
            for r in ranked:
                lines.append(
                    f"{tex_esc(r['desc'])} & {r['capacity']:.2f} & {r['strength_ratio']:.3f} & "
                    f"{r['defl_ratio']:.3f} & {tex_esc(r['worst_region'])} & "
                    f"{'PASS' if r['strength_ok'] else 'FAIL'} & "
                    f"{'PASS' if r['defl_ok'] else 'FAIL'} \\\\"
                )
            lines += [r'\bottomrule\end{tabular}\end{center}']

    lines += [
        r'\section*{6. Deflection Calculation}',
        r'The elastic curve is calculated from $EIy^{\prime\prime}(x)=M(x)$. '
        r'The moment diagram is numerically integrated along the full beam, and the '
        r'integration constants are solved from $y(0)=0$ and $y(L)=0$.',
        r'\textbf{Member used for the deflection trace:} ' + tex_esc(deflection_member_label) + r'.',
    ]
    if deflection_reference:
        lines += [
            r'Cantilever deflection is checked independently as local bending relative '
            r'to the tangent at the adjacent support:',
            r'\[\delta_{local}(x)=y(x)-y_s-\theta_s(x-x_s).\]',
            r'This removes rigid-line movement caused by main-span support rotation. '
            r'The main span is checked relative to the chord between supports. For '
            r'cantilever allowable deflection, the check length is $L=2L_c$, while '
            r'the elastic bending calculation uses the actual length $L_c$.',
            r'\begin{center}\begin{tabular}{lrrrrrl}',
            r'\toprule Region & Actual $L_c$ (ft) & Check $L$ (ft) & Max checked $|\delta|$ (in) & Allowable (in) & Ratio & Check \\ \midrule',
        ]
        for bid in (1, 2, 3):
            if bid not in deflection_reference['spans']:
                continue
            d = deflection_reference['spans'][bid]
            actual_length = d.get('actual_length', analysis['span_extrema'][bid]['length'])
            check_length = d.get('check_length', actual_length)
            lines.append(
                f"{d['name']} & {actual_length:.3f} & {check_length:.3f} & "
                f"{d['delta']:.4f} & {d['allow']:.4f} & {d['ratio']:.3f} & "
                f"{'PASS' if d['passes'] else 'FAIL'} \\\\"
            )
        lines += [r'\bottomrule\end{tabular}\end{center}']

        equivalent = deflection_reference.get('equivalent_moment')
        if equivalent and equivalent.get('spans'):
            lines += [
                r'\subsection*{Equivalent-Moment Uniform-Load Comparison}',
                r'This comparison uses the real governing moment from the same global '
                r'analysis for each region. The equivalent uniform load is',
                r'\[w_{eq}=\frac{8|M_{real}|}{L_{eq}^{2}}\]',
                r'and the simply-supported uniform-load deflection is',
                r'\[\delta_{eq}=\frac{5w_{eq}L_{eq}^{4}}{384EI}.\]',
                r'For the main span, $L_{eq}=L$. For a cantilever, $L_{eq}=2L_c$. '
                r'This is a comparison method only. The exact regional method governs member selection: '
                r'cantilevers are checked by local bending relative to the support tangent, '
                r'and the main span is checked relative to the support chord.',
                r'\begin{center}\scriptsize\begin{tabular}{lrrrrrrl}',
                r'\toprule Region & $|M_{real}|$ & $L_{eq}$ & $w_{eq}$ & $\delta_{eq}$ & Allow. & Ratio & Check \\',
                r' & (kip-ft) & (ft) & (k/ft) & (in) & (in) & & \\ \midrule',
            ]
            for bid in (1, 2, 3):
                if bid not in equivalent['spans']:
                    continue
                d = equivalent['spans'][bid]
                lines.append(
                    f"{tex_esc(d['name'])} & {d['real_moment']:.3f} & "
                    f"{d['equivalent_span']:.3f} & {d['w_eq']:.4f} & "
                    f"{d['delta']:.4f} & {d['allow']:.4f} & {d['ratio']:.3f} & "
                    f"{'PASS' if d['passes'] else 'FAIL'} \\\\"
                )
            lines += [r'\bottomrule\end{tabular}\normalsize\end{center}']

        if section_diagnostics:
            lines += [
                r'\subsection*{All Listed Sections: Exact vs. Equivalent-Moment Deflection}',
                r'The equivalent result below is comparison-only. The Exact column is '
                r'used for the design serviceability decision.',
                r'\scriptsize',
                r'\begin{longtable}{p{0.25\textwidth}rrrllll}',
                r'\toprule Section & $I$ & Exact ratio & Eq. ratio & Exact region & Eq. region & Exact & Eq. \\',
                r' & (in$^4$) & & & & & check & compare \\ \midrule',
                r'\endhead',
            ]
            for r in sorted(section_diagnostics, key=diagnostic_rank):
                lines.append(
                    f"{tex_esc(r['desc'])} & {r['I_prov']:.2f} & {r['defl_ratio']:.3f} & "
                    f"{r['equiv_defl_ratio']:.3f} & {tex_esc(r['worst_region'])} & "
                    f"{tex_esc(r['equiv_worst_region'])} & "
                    f"{'PASS' if r['defl_ok'] else 'FAIL'} & "
                    f"{'PASS' if r['equiv_defl_ok'] else 'FAIL'} \\\\"
                )
            lines += [r'\bottomrule\end{longtable}', r'\normalsize']

        breakdown = deflection_reference.get('cantilever_breakdown', {})
        if breakdown:
            lines += [
                r'\subsection*{Cantilever-Tip Deflection Breakdown}',
                r'For each overhang tip, the signed total displacement is decomposed as',
                r'\[\delta_{tip}=\underbrace{\theta_s\Delta x}_{\text{support-rotation component}}'
                r'+\underbrace{\delta_{local}}_{\text{local cantilever bending}}\]',
                r'The local cantilever design check uses $\delta_{local}$ and excludes the support-rotation '
                r'component. The support-rotation component is retained only to show absolute tip '
                r'movement. Signed values add algebraically, so support rotation can either reduce '
                r'or increase the absolute tip movement; it does not change local cantilever bending.',
                r'\begin{center}\begin{tabular}{llrrrrr}',
                r'\toprule Cantilever & Support & $\theta_s$ (rad) & $\Delta x$ (in) & '
                r'$\theta_s\Delta x$ (in) & $\delta_{local}$ (in) & $\delta_{tip}$ (in) \\ \midrule',
            ]
            for bid in (1, 3):
                if bid not in breakdown:
                    continue
                b = breakdown[bid]
                lines.append(
                    f"{b['name']} & {b['support']} & {b['support_rotation_rad']:.8f} & "
                    f"{b['lever_arm_in']:.3f} & {b['rotation_component_signed']:.5f} & "
                    f"{b['local_bending_signed']:.5f} & {b['total_tip_signed']:.5f} \\\\"
                )
            lines += [r'\bottomrule\end{tabular}\end{center}']

    lines += [
        r'\section*{7. Scope and Design Notes}',
        r'\begin{itemize}',
        r'\item This calculator performs a linear-elastic, one-dimensional beam analysis '
        r'using the entered service loads. It does not generate code load combinations.',
        r'\item Listed member self-weight is reported but is not automatically added to the '
        r'entered loads. Add it as a distributed load when required.',
        r'\item Wood and engineered-wood design values are generic app assumptions. Verify '
        r'product-specific values, adjustment factors, bearing, shear, stability, connections, '
        r'fire, vibration, and local code requirements.',
        r'\item Final structural design must be reviewed by a qualified design professional.',
        r'\end{itemize}', r'\end{document}', ''
    ]
    return '\n'.join(lines)


def compile_latex_to_pdf(tex_content, image_files):
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tex_path = os.path.join(tmp, 'beam_report.tex')
            with open(tex_path, 'w') as f:
                f.write(tex_content)
            for filename, data in image_files.items():
                with open(os.path.join(tmp, filename), 'wb') as f:
                    f.write(data)
            for _ in range(2):
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode',
                     '-output-directory', tmp, tex_path],
                    capture_output=True, timeout=30
                )
            pdf_path = os.path.join(tmp, 'beam_report.pdf')
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    return f.read()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


# ── Streamlit UI ──────────────────────────────────────────────────────
_ALLOWED_BINARY_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}
_ALLOWED_UNARY_OPS = {
    ast.UAdd: lambda a: a,
    ast.USub: lambda a: -a,
}
_MATH_CONSTANTS = {'pi': math.pi, 'e': math.e}


def _normalize_math_expression(expression):
    """Normalize common calculator symbols without permitting code execution."""
    return (
        str(expression).strip()
        .replace('×', '*')
        .replace('÷', '/')
        .replace('^', '**')
    )


def safe_eval_math_expression(expression, variables=None):
    """Safely evaluate arithmetic used in load and position input fields.

    Supported syntax: numbers, named variables, parentheses, +, -, *, / and
    powers (** or ^). Python functions, attributes, indexing and all other
    executable syntax are rejected.
    """
    expr = _normalize_math_expression(expression)
    if not expr:
        raise ValueError('expression is blank')
    if len(expr) > 250:
        raise ValueError('expression is too long')

    names = dict(_MATH_CONSTANTS)
    if variables:
        names.update(variables)

    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError as exc:
        raise ValueError('invalid math syntax') from exc

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError('only numeric constants are allowed')
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise ValueError(f"undefined variable '{node.id}'")
            return float(names[node.id])
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
            return _ALLOWED_UNARY_OPS[type(node.op)](evaluate(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY_OPS:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError('power exponent must be between -12 and 12')
            try:
                return _ALLOWED_BINARY_OPS[type(node.op)](left, right)
            except ZeroDivisionError as exc:
                raise ValueError('division by zero') from exc
            except (OverflowError, ValueError) as exc:
                raise ValueError('math result is outside the supported range') from exc
        raise ValueError('allowed operators are +, -, *, /, **, ^ and parentheses')

    value = float(evaluate(tree))
    if not math.isfinite(value) or abs(value) > 1.0e15:
        raise ValueError('result must be finite and smaller than 1e15 in magnitude')
    return value


def parse_variable_definitions(definition_text):
    """Parse optional assignments such as a=0.015, b=20, c=0.01, d=8."""
    variables = {}
    errors = []
    text = str(definition_text or '').strip()
    if not text:
        return variables, errors

    parts = [p.strip() for p in re.split(r'[,;\n]+', text) if p.strip()]
    for part in parts:
        if '=' not in part:
            errors.append(f"Variable definition '{part}' must use name = expression.")
            continue
        name, expr = [piece.strip() for piece in part.split('=', 1)]
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name):
            errors.append(f"'{name}' is not a valid variable name.")
            continue
        if name in _MATH_CONSTANTS:
            errors.append(f"'{name}' is reserved as a math constant.")
            continue
        try:
            variables[name] = safe_eval_math_expression(expr, variables)
        except ValueError as exc:
            errors.append(f"Variable {name}: {exc}.")
    return variables, errors


def _expression_input(container, label, default, key, variables, errors,
                      minimum=None, maximum=None, unit=''):
    """Render one expression field and return (evaluated_value, original_text)."""
    expression = container.text_input(label, value=str(default), key=key)
    try:
        value = safe_eval_math_expression(expression, variables)
        if minimum is not None and value < minimum - 1e-12:
            raise ValueError(f'must be at least {minimum:g}')
        if maximum is not None and value > maximum + 1e-12:
            raise ValueError(f'must not exceed {maximum:g}')
        suffix = f' {unit}' if unit else ''
        container.caption(f'Calculated value: {value:.6g}{suffix}')
        return value, expression
    except ValueError as exc:
        container.error(f'Invalid expression: {exc}')
        errors.append(f'{label}: {exc}')
        return 0.0, expression


def span_input(name, span_len, prefix, variables):
    errors = []
    n_pt = int(st.number_input('Number of point loads', 0, 10, 0, key=f'{prefix}_n'))
    point_loads = []
    cumul = 0.0
    for i in range(n_pt):
        c1, c2 = st.columns(2)
        P, P_expr = _expression_input(
            c1, f'P{i+1} (kips) — expression', '0', f'{prefix}_P{i}',
            variables, errors, unit='kips'
        )
        lbl = ('Distance from support (ft) — expression' if i == 0
               else f'Distance from P{i} (ft) — expression')
        remaining = max(float(span_len) - cumul, 0.0)
        d, d_expr = _expression_input(
            c2, lbl, '0', f'{prefix}_d{i}', variables, errors,
            minimum=0.0, maximum=remaining, unit='ft'
        )
        cumul += d
        point_loads.append({
            'x': cumul, 'P': P, 'P_expr': P_expr, 'd_expr': d_expr,
        })

    seg_bounds = [0.0] + [pl['x'] for pl in point_loads] + [span_len]
    dist_loads = []
    st.write('**Distributed loads (k/ft) per segment — expressions accepted:**')
    cols = st.columns(min(len(seg_bounds) - 1, 4))
    for s in range(len(seg_bounds) - 1):
        x1, x2 = seg_bounds[s], seg_bounds[s + 1]
        w, w_expr = _expression_input(
            cols[s % 4], f'Seg {s+1}  {x1:.2f}–{x2:.2f} ft', '0',
            f'{prefix}_w{s}', variables, errors, unit='k/ft'
        )
        if abs(w) > 1e-14 and x2 > x1:
            dist_loads.append({
                'x1': x1, 'x2': x2, 'w': w, 'w_expr': w_expr,
            })
    return point_loads, dist_loads, errors


def _fig_to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=160, bbox_inches='tight')
    return buf.getvalue()


def main():
    st.set_page_config(page_title='Beam Design', page_icon='🏗', layout='wide')
    st.title('🏗 Wood / Steel Beam Design Calculator')
    st.caption('One global overhanging-beam analysis · Sawn Lumber · PSL · LVL · Steel')
    st.warning(
        'Preliminary design tool. Loads are analyzed as entered; code load combinations, '
        'shear, bearing, stability, connections, and product-specific adjustment factors '
        'require separate professional verification.'
    )
    st.divider()

    c1, c2, c3 = st.columns([2, 2, 2])
    mat_choice = c1.selectbox(
        'Beam Type', ['STEEL BEAM', 'WOOD/PSL BEAM', 'ROOF BEAM', 'FLOOR BEAM', 'LVL BEAM']
    )
    loc = c2.text_input('Beam Location / Mark', 'BM-1')
    choices = ['STEEL BEAM', 'WOOD/PSL BEAM', 'ROOF BEAM', 'FLOOR BEAM', 'LVL BEAM']
    beam_mat = choices.index(mat_choice)
    force_steel = beam_mat == 0
    force_lvl = beam_mat == 4
    beam_label = mat_choice

    if beam_mat == 2:
        finish = c3.selectbox(
            'Roof Finish',
            ['Plaster ceiling (L/240)', 'Non-plaster ceiling (L/180)', 'No ceiling (L/120)']
        )
        defl_limit = 240 if '240' in finish else (180 if '180' in finish else 120)
    else:
        defl_limit = 240
        c3.metric('Deflection Limit', f'L/{defl_limit}')

    mat_filter = None
    if force_lvl:
        mat_filter = 'lvl'
        st.info('LVL: 1.75 in per ply, common depths through 18 in, 1–4 plies; '
                'generic Fb = 2600 psi and E = 1900 ksi.')
    elif not force_steel:
        wood_mat_choice = st.radio(
            'Wood Material',
            ['All (Sawn + PSL + LVL)', 'Sawn Lumber Only', 'PSL Only',
             'LVL Only (5.5–18 in depths, 1–4 plies)'], horizontal=True
        )
        if wood_mat_choice == 'Sawn Lumber Only':
            mat_filter = 'sawn'
        elif wood_mat_choice == 'PSL Only':
            mat_filter = 'psl'
        elif wood_mat_choice.startswith('LVL Only'):
            mat_filter = 'lvl'

    const_dim, const_value = None, None
    if not force_steel:
        with st.expander('Dimension Constraints (optional)'):
            cc1, cc2 = st.columns(2)
            constr = cc1.radio('Constrain', ['None', 'Max Depth', 'Max Width'], horizontal=True)
            if constr == 'Max Depth':
                const_dim = 'D'
                const_value = cc2.number_input('Max depth (in)', 5.5, 36.0, 18.0)
            elif constr == 'Max Width':
                const_dim = 'B'
                const_value = cc2.number_input('Max width (in)', 1.5, 12.0, 8.0)

    st.divider()
    st.subheader('Span Lengths (ft)')
    s1, s2, s3 = st.columns(3)
    left_len = s1.number_input('Left Cantilever', 0.0, 100.0, 0.0, 0.5)
    main_len = s2.number_input('Main Support Span', 0.5, 200.0, 20.0, 0.5)
    right_len = s3.number_input('Right Cantilever', 0.0, 100.0, 0.0, 0.5)
    L0 = [0.0, left_len, main_len, right_len, 0.0]

    st.divider()
    st.subheader('Load Inputs')
    st.caption('Left/right cantilever distances are measured outward from their adjacent support.')
    st.caption('Cantilevers are checked independently by local bending relative to the support tangent. Allowable deflection uses L = 2Lc; bending analysis uses the actual length Lc.')
    st.info(
        'Load magnitudes and point-load distances accept math expressions. '
        'Enter a numeric expression such as `0.015*20+0.010*8`, or define '
        'variables below and then enter `a*b+c*d`. Supported operators: '
        '`+  -  *  /  **  ^` and parentheses.'
    )
    variable_text = st.text_area(
        'Optional load-expression variables',
        value='',
        placeholder='a=0.015, b=20, c=0.010, d=8',
        help='Separate assignments with commas, semicolons, or new lines. '
             'Definitions are evaluated from left to right.'
    )
    load_variables, variable_errors = parse_variable_definitions(variable_text)
    if load_variables:
        st.caption('Variables: ' + ', '.join(
            f'{name}={value:.6g}' for name, value in load_variables.items()
        ))
    for message in variable_errors:
        st.error(message)

    span_cfg = [
        (1, 'Left Cantilever', left_len, 'lc'),
        (2, 'Main Span', main_len, 'ms'),
        (3, 'Right Cantilever', right_len, 'rc'),
    ]
    all_pl, all_dl = {}, {}
    input_errors = list(variable_errors)
    for bid, sname, slen, pfx in span_cfg:
        if slen > 0:
            with st.expander(f'{sname} ({slen:.1f} ft)', expanded=True):
                all_pl[bid], all_dl[bid], span_errors = span_input(
                    sname, slen, pfx, load_variables
                )
                input_errors.extend(span_errors)
        else:
            all_pl[bid], all_dl[bid] = [], []

    if input_errors:
        st.warning('Correct the highlighted math-expression input errors before calculating.')

    st.divider()
    if st.button(
        '⚡ Calculate', type='primary', use_container_width=True,
        disabled=bool(input_errors)
    ):
        analysis = analyze_overhanging_beam(
            left_len, main_len, right_len, all_pl, all_dl
        )

        wood_diagnostics = []
        section_diagnostics = []
        if force_steel:
            section_diagnostics = evaluate_steel_sections_global(
                analysis, defl_limit
            )
            selection = select_steel_beam_global(analysis, defl_limit)
        else:
            wood_diagnostics = evaluate_wood_sections_global(
                analysis, defl_limit, const_dim, const_value, mat_filter
            )
            section_diagnostics = wood_diagnostics
            selection = select_wood_beam_global(
                analysis, defl_limit, const_dim, const_value, mat_filter
            )

        steel_alternative = None
        if not force_steel and selection is None:
            steel_alternative = select_steel_beam_global(analysis, defl_limit)
        reference_candidate = (
            strongest_candidate(section_diagnostics) if section_diagnostics else None
        )

        st.header('Results')
        m1, m2, m3, m4 = st.columns(4)
        m1.metric('Support reaction RA', f"{analysis['RA']:.3f} k")
        m2.metric('Support reaction RB', f"{analysis['RB']:.3f} k")
        m3.metric('Governing |M|', f"{analysis['M_abs_max']:.3f} kip-ft")
        m4.metric('Moment location', f"x = {analysis['x_M_governing']:.3f} ft")
        st.caption(
            f"Signed governing moment: M = {analysis['M_governing']:.3f} kip-ft. "
            'This exact value is used in the diagrams, report, and member selection.'
        )

        span_table = []
        for bid in (1, 2, 3):
            if bid not in analysis['span_extrema']:
                continue
            e = analysis['span_extrema'][bid]
            span_table.append({
                'Region': e['name'], 'M max + (kip-ft)': round(e['M_pos'], 4),
                'M min - (kip-ft)': round(e['M_neg'], 4),
                'Governing M (kip-ft)': round(e['M_governing'], 4),
                'x (ft)': round(e['x_governing'], 4),
            })
        st.dataframe(span_table, use_container_width=True, hide_index=True)

        st.subheader('Selected Member')
        if selection:
            st.success(f"**{selection['desc']}**")
            c = st.columns(5)
            c[0].metric('Required S', f"{selection['S_req']:.2f} in³")
            c[1].metric('Provided S', f"{selection['S_prov']:.2f} in³")
            c[2].metric('Provided I', f"{selection['I_prov']:.1f} in⁴")
            c[3].metric('Capacity', f"{selection['capacity']:.2f} kip-ft")
            c[4].metric('Max checked deflection', f"{selection['deflection']['max_check_abs']:.3f} in")
            if selection['type'] == 'wood':
                st.info(
                    f"Dimensions: {selection['width']:.3f} in × {selection['depth']:.3f} in | "
                    f"Listed self-weight: {selection['plf']:.1f} lb/ft (not automatically added)."
                )
        else:
            st.error(
                'DESIGN RESULT — No eligible listed section passes both the global '
                'moment demand and every regional deflection limit. This is not a software error.'
            )
            if not force_steel and wood_diagnostics:
                strongest = reference_candidate
                if strongest:
                    strength_word = 'PASS' if strongest['strength_ok'] else 'FAIL'
                    defl_word = 'PASS' if strongest['defl_ok'] else 'FAIL'
                    st.warning(
                        f"Reference candidate only — **NOT SELECTED: {strongest['desc']}**. "
                        f"Strength: |M|/capacity = {analysis['M_abs_max']:.3f}/"
                        f"{strongest['capacity']:.3f} = {strongest['strength_ratio']:.3f} "
                        f"(**{strength_word}**). Governing regional deflection check: "
                        f"{strongest['worst_region']} δ/allowable = "
                        f"{strongest['worst_delta']:.4f}/{strongest['worst_allow']:.4f} "
                        f"= {strongest['defl_ratio']:.3f} (**{defl_word}**)."
                    )
                    st.write(
                        '**All regional deflection checks:** ' +
                        regional_deflection_summary(strongest['deflection'])
                    )
                    moment_deflection_note = cantilever_moment_deflection_note(
                        analysis, strongest['deflection']
                    )
                    if moment_deflection_note:
                        st.info(moment_deflection_note)
                    guide = serviceability_guidance(strongest)
                    if guide and strongest['defl_ratio'] > 1.0:
                        g1, g2, g3 = st.columns(3)
                        g1.metric('Provided I', f"{guide['I_current']:.1f} in⁴")
                        g2.metric('Required I', f"{guide['I_required']:.1f} in⁴")
                        g3.metric('Required stiffness factor', f"{guide['ratio']:.3f}×")
                        if 'equivalent_plies' in guide:
                            st.info(
                                f"At the same {strongest['depth']:.3f} in depth and assumed E, "
                                f"this equals about {guide['equivalent_plies']:.2f} LVL plies. "
                                f"The next whole number is {guide['whole_plies']} plies "
                                f"({guide['equivalent_width']:.2f} in total width), outside the "
                                'current 1–4 ply catalog. This is a stiffness equivalence only, '
                                'not a product or connection recommendation.'
                            )
                    if steel_alternative:
                        st.success(
                            f"First listed steel alternative passing strength and deflection: "
                            f"**{steel_alternative['desc']}** — capacity "
                            f"{steel_alternative['capacity']:.3f} kip-ft, "
                            f"I = {steel_alternative['I_prov']:.1f} in⁴, maximum checked deflection "
                            f"{steel_alternative['deflection']['max_check_abs']:.4f} in."
                        )

                psl718 = next((r for r in wood_diagnostics
                               if r['desc'] == '7\" x 18\" PSL'), None)
                if psl718:
                    st.info(
                        f'**7" × 18" PSL was evaluated.** '
                        f"Capacity = {psl718['capacity']:.3f} kip-ft versus "
                        f"demand = {analysis['M_abs_max']:.3f} kip-ft "
                        f"({'PASS' if psl718['strength_ok'] else 'FAIL'}); "
                        f"worst deflection is in {psl718['worst_region']}: "
                        f"{psl718['worst_delta']:.4f} in versus "
                        f"{psl718['worst_allow']:.4f} in allowable "
                        f"({'PASS' if psl718['defl_ok'] else 'FAIL'})."
                    )
                else:
                    exclusion = psl_7x18_exclusion_reason(
                        mat_filter, const_dim, const_value
                    )
                    if exclusion:
                        st.info(f'7" × 18" PSL was not evaluated because {exclusion}.')

                with st.expander('Section failure diagnostics', expanded=True):
                    ranked = sorted(wood_diagnostics, key=diagnostic_rank)
                    diagnostic_table = []
                    for r in ranked:
                        spans = r['deflection']['spans'] if r.get('deflection') else {}
                        diagnostic_table.append({
                            'Section': r['desc'],
                            'Material': r['mat'].upper(),
                            'Capacity (kip-ft)': round(r['capacity'], 3),
                            'Moment/capacity': round(r['strength_ratio'], 3),
                            'Strength': 'PASS' if r['strength_ok'] else 'FAIL',
                            'Left defl./allow.': round(spans[1]['ratio'], 3) if 1 in spans else None,
                            'Main defl./allow.': round(spans[2]['ratio'], 3) if 2 in spans else None,
                            'Right defl./allow.': round(spans[3]['ratio'], 3) if 3 in spans else None,
                            'Worst region': r['worst_region'],
                            'Checked deflection (in)': round(r['worst_delta'], 4),
                            'Allowable (in)': round(r['worst_allow'], 4),
                            'Defl./allow.': round(r['defl_ratio'], 3),
                            'Deflection': 'PASS' if r['defl_ok'] else 'FAIL',
                            'Overall': 'PASS' if r['overall_ok'] else 'FAIL',
                        })
                    st.dataframe(diagnostic_table, use_container_width=True,
                                 hide_index=True)

        with st.expander('Equivalent-Moment UDL Deflection Comparison — All Sections', expanded=True):
            st.latex(r'w_{eq}=\frac{8|M_{real}|}{L_{eq}^{2}}')
            st.latex(r'\delta_{eq}=\frac{5w_{eq}L_{eq}^{4}}{384EI}')
            st.caption(
                'Mreal is the actual governing regional moment from the same global beam analysis. '
                'For the main span, Leq = L. For each cantilever, Leq = 2Lc. '
                'This equivalent simply-supported UDL method is shown for comparison only; '
                'the exact regional method governs. Cantilevers use local bending relative '
                'to the support tangent, while the main span uses the support chord.'
            )

            equivalent_basis_rows = []
            for bid in (1, 2, 3):
                ext = analysis['span_extrema'].get(bid)
                if not ext:
                    continue
                actual_length = float(ext['length'])
                equivalent_span = 2.0 * actual_length if bid in (1, 3) else actual_length
                real_moment = abs(float(ext['M_governing']))
                w_eq = 8.0 * real_moment / equivalent_span ** 2 if equivalent_span > 0 else 0.0
                equivalent_basis_rows.append({
                    'Region': ext['name'],
                    'Real governing M (kip-ft)': round(real_moment, 5),
                    'Moment location x (ft)': round(ext['x_governing'], 5),
                    'Actual length (ft)': round(actual_length, 5),
                    'Equivalent span Leq (ft)': round(equivalent_span, 5),
                    'Equivalent w (k/ft)': round(w_eq, 6),
                })
            st.markdown('**Equivalent-load basis from the real moment diagram**')
            st.dataframe(equivalent_basis_rows, use_container_width=True, hide_index=True)

            if section_diagnostics:
                comparison_rows = []
                for r in sorted(section_diagnostics, key=diagnostic_rank):
                    exact_spans = r['deflection']['spans'] if r.get('deflection') else {}
                    eq_result = (
                        r['deflection'].get('equivalent_moment')
                        if r.get('deflection') else None
                    )
                    eq_spans = eq_result.get('spans', {}) if eq_result else {}
                    comparison_rows.append({
                        'Section': r['desc'],
                        'Material': r['mat'].upper(),
                        'I (in⁴)': round(r['I_prov'], 3),
                        'Exact left ratio': round(exact_spans[1]['ratio'], 4) if 1 in exact_spans else None,
                        'Exact main ratio': round(exact_spans[2]['ratio'], 4) if 2 in exact_spans else None,
                        'Exact right ratio': round(exact_spans[3]['ratio'], 4) if 3 in exact_spans else None,
                        'Exact worst ratio': round(r['defl_ratio'], 4),
                        'Exact check': 'PASS' if r['defl_ok'] else 'FAIL',
                        'Eq. left ratio': round(eq_spans[1]['ratio'], 4) if 1 in eq_spans else None,
                        'Eq. main ratio': round(eq_spans[2]['ratio'], 4) if 2 in eq_spans else None,
                        'Eq. right ratio': round(eq_spans[3]['ratio'], 4) if 3 in eq_spans else None,
                        'Eq. worst region': r['equiv_worst_region'],
                        'Eq. worst ratio': round(r['equiv_defl_ratio'], 4),
                        'Eq. comparison': 'PASS' if r['equiv_defl_ok'] else 'FAIL',
                        'Strength': 'PASS' if r['strength_ok'] else 'FAIL',
                        'Design overall (exact)': 'PASS' if r['overall_ok'] else 'FAIL',
                    })
                st.markdown('**All eligible listed sections: exact analysis versus equivalent-moment comparison**')
                st.dataframe(comparison_rows, use_container_width=True, hide_index=True)
            else:
                st.info('No eligible listed sections are available under the active material and dimension filters.')

        with st.expander('Detailed Beam Calculation — Full Procedure', expanded=True):
            st.markdown('#### 1. Coordinate system and load conversion')
            st.write(
                f"Support A is x = 0 ft and Support B is x = {main_len:.3f} ft. "
                f"The beam extends from x = {-left_len:.3f} ft to "
                f"x = {main_len + right_len:.3f} ft."
            )
            if analysis['load_rows']:
                st.dataframe(analysis['load_rows'], use_container_width=True, hide_index=True)
            else:
                st.info('No nonzero loads were entered.')

            st.markdown('#### 2. Reactions from whole-beam equilibrium')
            st.latex(r'R_A+R_B=\sum W')
            st.latex(r'R_B L=\sum(W\bar{x})')
            st.write(
                f"ΣW = {analysis['total_load']:.4f} k; "
                f"Σ(Wx̄) about A = {analysis['moment_about_A']:.4f} kip-ft."
            )
            st.write(
                f"RB = {analysis['moment_about_A']:.4f} / {main_len:.4f} "
                f"= **{analysis['RB']:.4f} k**; "
                f"RA = {analysis['total_load']:.4f} − {analysis['RB']:.4f} "
                f"= **{analysis['RA']:.4f} k**."
            )

            st.markdown('#### 3. Shear and bending moment')
            st.latex(
                r'M(x)=R_A\langle x\rangle+R_B\langle x-L\rangle'
                r'-\sum P_i\langle x-x_i\rangle'
                r'-\sum\frac{w_j}{2}\left[\langle x-x_{1j}\rangle^2'
                r'-\langle x-x_{2j}\rangle^2\right]'
            )
            st.write(
                f"The global governing result is M = {analysis['M_governing']:.4f} kip-ft "
                f"at x = {analysis['x_M_governing']:.4f} ft; "
                f"therefore |M|max = **{analysis['M_abs_max']:.4f} kip-ft**."
            )
            st.dataframe(span_table, use_container_width=True, hide_index=True)

            st.markdown('#### 4. Section modulus and moment-capacity check')
            if selection:
                st.latex(r'S_{req}=\frac{|M|_{max}(12{,}000)}{F_b}')
                st.write(
                    f"Sreq = {analysis['M_abs_max']:.4f} × 12,000 / "
                    f"{selection['fb']:.0f} = **{selection['S_req']:.4f} in³**."
                )
                st.write(
                    f"Selected S = {selection['S_prov']:.4f} in³; "
                    f"capacity = FbS/12,000 = **{selection['capacity']:.4f} kip-ft**."
                )

                st.markdown('#### 5. Deflection integration and checks')
                st.latex(r'EI\,y^{\prime\prime}(x)=M(x),\qquad y(0)=0,\quad y(L)=0')
                defl_rows = []
                for bid in (1, 2, 3):
                    if bid not in selection['deflection']['spans']:
                        continue
                    d = selection['deflection']['spans'][bid]
                    defl_rows.append({
                        'Region': d['name'],
                        'Actual length (ft)': round(d.get('actual_length', 0.0), 4),
                        'Check length (ft)': round(d.get('check_length', 0.0), 4),
                        'Max checked |δ| (in)': round(d['delta'], 5),
                        'Location x (ft)': round(d['x'], 4),
                        'Allowable (in)': round(d['allow'], 5),
                        'Demand/allowable': round(d['ratio'], 4),
                        'Basis': d.get('basis', ''),
                        'Check': 'PASS' if d['passes'] else 'FAIL',
                    })
                st.dataframe(defl_rows, use_container_width=True, hide_index=True)
            else:
                st.markdown('#### 4. Reference candidate and required stiffness')
                strongest = reference_candidate
                if strongest:
                    guide = serviceability_guidance(strongest)
                    st.write(
                        f"**{strongest['desc']} is not selected.** Its strength ratio is "
                        f"{strongest['strength_ratio']:.4f}; the controlling regional deflection "
                        f"check is {strongest['worst_region']} at a ratio of "
                        f"{strongest['defl_ratio']:.4f}."
                    )
                    reference_defl_rows = []
                    for bid in (1, 2, 3):
                        if bid not in strongest['deflection']['spans']:
                            continue
                        d = strongest['deflection']['spans'][bid]
                        reference_defl_rows.append({
                            'Region': d['name'],
                            'Actual length (ft)': round(d.get('actual_length', 0.0), 4),
                            'Check length (ft)': round(d.get('check_length', 0.0), 4),
                            'Max checked |δ| (in)': round(d['delta'], 5),
                            'Location x (ft)': round(d['x'], 4),
                            'Allowable (in)': round(d['allow'], 5),
                            'Demand/allowable': round(d['ratio'], 4),
                            'Check': 'PASS' if d['passes'] else 'FAIL',
                        })
                    st.dataframe(reference_defl_rows, use_container_width=True, hide_index=True)
                    moment_deflection_note = cantilever_moment_deflection_note(
                        analysis, strongest['deflection']
                    )
                    if moment_deflection_note:
                        st.info(moment_deflection_note)
                    if guide:
                        st.latex(r'I_{required}=I_{provided}\left(\frac{\delta}{\delta_{allow}}\right)')
                        st.write(
                            f"Irequired = {guide['I_current']:.4f} × {guide['ratio']:.4f} "
                            f"= **{guide['I_required']:.4f} in⁴**."
                        )
                    if steel_alternative:
                        st.write(
                            f"The first listed steel section passing both checks is "
                            f"**{steel_alternative['desc']}**."
                        )
                else:
                    st.warning('No eligible listed member was available for a diagnostic check.')

            # Show a traceable tip-deflection decomposition for the selected
            # member, or for the reference candidate when no wood member passes.
            deflection_reference = (
                selection['deflection'] if selection
                else (reference_candidate['deflection'] if reference_candidate else None)
            )
            if deflection_reference and deflection_reference.get('cantilever_breakdown'):
                st.markdown('#### 6. Cantilever-tip deflection breakdown')
                st.latex(
                    r'\delta_{tip}=\underbrace{\theta_s\,\Delta x}_{\text{support-rotation component}}'
                    r'+\underbrace{\delta_{local}}_{\text{local cantilever bending}}'
                )
                st.caption(
                    'Signed values are shown so the components add algebraically to the absolute tip movement. '
                    'The design cantilever check uses only the local bending component relative to the support tangent. '
                    'Main-span rotation can reduce or increase absolute tip movement, but it does not alter local bending.'
                )
                breakdown_rows = []
                for bid in (1, 3):
                    if bid not in deflection_reference['cantilever_breakdown']:
                        continue
                    b = deflection_reference['cantilever_breakdown'][bid]
                    breakdown_rows.append({
                        'Cantilever': b['name'],
                        'Support': b['support'],
                        'Support rotation θ (rad)': round(b['support_rotation_rad'], 8),
                        'Tip lever arm Δx (in)': round(b['lever_arm_in'], 3),
                        'Rotation component θΔx (in)': round(b['rotation_component_signed'], 5),
                        'Local bending component (in)': round(b['local_bending_signed'], 5),
                        'Total tip deflection (in)': round(b['total_tip_signed'], 5),
                    })
                st.dataframe(breakdown_rows, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader('Beam Loading Diagram')
        fig_load = plot_beam(analysis, loc, beam_label, selection, defl_limit)
        st.pyplot(fig_load)
        load_png = _fig_to_png(fig_load)
        plt.close(fig_load)

        st.subheader('Shear and Moment Diagrams')
        fig_vm = plot_shear_moment(analysis, loc)
        st.pyplot(fig_vm)
        vm_png = _fig_to_png(fig_vm)
        plt.close(fig_vm)

        st.divider()
        st.subheader('Downloads')
        tex_str = generate_latex_content(
            loc, beam_label, defl_limit, L0, analysis, selection,
            wood_diagnostics=wood_diagnostics,
            steel_alternative=steel_alternative,
            section_diagnostics=section_diagnostics
        )
        pdf_bytes = compile_latex_to_pdf(tex_str, {
            'beam_diagram.png': load_png,
            'shear_moment_diagram.png': vm_png,
        })

        d1, d2, d3, d4 = st.columns(4)
        d1.download_button('⬇ Loading Diagram', load_png, file_name='beam_diagram.png',
                           mime='image/png', use_container_width=True)
        d2.download_button('⬇ V-M Diagram', vm_png, file_name='shear_moment_diagram.png',
                           mime='image/png', use_container_width=True)
        d3.download_button('⬇ Detailed LaTeX', tex_str, file_name='beam_report.tex',
                           mime='text/plain', use_container_width=True)
        if pdf_bytes:
            d4.download_button('⬇ Detailed PDF Report', pdf_bytes,
                               file_name='beam_report.pdf', mime='application/pdf',
                               use_container_width=True)
            st.success('Detailed PDF generated successfully.')
        else:
            d4.info('Install MiKTeX/TeX Live for PDF, or compile the .tex file in Overleaf.')


if __name__ == '__main__':
    main()
