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

# ------------------------------------------------------------
# Helper: initialize a variable in session_state if missing
# ------------------------------------------------------------
def init(name, value):
    if name not in st.session_state:
        st.session_state[name] = value

# ------------------------------------------------------------
# Initialize ALL global variables exactly as original program
# ------------------------------------------------------------
def initialize_globals():

    # Arrays
    init("T", [0.0] * 61)
    init("D", [0.0] * 5)
    init("C", [0.0] * 61)
    init("A", [0.0] * 8)

    # Scalars
    names_defaults = {
        "P1": "", "P2": "", "P3s": "", "P4s": "", "P5s": "",
        "H": 0.0, "H1": 0.0, "H2": 0.0, "H3": 0.0, "H4": 0.0,
        "L": 0.0, "L1": 0.0, "L2": 0.0,
        "P": 0.0, "P4": 0.0, "S1": 0.0, "S2": 0.0, "C9": 0.0,
        "Y": 0.0, "C1": 0, "Cw": 0, "T1": 0,
        "Dval": 0.0, "F": 0.0, "F1": 0.0, "F2": 0.0,
        "N1": 0, "N2": 0, "G": 0,
        "W1": 0.0, "W2": 0.0, "W3": 0.0, "W4": 0.0,
        "W5": 0.0, "W6": 0.0, "W7": 0.0, "W8": 0.0,
        "M1": 0.0, "M2": 0.0, "M3": 0.0, "M4": 0.0,
        "M5": 0.0, "M6": 0.0, "M7": 0.0, "M8": 0.0,
        "X": 0.0, "S": 0.0, "E": 0.0, "E1": 0.0,
        "E2": 0, "K1": 0, "Areq": 0.0, "A2": 0.0,
        "P1s": 0.0, "K": 0.0, "J": 0.0,
        "A1": 0.0, "S9": 0.0, "D9": 0,
        "R": "", "P3": 0.0, "P9": 0.0, "X9": 0.0,
        "B": 0.0, "M": 0.0, "I1": 0, "I2": 0,
        "TABLE_ROWS": [],
        "KERN_MODE": 1,
    }

    for name, value in names_defaults.items():
        init(name, value)

# ------------------------------------------------------------
# Initialize block sizes and rebar areas
# ------------------------------------------------------------
def initialize_block_and_rebar():
    ss = st.session_state

    ss.D[1] = 5.5
    ss.D[2] = 9.5
    ss.D[3] = 13.5
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

# ------------------------------------------------------------
# One-time initialization guard
# ------------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    initialize_globals()
    initialize_block_and_rebar()
    st.session_state.initialized = True

