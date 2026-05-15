#!/usr/bin/env python3
"""
JSTSCRN8.BAS - Joist Table Program converted to Streamlit.

This is intentionally joist-only and follows the original script closely:
floor/roof selection, nominal joist input, simple or itemized loads,
Douglas Fir-Larch (North) grade selection, NDS adjustment factors, and
the allowable span table for 24", 16", 12", and 19" O.C. spacing.
"""

import math
import re

import streamlit as st


S = {11: 24, 12: 16, 13: 12, 14: 19}

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

GRADE_OPTIONS = {
    "1. Select Structural": ("Select Structural", 1600.0, 1.6, 0.58),
    "2. No.1": ("No.1", 1500.0, 1.6, 0.58),
    "3. No.2 (DEFAULT)": ("No.2", 1350.0, 1.6, 0.58),
    "4. No.3": ("No.3", 675.0, 1.4, 0.51),
    "5. Custom": ("Custom", 1350.0, 1.6, 0.58),
}


def parse_joist_dimension(input_str):
    """Accepts '2x8', '2x10', '1.5x7.25', or '1.5,7.25'."""
    input_str = input_str.strip().lower().replace(" ", "")

    match = re.match(r"^(\d+)x(\d+)$", input_str)
    if match:
        nominal_w = int(match.group(1))
        nominal_d = int(match.group(2))
        size_key = f"{nominal_w}x{nominal_d}"

        if size_key in COMMON_SIZES:
            return COMMON_SIZES[size_key]

        if nominal_w == 2:
            actual_w = 1.5
        elif nominal_w == 3:
            actual_w = 2.5
        elif nominal_w == 4:
            actual_w = 3.5
        elif nominal_w == 6:
            actual_w = 5.5
        else:
            actual_w = nominal_w - 0.5

        if nominal_w == 2:
            actual_d = nominal_d - 0.5
        elif nominal_w in [3, 4]:
            actual_d = nominal_d - 0.75
        else:
            actual_d = nominal_d - 0.5

        return actual_w, actual_d

    match = re.match(r"^(\d+(?:\.\d+)?)[x,\s]+(\d+(?:\.\d+)?)$", input_str)
    if match:
        return float(match.group(1)), float(match.group(2))

    raise ValueError("Invalid dimension format. Use '2x8' or '1.5x7.25'.")


def get_nominal_name(actual_w, actual_d):
    for name, dims in COMMON_SIZES.items():
        if abs(actual_w - dims[0]) < 0.1 and abs(actual_d - dims[1]) < 0.1:
            return f"{name} nominal"
    return f'{actual_w:.1f}" x {actual_d:.1f}" actual'


def get_load_duration_factor(load_type, is_roof):
    """CD - Load Duration Factor per NDS Table 2.3.2."""
    return 1.00


def get_wet_service_factor(service_condition):
    """CM - Wet Service Factor per NDS Table 4.3.3."""
    return 1.00


def get_temperature_factor(temp_f):
    """Ct - Temperature Factor per NDS Table 2.3.3."""
    if temp_f <= 100:
        return 1.00
    if temp_f <= 125:
        return 0.90
    if temp_f <= 150:
        return 0.80
    return 0.70


def get_size_factor(Fb_ref, actual_width, actual_depth, species_group):
    """CF - Size Factor per NDS Table 4A/4B."""
    if actual_width <= 3.5:
        if actual_depth <= 3.5:
            return 1.5
        if actual_depth <= 5.5:
            return 1.3
        if actual_depth <= 7.25:
            return 1.2
        if actual_depth <= 9.25:
            return 1.1
        return 1.0
    return 1.0


def get_repetitive_member_factor(spacing, is_connected):
    """Cr - Repetitive Member Factor per NDS 4.3.9."""
    if spacing <= 24 and is_connected:
        return 1.15
    return 1.0


def get_incising_factor(is_incised, species):
    """Ci - Incising Factor per NDS Table 4.3.8."""
    if is_incised:
        return 0.80
    return 1.00


def get_beam_stability_factor(depth, width, unsupported_length, E_min, Fb_adj):
    """CL - Beam Stability Factor per NDS 3.3.3."""
    if unsupported_length == 0:
        return 1.0

    le = unsupported_length * 12
    RB = math.sqrt(le * depth) / (width**2)
    Fbe = (1.20 * E_min) / (RB**2)
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


