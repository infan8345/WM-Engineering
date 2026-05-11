import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from solver import (
    compute_reactions,
    shear_at,
    moment_at,
    compute_max_moment,
    compute_midspan_deflection
)

from beam_selection import (
    select_steel_beam,
    select_wood_beam,
    E_steel,
    E_wood
)

# ============================================================
#   STREAMLIT UI
# ============================================================

st.title("General Overhang Beam — Steel & Wood Selector")
st.write("Left Overhang → Simple Span → Right Overhang")

# ------------------------------------------------------------
#   GEOMETRY INPUT
# ------------------------------------------------------------
st.header("Beam Geometry")

L_left = st.number_input("Left Overhang Length (ft)", min_value=0.0, value=0.0)
L_main = st.number_input("Main Span Length (ft)", min_value=1.0, value=10.0)
L_right = st.number_input("Right Overhang Length (ft)", min_value=0.0, value=0.0)

# Convert to inches
a = L_left * 12
b = (L_left + L_main) * 12
L_total = (L_left + L_main + L_right) * 12

# ------------------------------------------------------------
#   LOAD INPUT — LEFT OVERHANG
# ------------------------------------------------------------
st.header("Left Overhang Loads")

Npt_left = st.number_input("Number of point loads (left overhang)", min_value=0, step=1)
point_left = []
for i in range(Npt_left):
    P = st.number_input(f"Left P{i+1} (kips)", value=1.0)
    x = st.number_input(f"Left P{i+1} location from left end (ft)", value=0.0)
    point_left.append((P, x * 12))

Nud_left = st.number_input("Number of uniform loads (left overhang)", min_value=0, step=1)
ud_left = []
for i in range(Nud_left):
    w = st.number_input(f"Left w{i+1} (kips/ft)", value=0.1)
    x1 = st.number_input(f"Left w{i+1} start (ft)", value=0.0)
    x2 = st.number_input(f"Left w{i+1} end (ft)", value=L_left)
    ud_left.append((w, x1 * 12, x2 * 12))

# ------------------------------------------------------------
#   LOAD INPUT — MAIN SPAN
# ------------------------------------------------------------
st.header("Main Span Loads")

Npt_main = st.number_input("Number of point loads (main span)", min_value=0, step=1)
point_main = []
for i in range(Npt_main):
    P = st.number_input(f"Main P{i+1} (kips)", value=1.0)
    x = st.number_input(f"Main P{i+1} location from left end (ft)", value=L_left)
    point_main.append((P, x * 12))

Nud_main = st.number_input("Number of uniform loads (main span)", min_value=0, step=1)
ud_main = []
for i in range(Nud_main):
    w = st.number_input(f"Main w{i+1} (kips/ft)", value=0.1)
    x1 = st.number_input(f"Main w{i+1} start (ft)", value=L_left)
    x2 = st.number_input(f"Main w{i+1} end (ft)", value=L_left + L_main)
    ud_main.append((w, x1 * 12, x2 * 12))

# ------------------------------------------------------------
#   LOAD INPUT — RIGHT OVERHANG
# ------------------------------------------------------------
st.header("Right Overhang Loads")

Npt_right = st.number_input("Number of point loads (right overhang)", min_value=0, step=1)
point_right = []
for i in range(Npt_right):
    P = st.number_input(f"Right P{i+1} (kips)", value=1.0)
    x = st.number_input(f"Right P{i+1} location from left end (ft)", value=L_left + L_main)
    point_right.append((P, x * 12))

Nud_right = st.number_input("Number of uniform loads (right overhang)", min_value=0, step=1)
ud_right = []
for i in range(Nud_right):
    w = st.number_input(f"Right w{i+1} (kips/ft)", value=0.1)
    x1 = st.number_input(f"Right w{i+1} start (ft)", value=L_left + L_main)
    x2 = st.number_input(f"Right w{i+1} end (ft)", value=L_left + L_main + L_right)
    ud_right.append((w, x1 * 12, x2 * 12))

# ------------------------------------------------------------
#   COMBINE LOADS
# ------------------------------------------------------------
point_loads = point_left + point_main + point_right
uniform_loads = ud_left + ud_main + ud_right

# ------------------------------------------------------------
#   ANALYSIS
# ------------------------------------------------------------
if st.button("Run Analysis"):

    # Reactions
    RA, RB = compute_reactions(point_loads, uniform_loads, a, b, L_total)

    st.subheader("Reactions")
    st.write(f"RA = {RA:.3f} kips")
    st.write(f"RB = {RB:.3f} kips")

    # Max moment
    M_max = compute_max_moment(point_loads, uniform_loads, RA, RB, a, b, L_total)
    st.write(f"Maximum Moment = {M_max:.3f} kip-in")

    # Midspan deflection
    delta = compute_midspan_deflection(point_loads, uniform_loads, a, b, E_steel, 1e6)
    st.write(f"Midspan Deflection (shape only) = {delta:.4f} in")

    # --------------------------------------------------------
    #   PLOTS
    # --------------------------------------------------------
    xs = np.linspace(0, L_total, 600)
    Vs = [shear_at(x, point_loads, uniform_loads, RA, RB, a, b) for x in xs]
    Ms = [moment_at(x, point_loads, uniform_loads, RA, RB, a, b) for x in xs]

    fig, ax = plt.subplots()
    ax.plot(xs/12, Vs)
    ax.set_title("Shear Diagram (kips)")
    ax.set_xlabel("x (ft)")
    ax.set_ylabel("V (kips)")
    st.pyplot(fig)

    fig, ax = plt.subplots()
    ax.plot(xs/12, Ms)
    ax.set_title("Moment Diagram (kip-in)")
    ax.set_xlabel("x (ft)")
    ax.set_ylabel("M (kip-in)")
    st.pyplot(fig)

    # --------------------------------------------------------
    #   BEAM SELECTION
    # --------------------------------------------------------
    st.header("Beam Selection")

    material = st.selectbox("Material", ["Steel (W-shapes)", "Wood (Dimensional + PSL)"])
    L_main_in = L_main * 12
    delta_allow = L_main_in / 360

    if material == "Steel (W-shapes)":
        name, S, I = select_steel_beam(abs(M_max), delta_allow, L_main_in)
        if name:
            st.success(f"Selected Steel Beam: {name}")
        else:
            st.error("No adequate steel beam found.")

    else:
        name, S, I = select_wood_beam(abs(M_max), delta_allow, L_main_in)
        if name:
            st.success(f"Selected Wood/PSL Beam: {name}")
        else:
            st.error("No adequate wood/PSL beam found.")
