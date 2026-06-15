import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math, re, os, io

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
    ("1-ply 1.75\" x 14\" LVL", "lvl", 1.75, 14.0,  6.1, 2600, 1900),
    ("1-ply 1.75\" x 16\" LVL", "lvl", 1.75, 16.0,  7.0, 2600, 1900),
    ("2-ply 1.75\" x 14\" LVL", "lvl", 3.50, 14.0, 12.2, 2600, 1900),
    ("2-ply 1.75\" x 16\" LVL", "lvl", 3.50, 16.0, 14.0, 2600, 1900),
    ("3-ply 1.75\" x 14\" LVL", "lvl", 5.25, 14.0, 18.4, 2600, 1900),
    ("3-ply 1.75\" x 16\" LVL", "lvl", 5.25, 16.0, 21.0, 2600, 1900),
    ("4-ply 1.75\" x 14\" LVL", "lvl", 7.00, 14.0, 24.5, 2600, 1900),
    ("4-ply 1.75\" x 16\" LVL", "lvl", 7.00, 16.0, 28.0, 2600, 1900),
]
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

# ── Deflection helpers ────────────────────────────────────────────────
def _ss_defl(x_ft, L_ft, pls, dls, E, I):
    L, x = L_ft*12, x_ft*12
    if I <= 0: return 1e6
    EI = E * I
    def pl_defl(a_ft, P):
        a = a_ft*12
        if a <= 0 or a >= L: return 0.0
        if x <= a:
            b = L - a
            return P*b*x*(L**2 - b**2 - x**2) / (6*EI*L)
        else:
            return P*a*(L-x)*(L**2 - a**2 - (L-x)**2) / (6*EI*L)
    def dl_defl(x1f, x2f, w):
        if w == 0 or x2f <= x1f: return 0.0
        dx = (x2f - x1f) / 100
        return sum(pl_defl(x1f+(i+.5)*dx, w*dx) for i in range(100))
    return sum(pl_defl(a, P) for a, P in pls) + sum(dl_defl(*seg) for seg in dls)

def max_defl_ss(L_ft, pls, dls, E, I):
    return max(abs(_ss_defl(i*L_ft/1000, L_ft, pls, dls, E, I)) for i in range(1001))

def _cant_defl(x_ft, L_ft, pls, dls, E, I):
    L, x = L_ft*12, x_ft*12
    if I <= 0: return 1e6
    EI = E * I
    def pl_defl(a_ft, P):
        a = min(a_ft*12, L)
        if a <= 0: return 0.0
        return P*x**2*(3*a-x)/(6*EI) if x <= a else P*a**2*(3*x-a)/(6*EI)
    def dl_defl(x1f, x2f, w):
        if w == 0 or x2f <= x1f: return 0.0
        dx = (x2f - x1f) / 100
        return sum(pl_defl(x1f+(i+.5)*dx, w*dx) for i in range(100))
    return sum(pl_defl(a, P) for a, P in pls) + sum(dl_defl(*seg) for seg in dls)

def max_defl_cant(L_ft, pls, dls, E, I):
    return max(abs(_cant_defl(i*L_ft/1000, L_ft, pls, dls, E, I)) for i in range(1001))

# ── Moment / reaction helpers ─────────────────────────────────────────
def compute_main_span_moment(L, pls, dls):
    RA = sum(P*(L-a)/L for a,P in pls) + sum(w*(x2-x1)*(L-(x1+(x2-x1)/2))/L for x1,x2,w in dls)
    RB = sum(P*a/L for a,P in pls)     + sum(w*(x2-x1)*((x1+(x2-x1)/2))/L   for x1,x2,w in dls)
    def V(x):
        v = RA
        for a,P in pls:
            if a <= x: v -= P
        for x1,x2,w in dls:
            if x2 <= x: v -= w*(x2-x1)
            elif x1 < x < x2: v -= w*(x-x1)
        return v
    crit = sorted({0.0, L} | {a for a,_ in pls} | {c for x1,x2,_ in dls for c in (x1,x2)})
    extra = []
    for i in range(len(crit)-1):
        xL, xR = crit[i], crit[i+1]
        if xR > xL and V(xL+1e-6)*V(xR-1e-6) < 0:
            lo, hi = xL, xR
            for _ in range(30):
                mid = (lo+hi)/2
                if V(mid) > 0: lo = mid
                else: hi = mid
            extra.append((lo+hi)/2)
    M_max = 0.0
    for x in sorted(set(crit+extra)):
        M = RA*x
        for a,P in pls:
            if a<=x: M -= P*(x-a)
        for x1,x2,w in dls:
            if x2<=x: M -= w*(x2-x1)*(x-(x1+(x2-x1)/2))
            elif x1<x<x2: M -= w*(x-x1)**2/2
        if M > M_max: M_max = M
    return M_max, RA, RB