def calculate_table(B, D1, loads, is_roof, plaster_flag, grade, factors_input):
    D = {1: loads["DL"], 2: loads["LL"], 3: loads["DL"] + loads["LL"]}
    Fb_ref = grade["Fb_ref"]
    E_ref = grade["E_ref"]
    E_min_ref = grade["E_min_ref"]

    Sx = B * (D1**2) / 6.0
    I1 = B * (D1**3) / 12.0

    CD = get_load_duration_factor("live", is_roof)
    CM = get_wet_service_factor("dry")
    Ct = get_temperature_factor(factors_input["temperature"])
    CF = get_size_factor(Fb_ref, B, D1, "DF-L")
    Ci = get_incising_factor(factors_input["is_incised"], "DF-L")

    rows = []
    for J in range(1, 5):
        spacing = S[10 + J]
        Cr = get_repetitive_member_factor(spacing, factors_input["is_connected"])
        Fb_prelim = Fb_ref * CD * CM * Ct * CF * Cr * Ci

        w_total_plf = D[3] * spacing / 12.0
        w_live_plf = D[2] * spacing / 12.0
        w_total_pli = w_total_plf / 12.0
        w_live_pli = w_live_plf / 12.0

        E_min_psi = E_min_ref * 1000000
        unsupported_len = factors_input["unsupported_len"]
        CL = get_beam_stability_factor(D1, B, unsupported_len, E_min_psi, Fb_prelim)

        Fb_adj = Fb_prelim * CL

        if w_total_plf > 0 and Fb_adj > 0 and Sx > 0:
            L_moment_ft = math.sqrt(8.0 * Fb_adj * Sx / (12.0 * w_total_plf))
        else:
            L_moment_ft = 0.0

        E_psi = E_ref * 1000000
        if w_live_pli > 0 and E_psi > 0 and I1 > 0:
            if is_roof:
                L_def_in = (384.0 * E_psi * I1 / (5.0 * w_total_pli * 240.0)) ** (1.0 / 3.0)
            else:
                if plaster_flag == 1:
                    L_def_360_in = (384.0 * E_psi * I1 / (5.0 * w_live_pli * 360.0)) ** (1.0 / 3.0)
                    L_def_240_in = (384.0 * E_psi * I1 / (5.0 * w_total_pli * 240.0)) ** (1.0 / 3.0)
                    L_def_in = min(L_def_360_in, L_def_240_in)
                else:
                    L_def_in = (384.0 * E_psi * I1 / (5.0 * w_live_pli * 360.0)) ** (1.0 / 3.0)
            L_def_ft = L_def_in / 12.0
        else:
            L_def_ft = 999.0

        Fv = 180
        Fv_adj = Fv * CD * CM * Ct * Ci
        if w_total_plf > 0:
            L_shear_ft = (2.0 * Fv_adj * B * D1) / (1.5 * w_total_plf)
        else:
            L_shear_ft = 999.0

        allowable = min(L_moment_ft, L_def_ft, L_shear_ft)
        rows.append(
            {
                "Spacing": f'{spacing}"',
                "Moment Span (ft)": round(L_moment_ft, 2),
                "Deflection Span (ft)": round(L_def_ft, 2),
                "Shear Span (ft)": round(L_shear_ft, 2),
                "CL (Stab)": round(CL, 3),
                "Allowable Span (ft)": round(allowable, 2),
            }
        )

    return {
        "D": D,
        "Sx": Sx,
        "I1": I1,
        "CD": CD,
        "CM": CM,
        "Ct": Ct,
        "CF": CF,
        "Cr_default": get_repetitive_member_factor(16, factors_input["is_connected"]),
        "Ci": Ci,
        "Fb_prelim_default": Fb_ref
        * CD
        * CM
        * Ct
        * CF
        * get_repetitive_member_factor(16, factors_input["is_connected"])
        * Ci,
        "rows": rows,
    }