# ------------------------------------------------------------
# FIX D: Output buffering — persists across reruns via
# session_state. print() appends to output_log; the display
# block at the bottom renders the full log on every rerun.
# Original code used st.text() directly inside button handlers
# which caused output to vanish on the very next rerun.
# ------------------------------------------------------------
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
# gosub_140 — INPUT BLOCK (Streamlit sidebar)
#
# FIX 1: Called unconditionally at top level (not inside a
#         button block) so widgets always render on every rerun.
#
# FIX A: KERN_MODE selectbox index derived from current value
#         instead of hardcoded 0 — preserves user's choice.
#
# FIX B: All selectboxes derive their index from current
#         session_state so nothing resets on rerun:
#         - TYPE OF WALL index from ss.T1
#         - CONT. INSPECTION index from ss.N1
#         - 12-IN BLOCK: sets D[2]=9.5 or 0.0 from selectbox
#         - 16-IN BLOCK: sets D[3]=13.5 or 0.0 from selectbox
#         - WALL T widget reflects current ss.Dval
#         - WALL HEIGHT INCREMENT reflects current ss.H2
# ------------------------------------------------------------
def gosub_140():
    ss = st.session_state

    with st.sidebar:
        st.header("Input Parameters")

        # TYPE OF WALL — derive index from current T1 value
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
            # FIX B: derive inspection index from current N1
            cur_insp = 1 if ss.N1 == 20 else 0
            I = st.selectbox("CONT. INSPECTION (0 OR 1)", [0, 1], index=cur_insp)
            if I == 1:
                ss.N1 = 20
                ss.F1 = 500.0
            else:
                ss.N1 = 40
                ss.F1 = 333.0

            # FIX B: set D[2] explicitly from selectbox — never zero blindly
            cur_12 = 1 if ss.D[2] != 0.0 else 0
            I = st.selectbox("12-IN BLOCK (0 OR 1)", [0, 1], index=cur_12)
            ss.D[2] = 9.5 if I == 1 else 0.0

            # FIX B: same for D[3]
            cur_16 = 1 if ss.D[3] != 0.0 else 0
            I = st.selectbox("16-IN BLOCK (0 OR 1)", [0, 1], index=cur_16)
            ss.D[3] = 13.5 if I == 1 else 0.0

        else:
            ss.F  = st.number_input("CONCRETE F'C (PSI)", value=ss.F if ss.F else 2000.0)
            ss.F2 = 0.45 * ss.F
            ss.N2 = int(29000 / (57 * (ss.F ** 0.5)))
            # FIX B: reflect current Dval back into widget
            wall_t_default = (ss.Dval + 2.5) if ss.Dval else 8.0
            I = st.number_input("WALL T (IN)", value=wall_t_default)
            ss.Dval = I - 2.5

        ss.Y  = st.number_input("STEEL ALLOWABLE (KSI)", value=ss.Y if ss.Y else 20.0)
        ss.C1 = st.selectbox("SLAB ON GRADE (0 OR 1)", [0, 1], index=ss.C1)

        # FIX B: reflect current H2 back into widget
        H2_in_default = (ss.H2 * 12.0) if ss.H2 else 96.0
        H2_in = st.number_input("WALL HEIGHT INCREMENT (IN)", value=H2_in_default)
        ss.H2 = H2_in / 12.0

        ss.E = st.number_input("TOE (IN)", value=ss.E)

        # FIX A: derive index from current KERN_MODE — preserves user choice
        kern_index = 0 if ss.KERN_MODE == 1 else 1
        kern_sel = st.selectbox(
            "ECCENTRICITY MODE",
            ["ALLOW OUTSIDE KERN (1)", "FORCE INSIDE KERN (2)"],
            index=kern_index
        )
        ss.KERN_MODE = 1 if kern_sel.startswith("ALLOW") else 2

# ------------------------------------------------------------
# gosub_5000 — placeholder
# ------------------------------------------------------------
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
# gosub_print_header — prints design parameters + table header
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
        print(f"    TOE                    = {ss.E:8.2f}{ss.P1}")
    print(f"    ALLOWABLE SOIL BEARING = {ss.S2:8.2f}{ss.P3s}")
    print(f"    ALLOWABLE STL. STRESS  = {ss.Y:8.2f} (KSI)")

    kern_label = "ALLOW OUTSIDE KERN" if ss.KERN_MODE == 1 else "FORCE INSIDE KERN"
    print(f"    ECCENTRICITY MODE      : {kern_label}")
    print()

    gosub_790()