def compute_cantilever_moment(L, pls, dls):
    return (sum(P*a for a,P in pls) +
            sum(w*(x2-x1)*(x1+(x2-x1)/2) for x1,x2,w in dls))

def compute_cantilever_reaction(L, pls, dls):
    return sum(P for _,P in pls) + sum(w*(x2-x1) for x1,x2,w in dls)

# ── Section selection ─────────────────────────────────────────────────
def select_wood_beam(M, L, pls, dls, defl_limit, const_dim, const_value,
                     is_cant, mat_filter=None):
    allow = L*12/defl_limit
    cands = []
    for desc,mat,w,d,plf,fb,e,Ix,Sx in wood_list:
        if mat_filter and mat != mat_filter: continue
        if const_dim=='D' and d > const_value: continue
        if const_dim=='B' and w > const_value: continue
        if Sx < M*12000/fb: continue
        defl = max_defl_cant(L,pls,dls,e,Ix) if is_cant else max_defl_ss(L,pls,dls,e,Ix)
        if defl <= allow:
            cands.append((plf,desc,mat,w,d,Ix,Sx,defl,M*12000/fb))
    if not cands: return None
    cands.sort(key=lambda x: x[0])
    b = cands[0]
    return (b[1],b[2],b[5],b[8],b[5],b[6],b[7],b[3],b[4],b[0])

def select_steel_beam(M, L, pls, dls, defl_limit, is_cant):
    allow = L*12/defl_limit
    cands = []
    for desc,Ix,Sx,plf,fb,e in steel_sections:
        S_req = M*12000/fb
        if Sx < S_req: continue
        defl = max_defl_cant(L,pls,dls,e,Ix) if is_cant else max_defl_ss(L,pls,dls,e,Ix)
        if defl <= allow:
            cands.append((plf,desc,Ix,Sx,defl,S_req))
    if cands:
        cands.sort(key=lambda x: x[0]); b=cands[0]
        return (b[1],b[2],b[5],b[2],b[3],b[4])
    last = steel_sections[-1]
    return (last[0],last[1],M*12000/last[4],last[1],last[2],0.0)

