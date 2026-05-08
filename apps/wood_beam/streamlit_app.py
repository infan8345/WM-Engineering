import streamlit as st
import math

st.title("Wood Beam Design Calculator")
st.write("NDS-based allowable stress design for residential and commercial beams.")

# -----------------------------
# INPUTS
# -----------------------------
st.header("Beam Inputs")

span_ft = st.number_input("Span (ft)", min_value=1.0, value=10.0)
span = span_ft * 12  # inches

Fb = st.number_input("Allowable bending stress Fb (psi)", value=1000.0)
Fv = st.number_input("Allowable shear stress Fv (psi)", value=135.0)
E = st.number_input("Modulus of Elasticity E (psi)", value=1_200_000.0)

b = st.number_input("Beam width b (in)", value=1.5)
d = st.number_input("Beam depth d (in)", value=9.25)

w = st.number_input("Uniform load w (plf)", value=500.0)
P = st.number_input("Point load P (lbs)", value=0.0)
a_ft = st.number_input("Point load location (ft from left)", value=span_ft/2)
a = a_ft * 12

# -----------------------------
# SECTION PROPERTIES
# -----------------------------
S = b * d**2 / 6
I = b * d**3 / 12

# -----------------------------
# UNIFORM LOAD RESULTS
# -----------------------------
M_w = w * span_ft**2 / 8  # ft-lb
M_w_in = M_w * 12

V_w = w * span_ft / 2  # lb

# -----------------------------
# POINT LOAD RESULTS
# -----------------------------
M_p = P * a_ft * (span_ft - a_ft) / span_ft  # ft-lb
M_p_in = M_p * 12

V_p = P / 2
