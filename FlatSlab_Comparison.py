import math
import os

# ============ CODE CONSTANTS (ACI 318-19 / ASCE 7-22) ============
PHI_FLEX = 0.9          # Tension-controlled flexure
PHI_SHEAR = 0.75        # Shear
LAMBDA = 1.0            # Normal weight concrete
FC_psi = 4000           # Default concrete strength (psi)
FY_psi = 60000          # Default steel strength (psi)

# ============ 1-INDEXED ARRAY HELPERS (FIDELITY TO ORIGINAL BASIC) ============
def arr1d(n): return [0.0] * (n + 1)
def arr2d(r, c): return [[0.0] * (c + 1) for _ in range(r + 1)]
def clear(): os.system("cls" if os.name == "nt" else "clear")
def fnb(a): return 3.1416 * a * a / 256  # Bar area formula (original)

# ============ GLOBALS (PRESERVED FROM ORIGINAL + UPDATED) ============
SIZE = 17
L = arr1d(SIZE); W = arr1d(SIZE); SB = arr1d(SIZE); MS = arr1d(SIZE)
MP = arr1d(SIZE); MPR = arr1d(SIZE); MPD = arr2d(SIZE, 2)
MF = arr2d(SIZE, 2); MT = arr2d(SIZE, 2); MB = arr2d(SIZE, 2)
MC = arr2d(SIZE, 2); ME = arr2d(SIZE, 2); MER = arr2d(SIZE, 2)
A = arr1d(8)
NS_s = [""] * (SIZE + 1)

# Input variables
BC = BL = BR = 0.0
T_in = D_in = 0.0  # Slab thickness, effective depth (in)
FC_ksi = FY_ksi = 0.0  # Input in KSI, converted to psi later
DL_psf = LL_psf = 0.0  # Dead/Live load (psf)
B = 0.0  # Current strip width
AMIN = MMIN = 0.0
BL1 = BR1 = 0.0
A7_val = L2 = A8 = 0.0
N1 = N2 = N3 = 0
D1 = D2 = D3 = 0
S1 = 0.0
NS = FSC = LSC = 0
SL_s = ""

# Moment storage for comparison
iter_neg_mom = arr2d(SIZE, 2)  # Iterative method moments
iter_pos_mom = arr1d(SIZE)
aci_neg_mom = arr2d(SIZE, 2)   # ACI Approx moments
aci_pos_mom = arr1d(SIZE)

# ============ ACI 318-19 REINFORCEMENT HELPERS ============
def calc_aci_min_as(b, d, fc, fy):
    """ACI 318-19 §9.6.1.2: Minimum flexural reinforcement"""
    as1 = 0.0018 * math.sqrt(fc) / fy * b * d
    as2 = 0.0014 * b * d
    as3 = 0.0018 * b * d  # Original 1985 default
    return max(as1, as2, as3)

def calc_aci_as_required(Mu_kip_in, b, d, fc, fy):
    """ACI 318-19 §22.4: Required As via strain compatibility"""
    if Mu_kip_in == 0: return 0.0, 0.0
    Mu = abs(Mu_kip_in)
    # Solve for a: Mu = phi * As * fy * (d - a/2), a = As*fy/(0.85*fc*b)
    # Quadratic: 0.85*fc*b/(2*phi*fy) * a² - (0.85*fc*b*d/phi*fy) * a + Mu = 0
    A_coeff = 0.85 * fc * b / (2 * PHI_FLEX * fy)
    B_coeff = - (0.85 * fc * b * d) / (PHI_FLEX * fy)
    C_coeff = Mu
    disc = B_coeff**2 - 4*A_coeff*C_coeff
    if disc < 0: return 0.0, 0.0
    a = (-B_coeff + math.sqrt(disc)) / (2 * A_coeff)
    As = a * 0.85 * fc * b / fy
    return As, a