# ------------------------------------------------------------
# gosub_1210 — "More Print" (KEY-1)
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
        print(f"    TOE                    = {ss.E:8.2f}{ss.P1}")
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
# gosub_510 — STEEL AREA CALC (with protection)
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
#
# FIX C: masonry-to-concrete fallback block originally wrote
# ss.Cw=1, ss.F2=900, ss.N2=11 directly, permanently corrupting
# the user's wall-type selection for all subsequent reruns.
# Fix: save and restore Cw/F2/N2 around the fallback block.
# ------------------------------------------------------------
def gosub_360():
    ss = st.session_state

    ss.H = 0.0
    I = 1
    ss.G = 0
    MAX_DVAL = 30.0

    while True:
        ss.H = ss.H + ss.H2
        if ss.H >= ss.H1:
            ss.H = ss.H1

        ss.M = ss.S1 * ss.P * ss.H * ss.H / 2.0 + ss.P * ss.H ** 3 / 6.0

        if ss.Cw == 1:
            found = False
            while ss.Dval <= MAX_DVAL:
                gosub_510()
                if ss.K1 == 1:
                    found = True
                    break
                ss.I1 = 7
                gosub_620()
                if ss.K1 == 1:
                    found = True
                    break
                ss.Dval += 1.0

            if not found:
                print(f"  WARNING: No valid concrete section found at H={ss.H:.2f} ft")

            if ss.H >= ss.H1 - 0.01:
                break

        else:
            if I > 4 or ss.D[I] == 0:
                prev_I = max(1, I - 1)
                # FIX C: save user wall-type before running concrete fallback
                save_Cw, save_F2, save_N2, save_Dval = ss.Cw, ss.F2, ss.N2, ss.Dval
                ss.Dval = ss.D[prev_I] if ss.D[prev_I] != 0 else 5.5
                ss.Cw   = 1
                ss.F2   = 900.0
                ss.N2   = 11
                found = False
                while ss.Dval <= MAX_DVAL:
                    gosub_510()
                    if ss.K1 == 1:
                        found = True
                        break
                    ss.I1 = 7
                    gosub_620()
                    if ss.K1 == 1:
                        found = True
                        break
                    ss.Dval += 1.0

                if not found:
                    print(f"  WARNING: No valid section found at H={ss.H:.2f} ft")

                # FIX C: always restore user's wall type
                # Keep found Dval if successful; restore old Dval if not
                ss.Cw = save_Cw
                ss.F2 = save_F2
                ss.N2 = save_N2
                if not found:
                    ss.Dval = save_Dval

                if ss.H >= ss.H1 - 0.01:
                    break

            else:
                ss.Dval = ss.D[I]
                gosub_510()
                if ss.K1 == 1:
                    if ss.H >= ss.H1 - 0.01:
                        break
                    continue
                ss.I1 = 7
                gosub_620()
                if ss.K1 == 1:
                    if ss.H >= ss.H1 - 0.01:
                        break
                    continue
                I += 1
                if I > 4:
                    print(f"  WARNING: Exhausted all block sizes at H={ss.H:.2f} ft")
                    if ss.H >= ss.H1 - 0.01:
                        break
                continue

# ------------------------------------------------------------
# gosub_1205 — EARTH PRESSURE BLOCK
# ------------------------------------------------------------
def gosub_1205():
    ss = st.session_state
    ss.P3 = (ss.S1 * ss.P * ss.H4 + ss.P * ss.H4 * ss.H4 / 2.0) / 3.0
    ss.M4 = ss.S1 * ss.P * ss.H4 * ss.H4 / 2.0 + ss.P * ss.H4 ** 3 / 6.0

