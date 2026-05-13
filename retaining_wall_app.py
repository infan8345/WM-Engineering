# =============================================================================
# RETAINING WALL PROGRAM  (original: 2-14-85)
# Python conversion — fully corrected  Rev-4
# =============================================================================
#
# BUGS FIXED (Rev-4 adds fix 19):
#
#  1.  S1 (surcharge) defaults to 0.0 on empty Enter.
#  2.  C1 (slab on grade) defaults to 0 on empty Enter.
#  3.  Dval initialised to D[1] for masonry path.
#  4.  gosub_510: computed stress stored in Fc, never clobbers F (f'c).
#  5.  gosub_620: bar-selection loop rewritten (was inverted).
#  6.  gosub_670: bar+spacing selection restructured.
#  7.  gosub_1205: earth-pressure corrected.
#      P3 = P*S1*H4 + P*H4²/2         (total lateral force)
#      M4 = P*S1*H4²/2 + P*H4³/6       (OTM about toe — triangular: /6 not /3)
#      Note: some versions use /3 which is 2× too large.
#  8.  gosub_830: W1/M1 computed once; W5/M5 moved inside B-loop
#      (heel-soil weight depends on B).
#  9.  gosub_830: M6 = Σ(vertical moments) − M4  (net stabilising).
# 10.  gosub_830: W6 = vertical loads only; P3 is horizontal.
# 11.  gosub_1400: sliding uses P3 directly; key-depth formula corrected.
# 12.  gosub_360: masonry block-size index reset to 1 at each height.
# 13.  gosub_360: masonry→concrete fallback seeds Dval from largest block.
# 14.  Unit consistency: E and T[] in inches; ÷12 when feet needed.
# 15.  HEEL SOIL BUG (root cause of B=11.45 instead of 6.28):
#      Moment arm for T1=1 heel soil was heel_ft/2 (measured from heel edge).
#      Correct arm = L/12 + heel_ft/2 (measured from TOE).
#      Heel soil is ONE prism (height H1, width B−L/12), not per-increment.
#      W5/M5 moved inside B-iteration loop, computed once per B trial.
# 16.  INPUT RULE: all prompts show default; Enter = use default (=0 where
#      applicable).  "Enter = x = 0" means x defaults to 0 on blank Enter.
#
# 17.  Tftg (footing thickness) comment clarified.
#      Tftg = max(T[G], 12) in INCHES — T[G] is already inches.
#      Streamlit bug: using H1 (feet) as Tftg inches gives Tftg=10 for
#      H1=10 ft — structurally wrong and drives B grossly oversized.
#
# 18.  gosub_1205: M4 OTM formula corrected from P*H4³/3 to P*H4³/6.
#      Triangular resultant P*H4²/2 acts at H4/3 from base → OTM = P*H4³/6.
#      The /3 formula (introduced in Rev-2 Fix 7) was 2× too large, causing
#      the footing to be over-sized to resist a phantom overturning moment.
#      The original 1985 BASIC correctly used /6.
#
# =============================================================================

import math

# ---------------------------------------------------------------------------
# GLOBAL ARRAYS  (1-based; index 0 unused)
# ---------------------------------------------------------------------------
T  = [0.0] * 61   # wall thickness at each height increment (inches)
D  = [0.0] * 5    # masonry block net depths (inches)
C  = [0.0] * 61   # wall-type flag (0=masonry, 1=concrete)
A  = [0.0] * 8    # rebar areas per foot of wall (in²/ft)