def select_rebar(As_req, b, d, fc, fy):
    """Select bar size/spacing for both methods"""
    bar_data = {
        3: (0.375, 0.11), 4: (0.5, 0.2), 5: (0.625, 0.31),
        6: (0.75, 0.44), 7: (0.875, 0.6), 8: (1.0, 0.79),
        9: (1.128, 1.0), 10: (1.27, 1.27), 11: (1.41, 1.56)
    }
    max_spacing = min(2 * T_in, 18)  # ACI 318-19 §9.7.3
    best = None
    for sz, (db, area) in bar_data.items():
        s_req = (area / As_req) * b if As_req > 0 else 999
        s_req = min(s_req, max_spacing)
        if s_req >= 3:  # Minimum 3" spacing
            s_rounded = math.ceil(s_req * 2) / 2  # Round to 0.5"
            n_bars = b / s_rounded + 1
            if best is None or s_rounded > best[1]:
                best = (sz, s_rounded, area, n_bars)
    if best:
        sz, s, area, n = best
        return sz, s, area * n, n
    return 0, 0, 0, 0

# ============ ORIGINAL ITERATIVE MOMENT DISTRIBUTION (UPDATED TO ACI) ============
def run_iterative_moment_distribution(w_u):
    """Preserves original 6-iteration MD, uses factored load w_u (K/FT)"""
    global ME, MER, MP, MPR, MT, MC, MB, MF, R_arr, iter_neg_mom, iter_pos_mom, NS, FSC, LSC, SB, BC, BL, BR
    # Reset moments
    R_arr = arr2d(SIZE, 2)
    for i in range(SIZE+1):
        for j in range(3):
            ME[i][j] = MER[i][j] = MP[i] = MPR[i] = 0
            MT[i][j] = MF[i][j] = MB[i][j] = MC[i][j] = 0
            iter_neg_mom[i][j] = iter_pos_mom[i] = 0

    # End conditions (preserved from original)
    if FSC == 1:  # Cantilever left
        MF[2][1] = -6 * w_u[1] * L[1]**2
        DF_2_1 = 0; DF_2_2 = 1
        R_arr[2][1] = w_u[1] * L[1]
    elif FSC == 2:  # Fixed left
        DF_2_1 = 1; DF_2_2 = 0
    elif FSC == 3:  # Pinned left
        DF_2_1 = 0; DF_2_2 = 1
    else:
        DF_2_1 = 0; DF_2_2 = 0

    if LSC == 1:  # Cantilever right
        MF[NS+2][2] = 6 * w_u[NS+2] * L[NS+2]**2
        DF_NS2_1 = 1; DF_NS2_2 = 0
        R_arr[NS+2][2] = w_u[NS+2] * L[NS+2]
    elif LSC == 2:  # Fixed right
        DF_NS2_1 = 0; DF_NS2_2 = 1
    elif LSC == 3:  # Pinned right
        DF_NS2_1 = 1; DF_NS2_2 = 0
    else:
        DF_NS2_1 = 0; DF_NS2_2 = 0

    # Distribution factors (preserved)
    DF = arr2d(SIZE, 2)
    if FSC == 1 or FSC == 2 or FSC == 3:
        DF[2][1] = DF_2_1; DF[2][2] = DF_2_2
    if LSC == 1 or LSC == 2 or LSC == 3:
        DF[NS+2][1] = DF_NS2_1; DF[NS+2][2] = DF_NS2_2

    for i in range(2, NS+1):
        total_L = L[i] + L[i+1]
        if total_L > 0:
            DF[i+1][1] = round((L[i+1]/total_L + 0.005) * 100) / 100
        else:
            DF[i+1][1] = 0
        DF[i+1][2] = 1 - DF[i+1][1]

    # Fixed end moments (using factored load)
    for i in range(2, NS+2):
        MF[i][2] = w_u[i] * L[i]**2
        MF[i+1][1] = -MF[i][2]
        MS = 1.5 * w_u[i] * L[i]**2
        R_arr[i][2] = w_u[i] * L[i]/2
        R_arr[i+1][1] = R_arr[i][2]

    # Initialize MT/ME (fixed original bug)
    for i in range(2, NS+3):
        for j in range(1,3):
            MT[i][j] = MF[i][j]
            ME[i][j] = 0

    # 6 iterations (preserved from original)
    for _ in range(6):
        for i in range(2, NS+3):
            MB[i][1] = -(MT[i][1] + MT[i][2]) * DF[i][1]
            MB[i][2] = -(MT[i][1] + MT[i][2]) * DF[i][2]
        for i in range(2, NS+3):
            MC[i][1] = MB[i-1][2]/2 if i>2 else 0
            MC[i][2] = MB[i+1][1]/2 if i<NS+2 else 0
        for i in range(2, NS+3):
            for j in range(1,3):
                ME[i][j] += MT[i][j] + MB[i][j]
                MT[i][j] = MC[i][j]

    # Reaction adjustment
    for i in range(2, NS+2):
        V = (ME[i][2] + ME[i+1][1]) / (L[i]*12)
        if V < 0: R_arr[i+1][1] -= V
        else: R_arr[i][2] += V

    # Reduced moments at column face
    for i in range(3, NS+2):
        for j in range(1,3):
            if ME[i][j] >=0:
                MER[i][j] = ME[i][j] - R_arr[i][j] * SB[i]/3
            else:
                MER[i][j] = ME[i][j] + R_arr[i][j] * SB[i]/3
    # Boundary conditions
    if FSC !=0:
        MER[2][1] = ME[2][1]; MER[2][2] = ME[2][2]
    if LSC !=0:
        MER[NS+2][1] = ME[NS+2][1]; MER[NS+2][2] = ME[NS+2][2]

    # Positive moments
    for i in range(2, NS+2):
        MP[i] = (1.5*w_u[i]*L[i]**2) - ME[i][2]/2 + ME[i+1][1]/2
        sgn = 1 if MP[i]>=0 else -1
        MPR[i] = MP[i] - sgn*(R_arr[i][2]*SB[i] + R_arr[i+1][1]*SB[i+1])/12

    # Store for comparison (convert K-ft to K-ft for output)
    for i in range(2, NS+3):
        iter_neg_mom[i][1] = MER[i][1]
        iter_neg_mom[i][2] = MER[i][2]
    for i in range(2, NS+2):
        iter_pos_mom[i] = MPR[i]