# ------------------------------------------------------------
# gosub_830 — FOOTING DESIGN
# ------------------------------------------------------------
def gosub_830():
    ss = st.session_state

    first_pass = True
    while True:
        if ss.T[ss.G] < 12:
            Tftg = 12.0
        else:
            Tftg = ss.T[ss.G]

        H3 = ss.H2
        ss.W1 = ss.W5 = ss.M1 = ss.M5 = 0.0

        if ss.T1 == 1:
            # P/3 arm = toe + bottom stem thickness - top stem thickness
            ss.L = ss.E + ss.T[ss.G] - ss.T[1]
        else:
            ss.L = ss.E

        for i in range(1, ss.G + 1):
            if i == ss.G:
                H3 = ss.H1 - ss.H2 * (ss.G - 1)

            if ss.C[i] == 1:
                W = 12.5 * ss.T[i] * H3
            else:
                W = 77.0 / 8.0 * ss.T[i] * H3
            ss.W1 += W

            if ss.T1 == 1:
                ss.M1 += W * (ss.L - ss.T[i] / 2.0) / 12.0
            else:
                ss.M1 += W * (ss.L + ss.T[i] / 2.0) / 12.0

            if ss.T1 == 1:
                W  = H3 * (ss.L - ss.T[i]) / 0.12
                Mw = W * (ss.L - ss.T[i]) / 24.0
            elif ss.T1 == 2:
                W  = ss.L * H3 / 0.12
                Mw = W * ss.L / 24.0
            else:
                W  = (Tftg - ss.T[i]) * H3 / 0.12
                Mw = W * (ss.L + ss.T[i] + (Tftg - ss.T[i]) / 2.0) / 12.0

            ss.W5 += W
            ss.M5 += Mw

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

        if ss.T1 != 4:
            ss.M3 = ss.P3 * (ss.L / 12.0)
            ss.W6 = ss.W1 + ss.W2 + ss.W5 + ss.P3
            ss.M6 = ss.M1 + ss.M2 + ss.M3 + ss.M4 + ss.M5
        else:
            ss.L1 = ss.B - ss.L / 12.0 - Tftg / 12.0
            ss.W7 = ss.L1 * ss.H1 * 100.0
            ss.M7 = ss.W7 * (ss.L1 / 2.0 + ss.L / 12.0 + Tftg / 12.0)
            M3_local = ss.P3 * (ss.L / 12.0)
            ss.M3 = M3_local
            ss.W6 = ss.W1 + ss.W2 + ss.W5 + ss.P3 + ss.W7 + ss.W8
            ss.M6 = ss.M1 + ss.M2 + M3_local + ss.M5 + ss.M7 + ss.M8 - ss.M4

        def _recalc_totals():
            """Recompute W2/M2/W6/M6 after B changes."""
            ss.W2 = 12.5 * Tftg * ss.B
            ss.M2 = ss.W2 * ss.B / 2.0
            if ss.T1 != 4:
                ss.M3 = ss.P3 * (ss.L / 12.0)
                ss.W6 = ss.W1 + ss.W2 + ss.W5 + ss.P3
                ss.M6 = ss.M1 + ss.M2 + ss.M3 + ss.M4 + ss.M5
            else:
                ss.L1 = ss.B - ss.L / 12.0 - Tftg / 12.0
                ss.W7 = ss.L1 * ss.H1 * 100.0
                ss.M7 = ss.W7 * (ss.L1 / 2.0 + ss.L / 12.0 + Tftg / 12.0)
                M3_loc = ss.P3 * (ss.L / 12.0)
                ss.M3 = M3_loc
                ss.W6 = ss.W1 + ss.W2 + ss.W5 + ss.P3 + ss.W7 + ss.W8
                ss.M6 = ss.M1 + ss.M2 + M3_loc + ss.M5 + ss.M7 + ss.M8 - ss.M4

        def _widen():
            ss.B = int(12 * ss.B + 2) / 12.0
            _recalc_totals()

        _recalc_totals()

        while True:
            ss.X = ss.M6 / ss.W6 if ss.W6 != 0 else 0

            # --- eccentricity / kern check ---
            if ss.KERN_MODE == 1:
                if ss.X <= 0 or ss.X >= ss.B:
                    _widen(); continue
            else:
                if ss.X < ss.B / 3.0 or ss.X > 2 * ss.B / 3.0:
                    _widen(); continue

            # --- S.F. overturning >= 1.5 ---
            OTM = ss.M4
            RM  = ss.M6 - OTM
            if OTM > 0 and RM / OTM < 1.5:
                _widen(); continue

            # --- S.F. sliding >= 1.5 ---
            # Lateral force = P3 (resultant earth pressure, already in lbs)
            # Resistance    = friction (W6 * C9) + passive (P4 * Tftg_ft * B)
            Tftg_ft = Tftg / 12.0
            friction  = ss.W6 * ss.C9
            passive   = ss.P4 * Tftg_ft * ss.B
            lateral   = ss.P3
            if lateral > 0 and (friction + passive) / lateral < 1.5:
                _widen(); continue

            # all checks passed
            break

        break

