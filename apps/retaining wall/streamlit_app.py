import streamlit as st

# ============================================================
#  RETAINING WALL PROGRAM — STREAMLIT VERSION (FINAL CLEAN)
# ============================================================

st.set_page_config(
    page_title="Retaining Wall Program",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar width lock
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        min-width: 350px;
        max-width: 350px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def init(name, value):
    if name not in st.session_state:
        st.session_state[name] = value

def initialize_globals():
    init("T", [0.0] * 61)
    init("D", [0.0] * 5)
    init("C", [0.0] * 61)
    init("A", [0.0] * 8)

    names_defaults = {
        "P1": "", "P2": "", "P3s": "", "P4s": "", "P5s": "",
        "H": 0.0, "H1": 0.0, "H2": 8.0/12.0, "H3": 0.0, "H4": 0.0,
        "L": 0.0, "L1": 0.0, "L2": 0.0,
        "P": 0.0, "P4": 0.0, "S1": 0.0, "S2": 0.0, "C9": 0.0,
        "Y": 0.0, "C1": 0, "Cw": 0, "T1": 0,
        "Dval": 0.0, "F": 0.0, "F1": 0.0, "F2": 0.0,
        "N1": 0, "N2": 0, "G": 0,
        "W1": 0.0, "W2": 0.0, "W3": 0.0, "W4": 0.0,
        "W5": 0.0, "W6": 0.0, "W7": 0.0, "W8": 0.0,
        "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0,
        "M5": 0.0, "M6": 0.0, "M7": 0.0, "M8": 0.0,
        "X": 0.0, "S": 0.0, "E": 8.0, "E1": 0.0,
        "E2": 0, "K1": 0, "Areq": 0.0, "A2": 0.0,
        "P1s": 0.0, "K": 0.0, "J": 0.0,
        "A1": 0.0, "S9": 0.0, "D9": 0,
        "R": "", "P3": 0.0, "Pf": 0.0, "Mpf": 0.0, "P9": 0.0, "X9": 0.0,
        "B": 0.0, "M": 0.0, "I1": 0, "I2": 0,
        "Tftg": 12.0,
        "_RM_toe": 0.0, "_OTM_toe": 0.0, "_SF_OT": 0.0,
        "TABLE_ROWS": [],
        "_silent": False,
        "KERN_MODE": 1,
        # Store final Pf state for reporting
        "Pf_applied": False,
        # Shear key
        "USE_KEY": False,
        "KEY_Hk": 0.0,    # key depth in ft — set to 1.0 (12 in) when engaged
        "KEY_used": False, # True when key was actually needed and applied
    }

    for name, value in names_defaults.items():
        init(name, value)

def initialize_block_and_rebar():
    ss = st.session_state
    ss.D[1] = 5.5
    ss.D[2] = 0.0
    ss.D[3] = 0.0
    ss.D[4] = 0.0
    ss.A[1] = 0.10
    ss.A[2] = 0.15
    ss.A[3] = 0.23
    ss.A[4] = 0.30
    ss.A[5] = 0.47
    ss.A[6] = 0.66
    ss.A[7] = 0.90
    ss.P1 = " (IN)"
    ss.P2 = " (FT)"
    ss.P3s = " (PSF)"
    ss.P4s = " (LB)"
    ss.P5s = " (LB/CF)"

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    initialize_globals()
    initialize_block_and_rebar()
    st.session_state.initialized = True

if "output_log" not in st.session_state:
    st.session_state.output_log = []

def print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text = sep.join(str(a) for a in args) + end
    st.session_state.output_log.append(text)

# ------------------------------------------------------------
# gosub_1580 — Program Title
# ------------------------------------------------------------
def gosub_1580():
    print("\n\n\nRETAINING WALL PROGRAM")
    print("REV. 2-12-84 (Python/Streamlit conversion)")

# ------------------------------------------------------------
# gosub_140 — INPUT BLOCK
# ------------------------------------------------------------
def gosub_140():
    ss = st.session_state
    with st.sidebar:
        st.header("Input Parameters")
        t1_options = [1, 2, 4]
        t1_index = t1_options.index(ss.T1) if ss.T1 in t1_options else 0
        ss.T1 = st.selectbox("TYPE OF WALL", t1_options, index=t1_index)
        ss.L2 = st.number_input("GROUND SLOPE (H:V) (X:1)", value=ss.L2)
        ss.H1 = st.number_input("RETAINING WALL HEIGHT (FT)", value=ss.H1)
        ss.P  = st.number_input("EQUIV. FLUID PRESSURE (#/CF)", value=ss.P if ss.P else 30.0)
        ss.S2 = st.number_input("ALLOWABLE SOIL BEARING (PSF)", value=ss.S2 if ss.S2 else 1000.0)
        ss.C9 = st.number_input("FRICTION COEFF", value=ss.C9 if ss.C9 else 0.4)
        ss.P4 = st.number_input("ALLOWABLE PASSIVE (PSF)", value=ss.P4 if ss.P4 else 300.0)
        ss.S1 = st.number_input("SURCHARGE (FT)", value=ss.S1)
        ss.Cw = st.selectbox("CONC. WALL (0=Masonry, 1=Concrete)", [0, 1], index=ss.Cw)

        if ss.Cw == 0:
            cur_insp = 1 if ss.N1 == 20 else 0
            I = st.selectbox(
                "CONT. INSPECTION (0=No → F'm≤333psi, 1=Yes → F'm≤500psi)",
                [0, 1], index=cur_insp
            )
            if I == 1:
                ss.N1 = 20; ss.F1 = 500.0
            else:
                ss.N1 = 40; ss.F1 = 333.0
            if I == 0:
                st.caption("⚠️ No cont. inspection: F'm limited to 333 psi.")

            cur_12 = 1 if ss.D[2] != 0.0 else 0
            I = st.selectbox("12-IN BLOCK (0=No, 1=Yes)", [0, 1], index=cur_12)
            ss.D[2] = 9.5 if I == 1 else 0.0

            cur_16 = 1 if ss.D[3] != 0.0 else 0
            I = st.selectbox("16-IN BLOCK (0=No, 1=Yes)", [0, 1], index=cur_16)
            ss.D[3] = 13.5 if I == 1 else 0.0
        else:
            ss.F  = st.number_input("CONCRETE F'C (PSI)", value=ss.F if ss.F else 2000.0)
            ss.F2 = 0.45 * ss.F
            ss.N2 = int(29000 / (57 * (ss.F ** 0.5)))
            wall_t_default = (ss.Dval + 2.5) if ss.Dval else 8.0
            I = st.number_input("WALL T (IN)", value=wall_t_default)
            ss.Dval = I - 2.5

        ss.Y  = st.number_input("STEEL ALLOWABLE (KSI)", value=ss.Y if ss.Y else 20.0)
        ss.C1 = st.selectbox("SLAB ON GRADE (0 OR 1)", [0, 1], index=ss.C1)
        H2_in_default = (ss.H2 * 12.0) if ss.H2 else 8.0
        H2_in = st.number_input("WALL HEIGHT INCREMENT (IN)", value=H2_in_default)
        ss.H2 = H2_in / 12.0
        ss.E = st.number_input("FTG. OVERHANG - SHORT SIDE (IN)", value=ss.E if ss.E else 8.0)

        kern_index = 0 if ss.KERN_MODE == 1 else 1
        kern_sel = st.selectbox(
            "ECCENTRICITY MODE",
            ["ALLOW OUTSIDE KERN (1)", "FORCE INSIDE KERN (2)"],
            index=kern_index
        )
        ss.KERN_MODE = 1 if kern_sel.startswith("ALLOW") else 2

        st.markdown("---")
        st.subheader("Shear Key Option")
        ss.USE_KEY = st.checkbox(
            "Use 12\" shear key (if sliding is the only failure)",
            value=ss.USE_KEY
        )
        if ss.USE_KEY:
            st.caption(
                "When checked: B is sized for OT / kern / soil bearing only. "
                "If sliding still fails after B is final, the minimum key depth "
                "for SF ≥ 1.5 is computed (rounded up to next inch) and reported."
            )

def gosub_5000():
    pass

# ------------------------------------------------------------
# gosub_790 — TABLE HEADER
# ------------------------------------------------------------
def gosub_790():
    print(
        f"{'HT(FT)':>8}"
        f"{'T(IN)':>8}"
        f"{'D(IN)':>8}"
        f"{'MOM(FT-LB)':>14}"
        f"{'A(REQ)':>10}"
        f"{'A(USE)':>10}"
        f"{'F\'M(PSI)':>12}"
        f"{'RE-BAR':>9}"
        f"{'WALL':>7}"
    )
    print("-" * 86)

# ------------------------------------------------------------
# gosub_670 — TABLE ROW PRINT
# ------------------------------------------------------------
def gosub_670():
    ss = st.session_state
    if getattr(ss, '_silent', False):
        return
    ss.G += 1
    ss.T[ss.G] = ss.Dval + 2.5
    ss.C[ss.G] = ss.Cw

    for ss.D9 in range(4, 9):
        if ss.Areq > 0.23 * 1.02 or ss.Areq < 0.15 / 1.01:
            ss.A1 = 3.14159 * (ss.D9 / 8.0) ** 2 / 4.0
            ss.S9 = ss.A1 * 12.0 / ss.Areq
        else:
            ss.A1 = 0.31
            ss.D9 = 5
            ss.S9 = 16.0
            break
        if ss.S9 > 8:
            break

    if ss.S9 >= 8:
        ss.S9 = int(ss.S9 / 8.0 + 0.1) * 8

    wall_type = "CONC." if ss.C[ss.G] == 1 else "BLK."
    if ss.H >= 1.9:
        rebar = f"#{ss.D9}@{int(ss.S9):3d}"
        row = (
            f"{ss.H:8.2f}"
            f"{ss.Dval+2.5:8.2f}"
            f"{ss.Dval:8.2f}"
            f"{int(ss.M):14d}"
            f"{ss.Areq:10.3f}"
            f"{ss.A1*12/ss.S9:10.3f}"
            f"{int(ss.F):12d}"
            f"{rebar:>9}"
            f"{wall_type:>7}"
        )
        ss.TABLE_ROWS.append(row)
        print(row)

# ------------------------------------------------------------
# gosub_print_header
# ------------------------------------------------------------
def gosub_print_header():
    ss = st.session_state
    print("\n  RETAINING WALL DESIGN\n")
    print("    WALL TYPE -", ss.T1)
    if ss.T1 == 4:
        print("    WALL FTG. IS ON THE SAME SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")
        if ss.L2 != 0:
            print(f"    GROUND SLOPE {ss.L2:.2f} : 1")
    elif ss.T1 == 2:
        print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")
    else:
        print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE OPP. SIDE OF RET. EARTH")
    print()
    print(f"    WALL HEIGHT            = {ss.H1:8.2f}{ss.P2}")
    print(f"    EQUIV. FLUID PRESSURE  = {ss.P:8.2f}{ss.P5s}")
    print(f"    ALLOWABLE PASSIVE      = {ss.P4:8.2f}{ss.P5s}")
    print(f"    COEFF. OF FRICTION     = {ss.C9:8.2f}")
    if ss.S1 != 0:
        print(f"    SURCHARGE              = {ss.S1:8.2f}{ss.P2}")
    if ss.E != 0:
        print(f"    FTG. OVERHANG (SHORT)  = {ss.E:8.2f}{ss.P1}")
# ------------------------------------------------------------
def gosub_1210():
    ss = st.session_state
    print("\n  RETAINING WALL DESIGN\n")
    print("    WALL TYPE -", ss.T1)
    if ss.T1 == 4:
        print("    WALL FTG. IS ON THE SAME SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")
        if ss.L2 != 0:
            print(f"    GROUND SLOPE {ss.L2:.2f} : 1")
    elif ss.T1 == 2:
        print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")
    else:
        print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE OPP. SIDE OF RET. EARTH")
    print()
    print(f"    WALL HEIGHT            = {ss.H1:8.2f}{ss.P2}")
    print(f"    EQUIV. FLUID PRESSURE  = {ss.P:8.2f}{ss.P5s}")
    print(f"    ALLOWABLE PASSIVE      = {ss.P4:8.2f}{ss.P5s}")
    print(f"    COEFF. OF FRICTION     = {ss.C9:8.2f}")
    if ss.S1 != 0:
        print(f"    SURCHARGE              = {ss.S1:8.2f}{ss.P2}")
    if ss.E != 0:
        print(f"    FTG. OVERHANG (SHORT)  = {ss.E:8.2f}{ss.P1}")
    print(f"    ALLOWABLE SOIL BEARING = {ss.S2:8.2f}{ss.P3s}")
    print(f"    ALLOWABLE STL. STRESS  = {ss.Y:8.2f} (KSI)")
    kern_label = "ALLOW OUTSIDE KERN" if ss.KERN_MODE == 1 else "FORCE INSIDE KERN"
    print(f"    ECCENTRICITY MODE      : {kern_label}")
    print()
    gosub_790()
    for row in ss.TABLE_ROWS:
        print(row)
    gosub_1400()

# ------------------------------------------------------------
# gosub_510 — STEEL AREA CALC
# ------------------------------------------------------------
def gosub_510():
    ss = st.session_state
    if ss.Dval == 0:
        print("ERROR: Dval = 0 (wall thickness not set). Run Input Block first.")
        ss.K1 = 0
        return

    ss.Areq = ss.M * 12.0 / (ss.Y * 7.0 / 8.0 * ss.Dval * 1000.0)
    ss.A2 = ss.Areq

    if ss.Cw == 0:
        ss.P1s = ss.N1 * ss.Areq / (12.0 * ss.Dval)
    else:
        ss.P1s = ss.N2 * ss.Areq / (12.0 * ss.Dval)

    ss.K = (2 * ss.P1s + ss.P1s * ss.P1s) ** 0.5 - ss.P1s
    ss.J = 1 - ss.K / 3.0
    if ss.K == 0 or ss.J == 0:
        print("ERROR: K or J = 0. Reinforcement calculation cannot proceed.")
        ss.K1 = 0
        return

    ss.F = ss.M * 2.0 / (ss.K * ss.J * ss.Dval * ss.Dval)
    ss.K1 = 0
    if ss.Cw == 0:
        if ss.F < ss.F1:
            gosub_670()
            ss.K1 = 1
        elif ss.N1 == 40 and ss.F < 500.0:
            if not getattr(ss, '_silent', False):
                print(f"    NOTE: D={ss.Dval:.1f}in  F'm={ss.F:.0f} psi > 333 — cont. inspection required; try next block size.")
            ss.K1 = 0
    else:
        if ss.F < ss.F2:
            gosub_670()
            ss.K1 = 1

# ------------------------------------------------------------
# gosub_620 — BAR SELECTION
# ------------------------------------------------------------
def gosub_620():
    ss = st.session_state
    for ss.I2 in range(1, ss.I1 + 1):
        if ss.Areq >= ss.A[ss.I2] / 1.02:
            continue
        if ss.A[ss.I2] >= ss.A2 / 1.02:
            return
        else:
            ss.Areq = ss.A[ss.I2]
        gosub_510()
        if ss.K1 == 1:
            return

# ------------------------------------------------------------
# gosub_360 — MOMENT + STEEL LOOP
# ------------------------------------------------------------
def gosub_360():
    ss = st.session_state
    MIN_ZONE = 2.0

    heights = []
    h = 0.0
    while True:
        h += ss.H2
        if h >= ss.H1:
            h = ss.H1
            heights.append(round(h, 6))
            break
        heights.append(round(h, 6))

    MAX_DVAL = 30.0

    def _check_block(idx, h_val):
        save = {k: ss[k] for k in ('Dval','G','K1','M','Areq','A2','F','I1','P1s','K','J')}
        ss._silent = True
        ss.M    = ss.S1 * ss.P * h_val**2 / 2.0 + ss.P * h_val**3 / 6.0
        ss.Dval = ss.D[idx]
        gosub_510()
        ok = ss.K1 == 1
        if not ok:
            ss.I1 = 7
            gosub_620()
            ok = ss.K1 == 1
        ss._silent = False
        for k, v in save.items():
            ss[k] = v
        return ok

    def _find_block_index(h_val):
        for idx in range(1, 5):
            if idx > 4 or ss.D[idx] == 0:
                return idx
            if _check_block(idx, h_val):
                return idx
        return 5

    raw_idx = []
    for h_val in heights:
        raw_idx.append(_find_block_index(h_val))

    enforced_idx = list(raw_idx)
    n = len(heights)
    for j in range(n - 1, -1, -1):
        if enforced_idx[j] >= 2:
            zone_top = j
            while zone_top > 0 and enforced_idx[zone_top-1] >= enforced_idx[j]:
                zone_top -= 1
            zone_ht = heights[n-1] - heights[zone_top] + ss.H2
            if zone_ht < MIN_ZONE:
                extra_steps = int((MIN_ZONE - zone_ht) / ss.H2) + 1
                new_top = max(0, zone_top - extra_steps)
                for k in range(new_top, zone_top):
                    if enforced_idx[k] < enforced_idx[j]:
                        enforced_idx[k] = enforced_idx[j]

    ss.H   = 0.0
    ss.G   = 0
    prev_I = 0

    for step, h_val in enumerate(heights):
        ss.H = h_val
        ss.M = ss.S1 * ss.P * ss.H**2 / 2.0 + ss.P * ss.H**3 / 6.0
        I    = enforced_idx[step]

        if I != prev_I and I >= 2:
            blk_name = {2: "12-in CMU", 3: "16-in CMU"}.get(I, "Concrete")
            print(f"    NOTE: {blk_name} zone starts at H={ss.H:.2f} ft (24-in min zone enforced).")
        prev_I = I

        if ss.Cw == 1 or I > 4 or ss.D[I] == 0:
            prev_I_cmu = max(1, I - 1)
            save_Cw, save_F2, save_N2, save_Dval = ss.Cw, ss.F2, ss.N2, ss.Dval
            ss.Dval = ss.D[prev_I_cmu] if (prev_I_cmu <= 4 and ss.D[prev_I_cmu] != 0) else 5.5
            ss.Cw = 1;  ss.F2 = 900.0;  ss.N2 = 11
            found = False
            while ss.Dval <= MAX_DVAL:
                gosub_510()
                if ss.K1 == 1: found = True; break
                ss.I1 = 7
                gosub_620()
                if ss.K1 == 1: found = True; break
                ss.Dval += 1.0
            if not found:
                print(f"  WARNING: No valid concrete section at H={ss.H:.2f} ft")
            ss.Cw = save_Cw;  ss.F2 = save_F2;  ss.N2 = save_N2
            if not found: ss.Dval = save_Dval
        else:
            ss.Dval = ss.D[I]
            gosub_510()
            if ss.K1 == 0:
                ss.I1 = 7
                gosub_620()
            if ss.K1 == 0:
                print(f"  WARNING: Block index {I} still fails at H={ss.H:.2f} ft")

# ------------------------------------------------------------
# gosub_1205 — EARTH PRESSURE BLOCK
# ------------------------------------------------------------
def gosub_1205():
    ss = st.session_state
    ss.P3 = ss.S1 * ss.P * ss.H4 + ss.P * ss.H4 * ss.H4 / 2.0
    ss.M4 = ss.S1 * ss.P * ss.H4 * ss.H4 / 2.0 + ss.P * ss.H4 ** 3 / 6.0
    # Pf computed here but whether it is APPLIED depends on kern check
    ss.Pf = ss.P3 * 0.3

# ============================================================
# gosub_830 — FOOTING DESIGN
#
# CHANGES:
#  1. Footing thickness minimum = 12 in (was 15 for H1>6).
#     Rule: H1<=4 → 12in, H1<=6 → 12in, H1<=8 → 12in,
#           H1>8  → max(12, T[G])
#     Simplified: always max(12, T[G]) — gives 12 at minimum.
#
#  2. Pf (back-face friction) applied ONLY when resultant is
#     OUTSIDE the kern (e > B/6). This is physically correct:
#     when the footing is within the kern, soil bears uniformly
#     (no lift-off tendency) so wall-back-face friction is not
#     mobilised for OT resistance.
#     Implementation uses an iterative approach:
#       - First solve WITHOUT Pf → get X → check kern
#       - If outside kern → add Pf → re-solve → repeat
#       - Converge when kern status stops changing
#
#  3. Tftg_ft bug fix in gosub_1400: was guarding with
#     "if T[G]>=12 else 1.0" which is wrong for thin slabs.
#     Now simply T[G]/12.0 always.
# ============================================================
def gosub_830():
    """
    Footing design — rewritten to match RETSCRN4.BAS exactly.

    BASIC reference (all moments measured from TOE):
      Type 1: L = E+T[G]
        Wall arm  = (L - T[i]/2) / 12     (from toe)
        Earth arm = (L + T[i]/2 + (T[G]-T[i])/2) / 12  ... actually BASIC:
          earth W = (T[G]-T[i])*H3*100/12 ; M = W*(L+T[i]/2+(T[G]-T[i])/2)/12 — NOT used
        Actually BASIC for T1==1:
          W5/M5 earth: W=(T[G]-T[i])*H3*100/12 ; arm=(L-T[i]/2)/12 — same as wall arm?
          No — from hex line ~99: arm = (L+T[i]/2+(T[G]-T[i])/2)/12  (from TOE)
        W6 = W1+W2+W5+P3  (P3 is used as vertical, = full lateral resultant)
        M6 = M1+M2+M4+M5  (M4 ADDED — all moments act same direction from TOE)

      Type 2: L = E
        Wall arm  = (L + T[i]/2) / 12
        Earth: W=L*H3*100/12 ; arm = L/2/12
        W6 = W1+W2+W5+P3 ; M6 = M1+M2+M3+M5-M4  (M3=P3*B for T4 only, else 0)

      Type 4: L = E
        Wall arm = (L + T[i]/2) / 12
        L1 = B - L/12 - T/12 (heel overhang)
        W7 = L1*H1*100 ; M7 = W7*(L1/2 + L/12 + T/12)
        M3 = P3*B
        W6 = W1+W2+W5+P3+W7+W8 ; M6 = M1+M2+M3+M5+M7+M8-M4

    Kern / widening: X = M6/W6 (from TOE)
      If X > B/2 → widen (B + 2/12)
      If X < B/2 → widen (B + 2/12)  [same — always widen until within kern]
      Actually BASIC: if X > B/2 → E2=0 else E2=1; widen differently per E2
      Simplified: keep widening until B/3 <= X <= 2B/3

    Soil bearing: S = (1 + 6*E1/B)*W6/B  (trapezoidal, kern enforced)

    Sliding (original BASIC):
      If C9*W6 >= P3: "FRICTION > SLIDING OK"
      Else if C9*W6 + P4*(Tftg/12) >= P3: "WITH PASSIVE ON FTG OK"
      Else: compute key depth = Tftg - T[G] (footing below stem bottom)
            "USE (key_depth) IN DEEP KEY"

    Added enhancements (beyond BASIC):
      - OT check (S.F. >= 1.5 about toe) as widen driver
      - USE_KEY option: post-convergence, compute min key depth for SF=1.5
      - Passive on footing included in sliding SF formula
    """
    import math
    ss = st.session_state

    ss.KEY_used = False

    # --- Footing thickness: minimum 12 in ---
    Tftg = max(12.0, ss.T[ss.G])
    ss.Tftg = Tftg

    # --- L = short overhang (toe side) ---
    # Type 1: L = E + T[G] (toe overhang + stem width, moments from TOE)
    # All others: L = E
    if ss.T1 == 1:
        ss.L = ss.E + ss.T[ss.G]
    else:
        ss.L = ss.E

    # --- H4: effective height for earth pressure ---
    if ss.C1 == 1:
        ss.H4 = ss.H1
    else:
        ss.H4 = ss.H1 + Tftg / 12.0

    gosub_1205()   # compute P3, M4, Pf

    # --- Initial B estimate ---
    ss.B = int(ss.H1 / 2.5 * 12.0) / 12.0

    # --------------------------------------------------
    # Inner helpers
    # --------------------------------------------------
    def _compute_W1_M1_W5_M5():
        """
        Wall weight W1/M1 and earth on heel W5/M5.
        All moments from TOE.
        BASIC exactly:
          Type 1: wall arm = (L - T[i]/2)/12
                  earth W  = (T[G]-T[i])*H3*100/12 ; arm = (L+T[i]/2+(T[G]-T[i])/2)/12
          Type 2: wall arm = (L + T[i]/2)/12
                  earth W  = L*H3*100/12 ; arm = L/24  [= L/2 / 12]
          Type 4: wall arm = (L + T[i]/2)/12
                  earth heel W = (Tftg - T[i])*H3*100/12 ; arm = (L+T[i]+(Tftg-T[i])/2)/12
        """
        W1 = M1 = W5 = M5 = 0.0
        H3 = ss.H2
        for i in range(1, ss.G + 1):
            if i == ss.G:
                H3 = ss.H1 - ss.H2 * (ss.G - 1)
            Ti = ss.T[i]
            # Wall weight
            if ss.C[i] == 1:
                W = 12.5 * Ti * H3
            else:
                W = (77.0 / 8.0) * Ti * H3
            W1 += W
            if ss.T1 == 1:
                # BASIC: wall arm from TOE = (L - T[i]/2) / 12
                arm_w = (ss.L - Ti / 2.0) / 12.0
            else:
                # BASIC: wall arm from TOE = (L + T[i]/2) / 12
                arm_w = (ss.L + Ti / 2.0) / 12.0
            M1 += W * arm_w
            # Earth on heel / behind wall
            if ss.T1 == 1:
                # BASIC Type 1: step earth + E-strip (toe-side earth column)
                # Step earth: (T[G]-T[i])*H3*100/12 ; arm=(L+T[i]/2+(T[G]-T[i])/2)/12
                step_in = ss.T[ss.G] - Ti
                Ws = step_in * H3 * 100.0 / 12.0
                arm_e = (ss.L + Ti / 2.0 + step_in / 2.0) / 12.0
                # E-strip is accumulated outside the loop (added once below)
            elif ss.T1 == 2:
                # BASIC: heel earth = L*H3*100/12 ; arm = L/24
                Ws = ss.L * H3 * 100.0 / 12.0
                arm_e = ss.L / 24.0
            else:  # Type 4
                # BASIC: heel earth = (Tftg-T[i])*H3*100/12
                step_in = Tftg - Ti
                Ws = step_in * H3 * 100.0 / 12.0
                arm_e = (ss.L + Ti / 2.0 + step_in / 2.0) / 12.0
            W5 += Ws
            M5 += Ws * arm_e
        # E-strip for Type 1: earth column in toe overhang, full wall height
        # W = E/12 * H1 * 100 ; arm from TOE = E/24
        if ss.T1 == 1:
            W_E   = (ss.E / 12.0) * ss.H1 * 100.0
            arm_E = ss.E / 24.0
            W5 += W_E
            M5 += W_E * arm_E

        return W1, M1, W5, M5

    def _build_totals():
        """
        Assemble W2/M2/W6/M6 per BASIC formulas.
        All moments from TOE.
        """
        ss.W2 = 12.5 * Tftg * ss.B
        ss.M2 = ss.W2 * ss.B / 2.0

        ss.Pf  = ss.P3 / 3.0   # rubbing back friction = P3/3 (horizontal resistance only)
        ss.Mpf = ss.Pf * (ss.L / 12.0)

        if ss.T1 == 1:
            ss.M3 = 0.0
            ss.W6 = ss.W1 + ss.W2 + ss.W5          # gravity loads only — Pf NOT in W6
            ss.M6 = ss.M1 + ss.M2 + ss.M4 + ss.M5
        elif ss.T1 == 2:
            ss.M3 = 0.0
            ss.W6 = ss.W1 + ss.W2 + ss.W5
            ss.M6 = ss.M1 + ss.M2 + ss.M3 + ss.M5 - ss.M4
        else:  # Type 4
            ss.L1  = ss.B - ss.L / 12.0 - Tftg / 12.0
            ss.W7  = ss.L1 * ss.H1 * 100.0
            ss.M7  = ss.W7 * (ss.L1 / 2.0 + ss.L / 12.0 + Tftg / 12.0)
            ss.M3  = ss.P3 * ss.B
            if ss.L2 != 0:
                ss.W8 = 100.0 * (ss.L1 * ss.L2) / 2.0 * (ss.L1 * ss.L2)
                ss.M8 = ss.W8 * (ss.L1 * ss.L2 / 3.0 + ss.L / 12.0 + Tftg / 12.0)
            ss.W6 = ss.W1 + ss.W2 + ss.W5 + ss.W7 + ss.W8
            ss.M6 = ss.M1 + ss.M2 + ss.M3 + ss.M5 + ss.M7 + ss.M8 - ss.M4

    def _widen():
        ss.B = int(12 * ss.B + 2) / 12.0

    # --- Compute W1/M1/W5/M5 (fixed, don't depend on B) ---
    ss.W1, ss.M1, ss.W5, ss.M5 = _compute_W1_M1_W5_M5()

    # --------------------------------------------------
    # Widening loop
    # --------------------------------------------------
    MAX_ITER = 200
    for _ in range(MAX_ITER):
        _build_totals()

        if ss.W6 == 0:
            break

        ss.X  = ss.M6 / ss.W6        # resultant from TOE
        ss.E1 = abs(ss.B / 2.0 - ss.X)
        ss.S  = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)  # max soil bearing

        # --- Kern check: keep resultant inside middle third ---
        # BASIC: widen if X>B/2 (toe side) or X<B/2 with E2 logic
        # Simplified: X must be in [B/3, 2B/3]
        if ss.X < ss.B / 3.0 or ss.X > 2.0 * ss.B / 3.0:
            _widen()
            continue

        # --- Soil bearing ---
        if ss.S > ss.S2:
            _widen()
            continue

        # --- Overturning about toe (added enhancement) ---
        # RM = M6 + M4 (since M6 already has M4 subtracted for types 2/4,
        # or M4 added for type 1 — reconstruct RM correctly)
        if ss.T1 == 1:
            # M6 = M1+M2+M4+M5 → RM = M6 (all resisting including P3 vertical)
            RM  = ss.M6
            OTM = ss.M4
        else:
            # M6 = M1+M2+M3+M5±... - M4 → RM = M6 + M4
            RM  = ss.M6 + ss.M4
            OTM = ss.M4
        if OTM > 0 and RM / OTM < 1.5:
            _widen()
            continue

        # --- Sliding ---
        # Pf = P3/3 acts as direct horizontal friction on wall back face.
        # W6 is gravity only, so friction = W6×C9. Add Pf separately.
        W6_grav  = ss.W6
        friction = W6_grav * ss.C9
        passive  = ss.P4 * (Tftg / 12.0)
        lateral  = ss.P3
        if lateral > 0 and (friction + passive + ss.Pf) / lateral < 1.5 and not ss.USE_KEY:
            _widen()
            continue

        # All checks passed
        break

    # --- Post-loop: verify all S.F. values and warn if any NG ---
    _build_totals()
    ss.X  = ss.M6 / ss.W6 if ss.W6 != 0 else 0
    ss.E1 = abs(ss.B / 2.0 - ss.X)
    ss.S  = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)

    if ss.T1 == 1:
        RM_chk = ss.M6;  OTM_chk = ss.M4
    else:
        RM_chk = ss.M6 + ss.M4;  OTM_chk = ss.M4

    W6_grav  = ss.W6
    friction = W6_grav * ss.C9
    passive  = ss.P4 * (Tftg / 12.0)
    lateral  = ss.P3
    SF_SL_check = (friction + passive + ss.Pf) / lateral if lateral > 0 else 999.0
    SF_OT_check = RM_chk / OTM_chk if OTM_chk > 0 else 999.0

    if SF_OT_check < 1.5:
        print(f"  ** WARNING: OT S.F. = {SF_OT_check:.2f} < 1.5 — max iterations reached **")
    if SF_SL_check < 1.5 and not ss.USE_KEY:
        print(f"  ** WARNING: SL S.F. = {SF_SL_check:.2f} < 1.5 — check inputs **")

    # Store OT values for reporting
    if ss.T1 == 1:
        ss._RM_toe  = ss.M6
        ss._OTM_toe = ss.M4
        ss._SF_OT   = ss.M6 / ss.M4 if ss.M4 > 0 else 999.0
    else:
        ss._RM_toe  = ss.M6 + ss.M4
        ss._OTM_toe = ss.M4
        ss._SF_OT   = (ss.M6 + ss.M4) / ss.M4 if ss.M4 > 0 else 999.0

    ss.Pf_applied = True

    # --------------------------------------------------
    # Post-convergence shear key check (USE_KEY option)
    # --------------------------------------------------
    if ss.USE_KEY:
        friction = ss.W6 * ss.C9
        passive  = ss.P4 * (Tftg / 12.0)
        lateral  = ss.P3
        if lateral > 0 and (friction + passive + ss.Pf) / lateral < 1.5:
            # Solve: friction + Pf + P4*(Tftg/12 + Hk) = 1.5*lateral
            Hk_needed = (1.5 * lateral - friction - passive - ss.Pf) / ss.P4 if ss.P4 > 0 else 0.0
            Hk_in = max(12, math.ceil(Hk_needed * 12.0))
            ss.KEY_Hk  = Hk_in / 12.0
            ss.KEY_used = True