# ---------------------------------------------------------------------------
# GLOBAL SCALARS
# ---------------------------------------------------------------------------
P1 = P2 = P3s = P4s = P5s = ""
H  = H1 = H2 = H3 = H4 = 0.0
L  = L1 = 0.0          # in inches
P  = P4 = S1 = S2 = C9 = 0.0
Y  = 0.0
C1 = 0
Cw = 0
T1 = 0
L2 = 0.0
Dval = 0.0
F  = F1 = F2 = 0.0
Fc = 0.0               # computed section stress (never clobbers F)
N1 = N2 = 0
G  = 0
W1 = W2 = W3 = W4 = W5 = W6 = W7 = W8 = 0.0
M1 = M2 = M3 = M4 = M5 = M6 = M7 = M8 = 0.0
X  = S = E = E1 = 0.0
K1 = 0
Areq = A2 = 0.0
P1s  = 0.0
K  = J  = 0.0
A1 = 0.0
S9 = 0.0
D9 = 0
P3 = 0.0
W_bf = 0.0   # back-friction vertical component (P3*tan_delta)
M_bf = 0.0   # back-friction stabilising moment
P9 = X9 = 0.0
B  = 0.0
M  = 0.0
I1 = 0
Tftg = 12.0
TABLE_ROWS = []
KERN_MODE  = 1    # 1=allow outside kern, 2=force inside kern


# =============================================================================
# HELPERS
# =============================================================================
def _inp(prompt, default):
    """Prompt with default shown; Enter returns default."""
    if isinstance(default, float) and default == 0.0:
        shown = "0"
    elif isinstance(default, int) and default == 0:
        shown = "0"
    else:
        shown = str(default)
    s = input(f"{prompt} [{shown}] ")
    if not s.strip():
        return default
    try:
        return type(default)(s)
    except ValueError:
        return type(default)(float(s))


# =============================================================================
# 1580  PROGRAM TITLE
# =============================================================================
def gosub_1580():
    print("\n\nRETAINING WALL PROGRAM")
    print("REV. 2-14-85  (Python — Rev-4 corrected)")


# =============================================================================
# 140  INPUT
# =============================================================================
def gosub_140():
    global T1, L2, H1, P, S2, C9, P4, S1, Cw, N1, F1, F, F2, N2
    global Dval, Y, C1, H2, E, D, KERN_MODE

    T1 = int(input("TYPE OF WALL (1, 2, 4) "))
    L2 = float(input("GROUND SLOPE (H:V)  (X:1) "))
    H1 = float(input("RETAINING WALL HT. (FT) "))

    P  = _inp("EQUIV. FLUID PRESSURE (#/CF)",  30.0)
    S2 = _inp("ALLOW. SOIL BEARING (PSF)",    1000.0)
    C9 = _inp("FRICTION COEFF",                 0.4)
    P4 = _inp("ALLOW. PASSIVE (PSF/FT)",        300.0)
    S1 = _inp("SURCHARGE (FT equiv) [Enter=x=0]", 0.0)  # FIX 1 / FIX 16

    Cw = int(input("CONC. WALL? (0=masonry  1=concrete) "))

    if Cw == 0:
        I = int(input("CONT. INSPECTION (0 OR 1) "))
        if I == 1:
            N1 = 20;  F1 = 500.0
        else:
            N1 = 40;  F1 = 250.0
        I = int(input("USE 12-IN BLOCK? (0 OR 1) "))
        if I != 1:
            D[2] = 0.0
        I = int(input("USE 16-IN BLOCK? (0 OR 1) "))
        if I != 1:
            D[3] = 0.0
        Dval = D[1]   # FIX 3

    else:
        F     = _inp("CONC. F'C (PSI)",  2000.0)
        F2    = 0.45 * F
        N2    = int(29000.0 / (57.0 * math.sqrt(F)))
        wall_T = _inp("WALL T (IN)", 8.0)
        Dval  = wall_T - 2.5

    Y  = _inp("STEEL ALLOWABLE (KSI)", 20.0)
    C1 = _inp("SLAB ON GRADE (0 OR 1) [Enter=0]", 0)    # FIX 2 / FIX 16
    H2 = _inp("WALL HT. INCREMENT (IN)", 8.0) / 12.0
    E  = _inp("TOE (IN) [Enter=x=0]", 0.0)               # FIX 14/16: stored in inches

    print("ECCENTRICITY MODE:")
    print("  1 = ALLOW E OUTSIDE KERN  (triangular pressure)")
    print("  2 = FORCE E INSIDE KERN   (footing sized until E <= B/6)")
    s = input("SELECT (1 OR 2)  [Enter=1] ")
    KERN_MODE = 2 if s.strip() == "2" else 1


