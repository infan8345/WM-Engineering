# RET. WALL PROGRAM (2-14-85)  - BASIC-style Python conversion (corrected)

# ----- GLOBAL ARRAYS (1-based style) -----
T = [0.0] * 61     # 1..60
D = [0.0] * 5      # 1..4
C = [0.0] * 61     # 1..60
A = [0.0] * 8      # 1..7

# ----- GLOBAL SCALARS -----
P1 = P2 = P3s = P4s = P5s = ""
H = H1 = H2 = H3 = H4 = 0.0
L = L1 = 0.0
P = P4 = S1 = S2 = C9 = 0.0
Y = 0.0
C1 = 0
Cw = 0
T1 = 0
L2 = 0.0
Dval = 0.0
F = F1 = F2 = 0.0
N1 = N2 = 0
G = 0
W1 = W2 = W3 = W4 = W5 = W6 = W7 = W8 = 0.0
M1 = M2 = M3 = M4 = M5 = M6 = M7 = M8 = 0.0
X = S = E = E1 = 0.0
E2 = 0
K1 = 0
Areq = A2 = 0.0
P1s = 0.0
K = J = 0.0
A1 = 0.0
S9 = 0.0
D9 = 0
R = ""
P3 = 0.0
P9 = X9 = 0.0
B = 0.0
M = 0.0
I1 = 0
I2 = 0
TABLE_ROWS = []   # cache of printed table rows for key-1 reprint
KERN_MODE = 1     # 1=allow outside kern, 2=force inside kern


# ----- 1580-1600 PROGRAM TITLE -----
def gosub_1580():
    print("\n" * 3 + "RETAINING WALL PROGRAM")
    print("REV. 2-12-84 (Python conversion corrected)")


# ----- 140-350 INPUT BLOCK -----
def gosub_140():
    global T1, L2, H1, P, S2, C9, P4, S1, Cw, N1, F1, F, F2, N2
    global Dval, Y, C1, H2, E, D

    T1 = int(input("TYPE OF WALL (1,2,4) "))
    L2 = float(input("GROUND SLOPE (H : V) (X : 1) "))
    H1 = float(input("RETAINING WALL HT. = (FT) "))

    P = 30.0
    s = input("EQUIV. FLUID PRESSURE = 30 (#/CF) [Enter=default] ")
    if s.strip():
        P = float(s)

    S2 = 1000.0
    s = input("ALLOW. SOIL BEARING = 1000 (PSF) [Enter=default] ")
    if s.strip():
        S2 = float(s)

    C9 = 0.4
    s = input("FRICTION COEFF = .4 [Enter=default] ")
    if s.strip():
        C9 = float(s)

    P4 = 300.0
    s = input("ALLOW. PASSIVE = 300 (PSF) [Enter=default] ")
    if s.strip():
        P4 = float(s)

    S1 = float(input("SURCHARGE (FT) = (X) "))

    Cw = int(input("CONC. WALL (0 OR 1) "))

    if Cw == 0:
        I = int(input("CONT. INSPECTION (0 OR 1) "))
        if I == 1:
            N1 = 20
            F1 = 500.0   # with special inspection: fb = f'm/3 = 1500/3
        else:
            N1 = 40
            F1 = 333.0   # no inspection: fb = f'm/6 = 2000/6 (TMS 402-16)

        I = int(input("12 (IN) BLOCK (0 OR 1) "))
        if I != 1:
            D[2] = 0.0

        I = int(input("16 (IN) BLOCK (0 OR 1) "))
        if I != 1:
            D[3] = 0.0

    else:
        F = 2000.0
        s = input("CONC. F'C = 2000 (PSI) [Enter=default] ")
        if s.strip():
            F = float(s)
        F2 = 0.45 * F
        N2 = int(29000 / (57 * (F ** 0.5)))

        I = 8.0
        s = input("WALL T = 8 (IN) [Enter=default] ")
        if s.strip():
            I = float(s)
        Dval = I - 2.5

    Y = 20.0
    s = input("STEEL ALLOWABLE = 20 (KSI) [Enter=default] ")
    if s.strip():
        Y = float(s)

    C1 = int(input("SLAB ON GRADE (0 OR 1) "))

    H2 = 8.0
    s = input("WALL HT. INCREMENT = 8 (IN) [Enter=default] ")
    if s.strip():
        H2 = float(s)
    H2 = H2 / 12.0

    E = 0.0
    s = input("TOE (IN) = (0) [Enter=default] ")
    if s.strip():
        E = float(s)

    global KERN_MODE
    print("ECCENTRICITY MODE:")
    print("  1 = ALLOW E OUTSIDE KERN (triangular pressure)")
    print("  2 = FORCE E INSIDE KERN  (footing sized until E <= B/6)")
    s = input("SELECT (1 OR 2) [Enter=1] ")
    KERN_MODE = 2 if s.strip() == "2" else 1


def gosub_5000():
    pass


# ----- 510-610 STEEL AREA CALC -----
def gosub_510():
    global Areq, A2, P1s, K, J, F, K1
    global Cw, N1, N2, Dval, M, Y, F1, F2

    Areq = M * 12.0 / (Y * 7.0 / 8.0 * Dval * 1000.0)
    A2 = Areq

    if Cw == 0:
        P1s = N1 * Areq / (12.0 * Dval)
    else:
        P1s = N2 * Areq / (12.0 * Dval)

    K = (2 * P1s + P1s * P1s) ** 0.5 - P1s
    J = 1 - K / 3.0
    F = M * 2.0 / (K * J * Dval * Dval)

    K1 = 0
    if Cw == 0:
        if F < F1:
            gosub_670()
            K1 = 1
    else:
        if F < F2:
            gosub_670()
            K1 = 1


# ----- 620-660 BAR SELECTION -----
def gosub_620():
    global I2, I1, Areq, A2, K1

    for I2 in range(1, I1 + 1):
        if Areq >= A[I2] / 1.02:
            continue
        if A[I2] >= A2 / 1.02:
            return
        else:
            Areq = A[I2]
        gosub_510()
        if K1 == 1:
            return


# ----- 670-783 TABLE ROW PRINT -----
def gosub_670():
    global G, T, C, Dval, Areq, H, F, A1, S9, D9, Cw, TABLE_ROWS

    G += 1
    T[G] = Dval + 2.5
    C[G] = Cw

    for D9 in range(4, 9):
        if Areq > 0.23 * 1.02 or Areq < 0.15 / 1.01:
            A1 = 3.14159 * (D9 / 8.0) ** 2 / 4.0
            S9 = A1 * 12.0 / Areq
        else:
            A1 = 0.31
            D9 = 5
            S9 = 16.0
            break
        if S9 > 8:
            break

    if S9 >= 8:
        S9 = int(S9 / 8.0 + 0.1) * 8

    wall_type = "  CONC." if C[G] == 1 else "  BLK."

    if H >= 1.9:
        rebar = f"#{D9}@{int(S9):3d}"
        wall_type = "CONC." if C[G] == 1 else "BLK. "
        row = (
            f"{H:8.2f}"
            f"{Dval+2.5:8.2f}"
            f"{Dval:8.2f}"
            f"{int(M):14d}"
            f"{Areq:10.3f}"
            f"{A1*12/S9:10.3f}"
            f"{int(F):12d}"
            f"{rebar:>9}"
            f"{wall_type:>7}"
        )
        TABLE_ROWS.append(row)
        print(row)


# ----- 790-794 TABLE HEADER -----
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


# ----- 360-500 MOMENT + STEEL LOOP (corrected) -----
def gosub_360():
    global H, H2, H1, S1, P, M, Cw, D, Dval, K1, I1, G, F2, N2

    H = 0.0
    I = 1
    G = 0
    MAX_DVAL = 30.0  # safety cap -- no wall section deeper than 30 in

    while True:
        H = H + H2
        if H >= H1:
            H = H1

        M = S1 * P * H * H / 2.0 + P * H ** 3 / 6.0

        if Cw == 1:
            # ---- concrete wall branch ----
            found = False
            while Dval <= MAX_DVAL:
                gosub_510()
                if K1 == 1:
                    found = True
                    break
                I1 = 7
                gosub_620()
                if K1 == 1:
                    found = True
                    break
                Dval += 1.0

            if not found:
                print(f"  WARNING: No valid concrete section found at H={H:.2f} ft")

            if H >= H1 - 0.01:
                break
            # else advance H and keep going

        else:
            # ---- masonry block wall branch ----
            if I > 4 or D[I] == 0:
                # no more block sizes -- switch to concrete
                prev_I = max(1, I - 1)
                Dval = D[prev_I] if D[prev_I] != 0 else 5.5
                Cw = 1
                F2 = 900.0
                N2 = 11
                found = False
                while Dval <= MAX_DVAL:
                    gosub_510()
                    if K1 == 1:
                        found = True
                        break
                    I1 = 7
                    gosub_620()
                    if K1 == 1:
                        found = True
                        break
                    Dval += 1.0

                if not found:
                    print(f"  WARNING: No valid section found at H={H:.2f} ft")

                if H >= H1 - 0.01:
                    break
                # else advance H

            else:
                Dval = D[I]
                gosub_510()
                if K1 == 1:
                    if H >= H1 - 0.01:
                        break
                    continue
                I1 = 7
                gosub_620()
                if K1 == 1:
                    if H >= H1 - 0.01:
                        break
                    continue
                # this block size not sufficient -- try next size
                I += 1
                if I > 4:
                    print(f"  WARNING: Exhausted all block sizes at H={H:.2f} ft")
                    if H >= H1 - 0.01:
                        break
                continue  # retry same H with new block size


# ----- 1205 EARTH PRESSURE BLOCK -----
def gosub_1205():
    global P3, M4, S1, P, H4
    P3 = (S1 * P * H4 + P * H4 * H4 / 2.0) / 3.0
    M4 = S1 * P * H4 * H4 / 2.0 + P * H4 ** 3 / 6.0


