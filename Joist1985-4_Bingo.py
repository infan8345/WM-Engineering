#!/usr/bin/env python3
"""
JSTSCRN8.BAS - Joist Table Program (Floor/Roof)
UPDATED: Follows NDS 2018/2024 standards with Douglas Fir-Larch (North) as default
Includes adjustment factors: CD, CM, Ct, CL, CF, Cr, Ci
NOW WITH NOMINAL DIMENSION INPUT (2x4, 2x6, 2x8, 2x10, 2x12)
"""

import math
import re
import sys

# ----------------------------------------------------------------------
# DIM statements
L = [[0.0] * 20 for _ in range(14)]
L1 = [[0.0] * 20 for _ in range(14)]
L2 = [[0.0] * 20 for _ in range(14)]
F = [0.0] * 14
E = [0.0] * 14
D = [0.0] * 15
D9 = [0.0] * 14
S = [0.0] * 16

W = [0.0] * 27
W_str = [""] * 15
A9_str = ""

# Initialize spacing values (inches O.C.)
S[11] = 24   # 24" O.C.
S[12] = 16   # 16" O.C.  
S[13] = 12   # 12" O.C.
S[14] = 19   # 19" O.C.

P9 = 1

W_str[1] = " D.L."
W_str[2] = " L.L."
W_str[3] = " T.L."

# ----------------------------------------------------------------------
# Nominal to Actual Dimension Conversion (inches)

NOMINAL_TO_ACTUAL = {
    # Width conversions (for dimension lumber)
    "2x": 1.5,    # 2x lumber actual width
    "3x": 2.5,    # 3x lumber actual width
    "4x": 3.5,    # 4x lumber actual width
    "6x": 5.5,    # 6x lumber actual width
    
    # Depth conversions for common sizes
    "2x2": (1.5, 1.5),
    "2x3": (1.5, 2.5),
    "2x4": (1.5, 3.5),
    "2x5": (1.5, 4.5),
    "2x6": (1.5, 5.5),
    "2x7": (1.5, 6.25),
    "2x8": (1.5, 7.25),
    "2x9": (1.5, 8.25),
    "2x10": (1.5, 9.25),
    "2x11": (1.5, 10.25),
    "2x12": (1.5, 11.25),
    "2x14": (1.5, 13.25),
    "2x16": (1.5, 15.25),
    
    "3x4": (2.5, 3.5),
    "3x6": (2.5, 5.5),
    "3x8": (2.5, 7.25),
    "3x10": (2.5, 9.25),
    "3x12": (2.5, 11.25),
    
    "4x4": (3.5, 3.5),
    "4x6": (3.5, 5.5),
    "4x8": (3.5, 7.25),
    "4x10": (3.5, 9.25),
    "4x12": (3.5, 11.25),
    
    "6x6": (5.5, 5.5),
    "6x8": (5.5, 7.25),
    "6x10": (5.5, 9.25),
    "6x12": (5.5, 11.25),
}

# Common nominal sizes with their actual dimensions (for quick reference)
COMMON_SIZES = {
    "2x4": (1.5, 3.5),
    "2x6": (1.5, 5.5),
    "2x8": (1.5, 7.25),
    "2x10": (1.5, 9.25),
    "2x12": (1.5, 11.25),
    "2x14": (1.5, 13.25),
    "2x16": (1.5, 15.25),
    "3x8": (2.5, 7.25),
    "3x10": (2.5, 9.25),
    "3x12": (2.5, 11.25),
    "4x8": (3.5, 7.25),
    "4x10": (3.5, 9.25),
    "4x12": (3.5, 11.25),
    "6x6": (5.5, 5.5),
    "6x8": (5.5, 7.25),
    "6x10": (5.5, 9.25),
    "6x12": (5.5, 11.25),
}