# ── Beam diagram ──────────────────────────────────────────────────────
def plot_beam(beams_data, L0, loc, beam_label, sel_desc, sel_mat,
              sel_w, sel_d, sel_cap, max_M, defl_limit):
    left_len, main_len, right_len = L0[1], L0[2], L0[3]
    fig, ax = plt.subplots(figsize=(11, 5.5))

    ax.plot([-left_len, main_len+right_len], [0,0], 'k-', linewidth=3, zorder=5)
    for sx in ([0, main_len] if main_len > 0 else []):
        ax.plot([sx,sx], [-0.35,0.1], 'g-', linewidth=3, zorder=4)

    all_p = [abs(P) for bid in [1,2,3] for a,P in beams_data[bid][0] if P!=0]
    all_w = [abs(w) for bid in [1,2,3] for x1,x2,w in beams_data[bid][1] if w!=0]
    max_p = max(all_p) if all_p else 1.0
    max_w = max(all_w) if all_w else 1.0

    for beam_id in [1,2,3]:
        pl,dl,M,R_left,R_right,L,is_cant = beams_data[beam_id]
        if L == 0: continue

        def to_x(a, bid=beam_id):
            return -a if bid==1 else (main_len+a if bid==3 else a)

        for x1,x2,w in dl:
            if w==0: continue
            if beam_id==1:   px1,px2 = -x2,-x1
            elif beam_id==2: px1,px2 = x1,x2
            else:            px1,px2 = main_len+x1,main_len+x2
            h = 0.42*(abs(w)/max_w)+0.08
            ax.add_patch(patches.Rectangle((px1,0),px2-px1,h,
                linewidth=1.5,edgecolor='blue',facecolor='lightblue',alpha=0.45))
            xv = float(math.ceil(px1+1e-6))
            while xv < px2-1e-6:
                ax.plot([xv,xv],[0,h],'b-',linewidth=0.8,alpha=0.7,zorder=3); xv+=1.0
            ax.plot([px1,px2],[h,h],'b-',linewidth=1.5)
            ax.text((px1+px2)/2,h+0.07,f"{w:.3g}k/ft",
                    ha='center',color='blue',fontsize=11)

        for a,P in pl:
            if P==0: continue
            xp = to_x(a)
            h = 0.65*(abs(P)/max_p)+0.1
            ax.annotate("",xy=(xp,0),xytext=(xp,h),
                arrowprops=dict(arrowstyle="-|>",color='red',lw=2.5))
            ax.text(xp,h+0.07,f"{P:.3g}k",ha='center',color='red',fontsize=11)

        if M > 0:
            mx = (-left_len/2 if beam_id==1 else
                  (main_len/2 if beam_id==2 else main_len+right_len/2))
            ax.text(mx,-0.28,f"M={M:.1f}",ha='center',color='purple',fontsize=11)

    if main_len > 0:
        R1 = beams_data[2][3] + (beams_data[1][3] if left_len>0 else 0)
        R2 = beams_data[2][4] + (beams_data[3][3] if right_len>0 else 0)
        ax.text(0,       -0.50,f"R1={R1:.1f}k",ha='center',color='green',fontsize=11)
        ax.text(main_len,-0.50,f"R2={R2:.1f}k",ha='center',color='green',fontsize=11)

    if sel_desc:
        ax.text((main_len-left_len)/2,-0.68,
                f"{sel_desc}  (Capacity={sel_cap:.1f} kip-ft)",
                ha='center',fontsize=11,color='black')

    ax.set_title(f"Beam Loading — {loc}",fontsize=13)
    ax.set_xlim(-left_len-0.8, main_len+right_len+0.8)
    ax.set_ylim(-0.82,1.05)
    ax.set_xlabel("Position (ft)",fontsize=11)
    ax.tick_params(labelsize=10)
    ax.grid(axis='x',linestyle='--',alpha=0.3)
    da = main_len*12/defl_limit if main_len>0 else 0
    fig.text(0.01,0.01,
             f"Max Moment: {max_M:.1f} kip-ft    "
             f"Deflection limit: L/{defl_limit} = {da:.2f} in    "
             f"Grade: {sel_mat.upper() if sel_mat else beam_label}",
             fontsize=10,color='white',backgroundcolor='black',va='bottom')
    plt.tight_layout(rect=[0,0.06,1,1])
    return fig

# ── Streamlit UI ──────────────────────────────────────────────────────
def span_input(name, span_len, prefix):
    n_pt = int(st.number_input("Number of point loads", 0, 10, 0, key=f"{prefix}_n"))
    point_loads = []
    cumul = 0.0
    for i in range(n_pt):
        c1, c2 = st.columns(2)
        P   = c1.number_input(f"P{i+1} (kips)", value=0.0, step=0.1, key=f"{prefix}_P{i}")
        lbl = "Distance from support (ft)" if i==0 else f"Distance from P{i} (ft)"
        d   = c2.number_input(lbl, 0.0, float(span_len), 0.0, step=0.5, key=f"{prefix}_d{i}")
        cumul += d
        point_loads.append((cumul, P))
    seg_bounds = [0.0] + [pl[0] for pl in point_loads] + [span_len]
    n_seg = n_pt + 1
    dist_loads = []
    st.write("**Distributed loads (k/ft) per segment:**")
    cols = st.columns(min(n_seg, 4))
    for s in range(n_seg):
        x1, x2 = seg_bounds[s], seg_bounds[s+1]
        w = cols[s % 4].number_input(
            f"Seg {s+1}  {x1:.1f}–{x2:.1f} ft",
            value=0.0, step=0.05, key=f"{prefix}_w{s}")
        if w != 0 and x2 > x1:
            dist_loads.append((x1, x2, w))
    return point_loads, dist_loads