# ------------------------------------------------------------
# gosub_1400 — FOOTING SUMMARY
# FIX: Tftg_ft now always T[G]/12.0 (removed incorrect guard).
#      Added Pf_applied note to clarify whether Pf was used.
# ------------------------------------------------------------
def gosub_1400():
    """
    Footing summary output — matches RETSCRN4.BAS output format.
    All quantities computed from TOE reference (same as gosub_830).
    """
    ss = st.session_state
    Tftg    = ss.Tftg
    Tftg_ft = Tftg / 12.0

    print()
    print(f"    FTG. WIDTH  = {ss.B:.2f}{ss.P2}")
    print(f"    FTG.  T     = {ss.Tftg:.2f}{ss.P1}")
    print(f"    X           = {ss.X:.2f}{ss.P2}  (from TOE)")

    ss.E1 = abs(ss.B / 2.0 - ss.X)
    kern_status = "WITHIN KERN" if ss.E1 <= ss.B / 6.0 else "OUTSIDE KERN"
    print(f"    ECCENTRICITY MODE : {'FORCE INSIDE KERN' if ss.KERN_MODE==2 else 'ALLOW OUTSIDE KERN'}")
    print(f"    ECCENTRICITY (E1) = {ss.E1:.2f}{ss.P2}  (B/6 = {ss.B/6:.2f}{ss.P2})  ** {kern_status} **")

    # Soil bearing — trapezoidal (kern enforced in design loop)
    ss.S = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
    S_min = (ss.W6 / ss.B) * (1.0 - 6.0 * ss.E1 / ss.B)
    sb_flag = "  ** OK **" if ss.S <= ss.S2 else f"  ** NG — EXCEEDS {ss.S2:.0f} PSF **"
    print(f"    SOIL BEAR'G MAX = {ss.S:.2f}{ss.P3s}", sb_flag)
    print(f"    SOIL BEAR'G MIN = {S_min:.2f}{ss.P3s}")
    print(f"    SOIL BEAR'G ALL = {ss.S2:.2f}{ss.P3s}")

    # Overturning about toe
    if ss.T1 == 1:
        RM  = ss.M6       # M6 = M1+M2+M4+M5 (all resisting including M4)
        OTM = ss.M4
    else:
        RM  = ss.M6 + ss.M4
        OTM = ss.M4
    if OTM > 0:
        SF_OT   = RM / OTM
        ot_flag = "  ** OK **" if SF_OT >= 1.5 else "  ** NG — S.F. < 1.5 **"
        print(f"    RESIST. MOM (RM)  = {RM:.2f} (FT-LB)")
        print(f"    OVERTURN MOM (OTM)= {OTM:.2f} (FT-LB)")
        print(f"    OT S.F. = {RM:.2f}/{OTM:.2f} = {SF_OT:.2f}", ot_flag)
    else:
        print("    OT S.F. = N/A")

    # Sliding — W6 is gravity only; Pf=P3/3 added as direct horizontal resistance
    friction = ss.W6 * ss.C9
    passive  = ss.P4 * Tftg_ft
    lateral  = ss.P3
    if lateral > 0:
        if ss.C1 == 1:
            print(f"    WITH SLAB SLID'G O.K.")
        else:
            print(f"    F--SLID'G   = {lateral:.2f}{ss.P4s}")
            print(f"    F--FRICTION = {friction:.2f}{ss.P4s}  W6×C9 = {ss.W6:.2f}×{ss.C9:.2f}")
            print(f"    BACK FRIC.  = {ss.Pf:.2f}{ss.P4s}  Pf = P3/3 = {lateral:.2f}/3")
            key_passive = ss.P4 * ss.KEY_Hk if ss.KEY_used else 0.0
            total_resist = friction + ss.Pf + passive + key_passive
            SF_SL = total_resist / lateral
            sl_flag = "  ** OK **" if SF_SL >= 1.5 else "  ** NG — S.F. < 1.5 **"
            if friction + ss.Pf >= lateral:
                print(f"    FRICTION > SLIDING  O.K.")
            elif friction + ss.Pf + passive >= lateral:
                print(f"    WITH PASSIVE ON FTG.  O.K.")
                print(f"    PASSIVE RES = P4×Tftg = {ss.P4:.0f}×{Tftg_ft:.2f} = {passive:.2f} (LB)")
                print(f"    SL S.F. = ({friction:.2f}+{ss.Pf:.2f}+{passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
            elif ss.KEY_used:
                Hk_in = round(ss.KEY_Hk * 12.0)
                total_passive = passive + key_passive
                basic_key_in = int((lateral - friction - ss.Pf) * 12.0 / ss.P4) if ss.P4 > 0 else 0
                print(f"    PASSIVE RES = P4×Tftg            = {ss.P4:.0f}×{Tftg_ft:.2f} = {passive:.2f} (LB)")
                print(f"    KEY PASSIVE = P4×Hk              = {ss.P4:.0f}×{ss.KEY_Hk:.3f} = {key_passive:.2f} (LB)  ** SHEAR KEY **")
                print(f"    TOTAL PASS  = P4×(Tftg+Hk)      = {ss.P4:.0f}×({Tftg_ft:.2f}+{ss.KEY_Hk:.3f}) = {total_passive:.2f} (LB)")
                print(f"    KEY DEPTH   = {Hk_in} IN below bottom of footing  (SF=1.5; BASIC min = {basic_key_in} IN)")
                print(f"    SL S.F. = ({friction:.2f}+{ss.Pf:.2f}+{total_passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
            else:
                key_depth_in = max(0.0, Tftg - ss.T[ss.G])
                print(f"    USE {key_depth_in:.0f} (IN) DEEP KEY")
                print(f"    SL S.F. = ({friction:.2f}+{ss.Pf:.2f}+{passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
    else:
        print("    SL S.F. = N/A")

# ------------------------------------------------------------
# gosub_1610 — MOMENT BREAKDOWN
# ------------------------------------------------------------
def gosub_1610():
    """Moment breakdown — KEY-2. Matches BASIC output labels."""
    ss = st.session_state
    print("    ITEMS          W           M      NOTES")
    print(f"    WALL       {ss.W1:10.2f}  {ss.M1:10.2f}")
    print(f"    FTG.       {ss.W2:10.2f}  {ss.M2:10.2f}")
    print(f"    P/3        {ss.Pf:10.2f}  {ss.Mpf:10.2f}  (rubbing back friction, label=P/3, value=P3)")
    print(f"    EARTH      {ss.W5:10.2f}  {ss.M5:10.2f}")
    print(f"    EARTH      {ss.W7:10.2f}  {ss.M7:10.2f}")
    print(f"    EARTH      {ss.W8:10.2f}  {ss.M8:10.2f}")
    print(f"    O.T.M.     {'---':>10}  {ss.M4:10.2f}  lateral earth OTM")
    print(f"    TOTAL      {ss.W6:10.2f}  {ss.M6:10.2f}")
    print(f"    P3 (horiz) {ss.P3:10.2f}  {'(lateral)':>10}  earth pressure resultant")
    print()

# ------------------------------------------------------------
# gosub_1700 — POINT LOAD CHECK
# FIX: Q2 sign corrected — M4 is OTM and must be subtracted
#      from resisting moments, consistent with how M6 is built.
# ------------------------------------------------------------
def gosub_1700():
    ss = st.session_state
    if ss.B == 0:
        print("    ERROR: B = 0. Run Footing Design first.")
        return

    B_trial = ss.B
    # W6 already includes Pf if applicable; add point load P9
    Q1 = ss.W6 + ss.P9
    # M6 = RM - OTM already. Add point load moment, subtract nothing extra.
    Q2 = ss.M6 + ss.P9 * ss.X9

    if Q1 == 0:
        print("    ERROR: Total weight Q1 = 0. Run Footing Design first.")
        return

    X_trial = Q2 / Q1
    E9 = abs(B_trial / 2 - X_trial)

    print(f"    P (LB)              {ss.P9:.2f}")
    print(f"    X9 (FT)             {ss.X9:.2f}")
    print(f"    B (FTG. WIDTH - FT) {B_trial:.2f}")
    print(f"    W = {Q1:.2f}")
    print(f"    M = {Q2:.2f}")
    print(f"    E = {E9:.2f}")

    if E9 > B_trial / 6.0:
        contact = 3.0 * X_trial if X_trial < B_trial / 2.0 else 3.0 * (B_trial - X_trial)
        SP_max = 2.0 * Q1 / contact if contact > 0 else 9999
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN =   0.00 (PSF)")
        print(f"    ECCENTRICITY = {E9:.2f} (FT)  (B/6 = {B_trial/6:.2f} FT)  ** OUTSIDE KERN **")
    else:
        SP_max = (Q1 / B_trial) * (1.0 + 6.0 * E9 / B_trial)
        SP_min = (Q1 / B_trial) * (1.0 - 6.0 * E9 / B_trial)
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN = {SP_min:.2f} (PSF)")
        print(f"    ECCENTRICITY = {E9:.2f} (FT)  (B/6 = {B_trial/6:.2f} FT)  ** WITHIN KERN **")

    OTM_t = ss.M4
    RM_t  = Q2 + ss.M4
    if OTM_t > 0:
        SF_t = RM_t / OTM_t
        ot_flag = "  ** OK **" if SF_t >= 1.5 else "  ** NG — S.F. < 1.5 **"
        print(f"    RESIST. MOM (RM)  = {RM_t:.2f} (FT-LB)")
        print(f"    OVERTURN MOM (OTM)= {OTM_t:.2f} (FT-LB)")
        print(f"    OT S.F. = RM/OTM = {RM_t:.2f}/{OTM_t:.2f} = {SF_t:.2f}", ot_flag)
    else:
        print("    OT S.F. = N/A")

# ============================================================
# MAIN PAGE LAYOUT
# ============================================================

st.title("Retaining Wall Program — Streamlit Version")

gosub_140()

if "show_ptload" not in st.session_state:
    st.session_state.show_ptload = False
if "pl_P9" not in st.session_state:
    st.session_state.pl_P9 = 0.0
if "pl_X9" not in st.session_state:
    st.session_state.pl_X9 = 0.0

with st.sidebar:
    st.markdown("---")
    st.session_state.show_ptload = st.checkbox(
        "Show Point Load inputs (KEY-3)",
        value=st.session_state.show_ptload
    )
    if st.session_state.show_ptload:
        st.subheader("Point Load Check (KEY‑3)")
        st.number_input("P (LB)",  step=1.0, format="%g", key="pl_P9")
        st.number_input("X9 (FT)", step=0.1, format="%g", key="pl_X9")

st.session_state.P9 = st.session_state.pl_P9
st.session_state.X9 = st.session_state.pl_X9

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

if col1.button("Run Input Block"):
    gosub_1580()
    gosub_5000()
    gosub_print_header()

if col2.button("Run Moment Loop"):
    if st.session_state.Dval == 0 and st.session_state.Cw == 1:
        print("ERROR: Run Input Block first (Dval not set).")
    else:
        gosub_360()

if col3.button("Run Footing Design"):
    if st.session_state.G == 0:
        print("ERROR: Run Moment Loop first.")
    else:
        gosub_830()
        gosub_1400()

if col4.button("More Print (KEY‑1)"):
    gosub_1210()

if col5.button("Footing Moment (KEY‑2)"):
    gosub_1610()

if col6.button("Point Load Check (KEY‑3)"):
    gosub_1700()

if st.session_state.output_log:
    st.markdown("---")
    st.subheader("Output")
    st.text("".join(st.session_state.output_log))

st.markdown("---")

if st.button("🔄 Reset All Inputs"):
    keys_to_clear = [
        "T","D","C","A","P1","P2","P3s","P4s","P5s","H","H1","H2","H3","H4",
        "L","L1","L2","P","P4","S1","S2","C9","Y","C1","Cw","T1","Dval","F",
        "F1","F2","N1","N2","G","W1","W2","W3","W4","W5","W6","W7","W8",
        "M1","M2","M3","M4","M5","M6","M7","M8","X","S","E","E1","E2","K1",
        "Areq","A2","P1s","K","J","A1","S9","D9","R","P3","P9","X9","B","M",
        "I1","I2","TABLE_ROWS","KERN_MODE","output_log","initialized",
        "pl_P9","pl_X9","show_ptload","Pf_applied","Tftg",
        "_RM_toe","_OTM_toe","_SF_OT",
        "USE_KEY","KEY_Hk","KEY_used",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    initialize_globals()
    initialize_block_and_rebar()
    st.session_state.initialized = True
    st.session_state.output_log = []
    st.rerun()
