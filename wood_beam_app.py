import streamlit as st
import math
import re

# ----------------------------------------------------------------------
# Wood section database (width <= 8", depth <= 18")
wood_sections_raw = [
    ("2x8 Douglas Fir-Larch No.1", "sawn", 1.5, 7.25, 2.6, 1200, 1600),
    ("2x10 Douglas Fir-Larch No.1", "sawn", 1.5, 9.25, 3.4, 1200, 1600),
    ("2x12 Douglas Fir-Larch No.1", "sawn", 1.5, 11.25, 4.1, 1200, 1600),
    ("4x8 Douglas Fir-Larch No.1", "sawn", 3.5, 7.25, 5.2, 1200, 1600),
    ("4x10 Douglas Fir-Larch No.1", "sawn", 3.5, 9.25, 6.8, 1200, 1600),
    ("4x12 Douglas Fir-Larch No.1", "sawn", 3.5, 11.25, 8.2, 1200, 1600),
    ("6x8 Douglas Fir-Larch No.1", "sawn", 5.5, 7.25, 7.8, 1200, 1600),
    ("6x10 Douglas Fir-Larch No.1", "sawn", 5.5, 9.25, 10.2, 1200, 1600),
    ("6x12 Douglas Fir-Larch No.1", "sawn", 5.5, 11.25, 12.3, 1200, 1600),
    ("6x14 Douglas Fir-Larch No.1", "sawn", 5.5, 13.25, 14.4, 1200, 1600),
    ("6x16 Douglas Fir-Larch No.1", "sawn", 5.5, 15.25, 16.5, 1200, 1600),
    ("6x18 Douglas Fir-Larch No.1", "sawn", 5.5, 17.25, 18.6, 1200, 1600),
    ("8x12 Douglas Fir-Larch No.1", "sawn", 7.25, 11.25, 16.4, 1200, 1600),
    ("8x14 Douglas Fir-Larch No.1", "sawn", 7.25, 13.25, 19.2, 1200, 1600),
    ("8x16 Douglas Fir-Larch No.1", "sawn", 7.25, 15.25, 22.0, 1200, 1600),
    ("8x18 Douglas Fir-Larch No.1", "sawn", 7.25, 17.25, 24.8, 1200, 1600),
    ("3.5\" x 11.875\" PSL (Parallam)", "psl", 3.5, 11.875, 12.7, 2900, 2000),
    ("3.5\" x 14\" PSL (Parallam)", "psl", 3.5, 14.0, 15.0, 2900, 2000),
    ("3.5\" x 16\" PSL (Parallam)", "psl", 3.5, 16.0, 17.2, 2900, 2000),
    ("3.5\" x 18\" PSL (Parallam)", "psl", 3.5, 18.0, 19.3, 2900, 2000),
    ("4x12 PSL (nominal)", "psl", 3.5, 11.5, 12.5, 2900, 2000),
    ("5.25\" x 11.875\" PSL (Parallam)", "psl", 5.25, 11.875, 19.0, 2900, 2000),
    ("5.25\" x 14\" PSL (Parallam)", "psl", 5.25, 14.0, 22.5, 2900, 2000),
    ("5.25\" x 16\" PSL (Parallam)", "psl", 5.25, 16.0, 25.8, 2900, 2000),
    ("5.25\" x 18\" PSL (Parallam)", "psl", 5.25, 18.0, 29.0, 2900, 2000),
    ("6x12 PSL (nominal)", "psl", 5.5, 11.5, 18.5, 2900, 2000),
    ("7\" x 11.875\" PSL (Parallam)", "psl", 7.0, 11.875, 25.3, 2900, 2000),
    ("7\" x 14\" PSL (Parallam)", "psl", 7.0, 14.0, 30.0, 2900, 2000),
    ("7\" x 16\" PSL (Parallam)", "psl", 7.0, 16.0, 34.4, 2900, 2000),
    ("7\" x 18\" PSL (Parallam)", "psl", 7.0, 18.0, 38.7, 2900, 2000),
]
wood_list = []
for entry in wood_sections_raw:
    desc, mat, w, d, plf, fb, e = entry
    Ix = w * d**3 / 12.0
    Sx = w * d**2 / 6.0
    wood_list.append((desc, mat, w, d, plf, fb, e, Ix, Sx))
