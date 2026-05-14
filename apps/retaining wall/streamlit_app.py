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
                "If sliding still fails after B is final, a 12\" deep key is added "
                "and its passive resistance (P4 × 1 ft) is credited."
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
    ss = st.session_state

    ss.KEY_used = False   # reset each run
    first_pass = True
    while True:
        # --- FIX 1: minimum footing thickness = 12 in ---
        # For walls taller than 8 ft match bottom stem but never < 12 in.
        # For all others 12 in is sufficient.
        # --- Footing thickness: minimum 12 in, match stem if larger ---
        Tftg = max(12.0, ss.T[ss.G])
        ss.Tftg = Tftg   # store for gosub_1400 reporting and sliding check

        H3 = ss.H2
        ss.W1 = ss.W5 = ss.M1 = ss.M5 = 0.0

        if ss.T1 == 1:
            ss.L = ss.E + ss.T[ss.G]   # L = E + T(G), moments from HEEL
        else:
            ss.L = ss.E

        # For Type 1: compute earth W5/M5 using zone heights directly
        # (two rectangles: E-strip full height + step exposure upper zone only)
        if ss.T1 == 1:
            # Determine zone heights from T array
            # E-strip: E/12 wide, full H1 height, arm from heel = E/24
            W_E   = 100.0 * (ss.E / 12.0) * ss.H1
            arm_E = ss.E / 24.0
            M_E   = W_E * arm_E
            # Step exposure: (T(G)-T(zone))/12 wide, zone height, arm=E/12+(step/2)
            # Sum over distinct stem thicknesses using per-segment H3
            ss.W5 = W_E;  ss.M5 = M_E

        for i in range(1, ss.G + 1):
            H3 = ss.H2
            if i == ss.G:
                H3 = ss.H1 - ss.H2 * (ss.G - 1)

            if ss.C[i] == 1:
                W = 12.5 * ss.T[i] * H3
            else:
                W = 77.0 / 8.0 * ss.T[i] * H3
            ss.W1 += W

            # Wall moment: arm = (L - T[i]/2)/12 for all types
            ss.M1 += W * (ss.L - ss.T[i] / 2.0) / 12.0

            if ss.T1 == 1:
                # Step earth per segment: (T[G]-T[i])/12 wide
                # arm from HEEL = E/12 + (T[G]-T[i])/24
                step_w = (ss.T[ss.G] - ss.T[i]) / 12.0
                W_s    = 100.0 * H3 * step_w
                arm_s  = ss.E / 12.0 + step_w / 2.0
                ss.W5 += W_s
                ss.M5 += W_s * arm_s
            elif ss.T1 == 2:
                heel_ft = ss.L / 12.0
                W  = 100.0 * H3 * heel_ft
                arm_ft = heel_ft / 2.0
                ss.W5 += W; ss.M5 += W * arm_ft
            else:
                heel_ft = (Tftg - ss.T[i]) / 12.0
                W  = 100.0 * H3 * heel_ft
                arm_ft = ss.L / 12.0 + ss.T[i] / 12.0 + heel_ft / 2.0
                ss.W5 += W; ss.M5 += W * arm_ft

        if ss.C1 == 1:
            ss.H4 = ss.H1
        else:
            ss.H4 = ss.H1 + Tftg / 12.0

        gosub_1205()

        if first_pass:
            ss.B = int(ss.H1 / 2.5 * 12.0) / 12.0
            first_pass = False

        ss.W2 = 12.5 * Tftg * ss.B
        ss.M2 = ss.W2 * ss.B / 2.0

        # --------------------------------------------------
        def _build_totals(use_pf: bool):
            """
            Assemble W6 / M6 with or without Pf contribution.
            use_pf=True  → include back-face friction (outside kern)
            use_pf=False → omit back-face friction (within kern)
            """
            pf_val  = ss.Pf if use_pf else 0.0
            mpf_val = pf_val * (ss.L / 12.0)
            ss.Mpf  = mpf_val

            if ss.T1 == 1:
                # Type 1: Pf=P3/3 vertical at heel (M=0), M4 adds to M6
                ss.Pf   = ss.P3 / 3.0
                ss.Mpf  = 0.0
                ss.M3   = 0.0
                ss.W6   = ss.W1 + ss.W2 + ss.W5 + ss.Pf
                ss.M6   = ss.M1 + ss.M2 + ss.M5 + ss.M4
            elif ss.T1 != 4:
                ss.M3  = 0.0
                ss.W6  = ss.W1 + ss.W2 + ss.W5 + pf_val
                ss.M6  = ss.M1 + ss.M2 + ss.M5 + mpf_val - ss.M4
            else:
                ss.L1  = ss.B - ss.L / 12.0 - Tftg / 12.0
                ss.W7  = ss.L1 * ss.H1 * 100.0
                ss.M7  = ss.W7 * (ss.L1 / 2.0 + ss.L / 12.0 + Tftg / 12.0)
                ss.M3  = 0.0
                ss.W6  = ss.W1 + ss.W2 + ss.W5 + pf_val + ss.W7 + ss.W8
                ss.M6  = ss.M1 + ss.M2 + ss.M5 + mpf_val + ss.M7 + ss.M8 - ss.M4

        def _recalc_totals(use_pf: bool):
            """Recompute W2/M2/W5/M5/W6/M6 after B changes."""
            ss.W2 = 12.5 * Tftg * ss.B
            ss.M2 = ss.W2 * ss.B / 2.0

            ss.W5 = 0.0; ss.M5 = 0.0
            if ss.T1 == 1:
                # E-strip: constant regardless of B
                W_E = 100.0 * (ss.E / 12.0) * ss.H1
                ss.W5 += W_E; ss.M5 += W_E * (ss.E / 24.0)
            H3 = ss.H2
            for i in range(1, ss.G + 1):
                if i == ss.G:
                    H3 = ss.H1 - ss.H2 * (ss.G - 1)
                if ss.T1 == 1:
                    step_w = (ss.T[ss.G] - ss.T[i]) / 12.0
                    W_s   = 100.0 * H3 * step_w
                    arm_s = ss.E / 12.0 + step_w / 2.0
                    ss.W5 += W_s; ss.M5 += W_s * arm_s
                elif ss.T1 == 2:
                    heel_ft = ss.L / 12.0
                    W  = 100.0 * H3 * heel_ft
                    arm_ft = heel_ft / 2.0
                    ss.W5 += W; ss.M5 += W * arm_ft
                else:
                    heel_ft = (Tftg - ss.T[i]) / 12.0
                    W  = 100.0 * H3 * heel_ft
                    arm_ft = ss.L / 12.0 + ss.T[i] / 12.0 + heel_ft / 2.0
                    ss.W5 += W; ss.M5 += W * arm_ft

            _build_totals(use_pf)

        def _widen(use_pf: bool):
            ss.B = int(12 * ss.B + 2) / 12.0
            _recalc_totals(use_pf)

        # --------------------------------------------------
        # Initial totals: start WITHOUT Pf (assume within kern).
        # Pf is always applied regardless of kern status.
        # --------------------------------------------------
        _recalc_totals(use_pf=True)
        ss.Pf_applied = True

        MAX_FOOTING_ITER = 200   # safety cap on outer widening loop
        outer_iter = 0

        while outer_iter < MAX_FOOTING_ITER:
            outer_iter += 1

            _recalc_totals(use_pf=True)

            # X measured from HEEL for T1==1, from TOE for others
            ss.X  = ss.M6 / ss.W6 if ss.W6 != 0 else 0
            ss.E1 = abs(ss.B / 2.0 - ss.X)

            if ss.T1 == 1:
                # Type 1: X computed from HEEL (for kern/soil bearing).
                # OT check uses explicit arm-to-TOE for each item.

                # --- OT S.F. >= 1.5 about TOE ---
                # Arms from TOE:
                #   Wall:        E/12 + T[i]/24
                #   Footing:     B/2
                #   Earth E-strip: L/12 + E/24  (L=E+T[G])
                #   Earth step:  (E+T[i])/12 + step_w/2
                #   Pf at heel:  B
                RM_toe = 0.0
                H3 = ss.H2
                for i in range(1, ss.G + 1):
                    if i == ss.G:
                        H3 = ss.H1 - ss.H2 * (ss.G - 1)
                    Ti = ss.T[i]
                    # wall weight
                    Ww = (12.5 if ss.C[i] == 1 else 77.0/8.0) * Ti * H3
                    arm_wall = ss.E/12.0 + Ti/24.0
                    RM_toe  += Ww * arm_wall
                    # earth step
                    step_w   = (ss.T[ss.G] - Ti) / 12.0
                    Ws       = 100.0 * H3 * step_w
                    arm_step = (ss.E + Ti)/12.0 + step_w/2.0
                    RM_toe  += Ws * arm_step
                # footing
                RM_toe += ss.W2 * ss.B / 2.0
                # earth E-strip
                W_E     = 100.0 * (ss.E/12.0) * ss.H1
                arm_E   = ss.L/12.0 + ss.E/24.0   # L=E+T[G]
                RM_toe += W_E * arm_E
                # Pf at heel: arm = B
                RM_toe += ss.Pf * ss.B
                OTM_toe = ss.M4
                SF_OT   = RM_toe / OTM_toe if OTM_toe > 0 else 999.0
                if SF_OT < 1.5:
                    _widen(use_pf=True)
                    continue

                # --- Kern check (controlled by KERN_MODE) ---
                # E1 = eccentricity = |B/2 - X| where X is from HEEL
                # X_toe = B - X  (resultant from TOE)
                X_toe = ss.B - ss.X
                if ss.KERN_MODE == 2:
                    # Force inside kern: E1 <= B/6
                    if ss.E1 > ss.B / 6.0:
                        _widen(use_pf=True)
                        continue
                else:
                    # Allow outside kern but resultant must stay on footing
                    if X_toe <= 0 or X_toe >= ss.B:
                        _widen(use_pf=True)
                        continue

                # --- Sliding S.F. >= 1.5 ---
                # When USE_KEY is on, skip sliding as a widen trigger here;
                # a post-convergence key check handles it after B is final.
                Tftg_ft = Tftg / 12.0
                friction = ss.W6 * ss.C9
                passive  = ss.P4 * Tftg_ft * ss.B
                lateral  = ss.P3
                if lateral > 0 and (friction + passive) / lateral < 1.5 and not ss.USE_KEY:
                    _widen(use_pf=True)
                    continue

                # --- Soil bearing <= allowable ---
                # Use triangular formula when outside kern, trapezoidal when inside
                if ss.E1 > ss.B / 6.0:
                    # Outside kern: triangular bearing, contact = 3*X_toe
                    contact = 3.0 * X_toe if X_toe > 0 else 0.001
                    S_max = 2.0 * ss.W6 / contact
                else:
                    # Inside kern: trapezoidal
                    S_max = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
                if S_max > ss.S2:
                    _widen(use_pf=True)
                    continue

                # Store for reporting
                ss._RM_toe  = RM_toe
                ss._OTM_toe = OTM_toe
                ss._SF_OT   = SF_OT
            else:
                # --- eccentricity / kern check ---
                need_widen = False
                if ss.KERN_MODE == 1:
                    if ss.X <= 0 or ss.X >= ss.B:
                        need_widen = True
                else:
                    if ss.X < ss.B / 3.0 or ss.X > 2.0 * ss.B / 3.0:
                        need_widen = True

                if need_widen:
                    _widen(use_pf=True)
                    continue

                # --- S.F. overturning >= 1.5 ---
                OTM = ss.M4
                RM  = ss.M6 + ss.M4
                if OTM > 0 and RM / OTM < 1.5:
                    _widen(use_pf=True)
                    continue

                # --- S.F. sliding >= 1.5 ---
                # When USE_KEY is on, skip sliding as a widen trigger here;
                # a post-convergence key check handles it after B is final.
                Tftg_ft = Tftg / 12.0
                friction = ss.W6 * ss.C9
                passive  = ss.P4 * Tftg_ft * ss.B
                lateral  = ss.P3
                if lateral > 0 and (friction + passive) / lateral < 1.5 and not ss.USE_KEY:
                    _widen(use_pf=True)
                    continue

                # --- Max soil bearing <= allowable ---
                ss.E1 = abs(ss.B / 2.0 - ss.X)
                if ss.KERN_MODE == 1 and ss.E1 > ss.B / 6.0:
                    contact = 3.0 * ss.X if ss.X < ss.B / 2.0 else 3.0 * (ss.B - ss.X)
                    S_max = 2.0 * ss.W6 / contact if contact > 0 else 9999
                else:
                    S_max = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
                if S_max > ss.S2:
                    _widen(use_pf=True)
                    continue

            # all checks passed
            break

        # --------------------------------------------------
        # Post-convergence sliding check with shear key.
        # B is now final (driven only by OT, kern, soil bearing).
        # If USE_KEY is on and sliding still fails, add a 12-in key.
        # Key passive = P4 * Hk (1 ft deep = 12 in default).
        # --------------------------------------------------
        if ss.USE_KEY:
            Tftg_ft  = Tftg / 12.0
            friction = ss.W6 * ss.C9
            passive  = ss.P4 * Tftg_ft * ss.B
            lateral  = ss.P3
            if lateral > 0 and (friction + passive) / lateral < 1.5:
                KEY_DEPTH_IN = 12.0          # fixed 12-inch key
                ss.KEY_Hk    = KEY_DEPTH_IN / 12.0   # store as ft
                key_passive  = ss.P4 * ss.KEY_Hk
                if (friction + passive + key_passive) / lateral >= 1.5:
                    ss.KEY_used = True
                else:
                    # Key alone not enough — note it but still NG
                    ss.KEY_used = True   # report the attempt; output will show NG

        break