def parse_joist_dimension(input_str):
    """
    Parse joist dimension input.
    Accepts: "2x8", "2x10", "2x12", "3x8", "4x10", "6x6", etc.
    Also accepts direct actual dimensions like "1.5x7.25" or "1.5,7.25"
    Returns (width_actual, depth_actual)
    """
    input_str = input_str.strip().lower().replace(" ", "")
    
    # Check for nominal format like "2x8"
    match = re.match(r'^(\d+)x(\d+)$', input_str)
    if match:
        nominal_w = int(match.group(1))
        nominal_d = int(match.group(2))
        size_key = f"{nominal_w}x{nominal_d}"
        
        if size_key in COMMON_SIZES:
            return COMMON_SIZES[size_key]
        else:
            # Calculate actual dimensions for custom nominal size
            # Width: 2x = 1.5, 3x = 2.5, 4x = 3.5, 6x = 5.5
            if nominal_w == 2:
                actual_w = 1.5
            elif nominal_w == 3:
                actual_w = 2.5
            elif nominal_w == 4:
                actual_w = 3.5
            elif nominal_w == 6:
                actual_w = 5.5
            else:
                actual_w = nominal_w - 0.5  # approximate for custom sizes
            
            # Depth: subtract 0.5" for 2x lumber, 0.75" for larger
            if nominal_w == 2:
                actual_d = nominal_d - 0.5
            elif nominal_w in [3, 4]:
                actual_d = nominal_d - 0.75
            else:
                actual_d = nominal_d - 0.5
            
            return (actual_w, actual_d)
    
    # Check for format like "1.5x7.25" or "1.5,7.25"
    match = re.match(r'^(\d+(?:\.\d+)?)[x,\s]+(\d+(?:\.\d+)?)$', input_str)
    if match:
        return (float(match.group(1)), float(match.group(2)))
    
    # Invalid format
    raise ValueError(f"Invalid dimension format: {input_str}. Use '2x8' or '1.5x7.25'")


def show_common_sizes():
    """Display common joist sizes"""
    print("\nCommon Joist Sizes:")
    print("  Nominal    Actual (W x D)    Common Uses")
    print("  --------   ---------------   -------------------")
    print("  2x4        1.5\" x 3.5\"       Light loads, short spans")
    print("  2x6        1.5\" x 5.5\"       Residential floors (short spans)")
    print("  2x8        1.5\" x 7.25\"      Residential floors (typical)")
    print("  2x10       1.5\" x 9.25\"      Residential floors (long spans)")
    print("  2x12       1.5\" x 11.25\"     Heavy loads, long spans")
    print("  2x14       1.5\" x 13.25\"     Commercial (long spans)")
    print("  3x8        2.5\" x 7.25\"      Heavy residential")
    print("  3x10       2.5\" x 9.25\"      Commercial floors")
    print("  3x12       2.5\" x 11.25\"     Heavy commercial")
    print("  4x10       3.5\" x 9.25\"      Beams, long spans")
    print("  4x12       3.5\" x 11.25\"     Beams, heavy loads")
    print("  6x6        5.5\" x 5.5\"       Posts, short beams")
    print("")
    print("  You can also enter actual dimensions (e.g., '1.5x7.25')")


def show_grade_table():
    """Display available grades with their reference values"""
    print("\n" + "=" * 70)
    print("AVAILABLE GRADES - Douglas Fir-Larch (North)")
    print("=" * 70)
    print("\n  │ Grade             │ Fb (psi) │ E (ksi) │ E_min (ksi) │ Typical Use")
    print("──┼───────────────────┼──────────┼─────────┼─────────────┼────────────────")
    print("  │ 1. Select Struct  │   1600   │   1.6   │    0.58     │ Highest strength")
    print("  │ 2. No.1           │   1500   │   1.6   │    0.58     │ Heavy loads")
    print("  │ 3. No.2           │   1350   │   1.6   │    0.58     │ Standard const. (DEFAULT)")
    print("  │ 4. No.3           │    675   │   1.4   │    0.51     │ Economy/Utility")
    print("  │ 5. Custom         │    User  │  User   │   User      │ Manual entry")
    print("=" * 70)
    print("\n  Note: Values shown are reference design values per NDS Supplement")
    print("  Final adjusted values apply CD, CM, Ct, CF, Cr, Ci, CL factors")
    print("=" * 70)


# ----------------------------------------------------------------------
# NDS Adjustment Factors (2018/2024)

def get_load_duration_factor(load_type, is_roof):
    """CD - Load Duration Factor per NDS Table 2.3.2"""
    if is_roof:
        return 1.00  # Roof live load (normal duration)
    else:
        return 1.00  # Floor live load (normal duration)


def get_wet_service_factor(service_condition):
    """CM - Wet Service Factor per NDS Table 4.3.3"""
    return 1.00  # Dry service


def get_temperature_factor(temp_f):
    """Ct - Temperature Factor per NDS Table 2.3.3"""
    if temp_f <= 100:
        return 1.00
    elif temp_f <= 125:
        return 0.90
    elif temp_f <= 150:
        return 0.80
    else:
        return 0.70