# =============================================================================
# 510  STEEL AREA CALCULATION
# =============================================================================
def gosub_510():
    """FIX 4: stress stored in Fc, never in F."""
    global Areq, A2, P1s, K, J, Fc, K1
    global Cw, N1, N2, Dval, M, Y, F1, F2

    if Dval <= 0:
        K1 = 0
        return

    Areq = (M * 12.0) / (Y * (7.0 / 8.0) * Dval * 1000.0)
    A2   = Areq

    P1s  = (N1 if Cw == 0 else N2) * Areq / (12.0 * Dval)
    K    = math.sqrt(2.0 * P1s + P1s ** 2) - P1s
    J    = 1.0 - K / 3.0
    denom = K * J * Dval ** 2
    Fc   = (M * 2.0 / denom) if denom != 0 else 1e9   # FIX 4

    K1 = 0
    allowable = F1 if Cw == 0 else F2
    if Fc < allowable:
        gosub_670()
        K1 = 1


# =============================================================================
# 620  BAR SELECTION
# =============================================================================
def gosub_620():
    """FIX 5: find smallest bar whose area >= Areq."""
    global I1, Areq, K1

    for i in range(1, I1 + 1):
        if A[i] >= Areq * 0.98:
            Areq = A[i]
            gosub_510()
            return
    # No bar large enough; K1 stays 0


# =============================================================================
# 670  TABLE ROW PRINT
# =============================================================================
def gosub_670():
    """FIX 6: bar+spacing selection restructured."""
    global G, T, C, Dval, Areq, H, Fc, A1, S9, D9, Cw, TABLE_ROWS

    G    += 1
    T[G]  = Dval + 2.5
    C[G]  = Cw

    if 0.15 <= Areq <= 0.23:
        A1 = math.pi * (5.0 / 8.0) ** 2 / 4.0   # #5
        D9 = 5
        S9 = min(A1 * 12.0 / Areq, 16.0)
    else:
        A1 = best_A1 = 0.0
        D9 = best_D9 = 4
        S9 = best_S9 = 4.0
        for bar in range(4, 9):
            area_bar = math.pi * (bar / 8.0) ** 2 / 4.0
            sp       = area_bar * 12.0 / Areq if Areq > 0 else 99
            if sp >= 8.0:
                A1 = area_bar; D9 = bar; S9 = sp
                break
            best_A1 = area_bar; best_D9 = bar; best_S9 = sp
        else:
            A1 = best_A1; D9 = best_D9; S9 = best_S9
        if S9 >= 8.0:
            S9 = int(S9 / 2.0) * 2.0

    if H >= 1.9:
        wall_label = "CONC." if C[G] == 1 else "BLK. "
        rebar      = f"#{D9}@{int(S9):3d}"
        A_use      = A1 * 12.0 / S9 if S9 > 0 else A1
        row = (
            f"{H:8.2f}"
            f"{T[G]:8.2f}"
            f"{Dval:8.2f}"
            f"{int(M):14d}"
            f"{Areq:10.3f}"
            f"{A_use:10.3f}"
            f"{int(Fc):12d}"
            f"{rebar:>9}"
            f"{wall_label:>7}"
        )
        TABLE_ROWS.append(row)
        print(row)


# =============================================================================
# 790  TABLE HEADER
# =============================================================================
def gosub_790():
    print(
        f"{'HT(FT)':>8}{'T(IN)':>8}{'D(IN)':>8}"
        f"{'MOM(FT-LB)':>14}{'A(REQ)':>10}{'A(USE)':>10}"
        f"{'F\'M(PSI)':>12}{'RE-BAR':>9}{'WALL':>7}"
    )
    print("-" * 86)


