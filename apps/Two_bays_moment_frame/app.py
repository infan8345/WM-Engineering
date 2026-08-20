"""
Two-Bay Steel Moment Frame Analyzer
------------------------------------
2D elastic direct-stiffness analysis of a two-bay (three-column) moment
frame with vertical (D/L), wind (uplift/downward/lateral), and seismic
loads, LRFD load combinations, diagrams, drift checks, and AISC 360
member screening.

Preliminary screening tool - not for construction.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from frame_solver import (W_SHAPES, build_model, analyze, combine,
                          DEFAULT_COMBOS)
from report_generator import build_latex, compile_pdf

st.set_page_config(page_title="Two-Bay Moment Frame Analyzer",
                   layout="wide")

# ---------------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------------
st.sidebar.header("1. Frame Geometry")
c1, c2 = st.sidebar.columns(2)
bay1 = c1.number_input("Bay 1 (ft)", 4.0, 40.0, 12.0, 0.5)
bay2 = c2.number_input("Bay 2 (ft)", 4.0, 40.0, 12.0, 0.5)
height = st.sidebar.number_input("Column height (ft)", 4.0, 40.0, 15.0, 0.5)
base_fix = st.sidebar.selectbox("Column base", ["fixed", "pinned"])

st.sidebar.header("2. Members")
E = st.sidebar.number_input("E (ksi)", 1000.0, 40000.0, 29000.0, 500.0)


def section_input(label, default):
    opts = list(W_SHAPES.keys()) + ["Custom"]
    sel = st.sidebar.selectbox(label, opts, index=opts.index(default))
    if sel == "Custom":
        cc1, cc2 = st.sidebar.columns(2)
        A = cc1.number_input(f"{label} A (in2)", 0.5, 200.0, 6.49)
        I = cc2.number_input(f"{label} I (in4)", 1.0, 20000.0, 118.0)
        Z = st.sidebar.number_input(f"{label} Zx (in3)", 1.0, 5000.0, 26.0)
        return sel, (A, I, Z)
    return sel, W_SHAPES[sel]


beam_name, (Ab, Ib, Zb) = section_input("Beam section", "W10x22")
col_name, (Ac, Ic, Zc) = section_input("Column section", "W12x26")
Fy = st.sidebar.number_input("Fy (ksi)", 30.0, 70.0, 50.0, 1.0)

st.sidebar.header("3. Vertical Loads")
v_mode = st.sidebar.radio("Input mode", ["Pressure x tributary factor",
                                         "Direct line loads"],
                          key="vmode")
if v_mode == "Pressure x tributary factor":
    cc1, cc2 = st.sidebar.columns(2)
    pD = cc1.number_input("Dead (psf)", 0.0, 500.0, 15.0, 1.0)
    pL = cc2.number_input("Live (psf)", 0.0, 500.0, 60.0, 5.0)
    Cj = st.sidebar.number_input(
        "Joist reaction factor Cj (ft2/ft)", 0.1, 100.0, 16.531, 0.1,
        help="Deck depth x (half-depth / backspan) per ft of width")
    ratio = st.sidebar.number_input(
        "Collected width / frame length", 0.1, 10.0, 50.0 / 24.0, 0.05,
        help="Full deck width collected by this frame / frame length")
    wD = pD * Cj * ratio / 1000.0
    wL = pL * Cj * ratio / 1000.0
    st.sidebar.caption(f"wD = {wD:.3f} kip/ft,  wL = {wL:.3f} kip/ft")
else:
    cc1, cc2 = st.sidebar.columns(2)
    wD = cc1.number_input("wD (kip/ft)", 0.0, 20.0, 0.517, 0.01)
    wL = cc2.number_input("wL (kip/ft)", 0.0, 40.0, 2.066, 0.01)

st.sidebar.header("4. Wind")
qh = st.sidebar.number_input("Velocity pressure qh (psf)", 0.0, 200.0,
                             26.86, 0.5)
G = st.sidebar.number_input("Gust factor G", 0.5, 1.5, 0.85, 0.01)
cc1, cc2 = st.sidebar.columns(2)
Cn_up = cc1.number_input("Cn uplift", 0.0, 3.0, 1.1, 0.05)
Cn_dn = cc2.number_input("Cn downward", 0.0, 3.0, 1.2, 0.05)
cc1, cc2 = st.sidebar.columns(2)
Cn_lat = cc1.number_input("Cn lateral (net)", 0.0, 3.0, 1.3, 0.05)
As = cc2.number_input("Projected lateral area (ft2)", 0.0, 5000.0,
                      225.0, 5.0)
if v_mode == "Pressure x tributary factor":
    wup = qh * G * Cn_up * Cj * ratio / 1000.0
    wdn = qh * G * Cn_dn * Cj * ratio / 1000.0
else:
    cc1, cc2 = st.sidebar.columns(2)
    wup = cc1.number_input("w uplift (kip/ft)", 0.0, 20.0, 0.865, 0.01)
    wdn = cc2.number_input("w downward (kip/ft)", 0.0, 20.0, 0.943, 0.01)
H_wind = qh * G * Cn_lat * As / 1000.0
st.sidebar.caption(f"w_up = {wup:.3f}, w_down = {wdn:.3f} kip/ft,  "
                   f"H_wind = {H_wind:.2f} kip")

st.sidebar.header("5. Seismic")
s_mode = st.sidebar.radio("Base shear", ["Computed (Cs x W)", "Direct V"],
                          key="smode")
if s_mode == "Computed (Cs x W)":
    cc1, cc2 = st.sidebar.columns(2)
    SDS = cc1.number_input("SDS (g)", 0.0, 3.0, 1.0, 0.05)
    R = cc2.number_input("R", 1.0, 12.0, 3.0, 0.5,
                         help="Ordinary steel moment frame ~3")
    Ie = st.sidebar.number_input("Ie", 0.5, 2.0, 1.0, 0.05)
    W_seis = wD * (bay1 + bay2)
    st.sidebar.caption(f"Seismic weight W = {W_seis:.1f} kip (dead load)")
    Cs = SDS / (R / Ie)
    V_seis = Cs * W_seis
else:
    V_seis = st.sidebar.number_input("V (kip)", 0.0, 500.0, 4.1, 0.1)
st.sidebar.caption(f"Base shear V = {V_seis:.2f} kip")

st.sidebar.header("6. Options")
lat_dist = st.sidebar.selectbox(
    "Lateral load application",
    ["Tributary (25/50/25)", "Concentrated at windward joint"])
both_dir = st.sidebar.checkbox("Check both lateral directions", True)
drift_limit = st.sidebar.selectbox("Drift limit", ["H/600", "H/400", "H/300",
                                                   "H/200"])

st.title("Two-Bay Steel Moment Frame Analyzer")
st.caption("2D elastic direct-stiffness analysis  |  LRFD combinations per "
           "ASCE 7  |  Member screening per AISC 360  |  "
           "**Preliminary - not for construction**")

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
KIN = 12.0  # in per ft
model = build_model([bay1 * KIN, bay2 * KIN], height * KIN,
                    (Ab, Ib), (Ac, Ic), base=base_fix)

# lateral distribution fractions by tributary width
L1, L2 = bay1, bay2
tw = np.array([L1 / 2, (L1 + L2) / 2, L2 / 2])
frac = tw / tw.sum()
if lat_dist.startswith("Concentrated"):
    frac = np.array([1.0, 0.0, 0.0])

wD_in, wL_in = wD / KIN, wL / KIN
wup_in, wdn_in = wup / KIN, wdn / KIN


def lateral_vec(total, sign=+1):
    return tuple(sign * total * frac)


cases = {
    "D": dict(w_beams=(wD_in, wD_in)),
    "L": dict(w_beams=(wL_in, wL_in)),
    "Wup": dict(w_beams=(-wup_in, -wup_in)),
    "Wdown": dict(w_beams=(wdn_in, wdn_in)),
    "Wlat": dict(H_top=lateral_vec(H_wind, +1)),
    "E": dict(H_top=lateral_vec(V_seis, +1)),
}
cases_m = dict(cases)
cases_m["Wlat"] = dict(H_top=lateral_vec(H_wind, -1))
cases_m["E"] = dict(H_top=lateral_vec(V_seis, -1))

res_pos = {k: analyze(model, E, case_name=k, **v) for k, v in cases.items()}
res_neg = {k: analyze(model, E, case_name=k, **v)
           for k, v in cases_m.items()}

combos_pos = {name: combine(res_pos, combo, name)
              for name, combo in DEFAULT_COMBOS}
combos_neg = {name: combine(res_neg, combo, name)
              for name, combo in DEFAULT_COMBOS}
combos_pos = {k: v for k, v in combos_pos.items() if v is not None}
combos_neg = {k: v for k, v in combos_neg.items() if v is not None}

all_combo_results = []
for name in combos_pos:
    all_combo_results.append((name, "+lat", combos_pos[name]))
    if both_dir:
        all_combo_results.append((name, "-lat", combos_neg[name]))

H_in = height * KIN
lim_map = {"H/200": 200, "H/300": 300, "H/400": 400, "H/600": 600}
lim_den = lim_map[drift_limit]
allow = H_in / lim_den

# ---------------------------------------------------------------------------
# Member capacity screening (AISC 360, in-plane)
# ---------------------------------------------------------------------------
def col_capacity(A, I, Lcol_in):
    r = np.sqrt(I / A)
    KLr = Lcol_in / r
    Fe = np.pi ** 2 * E / KLr ** 2
    if KLr <= 4.71 * np.sqrt(E / Fy):
        Fcr = 0.658 ** (Fy / Fe) * Fy
    else:
        Fcr = 0.877 * Fe
    return 0.9 * A * Fcr, KLr


phiMn_b = 0.9 * Fy * Zb / 12.0          # kip-ft (assume compact, braced)
phiMn_c = 0.9 * Fy * Zc / 12.0
phiPn_c, KLr_c = col_capacity(Ac, Ic, H_in)
phiTn_c = 0.9 * Fy * Ac

# ---------------------------------------------------------------------------
# Envelope table
# ---------------------------------------------------------------------------
env_rows = []
for mname in ["B1", "B2", "C1", "C2", "C3"]:
    Mmax = Vmax = Pc = Pt = 0.0
    Mcombo = Pcombo = ""
    for cname, d, res in all_combo_results:
        m = [mm for mm in res.members if mm.name == mname][0]
        mloc = max(abs(m.M).max(), abs(m.end_forces[2]), abs(m.end_forces[5]))
        if mloc > Mmax:
            Mmax, Mcombo = mloc, f"{cname} ({d})"
        Vmax = max(Vmax, abs(m.V).max())
        Nmin, Nmaxv = m.N.min(), m.N.max()
        if -Nmin > Pc:
            Pc, Pcombo = -Nmin, f"{cname} ({d})"
        Pt = max(Pt, Nmaxv)
    kind = "beam" if mname.startswith("B") else "column"
    phiMn = phiMn_b if kind == "beam" else phiMn_c
    Mmax_ft = Mmax / 12.0                     # kip-in -> kip-ft
    dcr_b = Mmax_ft / phiMn
    if kind == "column":
        pr = Pc / phiPn_c if phiPn_c > 0 else 0
        inter = (pr + 8 / 9 * dcr_b) if pr >= 0.2 else (pr / 2 + dcr_b)
        dcr_t = Pt / phiTn_c
        dcr = max(inter, dcr_t)
        note = f"P-M interaction {inter:.2f}, tension {dcr_t:.2f}"
    else:
        dcr = dcr_b
        note = "flexure (compact, braced assumed)"
    env_rows.append({
        "Member": mname, "Type": kind,
        "max |M| (kip-ft)": round(Mmax_ft, 1),
        "max |V| (kip)": round(Vmax, 1),
        "max P comp (kip)": round(Pc, 1),
        "max P tens (kip)": round(Pt, 1),
        "Governing combo (M)": Mcombo,
        "phiMn (kip-ft)": round(phiMn, 1),
        "DCR": round(dcr, 2), "Check basis": note,
    })
env_df = pd.DataFrame(env_rows)

# ---------------------------------------------------------------------------
# Drift table
# ---------------------------------------------------------------------------
drift_rows = []
for cname, d, res in all_combo_results:
    drift = res.top_drift
    drift_rows.append({
        "Combination": cname, "Dir": d,
        "Delta max (in)": round(drift, 3),
        "Drift ratio": (f"H/{int(round(H_in / drift))}"
                        if drift >= 0.01 else "-"),
        f"Limit {drift_limit} ({allow:.3f} in)":
            "Pass" if drift <= allow else "FAIL",
    })
drift_df = pd.DataFrame(drift_rows)

# ---------------------------------------------------------------------------
# Diagram drawing (shared by Diagrams tab and PDF report)
# ---------------------------------------------------------------------------
def draw_diagram(ax, res, dtype, span_ft, defl_scale=100, title=""):
    nodes = res.node_xy
    for m in res.members:                       # undeformed frame
        x1, y1 = nodes[m.n1]
        x2, y2 = nodes[m.n2]
        ax.plot([x1 / 12, x2 / 12], [y1 / 12, y2 / 12], "k-", lw=2,
                zorder=1)
    for i, (xx, yy) in enumerate(nodes):
        ax.annotate(f"J{i+1}", (xx / 12, yy / 12), textcoords="offset points",
                    xytext=(6, -12), fontsize=9, color="dimgray")
    if dtype == "Deflected shape":
        for m in res.members:
            x1, y1 = nodes[m.n1]
            x2, y2 = nodes[m.n2]
            c, s = (x2 - x1) / m.length, (y2 - y1) / m.length
            dx = c * m.defl_u - s * m.defl_v
            dy = s * m.defl_u + c * m.defl_v
            ax.plot((x1 + m.x * c + defl_scale * dx) / 12,
                    (y1 + m.x * s + defl_scale * dy) / 12, "r-", lw=1.8)
        ax.set_title(title or f"Deflected shape x{defl_scale}")
    else:
        arr, div, unit = {"Moment": ("M", 12.0, "kip-ft"),
                          "Shear": ("V", 1.0, "kip"),
                          "Axial": ("N", 1.0, "kip")}[dtype]
        vmax = max(abs(getattr(m, arr)).max() for m in res.members) / div
        sc = 0.18 * span_ft / max(vmax, 1e-9)
        for m in res.members:
            x1, y1 = nodes[m.n1]
            vals = getattr(m, arr) / div
            if m.kind == "beam":                # sagging (+) below beam
                px = (x1 + m.x) / 12
                py = (y1 - vals * sc * 12) / 12
            else:
                px = (x1 - vals * sc * 12) / 12
                py = (y1 + m.x) / 12
            ax.plot(px, py, "b-", lw=1.6)
            ax.fill(np.append(px, px[0]), np.append(py, py[0]),
                    alpha=0.25, color="b")
            for xi in (0, -1):
                ax.annotate(f"{vals[xi]:.1f}", (px[xi], py[xi]),
                            textcoords="offset points",
                            xytext=(0, 6 if m.kind == "column" else -12),
                            ha="center", fontsize=8, color="navy")
        ax.set_title(title or f"{dtype} diagram ({unit})")
    ax.set_aspect("equal")
    ax.set_xlabel("ft")
    ax.set_ylabel("ft")
    ax.grid(alpha=0.3)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
tab_sum, tab_react, tab_forces, tab_diag, tab_drift, tab_report = st.tabs(
    ["Summary / Envelope", "Reactions", "Member-End Forces",
     "Diagrams", "Drift & Serviceability", "Report (PDF / LaTeX)"])

with tab_sum:
    st.subheader("Design envelope (all combinations"
                 + (" and both lateral directions)" if both_dir else ")"))
    st.dataframe(env_df, width="stretch", hide_index=True)
    st.caption(
        f"Beam phiMn = {phiMn_b:.1f} kip-ft ({beam_name}, compact & braced "
        f"assumed).  Column phiMn = {phiMn_c:.1f} kip-ft, phiPn = "
        f"{phiPn_c:.1f} kip (KL/r = {KLr_c:.0f}), phiTn = {phiTn_c:.0f} kip "
        f"({col_name}, Fy = {Fy} ksi).  Column interaction per AISC H1 "
        f"using max coexisting P and M envelope - conservative screening "
        f"only; second-order (P-Delta) effects not included.")
    worst = env_df["DCR"].max()
    if worst <= 1.0:
        st.success(f"Maximum DCR = {worst:.2f} <= 1.0  (screening passes)")
    else:
        st.error(f"Maximum DCR = {worst:.2f} > 1.0  (screening fails - "
                 f"resize members)")

with tab_react:
    sel = st.selectbox("Combination",
                       [f"{n} ({d})" for n, d, _ in all_combo_results])
    res = all_combo_results[[f"{n} ({d})" for n, d, _ in
                             all_combo_results].index(sel)][2]
    rrows = []
    for j, vals in res.reactions.items():
        rrows.append({"Joint": j, "Fx (kip)": round(vals[0], 2),
                      "Fy (kip)": round(vals[1], 2),
                      "M (kip-ft)": round(vals[2] / 12.0, 1)})
    st.dataframe(pd.DataFrame(rrows), width="stretch",
                 hide_index=True)
    st.caption("Positive Fx = rightward, positive Fy = upward on the "
               "foundation. J1/J2/J3 = left/center/right base.")

with tab_forces:
    sel2 = st.selectbox("Combination ", [f"{n} ({d})" for n, d, _ in
                                         all_combo_results])
    res2 = all_combo_results[[f"{n} ({d})" for n, d, _ in
                              all_combo_results].index(sel2)][2]
    frows = []
    for m in res2.members:
        e = m.end_forces
        frows.append({
            "Member": m.name,
            "End": "1 (base/left)" if m.kind == "column" else "1 (left)",
            "N (kip)": round(e[0], 2), "V (kip)": round(e[1], 2),
            "M (kip-ft)": round(e[2] / 12.0, 1)})
        frows.append({
            "Member": m.name,
            "End": "2 (top/right)" if m.kind == "column" else "2 (right)",
            "N (kip)": round(e[3], 2), "V (kip)": round(e[4], 2),
            "M (kip-ft)": round(e[5] / 12.0, 1)})
    st.dataframe(pd.DataFrame(frows), width="stretch",
                 hide_index=True)
    st.caption("Local member sign convention: N tension +, V local +v, "
               "M local +rotation. Beams B1: J4-J5, B2: J5-J6. Columns "
               "C1: J1-J4, C2: J2-J5, C3: J3-J6.")

with tab_diag:
    cc1, cc2 = st.columns(2)
    sel3 = cc1.selectbox("Combination  ", [f"{n} ({d})" for n, d, _ in
                                           all_combo_results])
    dtype = cc2.selectbox("Diagram", ["Moment", "Shear", "Axial",
                                      "Deflected shape"])
    res3 = all_combo_results[[f"{n} ({d})" for n, d, _ in
                              all_combo_results].index(sel3)][2]
    scale = st.slider("Exaggeration", 1, 500, 100) \
        if dtype == "Deflected shape" else 100
    fig, ax = plt.subplots(figsize=(11, 5.5))
    draw_diagram(ax, res3, dtype, bay1 + bay2, defl_scale=scale,
                 title=(f"Deflected shape x{scale}  ({sel3})"
                        if dtype == "Deflected shape"
                        else f"{dtype} diagram  ({sel3})"))
    st.pyplot(fig)
    if dtype == "Moment":
        st.caption("Beams: sagging plotted below the member. Columns: "
                   "plotted to the left of the member axis; see Member-End "
                   "Forces tab for signed values.")

with tab_drift:
    st.subheader("Wind-drift serviceability")
    st.write(
        f"ASCE 7 Appendix C treats wind drift as a serviceability issue "
        f"without one universal mandatory limit. Selected screening limit: "
        f"**{drift_limit}** = {allow:.3f} in for the {height:.1f}-ft "
        f"({H_in:.0f}-in) frame. H/600 is customary where glass guards or "
        f"brittle finishes are present; H/400 is a common general "
        f"screening value.")
    st.dataframe(drift_df, width="stretch", hide_index=True)
    worst_d = drift_df["Delta max (in)"].max()
    if worst_d <= allow:
        st.success(f"Maximum drift {worst_d:.3f} in <= {allow:.3f} in  "
                   f"(passes {drift_limit})")
    else:
        st.error(f"Maximum drift {worst_d:.3f} in > {allow:.3f} in  "
                 f"(fails {drift_limit})")
    st.caption("Elastic gross-section drift. Foundation rotation, anchor/"
               "base-plate flexibility, connection flexibility, and "
               "second-order effects increase real drift and are not "
               "included.")

with tab_report:
    st.subheader("Calculation report (LaTeX + PDF)")
    st.write(
        "Builds a calculation report from the **current sidebar inputs**: "
        "frame model, loads, LRFD combinations, design envelope with DCRs, "
        "reactions and member-end forces for the governing combination, "
        "moment and deflected-shape diagrams, and the ASCE 7 Appendix C "
        "drift check. Outputs the LaTeX source (.tex) and, when a LaTeX "
        "engine is available on the server, a compiled PDF.")

    if st.button("Generate report", type="primary"):
        with st.spinner("Analyzing and building report..."):
            # governing combination = max beam |M|
            def _beam_mmax(rr):
                return max(max(abs(m.M).max(), abs(m.end_forces[2]),
                               abs(m.end_forces[5]))
                           for m in rr.members if m.kind == "beam")
            gname, gdir, gres = max(all_combo_results,
                                    key=lambda t: _beam_mmax(t[2]))
            gov_label = f"{gname} ({gdir})"

            import datetime
            import tempfile
            tmpdir = tempfile.mkdtemp()
            figs = []
            for kind, fn, cap in [
                    ("Moment", "moment_diagram.png",
                     f"Bending-moment diagram (kip-ft), {gov_label}. "
                     "Sagging plotted below beams."),
                    ("Deflected shape", "deflected_shape.png",
                     f"Deflected shape (x100), {gov_label}.")]:
                f, a = plt.subplots(figsize=(9, 4.8))
                draw_diagram(a, gres, kind, bay1 + bay2)
                fp = f"{tmpdir}/{fn}"
                f.savefig(fp, dpi=150, bbox_inches="tight")
                plt.close(f)
                figs.append((fp, cap))

            if v_mode == "Pressure x tributary factor":
                vb_d = f"{pD:.0f} psf x Cj = {Cj} ft2/ft x {ratio:.3f}"
                vb_l = f"{pL:.0f} psf x Cj = {Cj} ft2/ft x {ratio:.3f}"
                wb = (f"qh G Cn Cj ratio = {qh:.2f} psf x {G:.2f} x Cn "
                      f"x {Cj:.3f} x {ratio:.3f}")
            else:
                vb_d = vb_l = "direct line-load input"
                wb = "direct line-load input"
            if s_mode == "Computed (Cs x W)":
                sb = (f"Cs W = SDS/(R/Ie) x W = {SDS:.2f}/({R:.1f}/"
                      f"{Ie:.2f}) x {W_seis:.1f} kip")
            else:
                sb = "direct base-shear input"

            ctx = {
                "title": "Two-Bay Moment Frame -- Structural Analysis",
                "date": datetime.date.today().isoformat(),
                "bay1": bay1, "bay2": bay2, "height": height,
                "base": base_fix, "beam": beam_name, "col": col_name,
                "Ab": Ab, "Ib": Ib, "Ac": Ac, "Ic": Ic, "E": E, "Fy": Fy,
                "wD": f"{wD:.3f}", "wL": f"{wL:.3f}",
                "wup": f"{wup:.3f}", "wdn": f"{wdn:.3f}",
                "wD_basis": vb_d, "wL_basis": vb_l, "wind_basis": wb,
                "Hwind": f"{H_wind:.2f}",
                "Hwind_basis": (f"qh G Cn,lat As = {qh:.2f} x {G:.2f} x "
                                f"{Cn_lat:.2f} x {As:.0f} ft2"),
                "Vseis": f"{V_seis:.2f}", "seis_basis": sb,
                "latdist": lat_dist,
                "combos": list(combos_pos.keys()),
                "env_df": env_df,
                "reactions": [(j, v[0], v[1], v[2] / 12.0)
                              for j, v in gres.reactions.items()],
                "forces": [row for m in gres.members for row in (
                    (m.name,
                     "1 (base)" if m.kind == "column" else "1 (left)",
                     m.end_forces[0], m.end_forces[1],
                     m.end_forces[2] / 12.0),
                    (m.name,
                     "2 (top)" if m.kind == "column" else "2 (right)",
                     m.end_forces[3], m.end_forces[4],
                     m.end_forces[5] / 12.0))],
                "drifts": [(cn, dd, rr.top_drift,
                            (f"H/{int(round(H_in / rr.top_drift))}"
                             if rr.top_drift >= 0.01 else "-"),
                            "Pass" if rr.top_drift <= allow else "FAIL")
                           for cn, dd, rr in all_combo_results],
                "driftlabel": drift_limit, "allow": f"{allow:.3f}",
                "Hin": f"{H_in:.0f}",
                "phiMnb": f"{phiMn_b:.1f}", "phiMnc": f"{phiMn_c:.1f}",
                "phiPn": f"{phiPn_c:.1f}", "phiTn": f"{phiTn_c:.0f}",
                "KLr": f"{KLr_c:.0f}",
                "govcombo": gov_label,
                "figures": figs,
            }
            try:
                tex = build_latex(ctx)
                st.session_state["tex_bytes"] = tex.encode()
                pdf, log = compile_pdf(tex, [p for p, _ in figs])
                st.session_state["pdf_bytes"] = pdf
                st.session_state["pdf_log"] = log
            except Exception as ex:  # noqa: BLE001
                st.session_state["tex_bytes"] = None
                st.session_state["pdf_bytes"] = None
                st.session_state["pdf_log"] = f"Report build failed: {ex}"

    if st.session_state.get("tex_bytes"):
        st.download_button("Download LaTeX source (.tex)",
                           st.session_state["tex_bytes"],
                           file_name="moment_frame_report.tex",
                           mime="text/plain")
        if st.session_state.get("pdf_bytes"):
            st.download_button("Download PDF report",
                               st.session_state["pdf_bytes"],
                               file_name="moment_frame_report.pdf",
                               mime="application/pdf")
        else:
            st.warning("PDF could not be compiled on this server "
                       "(no LaTeX engine or compile error). Download the "
                       ".tex file and compile it locally with pdflatex.")
            with st.expander("LaTeX log (tail)"):
                st.code(st.session_state.get("pdf_log", "")[-2500:])

st.divider()
st.caption(
    "Method: 2D Euler-Bernoulli direct-stiffness frame analysis, rigid "
    f"beam-column joints, {base_fix} column bases, E = {E:.0f} ksi. "
    "Combinations per ASCE 7 LRFD (1.4D; 1.2D+1.6L; 1.2D+L+W; 0.9D+W; "
    "1.2D+E+L; 0.9D+E). Linear elastic - no P-Delta, no stiffness "
    "reduction. **Preliminary screening tool only - not for construction; "
    "final design requires review by a licensed structural engineer.**")