def get_size_factor(Fb_ref, actual_width, actual_depth, species_group):
    """CF - Size Factor per NDS Table 4A/4B"""
    if actual_width <= 3.5:  # 2x lumber
        if actual_depth <= 3.5:      # 2x2 to 2x4
            return 1.5
        elif actual_depth <= 5.5:    # 2x6
            return 1.3
        elif actual_depth <= 7.25:   # 2x8
            return 1.2
        elif actual_depth <= 9.25:   # 2x10
            return 1.1
        else:                         # 2x12 and larger
            return 1.0
    else:
        return 1.0


def get_repetitive_member_factor(spacing, is_connected):
    """Cr - Repetitive Member Factor per NDS 4.3.9"""
    if spacing <= 24 and is_connected:
        return 1.15
    else:
        return 1.0


def get_incising_factor(is_incised, species):
    """Ci - Incising Factor per NDS Table 4.3.8"""
    if is_incised:
        return 0.80
    else:
        return 1.00


def get_beam_stability_factor(depth, width, unsupported_length, E_min, Fb_adj):
    """CL - Beam Stability Factor per NDS 3.3.3"""
    if unsupported_length == 0:
        return 1.0
    
    le = unsupported_length * 12  # inches
    RB = math.sqrt(le * depth) / (width ** 2)
    
    Fbe = (1.20 * E_min) / (RB ** 2)
    ratio = Fbe / Fb_adj
    
    if ratio <= 0.125:
        CL = ratio / 0.225
    elif ratio <= 0.5:
        CL = ratio / 1.125
    elif ratio <= 1.0:
        CL = (1 + ratio) / 1.875
    else:
        CL = 1.0
    
    return min(CL, 1.0)


# ----------------------------------------------------------------------
# NDS Reference Design Values for Douglas Fir-Larch (North)

DFIR_NORTH_VALUES = {
    "Select Structural": (1600, 180, 625, 1.6, 0.58),
    "No.1": (1500, 180, 625, 1.6, 0.58),
    "No.2": (1350, 180, 625, 1.6, 0.58),
    "No.3": (675, 180, 625, 1.4, 0.51),
    "Stud": (800, 180, 625, 1.3, 0.47),
    "Construction": (1600, 180, 625, 1.3, 0.47),
    "Standard": (925, 180, 625, 1.3, 0.47),
    "Utility": (350, 180, 625, 1.2, 0.43),
}


def input_itemized_loads(B, D1, is_roof=False):
    """Itemized loading subroutine"""
    print("\n" + "=" * 50)
    print("ITEMIZED LOADING INPUT")
    print("=" * 50)
    
    total_dl = 0.0
    
    print("\nDEAD LOADS (PSF):")
    
    if is_roof:
        roofing = float(input("  Roofing (asphalt shingles ~15 PSF, tile ~20 PSF): ") or "15")
    else:
        roofing = float(input("  Floor finish (carpet ~2 PSF, hardwood ~5 PSF, tile ~10 PSF): ") or "5")
    total_dl += roofing
    print(f"    -> {roofing:.1f} PSF")
    
    sheathing = float(input("  Sheathing (plywood/OSB ~2-3 PSF for 1/2\"): ") or "2.5")
    total_dl += sheathing
    print(f"    -> {sheathing:.1f} PSF")
    
    # Joists self-weight (35 pcf for DF-L)
    joist_wt = (B * D1 / 144.0) * 35
    print(f"  Joists (self-weight, calculated): {joist_wt:.2f} PSF")
    total_dl += joist_wt
    
    print("\n  Ceiling:")
    print("    (1) Plaster (7-10 PSF)")
    print("    (2) Drywall (5 PSF)")
    print("    (3) None (0 PSF)")
    ceiling_choice = input("    Choice (1/2/3): ") or "2"
    if ceiling_choice == "1":
        ceiling = 8.0
        plaster_flag = 1
    elif ceiling_choice == "2":
        ceiling = 5.0
        plaster_flag = 0
    else:
        ceiling = 0.0
        plaster_flag = 0
    total_dl += ceiling
    print(f"    -> {ceiling:.1f} PSF")
    
    insulation = float(input("  Insulation (fiberglass batts ~2-3 PSF): ") or "2")
    total_dl += insulation
    print(f"    -> {insulation:.1f} PSF")
    
    mech = float(input("  Mechanical/Electrical (~1-2 PSF): ") or "1.5")
    total_dl += mech
    print(f"    -> {mech:.1f} PSF")
    
    misc = float(input("  Miscellaneous (sprinklers, lights, etc.): ") or "0")
    total_dl += misc
    print(f"    -> {misc:.1f} PSF")
    
    print("\n" + "-" * 50)
    print(f" TOTAL DEAD LOAD = {total_dl:.1f} PSF")
    
    print("\n" + "-" * 50)
    if is_roof:
        print("LIVE LOADS (PSF) - per CBC/IBC:")
        print("  Roof slope < 4:12   : 20 PSF")
        print("  Roof slope >= 4:12  : 16 PSF")
        print("  Roof slope >= 12:12 : 12 PSF")
        ll = float(input("  Enter roof live load: ") or "20")
    else:
        print("LIVE LOADS (PSF) - per CBC/IBC:")
        print("  Residential bedrooms: 30 PSF")
        print("  Residential living areas: 40 PSF")
        print("  Sleeping dorms: 40 PSF")
        print("  Commercial offices: 50 PSF")
        ll = float(input("  Enter floor live load: ") or "40")
    
    print(f"    -> LL = {ll:.1f} PSF")
    
    return total_dl, ll, plaster_flag