# =============================================================================
# 360  MOMENT + STEEL LOOP
# =============================================================================
def gosub_360():
    """FIX 12/13: block index reset each height; concrete fallback seeded correctly."""
    global H, H2, H1, S1, P, M, Cw, D, Dval, K1, I1, G, F2, N2

    MAX_DVAL = 36.0
    H = 0.0
    G = 0

    while True:
        H = round(H + H2, 6)
        if H > H1 - 1e-6:
            H = H1

        M = S1 * P * H ** 2 / 2.0 + P * H ** 3 / 6.0

        if Cw == 1:
            if G > 0:
                Dval = max(T[G] - 2.5, Dval)
            found = False
            d_try = Dval
            while d_try <= MAX_DVAL:
                Dval = d_try
                gosub_510()
                if K1 == 1:
                    found = True; break
                I1 = 7; gosub_620()
                if K1 == 1:
                    found = True; break
                d_try += 1.0
            if not found:
                print(f"  WARNING: no valid concrete section at H={H:.2f} ft")

        else:
            section_found = False
            for I in range(1, 5):   # FIX 12: always start at 1
                if D[I] == 0.0:
                    continue
                Dval = D[I]
                gosub_510()
                if K1 == 1:
                    section_found = True; break
                I1 = 7; gosub_620()
                if K1 == 1:
                    section_found = True; break

            if not section_found:
                seed = 5.5
                for idx in range(3, 0, -1):   # FIX 13
                    if D[idx] != 0.0:
                        seed = D[idx]; break
                Dval = max(seed, 5.5)
                Cw = 1;  F2 = 900.0;  N2 = 11
                found = False
                while Dval <= MAX_DVAL:
                    gosub_510()
                    if K1 == 1:
                        found = True; break
                    I1 = 7; gosub_620()
                    if K1 == 1:
                        found = True; break
                    Dval += 1.0
                if not found:
                    print(f"  WARNING: no valid section at H={H:.2f} ft")

        if H >= H1 - 1e-6:
            break


# =============================================================================
# 1205  EARTH PRESSURE
# =============================================================================
def gosub_1205():
    """FIX 7: correct P3 and M4 formulas."""
    global P3, M4, S1, P, H4
    # P3 = total horizontal earth-pressure force (lb/ft)
    # M4 = overturning moment ABOUT THE TOE (ft-lb/ft)
    #      Triangular: resultant = P*H4²/2 acting at H4/3 from base
    #      → OTM = P*H4²/2 × H4/3 = P*H4³/6  (S1=0 case)
    #      With surcharge rectangle acting at H4/2:
    #      → OTM = P*S1*H4²/2 + P*H4³/6
    # NOTE: some Streamlit versions use P*H4³/3 for OTM — WRONG (2× too large).
    P3 = P * S1 * H4 + P * H4 ** 2 / 2.0
    M4 = P * S1 * H4 ** 2 / 2.0 + P * H4 ** 3 / 6.0   # /6 is correct for triangular


