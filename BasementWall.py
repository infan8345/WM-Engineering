#!/usr/bin/env python3
"""
BASEMENT WALL PROGRAM
Original: BWMNSCRN.BAS (GW-BASIC)
Converted to Python
REV. 2-9-85
"""

import math

P1 = "  (IN)"
P2 = "  (FT)"
P3 = "  (PSF)"
P4 = "  (LB)"
P5 = "  (LB/CF)"

def get_float(prompt, default=0):
    val = input(prompt)
    return float(val) if val else default

def get_int(prompt, default=0):
    val = input(prompt)
    return int(val) if val else default

def input_sr():
    """INPUT S.R. - Input design parameters"""
    print()
    print(" BASEMENT WALL PROGRAM")
    print("="*50)
    
    print("\n  INPUT S.R.")
    print("-"*30)
    
    H1 = get_float("WALL HT. = (FT) : ")
    H3 = get_float("RETAIN'G EARTH HT. = (FT) : ")
    J = get_float("EQUIV. FLUID PRESSURE = 30 (#/CF) : ", 30)
    S1 = get_float("SURCHARGE (FT) = (X) : ")
    C = get_int("CONC. WALL (0 OR 1) : ")
    
    if C == 1:
        T = "CONC. "
    else:
        T = "BLK. "
    
    C1 = get_int("CONT. INSPECTION (0 OR 1) : ")
    
    if C1 == 0:
        N1 = 2000
        F1 = 1350
    else:
        N1 = 2000
        F1 = 2000
    
    I = get_float("CONC. F'C=2000 (PSI) : ", 2000)
    F2 = I
    
    J = get_float("WALL T = 8 (IN) : ", 8)
    T = J
    D = get_float("D = (IN) : ", 6)
    V = get_float("VERT. LOAD = (K/FT) : ", 0)
    D9 = get_int("BAR SIZE #- : ", 4)
    S9 = get_float("BAR SPACING : ", 12)
    Y = get_float("STEEL ALLOWABLE = 20 (KSI) : ", 20)
    U = get_int("PRINT (0 OR 1) : ", 1)
    
    if Y == 0: Y = 20
    if D == 0: D = 6
    
    print(" END INPUT S.R.")
    
    return calc_sr(H1, H3, J, S1, N1, F1, I, F2, T, D, V, D9, S9, Y, U, C, C1)

def calc_sr(H1, H3, P, S1, N1, F1, I, F2, T, D, V, D9, S9, Y, U, C, C1):
    """CALC S.R. - Calculate results"""
    
    P = P * (H3 + S1)
    R1 = P * (H3 + S1) / 2
    R2 = P * (H3 + S1) / 2
    X1 = S1 + (H3 * (H3 + 2 * S1)) / (3 * (H3 + S1))
    M = R1 * X1
    
    A2 = (12 * M) / (Y * 1000 * D)
    
    def calc_for_fm():
        """CALC FOR F'M"""
        F3 = M * 12 / (I * T * T / 2)
        
        bar_areas = {
            3: 0.11,
            4: 0.20,
            5: 0.31,
            6: 0.44,
            7: 0.60,
            8: 0.79,
            9: 1.00,
            10: 1.27,
            11: 1.56,
            14: 2.25
        }
        
        A = bar_areas.get(D9, 0.20) * 12 / S9
        F5 = F1
        F6 = (V * 1000) / (T * D)
        F8 = F6 + F3
        
        return F3, A, F5, F6, F8
    
    F3, A, F5, F6, F8 = calc_for_fm()
    
    F7 = F8
    
    if U == 1:
        print_results(P, R1, R2, X1, M, D, A2, D9, S9, A, F3, F5, F6, F8, C, C1, H1, H3, P, S1, Y, V)
    
    return {
        'P': P,
        'R1': R1,
        'R2': R2,
        'X1': X1,
        'M': M,
        'D': D,
        'A2': A2,
        'A': A,
        'F3': F3,
        'F5': F5,
        'F6': F6,
        'F8': F8
    }

def print_results(P, R1, R2, X1, M, D, A2, D9, S9, A, F3, F5, F6, F8, C, C1, H1, H3, P_orig, S1, Y, V):
    """PRINT S.R. - Print results"""
    print()
    print(" BASEMENT WALL DESIGN")
    print("="*50)
    
    print(f"WALL HEIGHT             = {H1} (FT)")
    print(f"RET. EARTH HEIGHT       = {H3} (FT)")
    print(f"EQUIV. FLUID PRESSURE   = {P_orig} (LB/CF)")
    print(f"SURCHARGE              = {S1} (FT)")
    print(f"ALLOWABLE STL. STRESS  = {Y} (KSI)")
    print(f"VERT. LOAD             = {V} (K/FT)")
    
    print()
    print(f"TOTAL EARTH PRESSURE    = {P} (LB)")
    print(f"R(T)                   = {R1:.2f} (LB)")
    print(f"R(B)                   = {R2:.2f} (LB)")
    print(f"X                      = {X1:.3f} (FT)")
    print(f"M                      = {M:.2f} (IN-K)")
    print(f"D                      = {D:.2f} (IN)")
    print(f"AS (REQ'D)             = {A2:.4f} (SQ-IN/FT)")
    print(f"USE #{D9} @ {S9:.2f} O.C.")
    print(f"AS (FURNISH)          = {A:.4f} (SQ-IN/FT)")
    print(f"F(B)                   = {F3:.2f} (PSI)")
    
    if C == 1:
        print(f"F'(B)                  = {F5:.2f} (PSI)")
    
    print(f"F(A)                   = {F6:.2f} (PSI)")
    print(f"F'(A)                  = {F8:.2f} (PSI)")
    print(f"F(A)/F'(A) + F(B)/F'(B) = {F6/F8 + F3/F5:.4f}")
    
    if C1 == 0:
        print("(NO CONT. INSPECTION)")
    else:
        print("(CONT. INSPECTION REQ'D)")

def main():
    """Main program"""
    while True:
        result = input_sr()
        print("\nCalculate another? (Y/N): ", end="")
        resp = input().upper()
        if resp != "Y":
            break

if __name__ == "__main__":
    main()