def main():
    global B, D1, I1, T, Z, T1, I_grade
    
    print("=" * 70)
    print("JOIST TABLE PROGRAM - JST-T PROG.")
    print("Based on NDS 2018/2024 Standards")
    print("Douglas Fir-Larch (North) as Default Species")
    print("=" * 70)
    
    # Floor (0) or Roof (1)
    while True:
        I_str = input("\n FLOOR JOISTS--(0)   ROOF JOISTS--(1): ")
        if I_str in ['0', '1']:
            Z = int(I_str)
            break
        print("Enter 0 or 1")
    
    is_roof = (Z == 1)
    
    # Joist dimensions with nominal input support
    show_common_sizes()
    
    while True:
        dim_input = input("\n Enter joist size (e.g., '2x8', '2x10', '1.5x7.25'): ")
        try:
            B, D1 = parse_joist_dimension(dim_input)
            print(f"  Accepted: Width = {B}\" (actual), Depth = {D1}\" (actual)")
            break
        except ValueError as e:
            print(f"  Error: {e}")
            print("  Please try again.")
    
    # Section properties
    Sx = B * (D1 ** 2) / 6.0      # in^3
    I1 = B * (D1 ** 3) / 12.0     # in^4
    
    print(f"\n Section Modulus Sx = {Sx:.2f} in^3")
    print(f" Moment of Inertia I = {I1:.2f} in^4")
    
    # Itemized loading or simple?
    T1 = int(input("\n ITEMIZED LOADING--(1) OR (0): "))
    
    if T1 == 1:
        dl, ll, plaster_flag = input_itemized_loads(B, D1, is_roof)
        D[1] = dl
        D[2] = ll
        D[3] = dl + ll
    else:
        D[1] = float(input(" DEAD LOAD (PSF): "))
        D[2] = float(input(" LIVE LOAD (PSF): "))
        D[3] = D[1] + D[2]
        plaster_flag = int(input(" PLASTER CEILING? (1) YES (0) NO: "))
    
    T = plaster_flag
    
    print(f"\n SUMMARY: DL = {D[1]:.1f} PSF, LL = {D[2]:.1f} PSF, TL = {D[3]:.1f} PSF")
    
    # ------------------------------------------------------------------
    # Grade Selection - WITH TABLE DISPLAY
    
    # Show the grade table first
    show_grade_table()
    
    print("\n" + "=" * 50)
    print("LUMBER PROPERTIES (Douglas Fir-Larch - North)")
    print("=" * 50)
    
    # Present options clearly
    print("\n  Select lumber grade:")
    print("  ┌─────┬──────────────────┬──────────┬─────────┬─────────────┐")
    print("  │ Opt │ Grade            │ Fb (psi) │ E (ksi) │ E_min (ksi) │")
    print("  ├─────┼──────────────────┼──────────┼─────────┼─────────────┤")
    print("  │ 1   │ Select Structural│   1600   │   1.6   │    0.58     │")
    print("  │ 2   │ No.1             │   1500   │   1.6   │    0.58     │")
    print("  │ 3   │ No.2 (DEFAULT)   │   1350   │   1.6   │    0.58     │")
    print("  │ 4   │ No.3             │    675   │   1.4   │    0.51     │")
    print("  │ 5   │ Custom           │   User   │  User   │   User      │")
    print("  └─────┴──────────────────┴──────────┴─────────┴─────────────┘")
    
    grade_choice = input("\n Enter option (1-5) [default=3]: ") or "3"
    
    if grade_choice == "1":
        grade_name = "Select Structural"
        Fb_ref = 1600
        E_ref = 1.6
        E_min_ref = 0.58
        print(f"\n  ✓ Selected: {grade_name}")
    elif grade_choice == "2":
        grade_name = "No.1"
        Fb_ref = 1500
        E_ref = 1.6
        E_min_ref = 0.58
        print(f"\n  ✓ Selected: {grade_name}")
    elif grade_choice == "3":
        grade_name = "No.2"
        Fb_ref = 1350
        E_ref = 1.6
        E_min_ref = 0.58
        print(f"\n  ✓ Selected: {grade_name} (DEFAULT)")
    elif grade_choice == "4":
        grade_name = "No.3"
        Fb_ref = 675
        E_ref = 1.4
        E_min_ref = 0.51
        print(f"\n  ✓ Selected: {grade_name}")
    else:
        grade_name = "Custom"
        print("\n  Custom Grade Entry:")
        Fb_ref = float(input("    Fb (bending stress, PSI): "))
        E_ref = float(input("    E (modulus of elasticity, KSI): "))
        E_min_ref = E_ref * 0.36  # Approximate E_min = 0.36 * E
        print(f"\n  ✓ Custom grade: Fb={Fb_ref} psi, E={E_ref} ksi, E_min={E_min_ref:.2f} ksi")
    
    print(f"\n Using {grade_name} Douglas Fir-Larch (North)")
    print(f" Reference Fb = {Fb_ref} PSI, E = {E_ref} KSI")
    
    # ------------------------------------------------------------------
    # NDS Adjustment Factors
    
    print("\n" + "=" * 50)
    print("NDS ADJUSTMENT FACTORS")
    print("=" * 50)
    
    CD = get_load_duration_factor("live", is_roof)
    print(f" CD (Load Duration) = {CD:.2f}")
    
    CM = get_wet_service_factor("dry")
    print(f" CM (Wet Service) = {CM:.2f}")
    
    Ct = get_temperature_factor(70)
    print(f" Ct (Temperature) = {Ct:.2f}")
    
    CF = get_size_factor(Fb_ref, B, D1, "DF-L")
    print(f" CF (Size Factor) = {CF:.2f}")
    
    Cr = get_repetitive_member_factor(16, True)
    print(f" Cr (Repetitive Member) = {Cr:.2f}")
    
    Ci = get_incising_factor(False, "DF-L")
    print(f" Ci (Incising) = {Ci:.2f}")
    
    Fb_prelim = Fb_ref * CD * CM * Ct * CF * Cr * Ci
    print(f" Preliminary F'b (before CL) = {Fb_prelim:.0f} PSI")
    
    # ------------------------------------------------------------------
    # Calculations
    
    print("\n" + "=" * 85)
    print("                         JOIST TABLE")
    print("=" * 85)
    print(f" Joist Size: {B}\" x {D1}\" ({get_nominal_name(B, D1)}) - {'ROOF' if is_roof else 'FLOOR'} JOIST")
    print(f" Species: Douglas Fir-Larch (North) - Grade: {grade_name}")
    print(f" Adjusted Fb = {Fb_prelim:.0f} PSI (before CL), E = {E_ref} KSI")
    print(f" Loads: DL = {D[1]:.1f} PSF, LL = {D[2]:.1f} PSF, TL = {D[3]:.1f} PSF")
    
    print("\n" + "-" * 85)
    print("  Spacing    |   Moment    |  Deflection  |   CL (Stab)  |  ALLOWABLE")
    print("  (O.C.)     | Span(ft)    |  Span(ft)    |    Factor    |   SPAN(ft)")
    print("-" * 85)
    
    for J in range(1, 5):
        spacing = S[10 + J]
        
        w_total_plf = D[3] * spacing / 12.0
        w_live_plf = D[2] * spacing / 12.0
        w_total_pli = w_total_plf / 12.0
        w_live_pli = w_live_plf / 12.0
        
        E_min_psi = E_min_ref * 1000000
        unsupported_len = 8
        CL = get_beam_stability_factor(D1, B, unsupported_len, E_min_psi, Fb_prelim)
        
        Fb_adj = Fb_prelim * CL
        
        # Moment span
        if w_total_plf > 0 and Fb_adj > 0 and Sx > 0:
            L_moment_ft = math.sqrt(8.0 * Fb_adj * Sx / (12.0 * w_total_plf))
        else:
            L_moment_ft = 0.0
        
        # Deflection span
        E_psi = E_ref * 1000000
        
        if w_live_pli > 0 and E_psi > 0 and I1 > 0:
            if is_roof:
                L_def_in = (384.0 * E_psi * I1 / (5.0 * w_total_pli * 240.0)) ** (1.0/3.0)
            else:
                if T == 1:
                    L_def_360_in = (384.0 * E_psi * I1 / (5.0 * w_live_pli * 360.0)) ** (1.0/3.0)
                    L_def_240_in = (384.0 * E_psi * I1 / (5.0 * w_total_pli * 240.0)) ** (1.0/3.0)
                    L_def_in = min(L_def_360_in, L_def_240_in)
                else:
                    L_def_in = (384.0 * E_psi * I1 / (5.0 * w_live_pli * 360.0)) ** (1.0/3.0)
            L_def_ft = L_def_in / 12.0
        else:
            L_def_ft = 999.0
        
        # Shear check
        Fv = 180
        Fv_adj = Fv * CD * CM * Ct * Ci
        if w_total_plf > 0:
            L_shear_ft = (2.0 * Fv_adj * B * D1) / (1.5 * w_total_plf * 12.0)
        else:
            L_shear_ft = 999.0
        
        allowable = min(L_moment_ft, L_def_ft, L_shear_ft)
        
        spacing_label = f"{spacing}\""
        print(f"  {spacing_label:8} |   {L_moment_ft:6.2f}     |    {L_def_ft:6.2f}     |    {CL:6.3f}    |    {allowable:6.2f}")
    
    print("-" * 85)
    
    print("\n DEFLECTION CRITERIA (per CBC/NDS):")
    if is_roof:
        print("   ROOF: L/240 (Total Load)")
    else:
        if T == 1:
            print("   FLOOR with PLASTER: L/360 (Live Load) AND L/240 (Total Load)")
        else:
            print("   FLOOR: L/360 (Live Load)")
    
    print("\n" + "=" * 85)
    print("Based on NDS 2018/2024 Standards for Douglas Fir-Larch (North)")
    print("Adjustment factors applied: CD, CM, Ct, CF, Cr, Ci, CL")
    print("=" * 85)