steel_sections = [
    ("W10 X 12", 53.8, 13.9, 12, 30000, 29000),
    ("W12 X 14", 88.6, 17.4, 14, 30000, 29000),
    ("W12 X 16", 103.0, 20.1, 16, 30000, 29000),
    ("W12 X 19", 130.0, 24.3, 19, 30000, 29000),
    ("W12 X 22", 156.0, 29.3, 22, 30000, 29000),
    ("W14 X 22", 199.0, 33.2, 22, 30000, 29000),
    ("W12 X 26", 204.0, 39.4, 26, 30000, 29000),
    ("W14 X 26", 245.0, 39.5, 26, 30000, 29000),
    ("W16 X 26", 301.0, 45.0, 26, 30000, 29000),
    ("W14 X 30", 291.0, 45.6, 30, 30000, 29000),
    ("W16 X 31", 375.0, 51.5, 31, 30000, 29000),
    ("W14 X 34", 340.0, 53.0, 34, 30000, 29000),
    ("W16 X 36", 448.0, 63.0, 36, 30000, 29000),
]
# ----------------------------------------------------------------------
def evaluate_expression(s):
    if not s or s.strip() == "":
        return 0.0
    s = s.strip()
    try:
        if re.match(r'^[\d\.\+\-\*/\s\(\)]+$', s):
            return float(eval(s))
        else:
            # In Streamlit UI we show a note
            st.write("   (Note: Only numeric expressions allowed. Using 0.)")
            return 0.0
    except:
        st.write("   (Invalid expression. Using 0.)")
        return 0.0
# ----------------------------------------------------------------------
# Deflection for simply supported beam (superposition of point loads)
def deflection_simply_supported(x_ft, L_ft, point_loads, dist_loads, E_ksi, I_in4):
    L_in = L_ft * 12.0
    x_in = x_ft * 12.0
    if I_in4 <= 0:
        return 1e6
    EI = E_ksi * I_in4  # kip-in^2
    def point_load_deflection(a_ft, P):
        a = a_ft * 12.0
        if a <= 0 or a >= L_in:
            return 0.0
        if x_in <= a:
            b = L_in - a
            term = (L_in**2 - b**2 - x_in**2)
            return P * b * x_in * term / (6.0 * EI * L_in)
        else:
            term = (L_in**2 - a**2 - (L_in - x_in)**2)
            return P * a * (L_in - x_in) * term / (6.0 * EI * L_in)
    def uniform_load_deflection(x1_ft, x2_ft, w):
        if w == 0 or x2_ft <= x1_ft:
            return 0.0
        n = 100
        dx = (x2_ft - x1_ft) / n
        total = 0.0
        for i in range(n):
            xi = x1_ft + (i + 0.5) * dx
            dP = w * dx
            total += point_load_deflection(xi, dP)
        return total
    d = 0.0
    for a, P in point_loads:
        d += point_load_deflection(a, P)
    for x1, x2, w in dist_loads:
        d += uniform_load_deflection(x1, x2, w)
    return d
def max_deflection_simply_supported(L_ft, point_loads, dist_loads, E_ksi, I_in4):
    max_d = 0.0
    for i in range(1001):
        x = i * L_ft / 1000.0
        d = abs(deflection_simply_supported(x, L_ft, point_loads, dist_loads, E_ksi, I_in4))
        if d > max_d:
            max_d = d
    return max_d