# =============================================================================
# 830  FOOTING DESIGN
# =============================================================================
def gosub_830():
    """
    FIX 8:  W1/M1 computed once outside B-loop (wall weight unchanged by B).
    FIX 15: W5/M5 (heel/toe soil) computed inside B-loop (width depends on B).
            T1==1 heel soil: W5=100*heel_ft*H1, arm = L/12+heel_ft/2 from TOE.
    FIX 9:  M6 = Σ(vert moments) − M4  (net stabilising about toe).
    FIX 10: W6 = vertical loads only.
    """
    global T, G, T1, E, H2, H1, W1, W5, M1, M5
    global C1, H4, B, W2, M2, W6, M6, P3, M4, M3
    global W7, M7, W8, M8, L, L1, S2, E1, X, C, L2, S, Tftg
    global W_bf, M_bf

    # FOOTING THICKNESS (inches)
    # Tftg = max(wall stem thickness at top, 12-in ACI minimum).
    # T[G] is already in INCHES (e.g. 16 for a 16-in CMU wall).
    # *** Common bug in Streamlit version: using H1 (feet) as Tftg (inches) ***
    # *** giving Tftg=10 in for H1=10 ft — WRONG.  Correct line is below:  ***
    Tftg = max(T[G], 12.0)   # always inches — never replace with H1

    # L = distance from TOE EDGE to back of wall stem (inches)
    L = E + T[G] if T1 == 1 else E

    if C1 == 1:
        H4 = H1
    else:
        H4 = H1 + Tftg / 12.0

    gosub_1205()   # FIX 7

    # FIX 8: wall weight once (does not depend on B)
    W1 = 0.0;  M1 = 0.0
    H3 = H2
    for i in range(1, G + 1):
        if i == G:
            H3 = H1 - H2 * (G - 1)
        W_seg = ((150.0 if C[i] == 1 else 115.0) / 12.0) * T[i] * H3
        W1   += W_seg
        # FIX 14: arm in feet
        arm   = L / 12.0 - T[i] / 24.0 if T1 == 1 else L / 12.0 + T[i] / 24.0
        M1   += W_seg * arm

    # Initial B
    B = max(round(H1 / 2.5, 1), Tftg / 12.0 + 0.5)

    # B-iteration
    for _ in range(500):
        W2 = 150.0 * (Tftg / 12.0) * B
        M2 = W2 * B / 2.0

        if T1 != 4:
            # FIX 15: heel/toe soil — depends on B, computed here
            if T1 == 1:
                # Heel soil: behind wall stem, from L/12 to B
                heel_ft = B - L / 12.0
                if heel_ft > 0:
                    W5 = 100.0 * heel_ft * H1
                    M5 = W5 * (L / 12.0 + heel_ft / 2.0)   # arm from TOE
                else:
                    W5 = M5 = 0.0
            elif T1 == 2:
                # Toe soil: in front of wall, from 0 to L/12
                toe_ft = L / 12.0
                if toe_ft > 0:
                    W5 = 100.0 * toe_ft * H1
                    M5 = W5 * (toe_ft / 2.0)   # arm from TOE (correct for T1=2)
                else:
                    W5 = M5 = 0.0
            else:
                W5 = M5 = 0.0

            W7 = W8 = M7 = M8 = 0.0
            # FIX 10: W6 = vertical loads only
            W6 = W1 + W2 + W5
            # FIX 9: M6 = stabilising − OTM
            M6 = M1 + M2 + M5 - M4

        else:  # T1 == 4
            L1  = max(B - L / 12.0 - Tftg / 12.0, 0.0)
            W7  = 100.0 * L1 * H1
            M7  = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
            W8 = M8 = 0.0
            if L2 != 0:
                W8 = 100.0 * L1 ** 2 / (2.0 * L2)
                M8 = W8 * (L1 * 2.0 / 3.0 + L / 12.0 + Tftg / 12.0)
            W5 = M5 = 0.0
            W6 = W1 + W2 + W7 + W8
            M6 = M1 + M2 + M7 + M8 - M4

        if W6 <= 0:
            B += 1.0 / 12.0; continue

        # Resultant from toe
        X  = (M6 + M4) / W6
        E1 = abs(B / 2.0 - X)

        if KERN_MODE == 2 and E1 > B / 6.0 + 1e-4:
            B += 1.0 / 12.0; continue
        if X <= 0 or X >= B:
            B += 1.0 / 12.0; continue

        # Soil bearing
        if E1 > B / 6.0:
            contact = 3.0 * X if X <= B / 2.0 else 3.0 * (B - X)
            S = 2.0 * W6 / contact if contact > 0 else 1e9
        else:
            S = (W6 / B) * (1.0 + 6.0 * E1 / B)

        if S > S2:
            B += 1.0 / 12.0; continue

        # S.F. overturning
        if M4 > 0 and (W6 * X / M4) < 1.5:
            B += 1.0 / 12.0; continue

        # Mode-2 trim
        if KERN_MODE == 2 and E1 < B / 6.0 - 1.0 / 72.0:
            B -= 1.0 / 12.0; continue

        break
    else:
        print("  WARNING: footing B-iteration did not converge")

    # Final store
    E1 = abs(B / 2.0 - X)

    # BACK FRICTION RULE (user-specified):
    # Wall friction vertical component = P3 * tan(δ), δ≈17° → tan≈0.3.
    # Applied ONLY when resultant is OUTSIDE the kern (E1 > B/6).
    # When within kern the footing is already well-balanced; adding back
    # friction would make a good design appear better than warranted.
    TAN_DELTA = 0.3          # wall friction coefficient (CMU on soil)
    arm_bf    = L / 12.0     # back face of wall from toe (ft)
    if E1 > B / 6.0 + 1e-4:
        W_bf = P3 * TAN_DELTA
        M_bf = W_bf * arm_bf
        # Recompute totals to include back friction
        W6 += W_bf
        M6 += M_bf
        X   = (M6 + M4) / W6
        E1  = abs(B / 2.0 - X)
    else:
        W_bf = 0.0
        M_bf = 0.0