def itemized_loads(B, D1, is_roof):
    st.markdown("#### DEAD LOADS (PSF)")
    if is_roof:
        finish = st.number_input("Roofing (asphalt shingles ~15 PSF, tile ~20 PSF)", value=15.0, min_value=0.0)
    else:
        finish = st.number_input("Floor finish (carpet ~2 PSF, hardwood ~5 PSF, tile ~10 PSF)", value=5.0, min_value=0.0)

    sheathing = st.number_input('Sheathing (plywood/OSB ~2-3 PSF for 1/2")', value=2.5, min_value=0.0)
    joist_wt = (B * D1 / 144.0) * 35
    st.number_input("Joists self-weight, calculated", value=joist_wt, disabled=True)

    ceiling_choice = st.radio("Ceiling", ["Plaster (8 PSF)", "Drywall (5 PSF)", "None (0 PSF)"], index=1)
    if ceiling_choice.startswith("Plaster"):
        ceiling = 8.0
        plaster_flag = 1
    elif ceiling_choice.startswith("Drywall"):
        ceiling = 5.0
        plaster_flag = 0
    else:
        ceiling = 0.0
        plaster_flag = 0

    insulation = st.number_input("Insulation (fiberglass batts ~2-3 PSF)", value=2.0, min_value=0.0)
    mech = st.number_input("Mechanical/Electrical (~1-2 PSF)", value=1.5, min_value=0.0)
    misc = st.number_input("Miscellaneous (sprinklers, lights, etc.)", value=0.0, min_value=0.0)

    total_dl = finish + sheathing + joist_wt + ceiling + insulation + mech + misc
    st.metric("TOTAL DEAD LOAD", f"{total_dl:.1f} PSF")

    st.markdown("#### LIVE LOADS (PSF)")
    if is_roof:
        st.caption("Roof slope < 4:12 = 20 PSF, >= 4:12 = 16 PSF, >= 12:12 = 12 PSF")
        ll = st.number_input("Enter roof live load", value=20.0, min_value=0.0)
    else:
        st.caption("Residential bedrooms = 30 PSF, living areas = 40 PSF, commercial offices = 50 PSF")
        ll = st.number_input("Enter floor live load", value=40.0, min_value=0.0)

    return total_dl, ll, plaster_flag