# ------------------------------------------------------------
# gosub_1400 — FOOTING SUMMARY
# ------------------------------------------------------------
def gosub_1400():
    ss = st.session_state

    kern_label = "ALLOW OUTSIDE KERN" if ss.KERN_MODE == 1 else "FORCE INSIDE KERN"
    print()
    print(f"    ECCENTRICITY MODE : {kern_label}")
    print(f"    FTG. WIDTH  = {ss.B:.2f}{ss.P2}")
    print(f"    FTG.  T     = {ss.T[ss.G]:.2f}{ss.P1}")
    print(f"    X           = {ss.X:.2f}{ss.P2}")

    ss.E1 = abs(ss.B / 2.0 - ss.X)

    if ss.E1 > ss.B / 6.0:
        contact = 3.0 * ss.X if ss.X < ss.B / 2.0 else 3.0 * (ss.B - ss.X)
        S_max = 2.0 * ss.W6 / contact
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}")
        print(f"    SOIL BEAR'G MIN =   0.00{ss.P3s}")
        print(f"    ECCENTRICITY    = {ss.E1:.2f}{ss.P2}  (B/6 = {ss.B/6:.2f}{ss.P2})  ** OUTSIDE KERN **")
    else:
        S_max = (ss.W6 / ss.B) * (1.0 + 6.0 * ss.E1 / ss.B)
        S_min = (ss.W6 / ss.B) * (1.0 - 6.0 * ss.E1 / ss.B)
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{ss.P3s}")
        print(f"    SOIL BEAR'G MIN = {S_min:.2f}{ss.P3s}")
        print(f"    ECCENTRICITY    = {ss.E1:.2f}{ss.P2}  (B/6 = {ss.B/6:.2f}{ss.P2})  ** WITHIN KERN **")

    OTM = ss.M4
    RM  = ss.M6 - ss.M4
    if OTM > 0:
        SF_OT = RM / OTM
        print(f"    RESIST. MOM = {RM:.2f} (FT-LB)")
        print(f"    OVERTURN MOM= {OTM:.2f} (FT-LB)")
        print(f"    S.F. OVERT. = {SF_OT:.2f}", "  ** OK **" if SF_OT >= 1.5 else "  ** NG — S.F. < 1.5 **")
    else:
        print("    S.F. OVERT. = N/A")

    # S.F. sliding
    Tftg_ft  = ss.T[ss.G] / 12.0 if ss.T[ss.G] >= 12 else 1.0
    friction  = ss.W6 * ss.C9
    passive   = ss.P4 * Tftg_ft * ss.B
    lateral   = ss.P3
    if lateral > 0:
        SF_SL = (friction + passive) / lateral
        print(f"    FRICTION RES= {friction:.2f} (LB)")
        print(f"    PASSIVE RES = {passive:.2f} (LB)")
        print(f"    LATERAL     = {lateral:.2f} (LB)")
        print(f"    S.F. SLIDE  = {SF_SL:.2f}", "  ** OK **" if SF_SL >= 1.5 else "  ** NG — S.F. < 1.5 **")
    else:
        print("    S.F. SLIDE  = N/A")

# ------------------------------------------------------------
# gosub_1610 — MOMENT BREAKDOWN
# ------------------------------------------------------------
def gosub_1610():
    ss = st.session_state

    print("    ITEMS        W           M")
    print(f"    WALL     {ss.W1:10.2f}  {ss.M1:10.2f}")
    print(f"    FTG.     {ss.W2:10.2f}  {ss.M2:10.2f}")
    print(f"    P/3      {ss.P3:10.2f}  {ss.M3:10.2f}  (arm={ss.L:.2f}in = toe+bot.stem-top.stem)")
    print(f"    EARTH    {ss.W5:10.2f}  {ss.M5:10.2f}")
    print(f"    EARTH2   {ss.W7:10.2f}  {ss.M7:10.2f}")
    print(f"    EARTH3   {ss.W8:10.2f}  {ss.M8:10.2f}")
    print(f"    O.T.M.   {'---':>10}  {ss.M4:10.2f}")
    print(f"    TOTAL    {ss.W6:10.2f}  {ss.M6:10.2f}")
    print()