# ----------------------------------------------------------------------
# Deflection for cantilever (fixed at x=0, free at x=L)
# Load position 'a' is measured from the FIXED support (x=0)
# Standard formulas:
#   For x <= a: delta = P*x^2*(3a - x) / (6EI)
#   For x >= a: delta = P*a^2*(3x - a) / (6EI)
def deflection_cantilever(x_ft, L_ft, point_loads, dist_loads, E_ksi, I_in4):
    L_in = L_ft * 12.0
    x_in = x_ft * 12.0
    if I_in4 <= 0:
        return 1e6
    EI = E_ksi * I_in4
    def point_load_deflection(a_ft, P):
        """Deflection at x due to point load P at distance a from fixed end."""
        a = a_ft * 12.0
        if a <= 0:
            return 0.0
        # Clamp a to beam length (load beyond tip has no additional effect)
        if a > L_in:
            a = L_in
        if x_in <= a:
            # x is between fixed end and load
            return P * x_in**2 * (3.0 * a - x_in) / (6.0 * EI)
        else:
            # x is beyond the load (towards free end)
            return P * a**2 * (3.0 * x_in - a) / (6.0 * EI)
    def uniform_load_deflection(x1_ft, x2_ft, w):
        """Deflection due to uniform load w (k/ft) from x1 to x2."""
        if w == 0 or x2_ft <= x1_ft:
            return 0.0
        n = 100
        dx = (x2_ft - x1_ft) / n
        total = 0.0
        for i in range(n):
            xi = x1_ft + (i + 0.5) * dx
            dP = w * dx
            total += point_load_deflection(xi, dP)
        return total
    d = 0.0
    for a, P in point_loads:
        d += point_load_deflection(a, P)
    for x1, x2, w in dist_loads:
        d += uniform_load_deflection(x1, x2, w)
    return d
def max_deflection_cantilever(L_ft, point_loads, dist_loads, E_ksi, I_in4):
    """Maximum deflection (typically at free end for cantilever)."""
    max_d = 0.0
    for i in range(1001):
        x = i * L_ft / 1000.0
        d = abs(deflection_cantilever(x, L_ft, point_loads, dist_loads, E_ksi, I_in4))
        if d > max_d:
            max_d = d
    return max_d
# ----------------------------------------------------------------------
# Maximum moment and reactions for simply supported beam
def compute_main_span_moment(L_ft, point_loads, dist_loads):
    R_A = 0.0
    R_B = 0.0
    for a, P in point_loads:
        R_A += P * (L_ft - a) / L_ft
        R_B += P * a / L_ft
    for x1, x2, w in dist_loads:
        length = x2 - x1
        total = w * length
        centroid = x1 + length / 2.0
        R_A += total * (L_ft - centroid) / L_ft
        R_B += total * centroid / L_ft
    def shear(x):
        V = R_A
        for a, P in point_loads:
            if a <= x:
                V -= P
        for x1, x2, w in dist_loads:
            if x2 <= x:
                V -= w * (x2 - x1)
            elif x1 < x < x2:
                V -= w * (x - x1)
        return V
    critical = [0.0, L_ft]
    for a, _ in point_loads:
        critical.append(a)
    for x1, x2, _ in dist_loads:
        critical.append(x1)
        critical.append(x2)
    critical_sorted = sorted(set(critical))
    for i in range(len(critical_sorted) - 1):
        xL = critical_sorted[i]
        xR = critical_sorted[i + 1]
        if xR - xL < 1e-4:
            continue
        sL = shear(xL + 1e-6)
        sR = shear(xR - 1e-6)
        if sL * sR < 0:
            lo, hi = xL, xR
            for _ in range(30):
                mid = (lo + hi) / 2.0
                if shear(mid) > 0:
                    lo = mid
                else:
                    hi = mid
            critical.append((lo + hi) / 2.0)
    critical = sorted(set(critical))
    M_max = 0.0
    for x in critical:
        M = R_A * x
        for a, P in point_loads:
            if a <= x:
                M -= P * (x - a)
        for x1, x2, w in dist_loads:
            if x2 <= x:
                length = x2 - x1
                M -= w * length * (x - (x1 + length / 2.0))
            elif x1 < x < x2:
                length = x - x1
                M -= w * length * (x - (x1 + length / 2.0))
        if M > M_max:
            M_max = M
    return M_max, R_A, R_B