def get_nominal_name(actual_w, actual_d):
    """Convert actual dimensions back to nominal name (approximate)"""
    # Common conversions
    if abs(actual_w - 1.5) < 0.1:
        if abs(actual_d - 3.5) < 0.1:
            return "2x4 nominal"
        elif abs(actual_d - 5.5) < 0.1:
            return "2x6 nominal"
        elif abs(actual_d - 7.25) < 0.1:
            return "2x8 nominal"
        elif abs(actual_d - 9.25) < 0.1:
            return "2x10 nominal"
        elif abs(actual_d - 11.25) < 0.1:
            return "2x12 nominal"
        elif abs(actual_d - 13.25) < 0.1:
            return "2x14 nominal"
        elif abs(actual_d - 15.25) < 0.1:
            return "2x16 nominal"
    elif abs(actual_w - 3.5) < 0.1:
        if abs(actual_d - 3.5) < 0.1:
            return "4x4 nominal"
        elif abs(actual_d - 5.5) < 0.1:
            return "4x6 nominal"
        elif abs(actual_d - 7.25) < 0.1:
            return "4x8 nominal"
        elif abs(actual_d - 9.25) < 0.1:
            return "4x10 nominal"
        elif abs(actual_d - 11.25) < 0.1:
            return "4x12 nominal"
    
    return f"{actual_w:.1f}\" x {actual_d:.1f}\" (actual)"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated.")
        sys.exit(0)
    except EOFError:
        print("\n\nInput ended.")
        sys.exit(0)
    except ValueError as e:
        print(f"\n\nInput error: {e}")
        print("Please enter numeric values where required.")
        sys.exit(1)