# ----- 830-1200 FOOTING DESIGN (corrected) -----
def gosub_830():
    global T, G, T1, E, H2, H1, W1, W5, M1, M5
    global C1, H4, B, W2, M2, W6, M6, P3, M4
    global W7, M7, W8, M8, W4, L, L1, S2, E1, E2, X, C, L2, M3, S

    first_pass = True
    while True:
        if T[G] < 12:
            Tftg = 12.0
        else:
            Tftg = T[G]

        H3 = H2
        W1 = W5 = M1 = M5 = 0.0

        if T1 == 1:
            L = E + T[G]
        else:
            L = E

        for i in range(1, G + 1):
            if i == G:
                H3 = H1 - H2 * (G - 1)

            if C[i] == 1:
                W = 12.5 * T[i] * H3
            else:
                W = 77.0 / 8.0 * T[i] * H3
            W1 += W

            if T1 == 1:
                M1 += W * (L - T[i] / 2.0) / 12.0
            else:
                M1 += W * (L + T[i] / 2.0) / 12.0

            if T1 == 1:
                W = H3 * (L - T[i]) / 0.12
                Mw = W * (L - T[i]) / 24.0
            elif T1 == 2:
                W = L * H3 / 0.12
                Mw = W * L / 24.0
            else:
                W = (Tftg - T[i]) * H3 / 0.12
                Mw = W * (L + T[i] + (Tftg - T[i]) / 2.0) / 12.0

            W5 += W
            M5 += Mw

        if C1 == 1:
            H4 = H1
        else:
            H4 = H1 + Tftg / 12.0

        gosub_1205()

        if first_pass:
            B = int(H1 / 2.5 * 12.0) / 12.0
            first_pass = False

        W2 = 12.5 * Tftg * B
        M2 = W2 * B / 2.0

        if T1 != 4:
            M3 = P3 * (L / 12.0)
            W6 = W1 + W2 + W5 + P3
            M6 = M1 + M2 + M3 + M4 + M5
        else:
            L1 = B - L / 12.0 - Tftg / 12.0
            W7 = L1 * H1 * 100.0
            M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
            M3_local = P3 * (L / 12.0)
            M3 = M3_local
            if L2 != 0:
                W8 = 100.0 * (L1 * L2) / (2.0 * L2)
                M8 = W8 * (L1 * 2.0 / 3.0 + L / 12.0 + Tftg / 12.0)
                H4 = H1 + Tftg / 12.0 + L1 / L2
                gosub_1205()
            else:
                W8 = 0.0
                M8 = 0.0
            M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
            W6 = W1 + W2 + W5 + P3 + W7 + W8

        # Inner loop: adjust B until resultant is valid
        while True:
            X = M6 / W6

            def _recalc_totals(B, Tftg, W1, W2, M2, W5, P3, M1, M4, M5,
                               L, L1, H1, W7, M7, W8, M8, T1):
                W2 = 12.5 * Tftg * B
                M2 = W2 * B / 2.0
                if T1 != 4:
                    M3 = P3 * (L / 12.0)
                    W6 = W1 + W2 + W5 + P3
                    M6 = M1 + M2 + M3 + M4 + M5
                else:
                    L1 = B - L / 12.0 - Tftg / 12.0
                    W7 = L1 * H1 * 100.0
                    M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                    M3 = P3 * (L / 12.0)
                    W6 = W1 + W2 + W5 + P3 + W7 + W8
                    M6 = M1 + M2 + M3 + M5 + M7 + M8 - M4
                return W2, M2, W6, M6, M3, L1, W7, M7

            if KERN_MODE == 1:
                # Mode 1: only enforce X stays on footing (0 < X < B)
                # widen if resultant falls completely off either edge
                if X <= 0 or X >= B:
                    B = int(12 * B + 2) / 12.0
                    W2 = 12.5 * Tftg * B
                    M2 = W2 * B / 2.0
                    if T1 != 4:
                        M3 = P3 * (L / 12.0)
                        W6 = W1 + W2 + W5 + P3
                        M6 = M1 + M2 + M3 + M4 + M5
                    else:
                        L1 = B - L / 12.0 - Tftg / 12.0
                        W7 = L1 * H1 * 100.0
                        M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                        M3_local = P3 * (L / 12.0)
                        M3 = M3_local
                        W6 = W1 + W2 + W5 + P3 + W7 + W8
                        M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
                    continue
                # X is on the footing -- accept and break
                break

            else:
                # Mode 2: enforce middle third (X between B/3 and 2B/3)
                if X < B / 3.0:
                    B = int(12 * B + 2) / 12.0
                    W2 = 12.5 * Tftg * B
                    M2 = W2 * B / 2.0
                    if T1 != 4:
                        M3 = P3 * (L / 12.0)
                        W6 = W1 + W2 + W5 + P3
                        M6 = M1 + M2 + M3 + M4 + M5
                    else:
                        L1 = B - L / 12.0 - Tftg / 12.0
                        W7 = L1 * H1 * 100.0
                        M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                        M3_local = P3 * (L / 12.0)
                        M3 = M3_local
                        W6 = W1 + W2 + W5 + P3 + W7 + W8
                        M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
                    continue
                if X > 2 * B / 3.0:
                    B = int(12 * B + 2) / 12.0
                    W2 = 12.5 * Tftg * B
                    M2 = W2 * B / 2.0
                    if T1 != 4:
                        M3 = P3 * (L / 12.0)
                        W6 = W1 + W2 + W5 + P3
                        M6 = M1 + M2 + M3 + M4 + M5
                    else:
                        L1 = B - L / 12.0 - Tftg / 12.0
                        W7 = L1 * H1 * 100.0
                        M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                        M3_local = P3 * (L / 12.0)
                        M3 = M3_local
                        W6 = W1 + W2 + W5 + P3 + W7 + W8
                        M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
                    continue
                # Resultant in middle third -- try to trim B
                if X <= B / 2.0:
                    if (X - B / 3.0) > 0.04:
                        B = B - 1.0 / 12.0
                        W2 = 12.5 * Tftg * B
                        M2 = W2 * B / 2.0
                        if T1 != 4:
                            M3 = P3 * (L / 12.0)
                            W6 = W1 + W2 + W5 + P3
                            M6 = M1 + M2 + M3 + M4 + M5
                        else:
                            L1 = B - L / 12.0 - Tftg / 12.0
                            W7 = L1 * H1 * 100.0
                            M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                            M3_local = P3 * (L / 12.0)
                            M3 = M3_local
                            W6 = W1 + W2 + W5 + P3 + W7 + W8
                            M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
                        continue
                    else:
                        break
                else:
                    if (2 * B / 3.0 - X) > 0.04:
                        B = B - 1.0 / 12.0
                        W2 = 12.5 * Tftg * B
                        M2 = W2 * B / 2.0
                        if T1 != 4:
                            M3 = P3 * (L / 12.0)
                            W6 = W1 + W2 + W5 + P3
                            M6 = M1 + M2 + M3 + M4 + M5
                        else:
                            L1 = B - L / 12.0 - Tftg / 12.0
                            W7 = L1 * H1 * 100.0
                            M7 = W7 * (L1 / 2.0 + L / 12.0 + Tftg / 12.0)
                            M3_local = P3 * (L / 12.0)
                            M3 = M3_local
                            W6 = W1 + W2 + W5 + P3 + W7 + W8
                            M6 = M1 + M2 + M3_local + M5 + M7 + M8 - M4
                        continue
                    else:
                        break

        E1 = abs(B / 2.0 - X)
        if E1 > B / 6.0:
            # triangular -- high pressure at the closer edge
            contact = 3.0 * X if X < B / 2.0 else 3.0 * (B - X)
            S = 2.0 * W6 / contact
            if KERN_MODE == 2:
                # force resultant inside kern -- widen footing
                B = B + 1.0 / 6.0
                continue
        else:
            S = (1.0 + E1 * 6.0 / B) * W6 / B

        if S >= S2:
            B = B + 1.0 / 6.0
            # restart outer loop with wider footing
            continue

        # Check S.F. overturning >= 1.5
        OTM_chk = M4
        RM_chk  = M6 - M4
        if OTM_chk > 0 and (RM_chk / OTM_chk) < 1.5:
            B = B + 1.0 / 6.0
            continue

        break


# ----- 1540-1576 ORIENTATION TEXT -----
def gosub_1540():
    print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")


def gosub_1550():
    print("    WALL FTG. IS ON THE SAME SIDE OF RET. EARTH")


def gosub_1560():
    print("    FLUSH WALL FACE IS ON THE OPP. SIDE OF RET. EARTH")


def gosub_1570():
    print("    FLUSH WALL FACE IS ON THE SAME SIDE OF RET. EARTH")


def gosub_1572():
    global L2
    if L2 != 0:
        print(f"    GROUND SLOPE {L2:.2f} : 1")


# ----- HEADER ONLY (used on first run before rows exist) -----
def gosub_print_header():
    global T1, P, P4, C9, S1, E, S2, Y, H1, P2, P5s, P3s, P1, KERN_MODE

    print("\n  RETAINING WALL DESIGN\n")
    print("    WALL TYPE -", T1)

    if T1 == 4:
        gosub_1550()
        gosub_1560()
        gosub_1572()
    elif T1 == 2:
        gosub_1540()
        gosub_1570()
    else:
        gosub_1540()
        gosub_1560()

    print()
    print(f"    WALL HEIGHT            = {H1:8.2f}{P2}")
    print(f"    EQUIV. FLUID PRESSURE  = {P:8.2f}{P5s}")
    print(f"    ALLOWABLE PASSIVE      = {P4:8.2f}{P5s}")
    print(f"    COEFF. OF FRICTION     = {C9:8.2f}")
    if S1 != 0:
        print(f"    SURCHARGE              = {S1:8.2f}{P2}")
    if E != 0:
        print(f"    TOE                    = {E:8.2f}{P1}")
    print(f"    ALLOWABLE SOIL BEARING = {S2:8.2f}{P3s}")
    print(f"    ALLOWABLE STL. STRESS  = {Y:8.2f} (KSI)")
    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print(f"    ECCENTRICITY MODE      : {kern_label}")
    print()
    gosub_790()  # column header only -- rows follow from gosub_360()


# ----- 1210-1390 SUMMARY PRINT (key-1 reprint with cached rows) -----
def gosub_1210():
    global T1, P, P4, C9, S1, E, S2, Y, H1, P2, P5s, P3s, P1, TABLE_ROWS, KERN_MODE

    print("\n  RETAINING WALL DESIGN\n")
    print("    WALL TYPE -", T1)

    if T1 == 4:
        gosub_1550()
        gosub_1560()
        gosub_1572()
    elif T1 == 2:
        gosub_1540()
        gosub_1570()
    else:
        gosub_1540()
        gosub_1560()

    print()
    print(f"    WALL HEIGHT            = {H1:8.2f}{P2}")
    print(f"    EQUIV. FLUID PRESSURE  = {P:8.2f}{P5s}")
    print(f"    ALLOWABLE PASSIVE      = {P4:8.2f}{P5s}")
    print(f"    COEFF. OF FRICTION     = {C9:8.2f}")
    if S1 != 0:
        print(f"    SURCHARGE              = {S1:8.2f}{P2}")
    if E != 0:
        print(f"    TOE                    = {E:8.2f}{P1}")
    print(f"    ALLOWABLE SOIL BEARING = {S2:8.2f}{P3s}")
    print(f"    ALLOWABLE STL. STRESS  = {Y:8.2f} (KSI)")
    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print(f"    ECCENTRICITY MODE      : {kern_label}")
    print()
    gosub_790()
    for row in TABLE_ROWS:
        print(row)
    gosub_1400()