# ----------------------------------------------------------------------
# Cantilever moment and reaction
# Load position 'a' is measured from the FIXED support
# Moment at fixed support = sum of (P * a) for each load
def compute_cantilever_moment(L_ft, point_loads, dist_loads):
    """Compute maximum moment at fixed support for cantilever."""
    M = 0.0
    for a, P in point_loads:
        # Moment = load * distance from fixed support
        M += P * a
    for x1, x2, w in dist_loads:
        length = x2 - x1
        centroid = x1 + length / 2.0
        # Moment = total load * centroid distance from fixed support
        M += w * length * centroid
    return M
def compute_cantilever_reaction(L_ft, point_loads, dist_loads):
    """Compute reaction (shear) at fixed support."""
    R = 0.0
    for a, P in point_loads:
        R += P
    for x1, x2, w in dist_loads:
        R += w * (x2 - x1)
    return R
# ----------------------------------------------------------------------
# Beam selection functions (wood first, then steel)
def select_wood_beam(M_ftkips, L_ft, point_loads, dist_loads, defl_limit,
                     const_dim, const_value, is_cantilever):
    allowed_defl = L_ft * 12.0 / defl_limit
    candidates = []
    for desc, mat, w, d, plf, fb, e, Ix, Sx in wood_list:
        if const_dim == 'D' and d > const_value:
            continue
        if const_dim == 'B' and w > const_value:
            continue
        # fb is in psi, convert M from ft-kips to lb-in
        S_req = M_ftkips * 12000.0 / fb
        if Sx < S_req:
            continue
        if is_cantilever:
            actual_defl = max_deflection_cantilever(L_ft, point_loads, dist_loads, e, Ix)
        else:
            actual_defl = max_deflection_simply_supported(L_ft, point_loads, dist_loads, e, Ix)
        if actual_defl <= allowed_defl:
            candidates.append((plf, desc, mat, w, d, Ix, Sx, actual_defl, S_req))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    best = candidates[0]
    return (best[1], best[2], best[5], best[8], best[5], best[6], best[7], best[3], best[4], best[0])
def select_steel_beam(M_ftkips, L_ft, point_loads, dist_loads, defl_limit, is_cantilever):
    allowed_defl = L_ft * 12.0 / defl_limit
    candidates = []
    for desc, Ix, Sx, plf, fb, e in steel_sections:
        # fb is in psi, convert M from ft-kips to lb-in
        S_req = M_ftkips * 12000.0 / fb
        if Sx < S_req:
            continue
        if is_cantilever:
            actual_defl = max_deflection_cantilever(L_ft, point_loads, dist_loads, e, Ix)
        else:
            actual_defl = max_deflection_simply_supported(L_ft, point_loads, dist_loads, e, Ix)
        if actual_defl <= allowed_defl:
            candidates.append((plf, desc, Ix, Sx, actual_defl, S_req))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        best = candidates[0]
        return (best[1], best[2], best[5], best[2], best[3], best[4])
    if steel_sections:
        last = steel_sections[-1]
        S_req = M_ftkips * 12000.0 / last[4]
        return (last[0], last[1], S_req, last[1], last[2], 0.0)
    return ("None", 0, 0, 0, 0, 0)
# ----------------------------------------------------------------------
# Streamlit UI and input_beam adapted to preserve original logic and variable names
st.set_page_config(page_title="Beam Program - Streamlit", layout="wide")
st.title("BEAM PROGRAM - CORRECTED (CANTILEVERS + MAIN SPAN)")

# Helper to display the same text as original print statements
def print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text = sep.join(str(a) for a in args) + end
    # Streamlit write will add its own newline; use markdown to preserve formatting
    st.write(text)