# =============================================================================
# ORIENTATION TEXT
# =============================================================================
def gosub_1540(): print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
def gosub_1550(): print("    WALL FTG. IS ON THE SAME SIDE OF RET. EARTH")
def gosub_1560(): print("    FLUSH WALL FACE IS ON THE OPP. SIDE OF RET. EARTH")
def gosub_1570(): print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")
def gosub_1572():
    if L2: print(f"    GROUND SLOPE {L2:.2f} : 1")


# =============================================================================
# DESIGN HEADER
# =============================================================================
def _print_header():
    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print("\n  RETAINING WALL DESIGN\n")
    print("    WALL TYPE -", T1)
    if   T1 == 4: gosub_1550(); gosub_1560(); gosub_1572()
    elif T1 == 2: gosub_1540(); gosub_1570()
    else:         gosub_1540(); gosub_1560()
    print()
    print(f"    WALL HEIGHT            = {H1:8.2f}{P2}")
    print(f"    EQUIV. FLUID PRESSURE  = {P:8.2f}{P5s}")
    print(f"    ALLOWABLE PASSIVE      = {P4:8.2f}{P5s}")
    print(f"    COEFF. OF FRICTION     = {C9:8.4f}")
    if S1: print(f"    SURCHARGE              = {S1:8.2f}{P2}")
    if E:  print(f"    TOE                    = {E:8.2f}{P1}")
    print(f"    ALLOWABLE SOIL BEARING = {S2:8.2f}{P3s}")
    print(f"    ALLOWABLE STL. STRESS  = {Y:8.2f} (KSI)")
    print(f"    ECCENTRICITY MODE      : {kern_label}")
    print()

def gosub_print_header():
    _print_header(); gosub_790()


# =============================================================================
# 1210  SUMMARY REPRINT  (key 1)
# =============================================================================
def gosub_1210():
    _print_header(); gosub_790()
    for row in TABLE_ROWS: print(row)
    gosub_1400()