def main():
    st.set_page_config(page_title="Beam Design", page_icon="🏗", layout="wide")
    st.title("🏗 Wood / Steel Beam Design Calculator")
    st.caption("Sawn Lumber · PSL · LVL · Steel  |  Cantilever + Main Span")
    st.divider()

    # ── Global settings ──────────────────────────────────────────────
    c1, c2, c3 = st.columns([2,2,2])
    mat_choice = c1.selectbox("Beam Type",
        ["STEEL BEAM","WOOD/PSL BEAM","ROOF BEAM","FLOOR BEAM","LVL BEAM"])
    loc = c2.text_input("Beam Location / Mark", "BM-1")

    beam_mat    = ["STEEL BEAM","WOOD/PSL BEAM","ROOF BEAM","FLOOR BEAM","LVL BEAM"].index(mat_choice)
    force_steel = (beam_mat == 0)
    force_lvl   = (beam_mat == 4)
    beam_label  = mat_choice

    if beam_mat == 2:
        finish = c3.selectbox("Roof Finish",
            ["Plaster ceiling (L/240)","Non-plaster ceiling (L/180)","No ceiling (L/120)"])
        defl_limit = 240 if "240" in finish else (180 if "180" in finish else 120)
    else:
        defl_limit = 240
        c3.metric("Deflection Limit", f"L/{defl_limit}")

    # Wood material sub-filter
    mat_filter = None
    if force_lvl:
        mat_filter = "lvl"
        st.info("LVL sections: 1.75\" × 14\" and 1.75\" × 16\", 1–4 plies  "
                "(Fb = 2600 psi, E = 1900 ksi)")
    elif not force_steel:
        wood_mat_choice = st.radio(
            "Wood Material",
            ["All (Sawn + PSL + LVL)", "Sawn Lumber Only", "PSL Only",
             "LVL Only  (1.75\" × 14\" / 16\", 1–4 plies)"],
            horizontal=True)
        if wood_mat_choice == "Sawn Lumber Only":
            mat_filter = "sawn"
        elif wood_mat_choice == "PSL Only":
            mat_filter = "psl"
        elif wood_mat_choice.startswith("LVL Only"):
            mat_filter = "lvl"

    const_dim, const_value = None, None
    if not force_steel:
        with st.expander("Dimension Constraints (optional)"):
            cc1, cc2 = st.columns(2)
            constr = cc1.radio("Constrain", ["None","Max Depth","Max Width"], horizontal=True)
            if constr == "Max Depth":
                const_dim = 'D'; const_value = cc2.number_input("Max depth (in)", 6.0, 36.0, 18.0)
            elif constr == "Max Width":
                const_dim = 'B'; const_value = cc2.number_input("Max width (in)", 1.5, 12.0, 8.0)

    st.divider()

    # ── Span lengths ─────────────────────────────────────────────────
    st.subheader("Span Lengths (ft)")
    s1, s2, s3 = st.columns(3)
    left_len  = s1.number_input("Left Cantilever",  0.0, 100.0,  0.0, 0.5)
    main_len  = s2.number_input("Main Span",         0.0, 200.0, 20.0, 0.5)
    right_len = s3.number_input("Right Cantilever",  0.0, 100.0,  0.0, 0.5)
    L0 = [0.0, left_len, main_len, right_len, 0.0]
    st.divider()

    # ── Loads per span ────────────────────────────────────────────────
    st.subheader("Load Inputs")
    span_cfg = [
        (1, "Left Cantilever",  left_len,  True,  "lc"),
        (2, "Main Span",        main_len,  False, "ms"),
        (3, "Right Cantilever", right_len, True,  "rc"),
    ]
    all_pl, all_dl = {}, {}
    for bid, sname, slen, is_cant, pfx in span_cfg:
        if slen > 0:
            with st.expander(f"{sname}  ({slen:.1f} ft)", expanded=True):
                all_pl[bid], all_dl[bid] = span_input(sname, slen, pfx)
        else:
            all_pl[bid], all_dl[bid] = [], []

    st.divider()

    if st.button("⚡  Calculate", type="primary", use_container_width=True):
        beams_data = {}
        for bid, sname, slen, is_cant, pfx in span_cfg:
            pl, dl = all_pl[bid], all_dl[bid]
            if slen == 0:
                beams_data[bid] = ([], [], 0.0, 0.0, 0.0, 0.0, is_cant)
            elif is_cant:
                M = compute_cantilever_moment(slen, pl, dl)
                R = compute_cantilever_reaction(slen, pl, dl)
                beams_data[bid] = (pl, dl, M, R, 0.0, slen, is_cant)
            else:
                M, R1, R2 = compute_main_span_moment(slen, pl, dl)
                beams_data[bid] = (pl, dl, M, R1, R2, slen, is_cant)

        st.divider()
        st.header("Results")
        results_summary = {}

        for bid, sname, slen, is_cant, pfx in span_cfg:
            pl, dl, M, R1, R2, L, _ = beams_data[bid]
            if L == 0: continue
            st.subheader(f"{sname}  —  {L:.2f} ft")
            da = L*12/defl_limit
            m1, m2, m3 = st.columns(3)
            m1.metric("Max Moment", f"{M:.2f} ft-kips")
            m2.metric(f"Defl. Limit L/{defl_limit}", f"{da:.2f} in")
            m3.metric("Reaction (fixed)" if is_cant else "R1 / R2",
                      f"{R1:.2f} kips" if is_cant else f"{R1:.2f} k / {R2:.2f} k")

            entry = {'L':L,'M':M,'R1':R1,'R2':R2,'is_cant':is_cant}

            if force_steel:
                desc,Ir,Sr,Ip,Sp,defl = select_steel_beam(M,L,pl,dl,defl_limit,is_cant)
                st.success(f"**Selected STEEL:  {desc}**")
                cc = st.columns(4)
                cc[0].metric("Req. S",    f"{Sr:.1f} in³")
                cc[1].metric("Prov. I",   f"{Ip:.0f} in⁴")
                cc[2].metric("Prov. S",   f"{Sp:.1f} in³")
                cc[3].metric("Deflection",f"{defl:.3f} in")
                entry.update({'type':'steel','desc':desc,'S_req':Sr,
                              'I_prov':Ip,'S_prov':Sp,'defl':defl})
            else:
                wr = select_wood_beam(M,L,pl,dl,defl_limit,const_dim,const_value,
                                      is_cant,mat_filter)
                if wr is None:
                    st.error("No adequate section found for this span.")
                    entry['type'] = 'none'
                    if mat_filter != 'lvl':
                        desc,Ir,Sr,Ip,Sp,defl = select_steel_beam(M,L,pl,dl,defl_limit,is_cant)
                        if desc != "None":
                            st.info(f"Steel alternative: **{desc}**  "
                                    f"(I={Ip:.0f} in⁴, S={Sp:.1f} in³, defl={defl:.3f} in)")
                else:
                    desc,mat,Ir,Sr,Ip,Sp,defl,width,depth,plf = wr
                    st.success(f"**Selected {mat.upper()}:  {desc}**")
                    cc = st.columns(4)
                    cc[0].metric("Req. S",    f"{Sr:.1f} in³")
                    cc[1].metric("Prov. I",   f"{Ip:.0f} in⁴")
                    cc[2].metric("Prov. S",   f"{Sp:.1f} in³")
                    cc[3].metric("Deflection",f"{defl:.3f} in")
                    st.info(f"Dimensions: **{width:.3f}\" × {depth:.1f}\"**  |  "
                            f"Self weight: {plf:.1f} lb/ft")
                    entry.update({'type':'wood','desc':desc,'mat':mat,'S_req':Sr,
                                  'I_prov':Ip,'S_prov':Sp,'defl':defl,
                                  'width':width,'depth':depth,'plf':plf})
            results_summary[bid] = entry

        # Diagram label — governing span, prefer main span
        all_M = [beams_data[bid][2] for bid in [1,2,3] if beams_data[bid][5]>0]
        max_M = max(all_M) if all_M else 0
        sel_desc = sel_mat = ""; sel_cap = sel_w = sel_d = 0.0
        best_M = 0
        for bid in [2, 1, 3]:
            if bid not in results_summary: continue
            r = results_summary[bid]
            if r.get('type') == 'wood' and r['M'] > best_M:
                best_M   = r['M']
                sel_desc = r['desc']
                sel_mat  = r['mat']
                sel_w    = r['width']
                sel_d    = r['depth']
                fb = 2600 if r['mat']=='lvl' else (2900 if r['mat']=='psl' else 1200)
                sel_cap  = fb * r['S_prov'] / 12000

        st.divider()
        st.subheader("Beam Loading Diagram")
        fig = plot_beam(beams_data, L0, loc, beam_label,
                        sel_desc, sel_mat, sel_w, sel_d, sel_cap, max_M, defl_limit)
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        png_bytes = buf.getvalue()
        plt.close(fig)

        st.divider()
        st.subheader("Download")
        st.download_button("⬇ Diagram (PNG)", png_bytes,
                           file_name="beam_diagram.png", mime="image/png",
                           use_container_width=True)

if __name__ == "__main__":
    main()