# ============ ACI 318-19 APPROXIMATE MOMENT METHOD ============
def run_aci_approx_moments(w_u):
    """ACI 318-19 Table 6.5.1: Approximate moments for continuous slabs"""
    global aci_neg_mom, aci_pos_mom, NS, FSC, LSC, L
    for i in range(SIZE+1):
        for j in range(3): aci_neg_mom[i][j] = 0
        aci_pos_mom[i] = 0

    for i in range(2, NS+2):
        L_ft = L[i]
        # Negative moments
        if i == 2:  # First span
            if FSC == 1:  # Cantilever left
                aci_neg_mom[i][1] = -0.5 * w_u[i] * L_ft**2  # Cantilever moment
            else:  # Exterior support
                aci_neg_mom[i][2] = w_u[i] * L_ft**2 / 16  # ACI Eq 6.5.1(a)
        else:  # Interior support
            aci_neg_mom[i][2] = w_u[i] * L_ft**2 / 10  # ACI Eq 6.5.1(b)
            aci_neg_mom[i+1][1] = aci_neg_mom[i][2]  # Shared support

        # Positive moment (span)
        aci_pos_mom[i] = w_u[i] * L_ft**2 / 16  # ACI Eq 6.5.1(c)

        # Last span adjustment
        if i == NS+1:
            if LSC ==1:  # Cantilever right
                aci_neg_mom[NS+2][2] = 0.5 * w_u[NS+2] * L[NS+2]**2
            else:
                aci_neg_mom[NS+2][1] = w_u[i] * L_ft**2 / 16

# ============ ORIGINAL REBAR SUBROUTINES (UPDATED TO ACI) ============
def sr_min_as():
    global AMIN, MMIN, B, D_in, FC_psi, FY_psi, FC_ksi
    # Updated to ACI 318-19 + original defaults
    AMIN = calc_aci_min_as(B, D_in, FC_psi, FY_psi)
    if 1.7 * B * FC_ksi ==0: MMIN=0
    else: MMIN = AMIN * 0.9 * FY_ksi * (D_in - (AMIN * FY_ksi)/(1.7*B*FC_ksi))

def sr_2260():
    global A, B, D_in, FC_ksi, FY_ksi
    A[6] = A[1] * (100 - A[2])/100
    d_ = 0.9 * B * D_in * D_in * FC_ksi
    if d_ ==0: A[7]=0
    else:
        rad = 1 - 2.36*A[6]/d_
        if rad <0: rad=0
        A[7] = FC_ksi * (1 - math.sqrt(rad)) / (1.18 * FY_ksi)
    A[8] = A[7] * B * D_in