def main():
    st.set_page_config(page_title="JST-T Joist Table", layout="wide")

    st.title("JOIST TABLE PROGRAM - JST-T PROG.")
    st.caption("Based on NDS 2018/2024 Standards - Douglas Fir-Larch (North) as Default Species")

    left, right = st.columns([0.9, 1.1])

    with left:
        st.subheader("Input")
        Z = st.radio("FLOOR JOISTS--(0)   ROOF JOISTS--(1)", [0, 1], format_func=lambda x: "Floor joists (0)" if x == 0 else "Roof joists (1)")
        is_roof = Z == 1

        st.markdown("#### Common Joist Sizes")
        st.dataframe(
            [
                {"Nominal": k, "Actual W": v[0], "Actual D": v[1]}
                for k, v in COMMON_SIZES.items()
            ],
            hide_index=True,
            use_container_width=True,
            height=210,
        )

        dim_input = st.text_input("Enter joist size (e.g., '2x8', '2x10', '1.5x7.25')", value="2x8")
        try:
            B, D1 = parse_joist_dimension(dim_input)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        Sx = B * (D1**2) / 6.0
        I1 = B * (D1**3) / 12.0
        st.write(f'Accepted: Width = **{B}"** actual, Depth = **{D1}"** actual')
        st.write(f"Section Modulus Sx = **{Sx:.2f} in^3**")
        st.write(f"Moment of Inertia I = **{I1:.2f} in^4**")

        T1 = st.radio("ITEMIZED LOADING--(1) OR (0)", [0, 1], format_func=lambda x: "0 - Simple" if x == 0 else "1 - Itemized")
        if T1 == 1:
            dl, ll, plaster_flag = itemized_loads(B, D1, is_roof)
        else:
            dl = st.number_input("DEAD LOAD (PSF)", value=10.0, min_value=0.0)
            ll_default = 20.0 if is_roof else 40.0
            ll = st.number_input("LIVE LOAD (PSF)", value=ll_default, min_value=0.0)
            plaster_flag = st.radio("PLASTER CEILING? (1) YES (0) NO", [0, 1], format_func=lambda x: "0 - No" if x == 0 else "1 - Yes")

    with right:
        st.subheader("Grade Selection")
        st.markdown("AVAILABLE GRADES - Douglas Fir-Larch (North)")
        st.dataframe(
            [
                {"Opt": 1, "Grade": "Select Structural", "Fb (psi)": 1600, "E (ksi)": 1.6, "E_min (ksi)": 0.58, "Typical Use": "Highest strength"},
                {"Opt": 2, "Grade": "No.1", "Fb (psi)": 1500, "E (ksi)": 1.6, "E_min (ksi)": 0.58, "Typical Use": "Heavy loads"},
                {"Opt": 3, "Grade": "No.2", "Fb (psi)": 1350, "E (ksi)": 1.6, "E_min (ksi)": 0.58, "Typical Use": "Standard const. (DEFAULT)"},
                {"Opt": 4, "Grade": "No.3", "Fb (psi)": 675, "E (ksi)": 1.4, "E_min (ksi)": 0.51, "Typical Use": "Economy/Utility"},
                {"Opt": 5, "Grade": "Custom", "Fb (psi)": "User", "E (ksi)": "User", "E_min (ksi)": "User", "Typical Use": "Manual entry"},
            ],
            hide_index=True,
            use_container_width=True,
        )

        grade_choice = st.selectbox("Enter option (1-5) [default=3]", list(GRADE_OPTIONS.keys()), index=2)
        grade_name, Fb_ref, E_ref, E_min_ref = GRADE_OPTIONS[grade_choice]
        if grade_name == "Custom":
            Fb_ref = st.number_input("Fb (bending stress, PSI)", value=1350.0, min_value=1.0)
            E_ref = st.number_input("E (modulus of elasticity, KSI)", value=1.6, min_value=0.1)
            E_min_ref = E_ref * 0.36
            st.write(f"Custom grade: Fb={Fb_ref:.0f} psi, E={E_ref:.2f} ksi, E_min={E_min_ref:.2f} ksi")
        else:
            st.write(f"Selected: **{grade_name}**")

        st.write(f"Using **{grade_name} Douglas Fir-Larch (North)**")
        st.write(f"Reference Fb = **{Fb_ref:.0f} PSI**, E = **{E_ref:.2f} KSI**")

        st.subheader("NDS Adjustment Factors")
        temperature = st.number_input("Temperature for Ct (F)", value=70.0)
        unsupported_len = st.number_input("Unsupported length for CL (ft)", value=8.0, min_value=0.0)
        is_connected = st.checkbox("Repetitive members connected", value=True)
        is_incised = st.checkbox("Incised lumber", value=False)

        result = calculate_table(
            B,
            D1,
            {"DL": dl, "LL": ll},
            is_roof,
            plaster_flag,
            {"Fb_ref": Fb_ref, "E_ref": E_ref, "E_min_ref": E_min_ref},
            {
                "temperature": temperature,
                "unsupported_len": unsupported_len,
                "is_connected": is_connected,
                "is_incised": is_incised,
            },
        )

        factors = [
            ("CD (Load Duration)", result["CD"]),
            ("CM (Wet Service)", result["CM"]),
            ("Ct (Temperature)", result["Ct"]),
            ("CF (Size Factor)", result["CF"]),
            ("Cr (Repetitive Member)", result["Cr_default"]),
            ("Ci (Incising)", result["Ci"]),
        ]
        for label, value in factors:
            st.write(f"{label} = **{value:.2f}**")
        st.write(f'Preliminary F\'b (before CL) = **{result["Fb_prelim_default"]:.0f} PSI**')

    st.divider()
    st.subheader("JOIST TABLE")
    st.write(f'Joist Size: **{B}" x {D1}" ({get_nominal_name(B, D1)})** - **{"ROOF" if is_roof else "FLOOR"} JOIST**')
    st.write(f"Species: **Douglas Fir-Larch (North)** - Grade: **{grade_name}**")
    st.write(f'Adjusted Fb = **{result["Fb_prelim_default"]:.0f} PSI** before CL, E = **{E_ref} KSI**')
    st.write(f'DL = **{result["D"][1]:.1f} PSF**, LL = **{result["D"][2]:.1f} PSF**, TL = **{result["D"][3]:.1f} PSF**')
    st.dataframe(result["rows"], hide_index=True, use_container_width=True)

    if is_roof:
        st.info("DEFLECTION CRITERIA: ROOF: L/240 (Total Load)")
    elif plaster_flag == 1:
        st.info("DEFLECTION CRITERIA: FLOOR with PLASTER: L/360 (Live Load) AND L/240 (Total Load)")
    else:
        st.info("DEFLECTION CRITERIA: FLOOR: L/360 (Live Load)")

    st.caption("Based on NDS 2018/2024 Standards for Douglas Fir-Larch (North). Adjustment factors applied: CD, CM, Ct, CF, Cr, Ci, CL.")


if __name__ == "__main__":
    main()