# ----- 1400-1530 FOOTING SUMMARY -----
def gosub_1400():
    global B, T, X, S, C1, P3, C9, W6, P4s, P3s, P2, P1, G, P4, E1, KERN_MODE, M4, M6, T1

    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print()
    print(f"    ECCENTRICITY MODE : {kern_label}")
    print(f"    FTG. WIDTH  = {B:.2f}{P2}")
    print(f"    FTG.  T     = {T[G]:.2f}{P1}")
    print(f"    X           = {X:.2f}{P2}")

    # E1 = eccentricity = |B/2 - X|
    if E1 > B / 6.0:
        # triangular -- high pressure at the closer edge
        contact = 3.0 * X if X < B / 2.0 else 3.0 * (B - X)
        S_max = 2.0 * W6 / contact
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{P3s}")
        print(f"    SOIL BEAR'G MIN =   0.00{P3s}  (footing lifts off)")
        print(f"    ECCENTRICITY    = {E1:.2f}{P2}  (B/6 = {B/6:.2f}{P2})  ** OUTSIDE KERN **")
    else:
        # Trapezoidal -- max and min
        S_max = (W6 / B) * (1.0 + 6.0 * E1 / B)
        S_min = (W6 / B) * (1.0 - 6.0 * E1 / B)
        print(f"    SOIL BEAR'G MAX = {S_max:.2f}{P3s}")
        print(f"    SOIL BEAR'G MIN = {S_min:.2f}{P3s}")
        print(f"    ECCENTRICITY    = {E1:.2f}{P2}  (B/6 = {B/6:.2f}{P2})  ** WITHIN KERN **")

    # ----- S.F. OVERTURNING -----
    # M4 = lateral earth pressure moment (overturning about toe)
    # Resisting moment = M6 - M4 (dead loads only: wall + footing + soil on heel)
    OTM = M4
    RM  = M6 - M4
    if OTM > 0:
        SF_OT = RM / OTM
        print(f"    RESIST. MOM = {RM:.2f} (FT-LB)")
        print(f"    OVERTURN MOM= {OTM:.2f} (FT-LB)")
        print(f"    S.F. OVERT. = {SF_OT:.2f}", end="")
        if SF_OT >= 1.5:
            print("  O.K.")
        else:
            print("  ** OVERTURN FAIL (need >= 1.50) **")
    else:
        print("    S.F. OVERT. = N/A (no overturning moment)")

    if C1 == 1:
        print("    WITH SLAB SLID'G O.K.")
        return

    F_slide   = P3 * 3
    F_fric    = C9 * W6
    print(f"    F--SLID'G   = {F_slide:.2f}{P4s}  (lateral earth pressure)")
    print(f"    F--FRICTION = {F_fric:.2f}{P4s}  (base friction: C={C9:.2f} x W={W6:.2f} lb)")
    print(f"    NOTE: P/3 = {P3:.2f} lb is passive soil pressure on key/footing")
    print(f"          moment arm = toe+wall = {L:.0f}in = {L/12:.2f}ft from toe")
    print(f"          (per ASCE 7 / IBC -- stem-face friction NOT credited as sliding resistance)")

    if F_fric >= F_slide:
        print("    FRICTION > SLIDING  O.K.")
        return

    T1loc = ((F_slide - F_fric) * 3 / P4) ** 0.5 * 12.0
    if T[G] > T1loc:
        print("    WITH PASSIVE ON FTG.  O.K.")
    else:
        print(f"    USE {int(T1loc - T[G])} (IN) DEEP KEY")


# ----- 1610-1685 MOMENT BREAKDOWN -----
def gosub_1610():
    global W1, M1, W2, M2, P3, M3, W5, M5, W7, M7, W8, M8, W4, M4, W6, M6, L

    print("    ITEMS        W           M")
    print(f"    WALL     {W1:10.2f}  {M1:10.2f}")
    print(f"    FTG.     {W2:10.2f}  {M2:10.2f}")
    print(f"    P/3      {P3:10.2f}  {M3:10.2f}  (arm={L:.0f}in from toe)")
    print(f"    EARTH    {W5:10.2f}  {M5:10.2f}")
    print(f"    EARTH2   {W7:10.2f}  {M7:10.2f}")
    print(f"    EARTH3   {W8:10.2f}  {M8:10.2f}")
    print(f"    O.T.M.   {'---':>10}  {M4:10.2f}")
    print(f"    TOTAL    {W6:10.2f}  {M6:10.2f}")
    print()


# ----- 1700-1790 POINT LOAD CHECK -----
def gosub_1700():
    global P9, X9, W1, P3, W4, W5, W7, W8
    global M1, M3, M4, M5, M7, M8, KERN_MODE, T1

    P9 = float(input("P (LB) "))
    X9 = float(input("X9 (FT) "))
    B_trial = float(input("B (FTG. WIDTH - FT) "))  # local -- does NOT overwrite design B

    Q1 = W1 + B_trial * 150 + P3 + W4 + W5 + W7 + W8 + P9
    Q2 = M1 + B_trial * 150 * B_trial / 2 + M3 + M4 + M5 + M7 + M8 + P9 * X9
    X_trial = Q2 / Q1
    E9 = abs(B_trial / 2 - X_trial)

    print(f"    P (LB)              {P9:.2f}")
    print(f"    X9 (FT)             {X9:.2f}")
    print(f"    B (FTG. WIDTH - FT) {B_trial:.2f}")
    print(f"    W = {Q1:.2f}")
    print(f"    M = {Q2:.2f}")
    print(f"    E = {E9:.2f}")

    if E9 > B_trial / 6.0:
        # triangular -- high pressure at the closer edge
        contact = 3.0 * X_trial if X_trial < B_trial / 2.0 else 3.0 * (B_trial - X_trial)
        SP_max = 2.0 * Q1 / contact
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN =   0.00 (PSF)  (footing lifts off)")
        print(f"    ECCENTRICITY = {E9:.2f}{' (FT)':8}  (B/6 = {B_trial/6:.2f} (FT))  ** OUTSIDE KERN **")
    else:
        SP_max = (Q1 / B_trial) * (1.0 + 6.0 * E9 / B_trial)
        SP_min = (Q1 / B_trial) * (1.0 - 6.0 * E9 / B_trial)
        print(f"    S.P. MAX = {SP_max:.2f} (PSF)")
        print(f"    S.P. MIN = {SP_min:.2f} (PSF)")
        print(f"    ECCENTRICITY = {E9:.2f}{' (FT)':8}  (B/6 = {B_trial/6:.2f} (FT))  ** WITHIN KERN **")

    # S.F. overturning for trial footing
    OTM_t = M4
    RM_t  = Q2 - M4
    if OTM_t > 0:
        SF_t = RM_t / OTM_t
        print(f"    RESIST. MOM = {RM_t:.2f} (FT-LB)")
        print(f"    OVERTURN MOM= {OTM_t:.2f} (FT-LB)")
        print(f"    S.F. OVERT. = {SF_t:.2f}", end="")
        if SF_t >= 1.5:
            print("  O.K.")
        else:
            print("  ** OVERTURN FAIL (need >= 1.50) **")
    else:
        print("    S.F. OVERT. = N/A")


# ----- MAIN PROGRAM -----
def main():
    global D, A, P1, P2, P3s, P4s, P5s, T, W4, M3
    global W7, W8, M7, M8

    D[1] = 5.5
    D[2] = 9.5
    D[3] = 13.5
    D[4] = 0.0

    A[1] = 0.10
    A[2] = 0.15
    A[3] = 0.23
    A[4] = 0.30
    A[5] = 0.47
    A[6] = 0.66
    A[7] = 0.90

    P1 = " (IN)"
    P2 = " (FT)"
    P3s = " (PSF)"
    P4s = " (LB)"
    P5s = " (LB/CF)"

    W4 = 0.0
    M3 = 0.0
    W7 = 0.0
    W8 = 0.0
    M7 = 0.0
    M8 = 0.0
    TABLE_ROWS.clear()

    gosub_1580()
    gosub_140()
    gosub_5000()
    gosub_print_header()  # print design params + table column header
    gosub_360()           # prints rows live AND fills TABLE_ROWS cache
    gosub_830()
    gosub_1400()

    if T1 == 1:
        show_type1_diagram()

    while True:
        print()
        print("MORE PRINT KEY---1")
        print("FTG. MOM   KEY---2")
        print("P--LOAD    KEY---3")
        print("QUIT       KEY---OTHER")
        try:
            I = int(input("> "))
        except (ValueError, EOFError):
            break
        if I == 1:
            gosub_1210()
        elif I == 2:
            gosub_1610()
        elif I == 3:
            gosub_1700()
        else:
            break

    print("Done.")
    generate_report()

    # Keep console window open on Windows
    try:
        import os
        if os.name == "nt":
            input("\n  Press Enter to close...")
    except Exception:
        pass