def sr_rebar():
    global A, B, D_in, FC_ksi, FY_ksi, D1,D2,D3,N3,N1,N2,S1, AMIN
    # Updated to ACI phi factors
    d_ = 0.9 * B * D_in * D_in * FC_ksi
    if d_ !=0 and 2.36*A[3]/d_ <1:
        rad = 1 - 2.36*A[3]/d_
        if rad <0: rad=0
        A[4] = FC_ksi * (1 - math.sqrt(rad)) / (1.18 * FY_ksi)
    else:
        A[4] = FC_ksi/(1.18 * FY_ksi)
    A[5] = B * D_in * A[4]

    if A[5] <=0:
        A[4]=abs(A[4]); A[5]=abs(A[5])
        D1=5; D2=D1+1
        N1=A[5]/fnb(D1) if fnb(D1) else 0
        N2=0; N3=3; return

    if AMIN >= A[5]:
        D1=5; D2=D1+1
        N1=AMIN/fnb(D1) if fnb(D1) else 0
        N2=0; N3=0
        # Updated to ACI spacing
        denom = AMIN *12 / B if B else 0
        S1 = fnb(D1)*12/denom if denom else 0
        S1 = int(S1*2)/2; D3=D1; return

    if AMIN >= A[8]:
        D1=5
        while True:
            N1=(A[5]-AMIN)/fnb(D1)
            N3=1
            if N1<9 or D1>=8: break
            D1=D1+1
        D2=D1+1; N2=(A[5]-AMIN)/fnb(D2)
    else:
        # Updated spacing for ACI
        denom = A[7]*12*D_in
        S1 = fnb(D1)*12/denom if denom else 0
        S1 = int(S1*2)/2; D3=D1
        D1=5
        while True:
            N1=(A[5]-A[8])/fnb(D1)
            N3=2
            if N1<10 or D1>=8: break
            D1=D1+1
        D2=D1+1; N2=(A[5]-A[8])/fnb(D2)

# ============ COMPARISON OUTPUT ============
def print_comparison():
    clear()
    print("="*120)
    print(f"SLAB LINE: {SL_s} | F'c={FC_ksi} KSI | F'y={FY_ksi} KSI | T={T_in} IN | D={D_in} IN")
    print("="*120)
    print("MOMENT COMPARISON (FACTORED K-FT) | ITERATIVE MD vs ACI 318-19 APPROX")
    print("-"*120)
    print(f"{'LOCATION':<20} {'ITER NEG (K-ft)':<20} {'ACI NEG (K-ft)':<20} {'DIFF (%)':<10} {'ITER POS (K-ft)':<20} {'ACI POS (K-ft)':<20} {'DIFF (%)':<10}")
    print("-"*120)

    # Supports (negative moments)
    for i in range(2, NS+3):
        loc = f"Support {NS_s[i]}"
        iter_n1 = iter_neg_mom[i][1]; iter_n2 = iter_neg_mom[i][2]
        aci_n1 = aci_neg_mom[i][1]; aci_n2 = aci_neg_mom[i][2]
        # Use max negative moment for comparison
        iter_n = max(abs(iter_n1), abs(iter_n2))
        aci_n = max(abs(aci_n1), abs(aci_n2))
        diff_n = ((iter_n - aci_n)/aci_n *100) if aci_n !=0 else 0

        # Positive moments
        iter_p = abs(iter_pos_mom[i-1]) if i<NS+2 else 0
        aci_p = abs(aci_pos_mom[i-1]) if i<NS+2 else 0
        diff_p = ((iter_p - aci_p)/aci_p *100) if aci_p !=0 else 0

        print(f"{loc:<20} {iter_n:<20.1f} {aci_n:<20.1f} {diff_n:<10.1f} {iter_p:<20.1f} {aci_p:<20.1f} {diff_p:<10.1f}")

    print("\nREINFORCEMENT COMPARISON (COLUMN STRIP)")
    print("-"*120)
    print(f"{'LOCATION':<20} {'ITER As (in²)':<15} {'ACI As (in²)':<15} {'ITER BAR':<20} {'ACI BAR':<20}")
    print("-"*120)

    B_col = BC  # Column strip width
    for i in range(2, NS+3):
        # Iterative method rebar
        A[1] = max(abs(iter_neg_mom[i][1]), abs(iter_neg_mom[i][2]))
        A[2] = 76; A[3] = A[1]*A[2]/100
        sr_2260(); sr_rebar()
        iter_As = A[5]
        iter_bar = f"#{D3}@{S1}\"" if D3 else "N/A"

        # ACI method rebar
        aci_M = max(abs(aci_neg_mom[i][1]), abs(aci_neg_mom[i][2])) *12  # Convert K-ft to K-in
        aci_As, _ = calc_aci_as_required(aci_M, BC, D_in, FC_psi, FY_psi)
        aci_As = max(aci_As, calc_aci_min_as(BC, D_in, FC_psi, FY_psi))
        sz, s, total_As, n = select_rebar(aci_As, BC, D_in, FC_psi, FY_psi)
        aci_bar = f"#{sz}@{s}\"" if sz else "N/A"

        print(f"Support {NS_s[i]:<15} {iter_As:<15.2f} {aci_As:<15.2f} {iter_bar:<20} {aci_bar:<20}")