# Input helper for a single beam using Streamlit widgets
def input_beam(beam_name, max_len, beam_id):
    st.subheader(f"INPUT FOR {beam_name}")
    # Number of point loads
    n = st.number_input(f"Number of point loads for {beam_name}", min_value=0, step=1, value=0, key=f"n_{beam_id}")
    point_loads = []
    cumulative_dist = 0.0
    if n > 0:
        st.write(f"Enter point loads for {beam_name}:")
        for i in range(1, int(n) + 1):
            st.markdown(f"**Point load {i}:**")
            p_expr = st.text_input(f"  P (KIPS) (e.g., 2*3+4) for point {i}", value="0", key=f"p_{beam_id}_{i}")
            p = evaluate_expression(p_expr)
            if i == 1:
                d_val = st.number_input(f"  Distance from support (FT) for point {i}", value=0.0, key=f"d_{beam_id}_{i}")
            else:
                d_val = st.number_input(f"  Distance from previous point (FT) for point {i}", value=0.0, key=f"d_{beam_id}_{i}")
            cumulative_dist += float(d_val)
            point_loads.append((cumulative_dist, p))
            st.write(f"    Load at {cumulative_dist:.2f} ft from support")
    num_seg = int(n) + 1
    dist_loads = []
    st.write(f"INPUT DISTRIBUTED LOADS (for {num_seg} segments) for {beam_name}")
    seg_boundaries = [0.0] + [pl[0] for pl in point_loads] + [max_len]
    for seg in range(num_seg):
        start = seg_boundaries[seg]
        end = seg_boundaries[seg + 1]
        w_expr = st.text_input(f"  W{seg} (K/FT) for segment {seg + 1} (from {start:.2f} to {end:.2f} ft)", value="0", key=f"w_{beam_id}_{seg}")
        w = evaluate_expression(w_expr)
        if w != 0 and end > start:
            dist_loads.append((start, end, w))
    return point_loads, dist_loads

# Sidebar inputs that correspond to the original top-level prompts
with st.sidebar:
    st.header("Beam Setup")
    st.write("SELECT BEAM MATERIAL TYPE:")
    st.write("STEEL BEAM (max W16x36)        --- 0")
    st.write("WOOD/PSL BEAM (max 8x18)       --- 1")
    st.write("ROOF BEAM (wood)               --- 2")
    st.write("FLOOR BEAM (wood)              --- 3")
    mat_choice = st.selectbox("Enter selection", options=["0", "1", "2", "3"], index=1, key="mat_choice")
    beam_mat = int(mat_choice)
    force_steel = (beam_mat == 0)
    if beam_mat == 2:
        beam_label = "ROOF BEAM"
        st.write("Roof finish for deflection limit:")
        finish = st.selectbox("Enter 1, 2 or 3", options=["1", "2", "3"], index=0, key="finish")
        if finish == '1':
            defl_limit = 240
        elif finish == '2':
            defl_limit = 180
        else:
            defl_limit = 120
    elif beam_mat == 3:
        beam_label = "FLOOR BEAM"
        defl_limit = 240
    elif beam_mat == 0:
        beam_label = "STEEL BEAM"
        defl_limit = 240
    else:
        beam_label = "WOOD/PSL BEAM"
        defl_limit = 240

    const_dim, const_value = None, None
    if not force_steel:
        st.write("Enter maximum wood dimensions (leave blank to skip)")
        ans = st.selectbox("Which dimension is CONSTANT?", options=["Skip", "D (depth)", "B (width)"], index=0, key="const_dim_choice")
        if ans == "D (depth)":
            const_dim = 'D'
            const_value = st.number_input("Maximum allowed depth (inches)", value=100.0, key="const_depth")
            st.write(f"Max depth = {const_value} in")
        elif ans == "B (width)":
            const_dim = 'B'
            const_value = st.number_input("Maximum allowed width (inches)", value=100.0, key="const_width")
            st.write(f"Max width = {const_value} in")

    loc = st.text_input("BM. LOCATION---", value="", key="loc")
    L0_1 = st.number_input("LEFT CANTILEVER LENGTH (FT):", value=0.0, key="L0_1")
    L0_2 = st.number_input("MAIN SPAN LENGTH (FT):", value=0.0, key="L0_2")
    L0_3 = st.number_input("RIGHT CANTILEVER LENGTH (FT):", value=0.0, key="L0_3")
    L0 = [0.0] * 5
    L0[1] = float(L0_1)
    L0[2] = float(L0_2)
    L0[3] = float(L0_3)
    st.write(f"Left cantilever: {L0[1]} ft, Main span: {L0[2]} ft, Right cantilever: {L0[3]} ft")