# ----- COMBINED PDF REPORT (calc pg1 + SVG diagram pg2) -----
def generate_report():
    global T1, H1, P, P4, C9, S1, E, S2, Y, B, T, G, X, E1, W6, M4, M6
    global C1, P3, P3s, P2, P1, TABLE_ROWS, KERN_MODE, L2

    import io, sys, os, subprocess, tempfile

    # ----------------------------------------------------------------
    # 1. Collect calc text
    # ----------------------------------------------------------------
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf

    kern_label = "ALLOW OUTSIDE KERN" if KERN_MODE == 1 else "FORCE INSIDE KERN"
    print("  RETAINING WALL DESIGN")
    print()
    print(f"    WALL TYPE             : {T1}")
    if T1 == 1:
        print("    WALL FTG. IS ON THE OPP. SIDE OF RET. EARTH")
        print("    FLUSH WALL FACE IS ON THE OPP. SIDE OF RET. EARTH")
    print(f"    WALL HEIGHT           = {H1:.2f} (FT)")
    print(f"    EQUIV. FLUID PRESSURE = {P:.2f} (LB/CF)")
    print(f"    ALLOWABLE PASSIVE     = {P4:.2f} (LB/CF)")
    print(f"    COEFF. OF FRICTION    = {C9:.2f}")
    if S1 != 0:
        print(f"    SURCHARGE             = {S1:.2f} (FT)")
    if E != 0:
        print(f"    TOE                   = {E:.2f} (IN)")
    print(f"    ALLOW. SOIL BEARING   = {S2:.2f} (PSF)")
    print(f"    ALLOW. STL. STRESS    = {Y:.2f} (KSI)")
    print(f"    ECCENTRICITY MODE     : {kern_label}")
    print()
    hdr = (f"{'HT(FT)':>8}{'T(IN)':>8}{'D(IN)':>8}"
           f"{'MOM(FT-LB)':>14}{'A(REQ)':>10}{'A(USE)':>10}"
           f"{'FM(PSI)':>12}{'RE-BAR':>9}{'WALL':>7}")
    print(hdr)
    print("-" * 86)
    for row in TABLE_ROWS:
        print(row)
    print()
    print(f"    FTG. WIDTH  = {B:.2f} (FT)")
    print(f"    FTG.  T     = {T[G]:.2f} (IN)")
    print(f"    X           = {X:.2f} (FT)")
    if E1 > B / 6.0:
        contact = 3.0 * X if X < B / 2.0 else 3.0 * (B - X)
        S_max = 2.0 * W6 / contact
        print(f"    ** E > B/6 : RESULTANT OUTSIDE KERN **")
        print(f"    SOIL BEAR'G MAX = {S_max:.2f} (PSF)")
        print(f"    SOIL BEAR'G MIN =   0.00 (PSF)  (footing lifts off)")
        print(f"    ECCENTRICITY    = {E1:.2f} (FT)  (B/6 = {B/6:.2f} (FT))  ** OUTSIDE KERN **")
    else:
        S_max = (W6 / B) * (1.0 + 6.0 * E1 / B)
        S_min = (W6 / B) * (1.0 - 6.0 * E1 / B)
        print(f"    SOIL BEAR'G MAX = {S_max:.2f} (PSF)")
        print(f"    SOIL BEAR'G MIN = {S_min:.2f} (PSF)")
        print(f"    ECCENTRICITY    = {E1:.2f} (FT)  (B/6 = {B/6:.2f} (FT))  ** WITHIN KERN **")
    OTM = M4
    RM  = M6 - M4
    if OTM > 0:
        SF_OT = RM / OTM
        ok = "O.K." if SF_OT >= 1.5 else "** OVERTURN FAIL **"
        print(f"    RESIST. MOM = {RM:.2f} (FT-LB)")
        print(f"    OVERTURN MOM= {OTM:.2f} (FT-LB)")
        print(f"    S.F. OVERT. = {SF_OT:.2f}  {ok}")

    sys.stdout = old
    calc_text = buf.getvalue()

    # ----------------------------------------------------------------
    # 2. Build PDF with reportlab (calc page 1, diagram page 2)
    # ----------------------------------------------------------------
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib import colors
    except ImportError:
        print("  reportlab not installed.  Run:  pip install reportlab")
        # Still write and open the HTML report
        html_file = "retaining_wall_report.html"
        _write_html_report(calc_text, html_file)
        try:
            if os.name == "nt":
                html_abs = os.path.abspath(html_file)
                subprocess.Popen(f'start "" "{html_abs}"', shell=True)
        except Exception:
            pass
        return

    pdf_file = "retaining_wall_report.pdf"
    PW, PH = letter          # 612 x 792 pts
    ML = 0.55 * inch         # left margin
    MR = 0.55 * inch         # right margin
    MT = 0.55 * inch         # top margin
    MB = 0.50 * inch         # bottom margin

    c = rl_canvas.Canvas(pdf_file, pagesize=letter)

    # ================================================================
    # PAGE 1: CALCULATION SHEET
    # ================================================================
    # Header bar
    c.setFillColor(colors.Color(0.15, 0.15, 0.15))
    c.rect(ML, PH - MT - 16, PW - ML - MR, 16, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Courier-Bold", 9)
    c.drawString(ML + 4, PH - MT - 11, "RETAINING WALL DESIGN  --  CALCULATION REPORT")
    c.setFillColor(colors.black)

    # Calc text
    c.setFont("Courier", 7.8)
    lh = 10.0          # line height pts
    y = PH - MT - 26   # start below header

    for line in calc_text.splitlines():
        if y < MB + lh:
            break
        c.drawString(ML, y, line)
        y -= lh

    # Footer
    c.setFont("Courier", 6.5)
    c.setFillColor(colors.Color(0.45, 0.45, 0.45))
    c.line(ML, MB - 2, PW - MR, MB - 2)
    c.drawString(ML, MB - 12, "Retaining Wall Program  REV. 2-12-84  (Python conversion)")
    c.drawRightString(PW - MR, MB - 12, "Page 1 of 2")
    c.setFillColor(colors.black)

    # ================================================================
    # PAGE 2: REBAR DIAGRAM  (SVG -> PNG -> embed in PDF)
    # ================================================================
    if T1 == 1:
        c.showPage()

        # Header bar
        c.setFillColor(colors.Color(0.15, 0.15, 0.15))
        c.rect(ML, PH - MT - 16, PW - ML - MR, 16, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Courier-Bold", 9)
        c.drawString(ML + 4, PH - MT - 11,
                     f"TYPE 1 WALL  --  REBAR DETAIL    H={H1:.2f}ft  B={B:.2f}ft  Slope={L2:.1f}:1")
        c.setFillColor(colors.black)

        # Generate SVG and render to PNG
        svg_tmp  = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
        png_tmp  = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        svg_tmp.close(); png_tmp.close()

        try:
            import cairosvg
            # Write SVG to temp file
            show_type1_diagram(svg_path=svg_tmp.name)
            # Render at 2x resolution for crisp PDF embedding
            cairosvg.svg2png(url=svg_tmp.name,
                             write_to=png_tmp.name,
                             output_width=1400)
            # Embed PNG in PDF, centered, filling available area
            img_x = ML
            img_y = MB
            img_w = PW - ML - MR
            img_h = PH - MT - MB - 26   # leave room for header
            c.drawImage(png_tmp.name, img_x, img_y,
                        width=img_w, height=img_h,
                        preserveAspectRatio=True, anchor='c')
        except ImportError:
            c.setFont("Courier-Bold", 11)
            c.setFillColor(colors.Color(0.2, 0.2, 0.2))
            c.drawCentredString(PW/2, PH/2 + 20,
                "Diagram not available in PDF.")
            c.setFont("Courier", 9)
            c.setFillColor(colors.Color(0.4, 0.4, 0.4))
            c.drawCentredString(PW/2, PH/2,
                "Open  retaining_wall_report.html  in Chrome or Edge")
            c.drawCentredString(PW/2, PH/2 - 18,
                "to see the full diagram and print both pages.")
            c.drawCentredString(PW/2, PH/2 - 40,
                "To enable diagram in PDF:  pip install cairosvg")
            c.setFillColor(colors.black)
        finally:
            try: os.unlink(svg_tmp.name)
            except: pass
            try: os.unlink(png_tmp.name)
            except: pass

        # Footer
        c.setFont("Courier", 6.5)
        c.setFillColor(colors.Color(0.45, 0.45, 0.45))
        c.line(ML, MB - 2, PW - MR, MB - 2)
        c.drawString(ML, MB - 12,
            "Type 1: Flush face opposite earth  |  Footing turns out (heel)  |  "
            "8-in block upper + 12-in CMU 24-in min base")
        c.drawRightString(PW - MR, MB - 12, "Page 2 of 2")
        c.setFillColor(colors.black)

    c.save()
    print(f"\n  PDF report saved to: {pdf_file}")

    # ----------------------------------------------------------------
    # 3. Write HTML report
    # ----------------------------------------------------------------
    html_file = pdf_file.replace('.pdf', '.html')
    _write_html_report(calc_text, html_file)

    # ----------------------------------------------------------------
    # 4. Open files on Windows — HTML always, PDF if available
    # ----------------------------------------------------------------
    try:
        if os.name == "nt":
            html_abs = os.path.abspath(html_file)
            pdf_abs  = os.path.abspath(pdf_file)
            # Open HTML first (always has diagram)
            subprocess.Popen(f'start "" "{html_abs}"', shell=True)
            import time; time.sleep(0.5)
            # Open PDF too
            subprocess.Popen(f'start "" "{pdf_abs}"', shell=True)
    except Exception as e:
        print(f"  (Could not auto-open browser: {e})")
        print(f"  Manually open: {html_file}")


def _write_html_report(calc_text, html_file):
    """Write letter-size HTML: calc page 1 + diagram page 2. Always shows diagram inline."""
    global T1, H1, B, E, L2, T, G, C, TABLE_ROWS

    C_base    = int(C[G]) if G > 0 else 0
    C_upper   = int(C[1]) if G > 0 else 0
    bar_upper = _get_upper_bar(TABLE_ROWS)
    svg = _build_type1_svg(H1, B, E, L2, T[G], C_base, C_upper, bar_upper) if T1 == 1 else ''
    # Strip XML declaration so SVG embeds cleanly inside HTML
    if svg.startswith('<?xml'):
        svg = svg[svg.index('<svg'):]

    # Escape HTML special chars in calc text
    ct = calc_text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    diag_title = (f"TYPE 1 WALL &mdash; REBAR DETAIL &nbsp;&nbsp; "
                  f"H={H1:.2f}ft &nbsp; B={B:.2f}ft &nbsp; Slope={L2:.1f}:1") if T1==1 else ""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Retaining Wall Design Report</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"Courier New",Courier,monospace;font-size:9pt;
     background:#d8d8d8;color:#000}}

/* page card */
.page{{width:8.5in;min-height:11in;margin:.25in auto;background:#fff;
      box-shadow:0 2px 10px rgba(0,0,0,.22);
      padding:.5in .6in .4in .6in;
      display:flex;flex-direction:column;page-break-after:always}}

/* title bar - double height */
.hdr{{background:#1c1c1c;color:#fff;padding:10px 14px;margin-bottom:12px}}
.hdr-main{{font-size:11.5pt;font-weight:bold;letter-spacing:.04em;line-height:1.4}}
.hdr-sub{{font-size:8pt;color:#aaa;margin-top:3px}}

/* calc text - fits on one page */
pre{{font-family:"Courier New",Courier,monospace;
     font-size:7.6pt;line-height:1.33;white-space:pre;
     flex:1;overflow:hidden}}

/* footer */
.foot{{font-size:7pt;color:#666;border-top:.5px solid #bbb;
       padding-top:5px;margin-top:8px;
       display:flex;justify-content:space-between}}

/* diagram page */
.diag{{min-height:11in}}
.diag-body{{flex:1;display:flex;align-items:center;justify-content:center;
            padding:4px 0}}
.diag-body svg{{width:100%;height:auto;max-height:9.1in}}

/* print */
@media print{{
  body{{background:#fff}}
  .page{{margin:0;box-shadow:none;padding:.4in .5in .3in .5in}}
  pre{{font-size:7.4pt;line-height:1.28}}
  .diag-body svg{{max-height:9.3in}}
}}
</style>
</head><body>

<!-- PAGE 1: CALC -->
<div class="page">
  <div class="hdr">
    <div class="hdr-main">RETAINING WALL DESIGN &mdash; CALCULATION REPORT</div>
    <div class="hdr-sub">REV. 2-12-84 &nbsp;|&nbsp; Python conversion &nbsp;|&nbsp; Type {T1} Wall</div>
  </div>
  <pre>{ct}</pre>
  <div class="foot">
    <span>Retaining Wall Program &nbsp; REV. 2-12-84</span>
    <span>Page 1 of 2</span>
  </div>
</div>

<!-- PAGE 2: DIAGRAM -->
{"" if not svg else f'''
<div class="page diag">
  <div class="hdr">
    <div class="hdr-main">{diag_title}</div>
    <div class="hdr-sub">Type 1: Flush face opposite earth &nbsp;|&nbsp;
      Footing turns out (heel) &nbsp;|&nbsp;
      8&quot; block upper stem + 12&quot; CMU 24&quot; min base</div>
  </div>
  <div class="diag-body">
    {svg}
  </div>
  <div class="foot">
    <span>Type 1: Flush face opposite earth &nbsp;|&nbsp; Footing turns out (heel)</span>
    <span>Page 2 of 2</span>
  </div>
</div>'''}

</body></html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  HTML report saved to: {html_file}")
    print("  -> Open in Chrome/Edge, press Ctrl+P to print/save both pages with diagram.")


# ----- DRAW TYPE 1 DIAGRAM DIRECTLY ON REPORTLAB CANVAS -----
def _draw_type1_diagram_pdf(c, W, H, M):
    global H1, B, E, L2, T, G

    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas

    # Page title
    c.setFont("Courier-Bold", 11)
    c.drawString(M, H - M, "TYPE 1 RETAINING WALL  --  REBAR DETAIL")
    c.setLineWidth(0.5)
    c.line(M, H - M - 4, W - M, H - M - 4)

    # ---- coordinate system ----
    # Draw area: x from M to W-M, y from M+50 to H-M-20
    # We map the wall into a fixed drawing box
    # Box: left=M, right=W-M*2.2, bottom=M+70, top=H-M-30
    # (right side reserved for labels)

    DL = M                       # draw left
    DR = W - 2.4*inch            # draw right (leave 2.2" for labels)
    DB = M + 1.1*inch            # draw bottom (leave room for dims)
    DT = H - M - 0.35*inch      # draw top

    draw_w = DR - DL
    draw_h = DT - DB

    # Wall layout proportions (same as SVG: heel~46%, wall~9%, toe~12%, earth rest)
    # Positions as fractions of draw_w
    heel_f  = 0.44
    wall_f  = 0.09
    toe_f   = 0.12
    # x positions in pts
    x0 = DL                             # footing left (heel end)
    xfl = DL + heel_f * draw_w          # flush face (wall left)
    x8r = xfl + wall_f * 0.45 * draw_w # 8" block right face
    xcr = xfl + wall_f * draw_w         # 12" CMU right face
    x_toe_r = xcr + toe_f * draw_w     # toe right / footing right
    xkey_r  = x0 + 0.09 * draw_w       # key right

    # y positions in pts (bottom=DB, top=DT)
    y_ftg_bot = DB
    y_ftg_top = DB + 0.12 * draw_h
    y_cmu_top = y_ftg_top + 0.22 * draw_h   # top of 12" CMU
    y_wall_top = DT
    y_key_bot  = y_ftg_bot - 0.18 * draw_h

    wall_h_pt = y_wall_top - y_ftg_top

    # slope geometry
    scale_pt = wall_h_pt / H1
    if L2 > 0:
        slope_run = min(H1 * L2 * scale_pt, DR - xcr - 4)
    else:
        slope_run = 0
    ex_top_r = xcr + slope_run   # top-right of earth wedge

    # ---- helpers ----
    def hatch_rect(x, y, w, h, spacing=5, angle=45):
        """Fill rect with grey fill (simplified)."""
        solid_rect(x, y, w, h)

    def solid_rect(x, y, w, h, fc=colors.Color(0.92,0.92,0.92)):
        c.setFillColor(fc)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.7)
        c.rect(x, y, w, h, fill=1, stroke=1)
        c.setFillColor(colors.black)

    def cmu_rect(x, y, w, h, course_h=12):
        """Draw rect with CMU block pattern."""
        solid_rect(x, y, w, h, fc=colors.Color(0.88, 0.88, 0.88))
        c.setLineWidth(0.4)
        c.setStrokeColor(colors.Color(0.5,0.5,0.5))
        # horizontal joints
        yj = y + course_h
        while yj < y + h - 1:
            c.line(x, yj, x+w, yj)
            yj += course_h
        # vertical joints (staggered)
        row = 0
        yj = y
        while yj < y + h:
            off = 0 if row % 2 == 0 else w/2
            xj = x + off + w/2
            while xj < x + w:
                c.line(xj, yj, xj, min(yj+course_h, y+h))
                xj += w/2
            row += 1
            yj += course_h
        c.setLineWidth(0.7)
        c.setStrokeColor(colors.black)

    def blk8_rect(x, y, w, h):
        cmu_rect(x, y, w, h, course_h=10)

    def rebar(x1, y1, x2, y2):
        c.setStrokeColor(colors.Color(0.88, 0.29, 0.29))
        c.setLineWidth(2.0)
        c.line(x1, y1, x2, y2)
        c.setLineWidth(0.7)
        c.setStrokeColor(colors.black)

    def rebar_tick(x, y, horiz=False):
        c.setStrokeColor(colors.Color(0.88, 0.29, 0.29))
        c.setLineWidth(2.0)
        if horiz:
            c.line(x, y-5, x, y+5)
        else:
            c.line(x-5, y, x+5, y)
        c.setLineWidth(0.7)
        c.setStrokeColor(colors.black)

    def dim_line(x1, y1, x2, y2, label, offset=8, label_side="mid"):
        """Draw dimension arrow line with label."""
        c.setStrokeColor(colors.Color(0.3,0.3,0.3))
        c.setLineWidth(0.5)
        # arrows
        import math
        dx = x2-x1; dy = y2-y1
        L = math.sqrt(dx*dx+dy*dy)
        if L < 1: return
        ux = dx/L; uy = dy/L
        ah = 6  # arrowhead size
        # draw line
        c.line(x1, y1, x2, y2)
        # arrowheads
        for px, py, sign in [(x1,y1,1),(x2,y2,-1)]:
            c.line(px, py, px + sign*ux*ah + uy*ah*0.4,
                            py + sign*uy*ah - ux*ah*0.4)
            c.line(px, py, px + sign*ux*ah - uy*ah*0.4,
                            py + sign*uy*ah + ux*ah*0.4)
        # label
        mx = (x1+x2)/2; my = (y1+y2)/2
        c.setFont("Courier", 6.5)
        c.setFillColor(colors.Color(0.3,0.3,0.3))
        c.drawCentredString(mx, my - 7, label)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.7)

    def label_r(x, y, txt, color=colors.Color(0.3,0.3,0.3)):
        """Label to right of drawing area."""
        c.setFont("Courier", 7)
        c.setFillColor(color)
        lx = DR + 6
        c.drawString(lx, y, txt)
        c.setLineWidth(0.3)
        c.setStrokeColor(color)
        c.line(x, y+3, lx-2, y+3)
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.7)

    RC = colors.Color(0.88, 0.29, 0.29)   # rebar red
    EC = colors.Color(0.55, 0.36, 0.16)   # earth brown
    PC = colors.Color(0.22, 0.55, 0.84)   # passive blue

    # ---- Draw earth (upside-down trapezoid) ----
    earth_color = colors.Color(0.78, 0.66, 0.43, alpha=0.45)
    p = c.beginPath()
    p.moveTo(xcr, y_wall_top)
    p.lineTo(ex_top_r, y_wall_top)
    p.lineTo(xcr, y_ftg_top)
    p.close()
    c.setFillColor(earth_color)
    c.setStrokeColor(EC)
    c.setLineWidth(0.8)
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)

    # Ground line top
    c.setStrokeColor(EC)
    c.setLineWidth(1.2)
    c.line(xcr, y_wall_top, min(ex_top_r+14, DR+10), y_wall_top)

    # Slope indicator triangle
    if L2 > 0:
        tri_b = min(40, slope_run * 0.5)   # horizontal leg
        tri_v = tri_b / L2                 # vertical leg
        tx = ex_top_r
        ty = y_wall_top
        c.setStrokeColor(EC)
        c.setLineWidth(0.6)
        c.line(tx, ty, tx, ty - tri_v)
        c.line(tx, ty - tri_v, tx - tri_b, ty - tri_v)
        c.line(tx - tri_b, ty - tri_v, tx, ty)
        c.setFont("Courier", 6.5)
        c.setFillColor(EC)
        c.drawCentredString(tx - tri_b/2, ty - tri_v - 8,
                            f"H={int(L2) if L2==int(L2) else round(L2,1)}")
        c.drawString(tx + 2, ty - tri_v/2, "V=1")
        slope_txt = f"{int(L2) if L2==int(L2) else round(L2,1)}:1 slope"
        c.setFont("Courier-Bold", 7)
        c.drawCentredString((xcr + ex_top_r)/2, y_wall_top + 8, slope_txt)

    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.7)

    # Exposed ground lines (dashed)
    c.setDash(4, 3)
    c.setStrokeColor(EC)
    c.line(x0 - 6, y_ftg_top, xfl, y_ftg_top)
    c.line(xcr, y_ftg_top, x_toe_r + 4, y_ftg_top)
    c.setDash()
    c.setStrokeColor(colors.black)

    # Earth pressure arrows
    arrow_steps = 5
    for i in range(1, arrow_steps + 1):
        ay = y_ftg_top + (y_wall_top - y_ftg_top) * i / (arrow_steps + 1)
        alen = 10 + 16 * i / arrow_steps
        c.setStrokeColor(EC)
        c.setLineWidth(0.8)
        c.line(xcr + alen, ay, xcr + 1, ay)
        # arrowhead
        c.line(xcr + 1, ay, xcr + 6, ay + 3)
        c.line(xcr + 1, ay, xcr + 6, ay - 3)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.7)

    # Passive pressure arrows
    for i in range(1, 3):
        ay = y_key_bot + (y_ftg_bot - y_key_bot) * i / 3
        c.setStrokeColor(PC)
        c.setLineWidth(0.8)
        c.line(x0 - 18, ay, x0 - 1, ay)
        c.line(x0 - 1, ay, x0 - 6, ay + 3)
        c.line(x0 - 1, ay, x0 - 6, ay - 3)
    c.setFont("Courier", 6.5)
    c.setFillColor(PC)
    c.drawString(x0 - 26, y_key_bot + (y_ftg_bot-y_key_bot)*0.5 + 4, "pass.")
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.7)

    # ---- Structural elements ----
    ftg_w = x_toe_r - x0
    ftg_h = y_ftg_top - y_ftg_bot
    solid_rect(x0, y_ftg_bot, ftg_w, ftg_h)           # footing
    solid_rect(x0, y_key_bot, xkey_r-x0, y_ftg_bot-y_key_bot)  # key
    blk8_rect(xfl, y_cmu_top, x8r-xfl, y_wall_top-y_cmu_top)   # 8" blk upper
    cmu_rect(xfl, y_ftg_top, xcr-xfl, y_cmu_top-y_ftg_top)     # 12" CMU

    # step-out at transition
    c.setStrokeColor(colors.black); c.setLineWidth(0.7)
    c.line(x8r, y_cmu_top, xcr, y_cmu_top)

    # ---- REBAR ----
    # A. Upper stem bar: earth face of 8" blk (x8r - 3pt cover)
    sx = x8r - 4
    rebar(sx, y_wall_top - 4, sx, y_cmu_top + 0.66*(y_cmu_top-y_ftg_top))
    rebar_tick(sx, y_cmu_top + 0.66*(y_cmu_top-y_ftg_top), horiz=True)

    # B. Base bar: earth face of 12" CMU (xcr - 3pt cover)
    bx = xcr - 5
    rebar(bx, y_cmu_top, bx, y_ftg_bot + 6)
    # bend toward heel
    c.setStrokeColor(RC); c.setLineWidth(2.0)
    c.arc(bx-5, y_ftg_bot+1, bx+1, y_ftg_bot+11, startAng=270, extent=90)
    rebar(bx - 5, y_ftg_bot + 6, x0 + 8, y_ftg_bot + 6)
    # 3" clr dim
    c.setStrokeColor(colors.Color(0.3,0.3,0.3)); c.setLineWidth(0.4)
    c.line(bx+8, y_ftg_bot, bx+8, y_ftg_bot+6)
    c.setFont("Courier",6); c.setFillColor(colors.Color(0.3,0.3,0.3))
    c.drawString(bx+10, y_ftg_bot+2, "3in clr")
    c.setFillColor(colors.black); c.setStrokeColor(colors.black); c.setLineWidth(0.7)

    # Lap bracket
    lap_top = y_cmu_top
    lap_bot = y_cmu_top + 0.66*(y_cmu_top-y_ftg_top)
    c.setStrokeColor(RC); c.setLineWidth(0.6); c.setDash(3,2)
    c.line(xcr+3, lap_top, xcr+3, lap_bot)
    c.setDash()
    c.line(xcr+1, lap_top, xcr+5, lap_top)
    c.line(xcr+1, lap_bot, xcr+5, lap_bot)
    c.setFont("Courier",6.5); c.setFillColor(RC)
    c.drawString(xcr+6, (lap_top+lap_bot)/2-3, "lap")
    c.setFillColor(colors.black); c.setStrokeColor(colors.black); c.setLineWidth(0.7)

    # C. Key bar L-shape: passive face of key (x0+4)
    kx = x0 + 5
    rebar(kx, y_key_bot+4, kx, y_ftg_top+6)
    c.setStrokeColor(RC); c.setLineWidth(2.0)
    c.arc(kx-1, y_ftg_top+1, kx+9, y_ftg_top+11, startAng=90, extent=90)
    # 24" horizontal leg = ~0.52 * heel width
    leg_end = kx + 0.52*(xfl-x0)
    rebar(kx+5, y_ftg_top+6, leg_end, y_ftg_top+6)
    rebar_tick(leg_end, y_ftg_top+6)
    # 24" dim
    c.setStrokeColor(colors.Color(0.3,0.3,0.3)); c.setLineWidth(0.4)
    c.line(kx+5, y_ftg_top+14, leg_end, y_ftg_top+14)
    c.setFont("Courier",6); c.setFillColor(colors.Color(0.3,0.3,0.3))
    c.drawCentredString((kx+5+leg_end)/2, y_ftg_top+16, "24in")
    c.setFillColor(colors.black); c.setStrokeColor(colors.black); c.setLineWidth(0.7)

    # ---- DIMENSION LINES ----
    # H (wall height)
    dim_line(x0-22, y_ftg_top, x0-22, y_wall_top, f"H={H1:.1f}'")
    # B (footing width)
    dim_line(x0, DB-18, x_toe_r, DB-18, f"B={B:.2f}'")
    # Heel
    dim_line(x0, DB-8, xfl, DB-8, "heel")
    # Toe
    dim_line(xcr, DB-8, x_toe_r, DB-8, "toe")
    # 8" block width
    dim_line(xfl, y_wall_top+10, x8r, y_wall_top+10, '8in')
    # 12" CMU width
    dim_line(xfl, y_ftg_top-8, xcr, y_ftg_top-8, '12in')
    # CMU 24" height
    dim_line(xfl-14, y_ftg_top, xfl-14, y_cmu_top, '24in')
    # Ftg thickness
    dim_line(x_toe_r+8, y_ftg_bot, x_toe_r+8, y_ftg_top,
             f"T={T[G]:.0f}in")

    # ---- LABELS ----
    c.setFont("Courier", 7)
    c.setFillColor(colors.Color(0.3,0.3,0.3))
    # flush face
    c.drawRightString(xfl-2, (y_ftg_top+y_wall_top)/2+6, "flush")
    c.drawRightString(xfl-2, (y_ftg_top+y_wall_top)/2-4, "face")
    # earth face
    c.drawString(x8r+2, (y_cmu_top+y_wall_top)/2, "earth face")
    # zone labels
    c.drawCentredString((x0+xfl)/2, y_ftg_top+3, "heel (turns out)")
    c.drawCentredString((xcr+x_toe_r)/2, y_ftg_top+3, "toe")
    c.drawCentredString((x0+xkey_r)/2, (y_key_bot+y_ftg_bot)/2, "key")
    # 8" blk / 12" CMU
    c.drawRightString(xfl-2, (y_cmu_top+y_wall_top)/2, "8in blk")
    c.drawRightString(xfl-2, (y_ftg_top+y_cmu_top)/2, "12in CMU")
    c.setFillColor(colors.black)

    # ---- RIGHT-SIDE REBAR LABELS ----
    label_r(sx, (y_cmu_top+y_wall_top)/2+10, "upper stem bar", RC)
    label_r(sx, (y_cmu_top+y_wall_top)/2-2,  "(8in blk, earth face)", RC)
    label_r(bx, (y_ftg_top+y_cmu_top)/2+6,  "base bar", RC)
    label_r(bx, (y_ftg_top+y_cmu_top)/2-6,  "(12in CMU, earth face)", RC)
    label_r(bx, (y_ftg_top+y_cmu_top)/2-16, "3in clr, bends->heel", RC)
    label_r(xcr+3, (lap_top+lap_bot)/2,      "lap splice", RC)
    label_r(kx, (y_key_bot+y_ftg_bot)/2,     "key bar L-shape", RC)
    label_r(kx, (y_key_bot+y_ftg_bot)/2-10,  "(passive face, 24in)", RC)

    # ---- TITLE NOTE ----
    c.setFont("Courier", 7)
    c.setFillColor(colors.Color(0.2,0.2,0.2))
    tx2 = DR + 6
    c.drawString(tx2, y_wall_top - 2,  "TYPE 1 WALL:")
    c.drawString(tx2, y_wall_top - 12, "Flush face opp. earth")
    c.drawString(tx2, y_wall_top - 22, "Ftg turns out (heel)")
    c.setFillColor(colors.black)





# ----- HELPER: find governing bar size for lap calculation -----
def _get_upper_bar(table_rows):
    """
    Return the governing bar number for lap length.
    The lap splice is between upper stem bar and base bar —
    use the LARGEST bar in ALL rows (upper + base) since
    the base bar often governs (e.g. #6 in 12" CMU base).
    """
    import re
    max_bar = 4  # default #4
    for row in table_rows:
        for p in row.split():
            m = re.match(r'#(\d+)@', p)
            if m:
                max_bar = max(max_bar, int(m.group(1)))
    return max_bar


# ----- PRINT-FRIENDLY SVG BUILDER (shared by HTML and PDF) -----
def _build_type1_svg(H1_val, B_val, E_val, L2_val, T_base_in,
                     C_base=0, C_upper=0, bar_upper=4):
    """
    Build Type 1 retaining wall SVG matching hand-sketch layout:
      - Flush face LEFT (straight vertical)
      - Earth RIGHT with back slope at H:V = L2_val:1
      - Slope shown as diagonal line from top of wall going RIGHT+DOWN
        at correct H:V angle, with right-triangle indicator
      - Slash hatch for retained earth (no fill)
      - White background, print-friendly
    Canvas: 760 x 580 px. Right 170px for labels.
    """
    # ----- Fixed layout constants -----
    # Wall extends 1ft ABOVE retained earth (ground level is 1ft below wall top)
    # So retained earth height = H1_val - 1.0 ft
    RET_H  = H1_val - 1.0        # retained earth height in ft
    ABOVE  = 1.0                  # ft wall above ground

    Y_TOP  = 56     # top of wall
    Y_FTG  = 448    # footing top

    WALL_H_PX = Y_FTG - Y_TOP    # px representing H1 ft (full wall height)
    SCALE     = WALL_H_PX / H1_val  # px per foot

    # Ground line is 1ft below wall top = ABOVE * SCALE px below Y_TOP
    Y_GND  = Y_TOP + int(ABOVE * SCALE)   # ground / retained earth top

    # 12" CMU base height:
    # Min lap for #5+ = 30" → need 32" (4 courses) to accommodate lap
    # Min lap for #4  = 24" → 24" (3 courses) is sufficient
    CMU_MIN_FT = 32/12 if bar_upper >= 5 else 24/12
    CMU_PX = int(CMU_MIN_FT * SCALE)
    Y_CMU  = Y_FTG - CMU_PX      # top of base CMU course
    CMU_HT_IN = int(CMU_MIN_FT * 12)   # for label (24" or 32")

    # Footing thickness to scale
    FTG_PX = max(int(T_base_in / 12.0 * SCALE), 36)
    Y_FBT  = Y_FTG + FTG_PX

    # Key depth: 24" = 2ft
    KEY_PX = int(2.0 * SCALE)
    Y_KEY  = Y_FBT + KEY_PX

    # Clear dimensions
    CLR3_PX = max(int(3/12 * SCALE), 7)   # 3" in px
    CLR2_PX = max(int(2/12 * SCALE), 5)   # 2" in px

    # ----- Determine actual block sizes from calc results -----
    # T_base_in = base (bottom) wall thickness from T[G]
    # Upper stem thickness = 8" unless base is also 8" (no step-out)
    # Scan TABLE_ROWS to find the upper block thickness (smallest T used)
    # and the base block thickness (T_base_in already passed in)
    T_base  = T_base_in                      # base CMU thickness (in)
    T_upper = 8.0                            # default upper = 8"
    # Check: if base == 8" (no step-out needed) then upper == base
    if T_base <= 8.0:
        T_upper = 8.0

    # x positions — compute from actual block sizes
    # Scale factor: 1 inch = SCALE/12 px
    PX_PER_IN = SCALE / 12.0
    # Fixed reference: flush face at X_FL, 8" block extends right by T_upper
    X_HEEL = 100
    X_FL   = 256                             # flush face (always straight)
    X_8R   = X_FL + int(T_upper * PX_PER_IN)   # earth face of upper stem
    X_CMU  = X_FL + int(T_base  * PX_PER_IN)   # earth face of base CMU
    # Cap X_CMU so it doesn't push into toe area
    X_CMU  = min(X_CMU, 340)
    X_8R   = min(X_8R, X_CMU)               # upper can't be wider than base
    X_TOE  = max(X_CMU + 50, 370)           # toe right edge (min 50px toe)
    X_KEY  = 150

    # Label strings for actual block sizes
    upper_lbl    = f'{int(T_upper)}&quot; {"CONC" if C_upper==1 else "BLK"}'
    base_lbl     = f'{int(T_base)}&quot; {"CONC" if C_base==1 else "BLK"}/{CMU_HT_IN}&quot;'
    base_dim     = f'{int(T_base)}&quot;'
    upper_dim    = f'{int(T_upper)}&quot;'
    base_bar_lbl = f'base bar ({int(T_base)}&quot; {"CONC" if C_base==1 else "BLK"})'

    # ----- Slope geometry -----
    # Slope starts at (X_TOE, Y_FTG) — footing right end (retained earth base)
    # rises at H:V = L2_val:1 to the top-right corner.
    # Retained height = RET_H ft → horizontal run = RET_H * L2_val * SCALE px
    # Top of slope is at Y_GND (ground line), not Y_TOP (wall top)
    # So slope line: from (X_TOE, Y_FTG) to (X_TOE + run_px, Y_GND)

    if L2_val > 0:
        run_px  = RET_H * L2_val * SCALE
        X_SLOPE = int(X_TOE + min(run_px, 570 - X_TOE))
    else:
        X_SLOPE = X_TOE

    # Triangle indicator: right-angle at BOTTOM-LEFT (X_TOE, Y_FTG)
    TRI_W = min(56, int(run_px * 0.25)) if L2_val > 0 else 0
    TRI_H = int(TRI_W / L2_val)        if L2_val > 0 else 0
    RM    = 7

    if L2_val == 0:
        # Level ground: slash ticks along horizontal top edge at Y_GND
        slope_els = (
            f'<line x1="{X_CMU}" y1="{Y_GND}" x2="{X_CMU+80}" y2="{Y_GND}" '
            f'stroke="#555" stroke-width="1.4"/>'
            + ''.join(
                f'<line x1="{X_CMU+8+i*16}" y1="{Y_GND}" x2="{X_CMU+i*16}" y2="{Y_GND+10}" '
                f'stroke="#555" stroke-width="1"/>'
                for i in range(5)
            )
            + f'<text class="sm" x="{X_CMU+88}" y="{Y_GND+4}" fill="#444">level</text>'
        )
    else:
        import math
        H_lbl = str(int(L2_val)) if L2_val == int(L2_val) else f"{L2_val:.1f}"
        sl    = H_lbl + ':1'

        # Slope symbol sits at the TOP of the earth face at (X_CMU, Y_GND)
        # Draw a short slope line segment showing the slope angle, then slash ticks
        # Slope rises H:V = L2_val:1, so for a segment of length SEG_LEN px:
        # dx = L2_val portion, dy = 1 portion (going right+up in screen = right+negative y)
        SEG_LEN = 90   # total length of slope symbol in px
        angle_rad = math.atan2(1, L2_val)   # angle from horizontal (V/H)
        # In SVG: x goes right, y goes down. Slope goes right and UP (y decreases)
        # unit vector along slope surface (going uphill = right+up):
        ux =  math.cos(angle_rad)   # rightward
        uy = -math.sin(angle_rad)   # upward (negative y)
        # perpendicular pointing INTO earth = rotate 90° CW from uphill direction
        px =  uy   # = -sin(angle) → downward component
        py = -ux   # = -cos(angle) → leftward component  ... ticks go down-left

        # Start point: 8" left of earth face of 8" block at ground level
        sx, sy = float(X_CMU - 24), float(Y_GND)
        ex = sx + ux * SEG_LEN
        ey = sy + uy * SEG_LEN

        hatch_sp = 12   # spacing between hatch lines along slope
        n_hatch  = max(3, int(SEG_LEN / hatch_sp))

        parts = [
            # Slope face line only — clean diagonal, no ticks above
            f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="#555" stroke-width="1.4"/>'
        ]
        # Hatch lines: drop straight DOWN from each point on slope to Y_GND
        # (below the slope line only, like soil hatch in geotechnical drawings)
        for i in range(n_hatch + 1):
            t = i / n_hatch
            hx = sx + t * (ex - sx)
            hy = sy + t * (ey - sy)
            parts.append(
                f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{hx:.1f}" y2="{Y_GND}" '
                f'stroke="#777" stroke-width="0.8"/>'
            )
        # Ratio label just past end of slope line
        lx = ex + ux * 8
        ly = ey + uy * 8
        parts.append(
            f'<text class="sm" x="{lx:.0f}" y="{ly:.0f}" text-anchor="start" '
            f'dominant-baseline="central" fill="#444">{sl}</text>'
        )
        slope_els = '\n'.join(parts)

    # Earth wedge: TL=(X_CMU,Y_GND) TR=(X_SLOPE,Y_GND) BR=(X_TOE,Y_FTG)
    # Clip path includes the wall-above-earth strip too for hatching
    wedge_pts = f"{X_CMU},{Y_GND} {X_SLOPE},{Y_GND} {X_TOE},{Y_FTG}"

    # Slash hatching clipped to earth wedge
    # Wedge: TL=(X_CMU,Y_TOP) TR=(X_SLOPE,Y_TOP) BR=(X_TOE,Y_FTG)
    sp = 16
    W  = X_SLOPE - X_CMU   # width at top
    Hh = Y_FTG   - Y_TOP
    slash_lines = []
    for i in range(-2, int((W + Hh) / sp) + 4):
        d   = i * sp
        lx1 = X_CMU + d
        ly1 = Y_TOP
        lx2 = X_CMU + d + Hh
        ly2 = Y_FTG
        slash_lines.append(
            f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" '
            f'stroke="#bbb" stroke-width="0.7"/>')
    slashes = '\n    '.join(slash_lines)

    # Dimension helpers
    def dh(x1, x2, y, lb, dy=-10):
        mx = (x1 + x2) // 2
        return (
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#444" '
            f'stroke-width="0.6" marker-start="url(#da)" marker-end="url(#da)"/>'
            f'<text class="sm" x="{mx}" y="{y+dy}" text-anchor="middle" fill="#444">{lb}</text>')
    def dv(x, y1, y2, lb, dx=8):
        my = (y1 + y2) // 2
        anchor = 'end' if dx < 0 else 'start'
        return (
            f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#444" '
            f'stroke-width="0.6" marker-start="url(#da)" marker-end="url(#da)"/>'
            f'<text class="sm" x="{x+dx}" y="{my}" text-anchor="{anchor}" dominant-baseline="central" fill="#444">{lb}</text>')

    ti = int(E_val) if E_val == int(E_val) else round(E_val, 1)

    # Earth pressure arrows (5 steps, increasing length going down)
    ep = '\n  '.join(
        f'<line x1="{X_8R+6+i*4}" y1="{Y_TOP+50+i*74}" x2="{X_8R}" y2="{Y_TOP+50+i*74}" '
        f'stroke="#888" stroke-width="1.2" marker-end="url(#pa)"/>'
        for i in range(5))

    LBX = 592   # label column x

    # ===== Pre-compute rebar positions (3" clear from ALL boundary lines) =====
    # Upper stem bar: 3" cover from earth face of 8" blk, 3" from wall top
    USX   = X_8R - CLR3_PX        # 3" from earth face of 8" blk
    US_T  = Y_TOP + CLR3_PX       # 3" from wall top
    US_B  = Y_FTG - CLR3_PX             # 3" from footing top

    # Base bar: 3" cover from earth face of 12" CMU, 3" from CMU top, 3" from ftg bottom
    BBX   = X_CMU - CLR3_PX       # 3" from earth face of 12" CMU
    BB_T  = Y_CMU + CLR3_PX       # 3" from CMU top
    BB_B  = Y_FBT - CLR3_PX       # 3" from footing bottom
    BB_HX = X_HEEL + CLR3_PX      # 3" from heel edge
    BB_BY = Y_FBT - CLR3_PX        # horizontal leg: 3" from footing bottom

    LAP_B = US_B                   # lap zone bottom

    # Key bar: 3" from passive face of key, 3" from key bottom, 3" from footing top
    KBX      = X_HEEL + CLR3_PX   # 3" from key left (passive) face
    KB_B     = Y_KEY - CLR3_PX    # 3" from key bottom
    KB_LEG_Y = Y_FTG + CLR3_PX    # 3" from footing top (horizontal leg inside footing)
    KB_ARC_R = max(4, int(0.25 / 12 * SCALE))
    KB_V_TOP = KB_LEG_Y + KB_ARC_R
    KB_HX2   = KBX + 6 + 80       # free end of 24" leg

    lines_out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg width="760" height="{Y_KEY+30}" viewBox="0 0 760 {Y_KEY+30}" xmlns="http://www.w3.org/2000/svg">',
        '<style>text{font-family:"Courier New",monospace}.sm{font-size:10px}.md{font-size:11px}.lg{font-size:12px;font-weight:bold}</style>',
        '<defs>',
        '<pattern id="ch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '<line x1="0" y1="0" x2="0" y2="7" stroke="#999" stroke-width="0.9"/></pattern>',
        '<pattern id="b8" width="28" height="14" patternUnits="userSpaceOnUse">',
        '<rect width="28" height="14" fill="#f5f5f5" stroke="#aaa" stroke-width="0.7"/>',
        '<line x1="14" y1="0" x2="14" y2="14" stroke="#aaa" stroke-width="0.4"/></pattern>',
        '<pattern id="b12" width="28" height="20" patternUnits="userSpaceOnUse">',
        '<rect width="28" height="20" fill="#eaeaea" stroke="#aaa" stroke-width="0.7"/>',
        '<line x1="14" y1="0" x2="14" y2="20" stroke="#aaa" stroke-width="0.4"/></pattern>',
        '<pattern id="b16" width="28" height="24" patternUnits="userSpaceOnUse">',
        '<rect width="28" height="24" fill="#e0e0e0" stroke="#aaa" stroke-width="0.7"/>',
        '<line x1="14" y1="0" x2="14" y2="24" stroke="#aaa" stroke-width="0.4"/></pattern>',
        '<marker id="da" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">',
        '<path d="M2 1L8 5L2 9" fill="none" stroke="#444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>',
        '<marker id="pa" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">',
        '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>',
        # (clipPath removed — no hatching)
        '</defs>',
        # White background
        f'<rect width="760" height="{Y_KEY+30}" fill="white"/>',
        # Wall-above-earth stub: dashed line on LEFT (flush) face of wall
        f'<line x1="{X_FL}" y1="{Y_TOP}" x2="{X_FL}" y2="{Y_GND}" stroke="#333" stroke-width="1" stroke-dasharray="4 2"/>',
        # 1ft dimension on left side of wall
        dv(X_FL-4, Y_TOP, Y_GND, "1ft", dx=-6),
        # Exposed heel ground (dashed)
        f'<line x1="{X_HEEL-10}" y1="{Y_FTG}" x2="{X_FL}" y2="{Y_FTG}" stroke="#666" stroke-width="1" stroke-dasharray="5 3"/>',
        # Slope symbol and label (no line, no hatching, no ground line)
        slope_els,

        # ===== STRUCTURAL =====
        # Footing
        f'<rect x="{X_HEEL}" y="{Y_FTG}" width="{X_TOE-X_HEEL}" height="{Y_FBT-Y_FTG}" fill="url(#ch)" stroke="#333" stroke-width="1"/>',
        # Key
        f'<rect x="{X_HEEL}" y="{Y_FBT}" width="{X_KEY-X_HEEL}" height="{Y_KEY-Y_FBT}" fill="url(#ch)" stroke="#333" stroke-width="1"/>',
        # 8" block upper stem — concrete if C_upper==1, else CMU block pattern
        f'<rect x="{X_FL}" y="{Y_TOP}" width="{X_8R-X_FL}" height="{Y_CMU-Y_TOP}" '
        f'fill="url({"#ch" if C_upper==1 else "#b8"})" stroke="#555" stroke-width="1"/>',
        # Base course — concrete hatch if C_base==1, else CMU block pattern sized to T_base
        f'<rect x="{X_FL}" y="{Y_CMU}" width="{X_CMU-X_FL}" height="{Y_FTG-Y_CMU}" '
        f'fill="url({"#ch" if C_base==1 else ("#b16" if T_base>=16 else "#b12")})" stroke="#555" stroke-width="1"/>',
        # Step-out line at 8"->12" transition
        f'<line x1="{X_8R}" y1="{Y_CMU}" x2="{X_CMU}" y2="{Y_CMU}" stroke="#555" stroke-width="1"/>',

        # ===== REBAR =====
        # Upper stem bar: 3" cover from earth face, 3" from wall top
        f'<line x1="{USX}" y1="{US_T}" x2="{USX}" y2="{US_B}" stroke="#C0392B" stroke-width="2.4"/>',
        # tick at bottom of upper stem bar
        f'<line x1="{USX-7}" y1="{US_B}" x2="{USX+3}" y2="{US_B}" stroke="#C0392B" stroke-width="2.4"/>',

        # Base bar: 3" cover from earth face, 3" from CMU top, 3" from ftg bottom
        f'<line x1="{BBX}" y1="{BB_T}" x2="{BBX}" y2="{BB_B}" stroke="#C0392B" stroke-width="2.4"/>',
        # bend CW toward heel
        f'<path d="M{BBX},{BB_B} A6,6 0 0 1 {BBX-6},{BB_BY}" fill="none" stroke="#C0392B" stroke-width="2.4"/>',
        # horizontal leg toward heel
        f'<line x1="{BBX-6}" y1="{BB_BY}" x2="{BB_HX}" y2="{BB_BY}" stroke="#C0392B" stroke-width="2.4"/>',
        # 3" clr dim: bar bottom to footing BOTTOM
        f'<line x1="{BBX+4}" y1="{BB_B}" x2="{BBX+4}" y2="{Y_FBT}" stroke="#C0392B" stroke-width="0.7" marker-start="url(#da)" marker-end="url(#da)"/>',
        f'<text class="sm" x="{BBX+8}" y="{BB_B + CLR3_PX//2 + 4}" fill="#C0392B">3&quot;clr</text>',

        # Lap bracket
        f'<line x1="{X_CMU+5}" y1="{Y_CMU}" x2="{X_CMU+5}" y2="{LAP_B}" stroke="#C0392B" stroke-width="0.8" stroke-dasharray="3 2"/>',
        f'<line x1="{X_CMU+3}" y1="{Y_CMU}"  x2="{X_CMU+7}" y2="{Y_CMU}"  stroke="#C0392B" stroke-width="0.8"/>',
        f'<line x1="{X_CMU+3}" y1="{LAP_B}" x2="{X_CMU+7}" y2="{LAP_B}" stroke="#C0392B" stroke-width="0.8"/>',
        f'<text class="sm" x="{X_CMU+9}" y="{(Y_CMU+LAP_B)//2}" dominant-baseline="central" fill="#C0392B">lap</text>',

        # Key bar: 3" from key face/bottom, 24" leg in footing 3" from ftg top
        f'<line x1="{KBX}" y1="{KB_B}" x2="{KBX}" y2="{KB_V_TOP}" stroke="#C0392B" stroke-width="2.4"/>',
        # arc: up→right, CCW (sweep=0)
        f'<path d="M{KBX},{KB_V_TOP} A{KB_ARC_R},{KB_ARC_R} 0 0 1 {KBX+KB_ARC_R},{KB_LEG_Y}" fill="none" stroke="#C0392B" stroke-width="2.4"/>',
        # 24" horizontal leg inside footing at 2" below ftg top — NO tick
        f'<line x1="{KBX+KB_ARC_R}" y1="{KB_LEG_Y}" x2="{KB_HX2}" y2="{KB_LEG_Y}" stroke="#C0392B" stroke-width="2.4"/>',
        # 24" dim
        f'<line x1="{KBX+KB_ARC_R}" y1="{KB_LEG_Y+14}" x2="{KB_HX2}" y2="{KB_LEG_Y+14}" stroke="#C0392B" stroke-width="0.7" marker-start="url(#da)" marker-end="url(#da)"/>',
        f'<text class="sm" x="{(KBX+KB_ARC_R+KB_HX2)//2}" y="{KB_LEG_Y+24}" text-anchor="middle" fill="#C0392B">24&quot;</text>',
        # 2" clr dim: from footing top to key bar leg
        f'<line x1="{KB_HX2+4}" y1="{Y_FTG}" x2="{KB_HX2+4}" y2="{KB_LEG_Y}" stroke="#C0392B" stroke-width="0.7" marker-start="url(#da)" marker-end="url(#da)"/>',
        f'<text class="sm" x="{KB_HX2+8}" y="{Y_FTG + CLR2_PX//2 + 3}" fill="#C0392B">2&quot;clr</text>',

        # ===== EARTH PRESSURE ARROWS =====
        ep,

        # ===== PASSIVE PRESSURE ARROWS =====
        f'<line x1="{X_HEEL-22}" y1="{Y_FBT+18}" x2="{X_HEEL-1}" y2="{Y_FBT+18}" stroke="#5577AA" stroke-width="1.2" marker-end="url(#pa)"/>',
        f'<line x1="{X_HEEL-26}" y1="{Y_FBT+36}" x2="{X_HEEL-1}" y2="{Y_FBT+36}" stroke="#5577AA" stroke-width="1.2" marker-end="url(#pa)"/>',
        f'<text class="sm" x="{X_HEEL-28}" y="{Y_FBT+16}" text-anchor="end" fill="#5577AA">passive</text>',

        # ===== DIMENSIONS =====
        dv(X_HEEL-30, Y_FTG, Y_GND, f"H={RET_H:.1f}ft", dx=-8),
        dh(X_HEEL, X_TOE, Y_KEY+16, f"B={B_val:.2f}ft"),
        dh(X_HEEL, X_FL,  Y_KEY+4,  "heel"),
        dh(X_CMU,  X_TOE, Y_KEY+4,  f"toe {ti}&quot;"),
        dh(X_FL,   X_8R,  Y_TOP-18, upper_dim),
        dh(X_FL,   X_CMU, Y_FBT+10, base_dim),
        dv(X_FL-18, Y_CMU, Y_FTG, f'{CMU_HT_IN}&quot;'),
        dv(X_TOE+8, Y_FTG, Y_FBT, f'{T_base_in:.0f}&quot;ftg'),

        # ===== STRUCTURAL LABELS =====
        f'<text class="sm" x="{X_FL-4}" y="{(Y_TOP+Y_CMU)//2+4}" text-anchor="end" fill="#333">flush face</text>',
        f'<text class="sm" x="{X_8R+3}" y="{Y_TOP+40}" fill="#333">earth face</text>',
        f'<text class="sm" x="{X_FL-4}" y="{Y_TOP+62}" text-anchor="end" fill="#666">{upper_lbl}</text>',
        f'<text class="sm" x="{X_FL-4}" y="{Y_CMU+48}" text-anchor="end" fill="#666">{base_lbl}</text>',
        f'<text class="sm" x="{(X_HEEL+X_FL)//2}" y="{Y_FTG-7}" text-anchor="middle" fill="#555">heel (turns out)</text>',
        f'<text class="sm" x="{(X_CMU+X_TOE)//2}" y="{Y_FTG-7}" text-anchor="middle" fill="#555">toe</text>',
        f'<text class="sm" x="{(X_HEEL+X_KEY)//2}" y="{Y_FBT+38}" text-anchor="middle" fill="#555">key</text>',

        # ===== RIGHT-SIDE REBAR LABELS =====
        f'<text class="sm" x="{LBX}" y="{(Y_TOP+Y_CMU)//2-6}" fill="#C0392B">upper stem bar</text>',
        f'<text class="sm" x="{LBX}" y="{(Y_TOP+Y_CMU)//2+8}" fill="#C0392B">({upper_lbl}, earth face)</text>',
        f'<line x1="{X_8R-4}" y1="{(Y_TOP+Y_CMU)//2}" x2="{LBX-2}" y2="{(Y_TOP+Y_CMU)//2}" stroke="#C0392B" stroke-width="0.5" stroke-dasharray="3 2"/>',
        f'<text class="sm" x="{LBX}" y="{(Y_CMU+Y_FTG)//2-8}" fill="#C0392B">{base_bar_lbl}</text>',
        f'<text class="sm" x="{LBX}" y="{(Y_CMU+Y_FTG)//2+6}" fill="#C0392B">earth face / 3&quot;clr</text>',
        f'<text class="sm" x="{LBX}" y="{(Y_CMU+Y_FTG)//2+20}" fill="#C0392B">bends to heel</text>',
        f'<line x1="{X_CMU-5}" y1="{(Y_CMU+Y_FTG)//2}" x2="{LBX-2}" y2="{(Y_CMU+Y_FTG)//2}" stroke="#C0392B" stroke-width="0.5" stroke-dasharray="3 2"/>',
        f'<text class="sm" x="{LBX}" y="{Y_CMU+34}" fill="#C0392B">lap splice</text>',
        f'<line x1="{X_CMU+4}" y1="{Y_CMU+30}" x2="{LBX-2}" y2="{Y_CMU+30}" stroke="#C0392B" stroke-width="0.5" stroke-dasharray="3 2"/>',
        f'<text class="sm" x="{LBX}" y="{(Y_FBT+Y_KEY)//2-4}" fill="#C0392B">key bar L-shape</text>',
        f'<text class="sm" x="{LBX}" y="{(Y_FBT+Y_KEY)//2+10}" fill="#C0392B">passive face / 24&quot;</text>',
        f'<line x1="{KBX}" y1="{(Y_FBT+Y_KEY)//2}" x2="{LBX-2}" y2="{(Y_FBT+Y_KEY)//2}" stroke="#C0392B" stroke-width="0.5" stroke-dasharray="3 2"/>',

        # ===== LEGEND =====
        f'<line x1="{LBX}" y1="440" x2="{LBX+24}" y2="440" stroke="#C0392B" stroke-width="2.4"/>',
        f'<text class="sm" x="{LBX+28}" y="444" fill="#C0392B">rebar</text>',
        f'<line x1="{LBX+24}" y1="454" x2="{LBX+24}" y2="466" stroke="#C0392B" stroke-width="2.4"/>',
        f'<text class="sm" x="{LBX+28}" y="464" fill="#C0392B">bar end (tick)</text>',
        f'<line x1="{LBX}" y1="478" x2="{LBX+24}" y2="478" stroke="#5577AA" stroke-width="1.5" marker-end="url(#pa)"/>',
        f'<text class="sm" x="{LBX+28}" y="482" fill="#5577AA">passive pressure</text>',
        f'<line x1="{LBX}" y1="494" x2="{LBX+24}" y2="494" stroke="#888" stroke-width="1.5" marker-end="url(#pa)"/>',
        f'<text class="sm" x="{LBX+28}" y="498" fill="#888">earth pressure</text>',

        # ===== TYPE 1 NOTE =====
        f'<text class="lg" x="{LBX}" y="{Y_TOP+2}" fill="#222">TYPE 1 WALL</text>',
        f'<text class="sm" x="{LBX}" y="{Y_TOP+16}" fill="#555">Flush face opp. earth</text>',
        f'<text class="sm" x="{LBX}" y="{Y_TOP+30}" fill="#555">Ftg turns out (heel)</text>',
        '</svg>',
    ]
    return '\n'.join(lines_out)