# ------------------------------------------------------------
# gosub_1700 — POINT LOAD CHECK
#
# FIX E: Original rendered P9/X9 inputs inside this function
# via st.sidebar.number_input — those widgets disappeared on
# every rerun since the function only ran on button click.
# Fix: P9/X9 inputs moved to always-visible sidebar section
# (controlled by a checkbox). This function now only calculates.
# ------------------------------------------------------------
def gosub_1700():
    ss = st.session_state

    if ss.B == 0:
        print("    ERROR: B = 0. Run Footing Design first.")
        return

    B_trial = ss.B
    Q1 = ss.W1 + B_trial * 150 + ss.P3 + ss.W4 + ss.W5 + ss.W7 + ss.W8 + ss.P9
    Q2 = ss.M1 + B_trial * 150 * B_trial / 2 + ss.M3 + ss.M4 + ss.M5 + ss.M7 + ss.M8 + ss.P9 * ss.X9

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
        SP_max = 2.0 * Q1 / contact
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
    RM_t  = Q2 - ss.M4
    if OTM_t > 0:
        SF_t = RM_t / OTM_t
        print(f"    RESIST. MOM = {RM_t:.2f} (FT-LB)")
        print(f"    OVERTURN MOM= {OTM_t:.2f} (FT-LB)")
        print(f"    S.F. OVERT. = {SF_t:.2f}", "  ** OK **" if SF_t >= 1.5 else "  ** NG — S.F. < 1.5 **")
    else:
        print("    S.F. OVERT. = N/A")

# ============================================================
# MAIN PAGE LAYOUT
# ============================================================

st.title("Retaining Wall Program — Streamlit Version")

# FIX 1: Always render sidebar inputs — not inside a button block
gosub_140()

# FIX E: Point Load inputs always visible when checkbox enabled.
# Checkbox state in session_state so it survives reruns.
# P9/X9 use key-only pattern — NO value= override.
# Passing value= resets the field to ss.P9/ss.X9 on every rerun
# (the door closes again as soon as the user types anything).
# We initialise the keyed slots once, then Streamlit owns them.
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
        st.subheader("Point Load Check (KEY‑ 3)")
        # key= only, no value= — widget retains whatever user typed
        st.number_input("P (LB)",  step=1.0, format="%g", key="pl_P9")
        st.number_input("X9 (FT)", step=0.1, format="%g", key="pl_X9")

# Always sync ss.P9/ss.X9 from keyed widgets so gosub_1700 reads
# the current typed values no matter when the button is clicked.
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

# FIX D: Persistent output — always rendered, survives every rerun
if st.session_state.output_log:
    st.markdown("---")
    st.subheader("Output")
    st.text("".join(st.session_state.output_log))

# ------------------------------------------------------------
# SAFE RESET BUTTON
# ------------------------------------------------------------
st.markdown("---")

if st.button("🔄 Reset All Inputs"):
    keys_to_clear = [
        "T","D","C","A","P1","P2","P3s","P4s","P5s","H","H1","H2","H3","H4",
        "L","L1","L2","P","P4","S1","S2","C9","Y","C1","Cw","T1","Dval","F",
        "F1","F2","N1","N2","G","W1","W2","W3","W4","W5","W6","W7","W8",
        "M1","M2","M3","M4","M5","M6","M7","M8","X","S","E","E1","E2","K1",
        "Areq","A2","P1s","K","J","A1","S9","D9","R","P3","P9","X9","B","M",
        "I1","I2","TABLE_ROWS","KERN_MODE","output_log","initialized",
        "pl_P9","pl_X9","show_ptload"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    initialize_globals()
    initialize_block_and_rebar()
    st.session_state.initialized = True
    st.session_state.output_log = []
    st.rerun()