# ============ INPUT (UPDATED TO ACI LOAD FACTORS) ============
def get_input():
    global SL_s, NS, FC_ksi, FY_ksi, T_in, D_in, BC, BL, BR, FSC, LSC, FC_psi, FY_psi
    global DL_psf, LL_psf, w_u, L, W, SB, NS_s
    clear()
    print("FLAT SLAB DESIGN | ITERATIVE MD + ACI 318-19 APPROX COMPARISON")
    print("-"*80)
    SL_s = input("SLAB LINE ID: ")
    NS = int(input("# OF SPANS (MAX 14): "))
    if NS>14: NS=14

    # Material inputs
    FC_ksi = float(input("F'c (KSI) [4]: ") or 4)
    FY_ksi = float(input("F'y (KSI) [60]: ") or 60)
    FC_psi = FC_ksi * 1000
    FY_psi = FY_ksi * 1000

    T_in = float(input("SLAB THICKNESS T (IN): "))
    D_in = float(input("EFFECTIVE DEPTH D (IN): "))

    # Load inputs (ASCE 7-22)
    DL_psf = float(input("DEAD LOAD (PSF, INCL. SLAB SELF-WEIGHT): "))
    LL_psf = float(input("LIVE LOAD (PSF): "))
    w_d = DL_psf / 1000  # K/FT per 1-ft strip
    w_l = LL_psf / 1000
    w_u = 1.2*w_d + 1.6*w_l  # LRFD factored load

    # Strip widths
    BC = float(input("COLUMN STRIP WIDTH B (IN): "))
    BL = float(input("LEFT MID STRIP WIDTH B(L) (IN): "))
    BR = float(input("RIGHT MID STRIP WIDTH B(R) (IN): "))

    # Supports
    for i in range(2, NS+3):
        NS_s[i] = input(f"SUPPORT #{i-1} NAME: ")
        SB[i] = float(input(f"COL/CAP WIDTH AT {NS_s[i]} (IN): "))

    # End conditions
    print("\nFIRST SPAN END CONDITION: 1=CANT, 2=FIXED, 3=PINNED")
    FSC = int(input("CHOICE: "))
    if FSC ==1:
        L[1] = float(input("CANTILEVER L (FT): "))
        W[1] = w_u  # Use factored load
    for i in range(2, NS+2):
        print(f"\nSPAN {NS_s[i]} - {NS_s[i+1]}")
        L[i] = float(input("L (FT): "))
        W[i] = w_u  # Use factored load
    print("\nLAST SPAN END CONDITION: 1=CANT, 2=FIXED, 3=PINNED")
    LSC = int(input("CHOICE: "))
    if LSC ==1:
        L[NS+2] = float(input("CANTILEVER L (FT): "))
        W[NS+2] = w_u

    return w_u

# ============ MAIN ============
def main():
    w_u = get_input()
    # Prepare load array for iterative method
    w_u_arr = arr1d(SIZE)
    for i in range(1, NS+3):
        w_u_arr[i] = w_u
    # Run both moment methods
    run_iterative_moment_distribution(w_u_arr)
    run_aci_approx_moments(w_u)
    # Print comparison
    print_comparison()
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