# ------------------------------------------------------------
# gosub_1400 — FOOTING SUMMARY
# FIX: Tftg_ft now always T[G]/12.0 (removed incorrect guard).
#      Added Pf_applied note to clarify whether Pf was used.
# ------------------------------------------------------------
def gosub_1400():
    ss = st.session_state

    kern_label = "ALLOW OUTSIDE KERN" if ss.KERN_MODE == 1 else "FORCE INSIDE KERN"
    print()
    if ss.T1 == 1:
        print(f"    TYPE 1: X measured from HEEL edge")
    else:
        print(f"    ECCENTRICITY MODE : {kern_label}")
    print(f"    FTG. WIDTH  = {ss.B:.2f}{ss.P2}")
    print(f"    FTG.  T     = {ss.Tftg:.2f}{ss.P1}")
    print(f"    X           = {ss.X:.2f}{ss.P2}  ({'from HEEL' if ss.T1==1 else 'from TOE'})")

    ss.E1 = abs(ss.B / 2.0 - ss.X)

    if ss.T1 == 1:
        # X from HEEL; X_toe from TOE
        X_toe = ss.B - ss.X
        kern_status = "WITHIN KERN" if ss.E1 <= ss.B / 6.0 else "OUTSIDE KERN"
        kern_mode_label = "FORCE INSIDE KERN" if ss.KERN_MODE == 2 else "ALLOW OUTSIDE KERN"
        print(f"    ECCENTRICITY MODE : {kern_mode_label}")
        print(f"    X from HEEL = {ss.X:.2f}{ss.P2},  X from TOE = {X_toe:.2f}{ss.P2}")
        print(f"    ECCENTRICITY (E1) = {ss.E1:.2f}{ss.P2}  "
              f"(B/6 = {ss.B/6:.2f}{ss.P2})  ** {kern_status} **")
        if ss.E1 > ss.B / 6.0:
            contact = 3.0 * X_toe if X_toe > 0 else 0.001
            S_max = 2.0 * ss.W6 / contact
            S_min = 0.0
            sb_flag = "  ** OK **" if S_max <= ss.S2 else f"  ** NG — EXCEEDS {ss.S2:.0f} PSF **"
            print(f"    ** TRIANGULAR BEARING (outside kern) **")
            print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}", sb_flag)
            print(f"    SOIL BEAR'G MIN =   0.00{ss.P3s}  (tension — footing lifts)")
        else:
            S_max = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
            S_min = (ss.W6 / ss.B) * (1.0 - 6.0 * ss.E1 / ss.B)
            sb_flag = "  ** OK **" if S_max <= ss.S2 else f"  ** NG — EXCEEDS {ss.S2:.0f} PSF **"
            print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}", sb_flag)
            print(f"    SOIL BEAR'G MIN = {S_min:.2f}{ss.P3s}")
        print(f"    SOIL BEAR'G ALL = {ss.S2:.2f}{ss.P3s}")
        # OT S.F. about TOE — explicit arm-to-TOE per item
        RM_toe  = ss._RM_toe
        OTM_toe = ss._OTM_toe
        if OTM_toe > 0:
            SF_OT = RM_toe / OTM_toe
            ot_flag = "  ** OK **" if SF_OT >= 1.5 else "  ** NG — S.F. < 1.5 **"
            print(f"    --- OVERTURNING CHECK ABOUT TOE ---")
            # Recompute per-item for display
            RM_wall=0; RM_step=0
            H3=ss.H2
            for i in range(1, ss.G+1):
                if i==ss.G: H3=ss.H1-ss.H2*(ss.G-1)
                Ti=ss.T[i]
                Ww=(12.5 if ss.C[i]==1 else 77.0/8.0)*Ti*H3
                RM_wall+=Ww*(ss.E/12.0+Ti/24.0)
                step_w=(ss.T[ss.G]-Ti)/12.0
                Ws=100.0*H3*step_w
                RM_step+=Ws*((ss.E+Ti)/12.0+step_w/2.0)
            RM_ftg  = ss.W2*ss.B/2.0
            W_E     = 100.0*(ss.E/12.0)*ss.H1
            RM_E    = W_E*(ss.L/12.0+ss.E/24.0)
            RM_Pf   = ss.Pf*ss.B
            print(f"    WALL  (arm=E/12+T/24):  M = {RM_wall:.2f} (FT-LB)")
            print(f"    FTG.  (arm=B/2):         M = {RM_ftg:.2f} (FT-LB)")
            print(f"    EARTH E-strip (arm={ss.L/12.0:.3f}+{ss.E/24.0:.3f}={ss.L/12.0+ss.E/24.0:.3f}ft): M = {RM_E:.2f} (FT-LB)")
            print(f"    EARTH step (arm=(E+T)/12+step/2): M = {RM_step:.2f} (FT-LB)")
            print(f"    Pf=P3/3 (arm=B={ss.B:.3f}ft): M = {RM_Pf:.2f} (FT-LB)")
            print(f"    RM  (about TOE) = {RM_toe:.2f} (FT-LB)")
            print(f"    OTM (about TOE) = P3 x H4/3 = {ss.P3:.2f} x {ss.H4/3.0:.3f} = {OTM_toe:.2f} (FT-LB)")
            print(f"    OT S.F. = {RM_toe:.2f}/{OTM_toe:.2f} = {SF_OT:.2f}", ot_flag)
        # Sliding
        Tftg_ft = ss.Tftg / 12.0
        friction = ss.W6 * ss.C9
        passive  = ss.P4 * Tftg_ft * ss.B
        lateral  = ss.P3
        if lateral > 0:
            key_passive = ss.P4 * ss.KEY_Hk if ss.KEY_used else 0.0
            total_resist = friction + passive + key_passive
            SF_SL = total_resist / lateral
            sl_flag = "  ** OK **" if SF_SL >= 1.5 else "  ** NG — S.F. < 1.5 **"
            print(f"    BASE FRIC.  = W6 x C9       = {ss.W6:.2f} x {ss.C9:.2f} = {friction:.2f} (LB)")
            print(f"    PASSIVE RES = P4 x Tftg x B = {ss.P4:.0f} x {Tftg_ft:.2f} x {ss.B:.2f} = {passive:.2f} (LB)")
            if ss.KEY_used:
                print(f"    KEY PASSIVE = P4 x Hk       = {ss.P4:.0f} x {ss.KEY_Hk:.2f} = {key_passive:.2f} (LB)  ** SHEAR KEY **")
                print(f"    KEY DEPTH   = {ss.KEY_Hk*12:.0f} IN below bottom of footing")
            print(f"    LATERAL     = P3             = {lateral:.2f} (LB)")
            if ss.KEY_used:
                print(f"    SL S.F. = (FRIC+PASSIVE+KEY)/LAT = ({friction:.2f}+{passive:.2f}+{key_passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
            else:
                print(f"    SL S.F. = ({friction:.2f}+{passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
        return

    kern_label2 = "B/3" if ss.KERN_MODE == 2 else "B/6"
    kern_limit  = ss.B / 3.0 if ss.KERN_MODE == 2 else ss.B / 6.0

    print(f"    BACK-FACE FRICTION (Pf={ss.Pf:.2f} lb) : APPLIED (always)")

    if ss.KERN_MODE == 1 and ss.E1 > ss.B / 6.0:
        contact = 3.0 * ss.X if ss.X < ss.B / 2.0 else 3.0 * (ss.B - ss.X)
        S_max = 2.0 * ss.W6 / contact if contact > 0 else 9999
        S_min = 0.0
        sb_flag = "  ** OK **" if S_max <= ss.S2 else f"  ** NG — EXCEEDS ALLOWABLE {ss.S2:.0f} PSF **"
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}", sb_flag)
        print(f"    SOIL BEAR'G MIN =   0.00{ss.P3s}  (tension — footing lifts)")
        print(f"    SOIL BEAR'G ALL = {ss.S2:.2f}{ss.P3s}")
        print(f"    ECCENTRICITY    = {ss.E1:.2f}{ss.P2}  ({kern_label2} = {kern_limit:.2f}{ss.P2})  ** OUTSIDE KERN **")
    else:
        S_max = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
        S_min = (ss.W6 / ss.B) * (1.0 - 6.0 * ss.E1 / ss.B)
        sb_flag = "  ** OK **" if S_max <= ss.S2 else f"  ** NG — EXCEEDS ALLOWABLE {ss.S2:.0f} PSF **"
        kern_status = "WITHIN KERN" if ss.E1 <= ss.B / 6.0 else "OUTSIDE KERN"
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}", sb_flag)
        print(f"    SOIL BEAR'G MIN = {S_min:.2f}{ss.P3s}")
        print(f"    SOIL BEAR'G ALL = {ss.S2:.2f}{ss.P3s}")
        print(f"    ECCENTRICITY    = {ss.E1:.2f}{ss.P2}  ({kern_label2} = {kern_limit:.2f}{ss.P2})  ** {kern_status} **")

    OTM = ss.M4
    RM  = ss.M6 + ss.M4
    if OTM > 0:
        SF_OT = RM / OTM
        ot_flag = "  ** OK **" if SF_OT >= 1.5 else "  ** NG — S.F. < 1.5 **"
        print(f"    RESIST. MOM (RM)  = {RM:.2f} (FT-LB)")
        print(f"    OVERTURN MOM (OTM)= {OTM:.2f} (FT-LB)")
        print(f"    OT S.F. = RM/OTM = {RM:.2f}/{OTM:.2f} = {SF_OT:.2f}", ot_flag)
    else:
        print("    OT S.F. = N/A")

    # Use stored Tftg (enforced minimum 12 in) for sliding resistance
    Tftg_ft  = ss.Tftg / 12.0
    friction  = ss.W6 * ss.C9
    passive   = ss.P4 * Tftg_ft * ss.B
    lateral   = ss.P3
    if lateral > 0:
        key_passive = ss.P4 * ss.KEY_Hk if ss.KEY_used else 0.0
        total_resist = friction + passive + key_passive
        SF_SL = total_resist / lateral
        sl_flag = "  ** OK **" if SF_SL >= 1.5 else "  ** NG — S.F. < 1.5 **"
        print(f"    BASE FRIC.  = W6 x C9       = {ss.W6:.2f} x {ss.C9:.2f} = {friction:.2f} (LB)")
        print(f"    PASSIVE RES = P4 x Tftg x B = {ss.P4:.0f} x {Tftg_ft:.2f} x {ss.B:.2f} = {passive:.2f} (LB)")
        if ss.KEY_used:
            print(f"    KEY PASSIVE = P4 x Hk       = {ss.P4:.0f} x {ss.KEY_Hk:.2f} = {key_passive:.2f} (LB)  ** SHEAR KEY **")
            print(f"    KEY DEPTH   = {ss.KEY_Hk*12:.0f} IN below bottom of footing")
        print(f"    LATERAL     = P3             = {lateral:.2f} (LB)")
        if ss.KEY_used:
            print(f"    SL S.F. = (FRIC+PASSIVE+KEY)/LAT = ({friction:.2f}+{passive:.2f}+{key_passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
        else:
            print(f"    SL S.F. = (BASE FRIC.+PASSIVE)/LATERAL = ({friction:.2f}+{passive:.2f})/{lateral:.2f} = {SF_SL:.2f}", sl_flag)
    else:
        print("    SL S.F. = N/A")

# ------------------------------------------------------------
# gosub_1610 — MOMENT BREAKDOWN
# ------------------------------------------------------------
def gosub_1610():
    ss = st.session_state
    pf_label = f"Pf={ss.Pf:.2f} lb APPLIED (always)"
    print("    ITEMS          W           M      NOTES")
    print(f"    WALL       {ss.W1:10.2f}  {ss.M1:10.2f}")
    print(f"    FTG.       {ss.W2:10.2f}  {ss.M2:10.2f}")
    print(f"    HEEL EARTH {ss.W5:10.2f}  {ss.M5:10.2f}")
    print(f"    BACK FRIC. {ss.Pf if ss.Pf_applied else 0.0:10.2f}  {ss.Mpf:10.2f}  {pf_label} (arm={ss.L/12:.2f} ft)")
    print(f"    HEEL SOIL2 {ss.W7:10.2f}  {ss.M7:10.2f}")
    print(f"    HEEL SOIL3 {ss.W8:10.2f}  {ss.M8:10.2f}")
    print(f"    O.T.M.     {'---':>10}  {ss.M4:10.2f}  lateral earth OTM (subtracted from M6)")
    print(f"    TOTAL      {ss.W6:10.2f}  {ss.M6:10.2f}")
    print(f"    P3 (horiz) {ss.P3:10.2f}  {'(lateral)':>10}  earth pressure resultant (not in W)")
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