def _type1_svg_string():
    global H1, B, E, L2, T, G, C, TABLE_ROWS
    C_base   = int(C[G]) if G > 0 else 0
    C_upper  = int(C[1]) if G > 0 else 0
    bar_upper = _get_upper_bar(TABLE_ROWS)
    return _build_type1_svg(H1, B, E, L2, T[G], C_base, C_upper, bar_upper)


def show_type1_diagram(svg_path=None):
    global H1, B, E, L2, T, G, C, TABLE_ROWS
    if svg_path is None:
        svg_path = "type1_wall_detail.svg"
    C_base    = int(C[G]) if G > 0 else 0
    C_upper   = int(C[1]) if G > 0 else 0
    bar_upper = _get_upper_bar(TABLE_ROWS)
    svg = _build_type1_svg(H1, B, E, L2, T[G], C_base, C_upper, bar_upper)
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(svg.split('\n', 1)[1])
    except Exception as xe:
        print(f"  WARNING: SVG XML issue: {xe}")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    if svg_path == "type1_wall_detail.svg":
        print(f"\n  Type 1 wall detail diagram saved to: {svg_path}")
        try:
            import cairosvg
            png = "type1_wall_detail.png"
            cairosvg.svg2png(url=svg_path, write_to=png, output_width=1400)
            print(f"  PNG version saved to:               {png}")
        except ImportError:
            print("  (Install cairosvg for PNG: pip install cairosvg)")
        print("  Open SVG in any web browser, or PNG in any image viewer.")



if __name__ == "__main__":
    main()