# Input loads for each beam using expanders in main area
beams_data = {}
for beam_id, name, length, is_cant in [(1, "LEFT CANTILEVER", L0[1], True),
                                       (2, "MAIN SPAN", L0[2], False),
                                       (3, "RIGHT CANTILEVER", L0[3], True)]:
    if length == 0:
        beams_data[beam_id] = ([], [], 0.0, 0.0, 0.0, 0.0, is_cant)
        continue
    with st.expander(f"Inputs for {name} (length {length} ft)", expanded=(beam_id==2)):
        point_loads, dist_loads = input_beam(name, length, beam_id)
    if is_cant:
        M = compute_cantilever_moment(length, point_loads, dist_loads)
        R = compute_cantilever_reaction(length, point_loads, dist_loads)
        beams_data[beam_id] = (point_loads, dist_loads, M, R, 0.0, length, is_cant)
    else:
        M, R_left, R_right = compute_main_span_moment(length, point_loads, dist_loads)
        beams_data[beam_id] = (point_loads, dist_loads, M, R_left, R_right, length, is_cant)

# Output results
st.markdown("---")
st.header("RESULTS")
for beam_id in [1, 2, 3]:
    point_loads, dist_loads, M, R_left, R_right, L, is_cant = beams_data[beam_id]
    if L == 0:
        continue
    st.markdown("----")
    if beam_id == 1:
        st.subheader("BEAM 1 - LEFT CANTILEVER")
        st.write(f"  Location: {loc}")
        st.write(f"  Length = {L} ft (fixed at right, free at left)")
    elif beam_id == 2:
        st.subheader("BEAM 2 - MAIN SPAN")
        st.write(f"  Location: {loc}")
        st.write(f"  Span = {L} ft (simply supported)")
    else:
        st.subheader("BEAM 3 - RIGHT CANTILEVER")
        st.write(f"  Location: {loc}")
        st.write(f"  Length = {L} ft (fixed at left, free at right)")
    st.write(f"  Type: {beam_label}")
    st.write(f"  Maximum moment = {M:.2f} ft-kips")
    st.write(f"  Deflection limit: L/{defl_limit} = {L * 12 / defl_limit:.2f} in")
    if force_steel:
        desc, I_req, S_req, I_prov, S_prov, defl = select_steel_beam(
            M, L, point_loads, dist_loads, defl_limit, is_cant)
        st.write(f"  Required S = {S_req:.1f} in^3, Required I = {I_req:.0f} in^4")
        st.write(f"  Selected STEEL: {desc}")
        st.write(f"  Provided I = {I_prov:.0f} in^4, S = {S_prov:.1f} in^3")
        st.write(f"  Actual deflection = {defl:.3f} in")
    else:
        wood_res = select_wood_beam(M, L, point_loads, dist_loads, defl_limit,
                                    const_dim, const_value, is_cant)
        if wood_res is None:
            st.write("  No wood beam (<=8x18) satisfies both strength and deflection.")
            desc, I_req, S_req, I_prov, S_prov, defl = select_steel_beam(
                M, L, point_loads, dist_loads, defl_limit, is_cant)
            if desc != "None":
                st.write(f"  Steel alternative: {desc} (I={I_prov:.0f} in^4, S={S_prov:.1f} in^3, deflection={defl:.3f} in)")
        else:
            desc, mat, I_req, S_req, I_prov, S_prov, defl, width, depth, plf = wood_res
            st.write(f"  Required S = {S_req:.1f} in^3, Required I = {I_req:.0f} in^4")
            st.write(f"  Selected WOOD: {desc} ({mat})")
            st.write(f"  Provided I = {I_prov:.0f} in^4, S = {S_prov:.1f} in^3")
            st.write(f"  Actual deflection = {defl:.3f} in")
            st.write(f"  Dimensions: {width:.1f}\" x {depth:.1f}\", weight = {plf:.1f} lb/ft")
    if is_cant:
        st.write(f"  Reaction at fixed support = {R_left:.2f} kips")
    else:
        st.write(f"  Left reaction = {R_left:.2f} kips, Right reaction = {R_right:.2f} kips")
st.markdown("====")