# =============================================================================
# 1400  FOOTING SUMMARY
# =============================================================================
def gosub_1400():
    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print()
    print(f"    ECCENTRICITY MODE  : {kern_label}")
    print(f"    FTG. WIDTH  = {B:.3f}{P2}")
    print(f"    FTG.  T     = {Tftg:.2f}{P1}")
    print(f"    WALL  T     = {T[G]:.2f}{P1}")
    print(f"    X (from toe)= {X:.3f}{P2}")

    if E1 > B / 6.0 + 1e-4:
        contact = 3.0 * X if X <= B / 2.0 else 3.0 * (B - X)
        S_max   = 2.0 * W6 / contact if contact > 0 else 1e9
        print(f"    ** E > B/6 — RESULTANT OUTSIDE KERN **")
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{P3s}")
        print(f"    SOIL BEAR'G MIN =    0.00{P3s}  (footing lifts off)")
        print(f"    ECCENTRICITY    = {E1:.3f}{P2}  (B/6={B/6:.3f}{P2})  OUTSIDE KERN")
    else:
        S_max = (W6 / B) * (1.0 + 6.0 * E1 / B)
        S_min = (W6 / B) * (1.0 - 6.0 * E1 / B)
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{P3s}")
        print(f"    SOIL BEAR'G MIN = {S_min:.2f}{P3s}")
        print(f"    ECCENTRICITY    = {E1:.3f}{P2}  (B/6={B/6:.3f}{P2})  WITHIN KERN")

    # Back-friction note
    if W_bf > 0.0:
        print(f"    BACK FRICTION   = P3×tan(δ) = {P3:.2f}×0.30 = {W_bf:.2f}{P4s}  (E OUTSIDE KERN — applied)")
        print(f"    BACK FRIC. ARM  = {M_bf/W_bf:.3f}{P2}  (back face of wall from toe)")
    else:
        print(f"    BACK FRICTION   = 0  (E WITHIN KERN — not applied per design rule)")

    OTM = M4;  RM = W6 * X
    if OTM > 0:
        SF = RM / OTM
        print(f"    RESIST. MOM  = {RM:.2f} (FT-LB/FT)")
        print(f"    OVERTURN MOM = {OTM:.2f} (FT-LB/FT)")
        print(f"    S.F. OVERT.  = {SF:.3f}", end="")
        print("  O.K." if SF >= 1.5 else "  ** FAIL — need >= 1.50 **")
    else:
        print("    S.F. OVERT.  = N/A")

    # FIX 11: sliding
    if C1 == 1:
        print("    WITH SLAB ON GRADE — SLIDING O.K.")
        return

    F_slide    = P3
    F_friction = C9 * W6
    print(f"    LATERAL FORCE (SLIDING) = {F_slide:.2f}{P4s}")
    print(f"    FRICTION RESIST.        = {F_friction:.2f}{P4s}")

    if F_friction >= F_slide:
        print("    FRICTION > SLIDING  O.K.")
        return

    passive_ftg = P4 * (Tftg / 12.0)
    if F_friction + passive_ftg >= F_slide:
        print("    WITH PASSIVE ON FTG. FACE  O.K.")
        return

    deficit      = F_slide - F_friction
    key_depth_in = (deficit / P4) * 12.0
    extra_in     = key_depth_in - Tftg
    if extra_in > 0:
        print(f"    USE KEY  {extra_in:.1f}{P1} BELOW FTG.")
    else:
        print(f"    TOTAL KEY DEPTH = {key_depth_in:.1f}{P1}  (within footing depth)")


# =============================================================================
# 1610  MOMENT BREAKDOWN  (key 2)
# =============================================================================
def gosub_1610():
    print()
    print("    ITEM          W (lb/ft)      M (ft-lb/ft)")
    print(f"    WALL          {W1:11.2f}     {M1:12.2f}")
    print(f"    FOOTING       {W2:11.2f}     {M2:12.2f}")
    print(f"    HEEL/TOE SOIL {W5:11.2f}     {M5:12.2f}")
    if W7: print(f"    WEDGE 1       {W7:11.2f}     {M7:12.2f}")
    if W8: print(f"    WEDGE 2       {W8:11.2f}     {M8:12.2f}")
    print(f"    LATERAL (OTM) {'---':>11}     {M4:12.2f}  (overturning)")
    if W_bf > 0.0:
        print(f"    BACK FRICTION {W_bf:12.2f}     {M_bf:12.2f}  (E outside kern — P3×0.30)")
    else:
        print(f"    BACK FRICTION {'0':>12}     {'0':>12}  (E within kern — not applied)")
    print(f"    TOTAL VERT.   {W6:11.2f}     {M6:12.2f}  (net stab = ΣM_vert − M4)")
    print()


# =============================================================================
# 1700  POINT-LOAD CHECK  (key 3)
# =============================================================================
def gosub_1700():
    P9_val  = float(input("POINT LOAD P (LB/FT) "))
    X9_val  = float(input("LOAD LOCATION from toe X9 (FT) "))
    B_trial = float(input("TRIAL FTG. WIDTH B (FT) "))

    W2_t = 150.0 * (Tftg / 12.0) * B_trial
    # Use last computed W5 (heel/toe soil at design B; approximate for trial B)
    Q1 = W1 + W2_t + W5 + W7 + W8 + P9_val
    Q2 = M1 + W2_t * B_trial / 2.0 + M5 + M7 + M8 - M4 + P9_val * X9_val

    Xt = (Q2 + M4) / Q1 if Q1 > 0 else B_trial / 2.0
    E9 = abs(B_trial / 2.0 - Xt)

    print(f"    P   = {P9_val:.2f} (LB/FT)")
    print(f"    X9  = {X9_val:.2f} (FT from toe)")
    print(f"    B   = {B_trial:.2f} (FT)")
    print(f"    W   = {Q1:.2f} (LB/FT)")
    print(f"    M   = {Q2:.2f} (FT-LB/FT)")
    print(f"    E   = {E9:.3f} (FT)")

    if E9 > B_trial / 6.0 + 1e-4:
        contact = 3.0 * Xt if Xt <= B_trial / 2.0 else 3.0 * (B_trial - Xt)
        SP_max  = 2.0 * Q1 / contact if contact > 0 else 1e9
        print("    ** E > B/6 — OUTSIDE KERN **")
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN =    0.00 (PSF)  (footing lifts off)")
    else:
        SP_max = (Q1 / B_trial) * (1.0 + 6.0 * E9 / B_trial)
        SP_min = (Q1 / B_trial) * (1.0 - 6.0 * E9 / B_trial)
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN = {SP_min:.2f} (PSF)")
    print(f"    ECCENT. = {E9:.3f} ft  (B/6 = {B_trial/6:.3f} ft)")

    RM_t = Q1 * Xt
    if M4 > 0:
        SF_t = RM_t / M4
        print(f"    RESIST. MOM  = {RM_t:.2f}")
        print(f"    OVERTURN MOM = {M4:.2f}")
        print(f"    S.F. OVERT.  = {SF_t:.3f}", end="")
        print("  O.K." if SF_t >= 1.5 else "  ** FAIL **")
    else:
        print("    S.F. OVERT.  = N/A")


# =============================================================================
# MAIN
# =============================================================================
def main():
    global D, A, P1, P2, P3s, P4s, P5s, W4, M3, W7, W8, M7, M8, TABLE_ROWS

    D[1] = 5.5;  D[2] = 9.5;  D[3] = 13.5;  D[4] = 0.0

    # Rebar areas (in²/ft at 12-in spacing) for bars #3–#9
    A[1] = 0.11   # #3
    A[2] = 0.20   # #4
    A[3] = 0.31   # #5
    A[4] = 0.44   # #6
    A[5] = 0.60   # #7
    A[6] = 0.88   # #8
    A[7] = 1.00   # #9

    P1  = " (IN)";  P2  = " (FT)"
    P3s = " (PSF)"; P4s = " (LB/FT)"; P5s = " (LB/CF)"

    W4 = W7 = W8 = 0.0
    M3 = M7 = M8 = 0.0
    globals()['W_bf'] = 0.0
    globals()['M_bf'] = 0.0
    TABLE_ROWS.clear()

    gosub_1580()
    gosub_140()
    gosub_print_header()
    gosub_360()
    gosub_830()
    gosub_1400()

    while True:
        print()
        print("MORE PRINT   KEY --- 1")
        print("FTG. MOMENTS KEY --- 2")
        print("POINT LOAD   KEY --- 3")
        print("QUIT         KEY --- other")
        try:
            choice = int(input("> "))
        except (ValueError, EOFError):
            break
        if   choice == 1: gosub_1210()
        elif choice == 2: gosub_1610()
        elif choice == 3: gosub_1700()
        else:             break

    print("Done.")


if __name__ == "__main__":
    main()
