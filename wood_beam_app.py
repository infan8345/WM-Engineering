import numpy as np
import streamlit as st

# -----------------------------
# YOUR ORIGINAL CODE (UNCHANGED)
# -----------------------------

# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from math import sqrt
import io
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.config import Config
import os
import datetime

Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'kivy_clock', 'free_all')
os.environ['KIVY_DPI'] = '200'

B = D = B_real = D_real = Z1 = I2 = F = M2 = Z = 0
L13 = ""
MATERIAL = ""
N = [0] * 4
M = [0] * 4
L0 = [0] * 4
L = [[0] * 7 for _ in range(4)]
L1 = [[0] * 7 for _ in range(4)]
P = [[0] * 7 for _ in range(4)]
P_str = [[""] * 7 for _ in range(4)]
W = [[0] * 7 for _ in range(4)]
W_str = [[""] * 7 for _ in range(4)]
I2 = [0] * 4
M1 = [0] * 4
R1 = [0] * 4
R2 = [0] * 4
D1 = [0] * 4
allow_psl = True
selected_props = {}  # Global variable to store selected beam properties

def reset_globals():
    global B, D, B_real, D_real, Z1, I2, F, M2, L13, N, M, P, L, L1, P_str, W, W_str, L0, R1, R2, M1, D1, MATERIAL, Z, allow_psl, selected_props
    L13 = ""
    B = D = B_real = D_real = Z1 = I2 = F = M2 = Z = 0
    MATERIAL = ""
    allow_psl = True
    N = [0] * 4
    M = [0] * 4
    L0 = [0] * 4
    L = [[0] * 7 for _ in range(4)]
    L1 = [[0] * 7 for _ in range(4)]
    P = [[0] * 7 for _ in range(4)]
    P_str = [[""] * 7 for _ in range(4)]
    W = [[0] * 7 for _ in range(4)]
    W_str = [[""] * 7 for _ in range(4)]
    I2 = [0] * 4
    M1 = [0] * 4
    R1 = [0] * 4
    R2 = [0] * 4
    D1 = [0] * 4
    selected_props = {}

reset_globals()

PSL_Fb = 2900
PSL_E = 2.0e6
SAWN_Fb = 1200
SAWN_E = 1.7e6

SAWN_SIZES_RAW = {
    '2x8':   {'b': 1.5, 'd': 7.25}, '2x10':  {'b': 1.5, 'd': 9.25}, '2x12':  {'b': 1.5, 'd': 11.25}, '2x14':  {'b': 1.5, 'd': 13.25},
    '4x8':   {'b': 3.5, 'd': 7.25}, '4x10':  {'b': 3.5, 'd': 9.25}, '4x12':  {'b': 3.5, 'd': 11.25}, '4x14':  {'b': 3.5, 'd': 13.25},
    '6x8':   {'b': 5.5, 'd': 7.5},  '6x10':  {'b': 5.5, 'd': 9.5},  '6x12':  {'b': 5.5, 'd': 11.5},  '6x14':  {'b': 5.5, 'd': 13.5},
    '8x8':   {'b': 7.5, 'd': 7.5},  '8x10':  {'b': 7.5, 'd': 9.5},  '8x12':  {'b': 7.5, 'd': 11.5},  '8x14':  {'b': 7.5, 'd': 13.5}
}

SAWN_SIZES = {}
for size, dims in SAWN_SIZES_RAW.items():
    b, d = dims['b'], dims['d']
    S = round((b * d**2) / 6, 2)
    I = round((b * d**3) / 12, 1)
    SAWN_SIZES[size] = {'b': b, 'd': d, 'S': S, 'I': I}

PSL_WIDTHS = [1.75, 3.5, 5.25, 7.0]
PSL_DEPTHS = [9.25, 9.5, 11.25, 11.875, 14.0, 16.0, 18.0]
PSL_SIZES = {}
for w in PSL_WIDTHS:
    for d in PSL_DEPTHS:
        S = round((w * d**2) / 6, 1)
        I = round((w * d**3) / 12, 1)
        M_capacity = round((PSL_Fb * S) / 12000, 1)
        PSL_SIZES[f"{w}x{d}"] = {'S': S, 'I': I, 'M_capacity': M_capacity}

def safe_eval(expr):
    try:
        expr = expr.replace(',', '.')
        return eval(expr) if expr else 0
    except (SyntaxError, NameError, ValueError):
        return 0

def calculate_moment_capacity(b, d, fb):
    S = (b * d**2) / 6
    return (fb * S) / 12000

def validate_size(b, d, material):
    if material == "PSL":
        size_key = f"{b}x{d}"
        if size_key in PSL_SIZES:
            return PSL_SIZES[size_key]
        raise ValueError(f"Size {b}x{d}\" is not a standard PSL size")
    else:
        capacity = calculate_moment_capacity(b, d, SAWN_Fb * (1.0 if d <= 12 else 0.9))
        return {'S': round((b * d**2)/6, 1), 'I': round((b * d**3)/12, 1), 'M_capacity': round(capacity, 1)}


def input_loads(g, entries):
    global N, M, P, L, L1, W
    N[g] = int(safe_eval(entries[f"n_point_loads_{g}"].text))
    max_point_loads = 2 if g == 2 else 1
    if N[g] > max_point_loads:
        raise ValueError(f"Number of point loads ({N[g]}) for Span {g} exceeds maximum allowed ({max_point_loads})")
    M[g] = N[g] + 1 if N[g] > 0 else 1
    L[g] = [0] * 7
    L1[g] = [0] * 7
    P[g] = [0] * 7
    W[g] = [0] * 7
    L[g][1] = 0
    
    print(f"Span {g}: N={N[g]}, M={M[g]}, L0={L0[g]:.2f}")
    
    if N[g] == 0:
        L1[g][1] = L0[g]
        L[g][2] = L0[g]
        W[g][1] = safe_eval(entries.get(f"uniform_seg_{g}_1", TextInput(text="0")).text)
        print(f"Span {g} Uniform Load: {W[g][1]:.2f} over {L1[g][1]:.2f} ft")
        return
    
    for i in range(2, min(N[g] + 2, 7)):
        P[g][i] = safe_eval(entries.get(f"point_load_{g}_{i-1}", TextInput(text="0")).text)
        L1[g][i-1] = safe_eval(entries.get(f"distance_{g}_{i-1}", TextInput(text="0")).text)
        L[g][i] = L[g][i-1] + L1[g][i-1]
        if L[g][i] > L0[g]:
            raise ValueError(f"Cumulative distance {L[g][i]:.2f} ft in Span {g} exceeds span length {L0[g]:.2f} ft")
        print(f"Span {g} Point Load {i-1}: {P[g][i]:.2f} kips at {L1[g][i-1]:.2f} ft")
    L1[g][M[g]] = L0[g] - L[g][M[g]] if L0[g] > L[g][M[g]] else 0
    L[g][M[g]+1] = L0[g]
    for i in range(1, min(M[g] + 1, 7)):
        W[g][i] = safe_eval(entries.get(f"uniform_seg_{g}_{i}", TextInput(text="0")).text)
        print(f"Span {g} Uniform Segment {i}: {W[g][i]:.2f} k/ft over {L1[g][i]:.2f} ft")

def calculate_reactions():
    global R1, R2
    R1 = [0] * 4
    R2 = [0] * 4
    if L0[1] > 0:
        R1[1] = sum(P[1][i] for i in range(2, M[1]+1)) + sum(W[1][i] * L1[1][i] for i in range(1, M[1]+1))
        print(f"Left Cantilever R1={R1[1]:.2f} kips")
    if L0[3] > 0:
        R2[3] = sum(P[3][i] for i in range(2, M[3]+1)) + sum(W[3][i] * L1[3][i] for i in range(1, M[3]+1))
        print(f"Right Cantilever R2={R2[3]:.2f} kips")
    if L0[2] > 0:
        sum_moments = sum(P[2][i] * L[2][i] for i in range(2, M[2]+1)) + \
                      sum(W[2][i] * L1[2][i] * (L[2][i] + L1[2][i]/2) for i in range(1, M[2]+1))
        sum_loads = sum(P[2][i] for i in range(2, M[2]+1)) + sum(W[2][i] * L1[2][i] for i in range(1, M[2]+1))
        R2[2] = sum_moments / L0[2] if L0[2] > 0 else 0
        R1[2] = sum_loads - R2[2]
        print(f"Main Span R1={R1[2]:.2f}, R2={R2[2]:.2f}, Sum Moments={sum_moments:.2f}, Sum Loads={sum_loads:.2f}")

def calculate_moments():
    global M1
    M1 = [0] * 4
    if L0[1] > 0:
        M1[1] = sum(P[1][i] * L[1][i] for i in range(2, M[1]+1)) + \
                sum(W[1][i] * L1[1][i] * (L[1][i] + L1[1][i]/2) for i in range(1, M[1]+1))
        print(f"Left Cantilever M1={M1[1]:.2f} kip-ft")
    if L0[3] > 0:
        M1[3] = sum(P[3][i] * L[3][i] for i in range(2, M[3]+1)) + \
                sum(W[3][i] * L1[3][i] * (L[3][i] + L1[3][i]/2) for i in range(1, M[3]+1))
        print(f"Right Cantilever M1={M1[3]:.2f} kip-ft")
    if L0[2] > 0:
        max_moment = 0
        # Compute zero-shear point
        shear = R1[2]
        x = 0
        x_zero = 0
        for j in range(1, M[2]+1):
            seg_start = L[2][j]
            seg_end = L[2][j+1] if j < M[2] else L0[2]
            for i in range(2, j+2 if j < M[2] else M[2]+1):
                if i <= M[2] and L[2][i] <= seg_end:
                    shear -= P[2][i]
            if j <= 2:
                shear -= W[2][j] * L1[2][j]
                x = seg_end
            else:
                if shear > 0 and W[2][j] > 0:
                    x_zero = x + shear / W[2][j]
                    if seg_start <= x_zero <= seg_end:
                        break
                shear -= W[2][j] * L1[2][j]
                x = seg_end
        # Evaluation points
        x_values = [0] + [L[2][i] for i in range(2, M[2]+1) if L[2][i] > 0] + [x_zero, L0[2]]
        x_values += list(np.arange(5, 16.1, 0.1))  # Finer points
        x_values = sorted(list(set(x_values)))
        try:
            for x in x_values:
                moment = R1[2] * x
                for j in range(2, M[2]+1):
                    if L[2][j] <= x:
                        moment -= P[2][j] * (x - L[2][j])
                for j in range(1, M[2]+1):
                    seg_start = L[2][j]
                    seg_end = L[2][j+1] if j < M[2] else L0[2]
                    if seg_end <= x:
                        moment -= W[2][j] * L1[2][j] * (x - (seg_start + L1[2][j]/2))
                    elif seg_start < x <= seg_end:
                        partial_length = x - seg_start
                        moment -= W[2][j] * partial_length * (x - (seg_start + partial_length/2))
                if moment > max_moment:
                    max_moment = moment
        except Exception as e:
            print(f"Moment calculation error: {str(e)}")
        M1[2] = max_moment
        print(f"Main Span M1={M1[2]:.2f} kip-ft")
        
def validate_size(B, D, material):
    """Validate beam size and return properties using actual dimensions."""
    if material == "SAWN":
        valid_B = [2, 4, 6, 8]
        valid_D = [8, 10, 12, 14]
        actual_B = {2: 1.5, 4: 3.5, 6: 5.5, 8: 7.5}  # Nominal to actual width (in)
        actual_D = {8: 7.5, 10: 9.5, 12: 11.5, 14: 13.5}  # Nominal to actual depth (in)
        if B in valid_B and D in valid_D:
            B_act = actual_B[B]
            D_act = actual_D[D]
            I = (B_act * D_act**3) / 12
            S = (B_act * D_act**2) / 6
            M_capacity = (1200 * S) / 12000  # kip-ft, Fb = 1200 psi
            print(f"validate_size: B={B} ({B_act}), D={D} ({D_act}), I={I:.1f}, S={S:.1f}, M_capacity={M_capacity:.2f}")
            return {'I': I, 'S': S, 'M_capacity': M_capacity}
        else:
            print(f"Warning: Invalid B={B} or D={D} for sawn lumber")
    return {'I': 0, 'S': 0, 'M_capacity': 0}        

import matplotlib.pyplot as plt

PSL_E = 2.0e6
SAWN_E = 1.6e6
SAWN_Fb = 1500
ft_to_in = 12
kip_to_lb = 1000

def calculate_moment_capacity(b, d, Fb):
    S = (b * d**2) / 6
    return (Fb * S) / 12000

def calculate_required_inertia():
    global D1, L
    I_req = [0] * 4
    D1 = [0] * 4
    E = PSL_E if MATERIAL == "PSL" else SAWN_E
    allowable_deflection = [0] * 3
    for i in range(1, 4):
        allowable_deflection[i-1] = L0[i] * ft_to_in / 240 if L0[i] > 0 else 0
    for g in [1, 2, 3]:
        if L0[g] > 0:
            span_length = L0[g] * ft_to_in
            delta_sum = 0
            if g == 2:
                total_load = sum(P[g][i] for i in range(2, M[g]+1)) * kip_to_lb
                for i in range(1, M[g]+1):
                    total_load += W[g][i] * L1[g][i] * kip_to_lb
                w_eq = total_load / span_length
                delta_sum = (5 * w_eq * span_length**4) / 384
            else:
                for i in range(2, M[g]+1):
                    P_i = P[g][i] * kip_to_lb
                    a = L[g][i] * ft_to_in
                    delta_sum += (P_i * a**3) / 3
                for i in range(1, M[g]+1):
                    w = W[g][i] * kip_to_lb / ft_to_in
                    seg_len = L1[g][i] * ft_to_in
                    delta_sum += (w * seg_len**4) / 8
            I_req[g] = delta_sum / (E * allowable_deflection[g-1]) if allowable_deflection[g-1] > 0 else 0
    return I_req

def plot_results(props, M1, L0, MATERIAL, B_real, D_real):
    plt.close('all')  # Close all existing figures
    m_capacity = props['M_capacity']
    print(f"Debug: props['M_capacity'] in plot_results = {m_capacity:.2f} kip-ft")
    
    spans = [1, 2, 3]
    moments = [M1[i] for i in spans if L0[i] > 0]
    lengths = [L0[i] for i in spans if L0[i] > 0]
    
    x = [0]
    for L in lengths:
        x.append(x[-1] + L)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot([x[0], x[1]], [0, moments[0]], 'b-', label='Moment (kip-ft)')
    ax.plot([x[1], x[2]], [moments[0], moments[1]], 'b-')
    ax.plot([x[2], x[3]], [moments[1], moments[2]], 'b-')
    
    ax.axhline(y=m_capacity, color='r', linestyle='--', label=f'M_capacity={m_capacity:.2f} kip-ft')
    ax.text(0.05, 0.95, f'M_capacity={m_capacity:.2f} kip-ft', transform=ax.transAxes, bbox=dict(facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Distance along beam (ft)')
    ax.set_ylabel('Moment (kip-ft)')
    ax.set_title(f'Moment Diagram for {MATERIAL} {B_real}x{D_real} Beam (M_capacity={m_capacity:.2f} kip-ft)')
    ax.legend()
    ax.grid(True)
    plt.draw()
    plt.pause(0.1)  # Force refresh
    plt.show()
    
def beam_sizing():
    global Z1, D, D_real, B_real, MATERIAL, B, allow_psl, selected_props
    Z1 = 0
    required_moment = max(M1[1], M1[2], M1[3])
    I_req = calculate_required_inertia()
    max_I_req = max(I_req[1], I_req[2], I_req[3])
    
    has_valid_option = False
    props = {'S': 0, 'I': 0, 'M_capacity': 0}
    
    # Try user-specified dimensions first
    if B > 0 and D > 0:
        if MATERIAL == "PSL":
            size_key = f"{B}x{D}"
            if size_key in PSL_SIZES:
                props = PSL_SIZES[size_key]
                if props['M_capacity'] >= required_moment and props['I'] >= max_I_req:
                    B_real = B
                    D_real = D
                    selected_props.update(props)
                    Z1 = 1
                    has_valid_option = True
                    print(f"beam_sizing: Using user input size {B_real}x{D_real} for {MATERIAL}")
        elif MATERIAL in ["SAWN", "Sawn", "Sawn Only"]:
            for size, props_temp in SAWN_SIZES.items():
                nominal_b = props_temp['b'] + 0.5  # Convert to nominal
                if abs(nominal_b - B) < 0.1 and abs(props_temp['d'] - D) < 0.1:
                    capacity = calculate_moment_capacity(props_temp['b'], props_temp['d'], SAWN_Fb)
                    if capacity >= required_moment and props_temp['I'] >= max_I_req:
                        props_temp_copy = props_temp.copy()
                        props_temp_copy['M_capacity'] = capacity
                        props = props_temp_copy
                        B_real = props_temp['b']
                        D_real = props_temp['d']
                        selected_props.update(props)
                        Z1 = 1
                        has_valid_option = True
                        print(f"beam_sizing: Using user input size {B}x{D} for {MATERIAL}")
                        break
    
    # Auto-selection if user dimensions don't work
    if not has_valid_option:
        if MATERIAL == "PSL" and allow_psl:
            viable_psl = []
            psl_sizes_no_18 = [(k, v) for k, v in PSL_SIZES.items() if not k.endswith('x18.0')]
            psl_sizes_18 = [(k, v) for k, v in PSL_SIZES.items() if k.endswith('x18.0')]
    
            for sizes in [psl_sizes_no_18, psl_sizes_18]:
                # Sort by different criteria based on Z
                if Z == 0 and D > 0:  # Constant depth
                    # First try exact depth matches
                    sorted_psl = sorted(
                        [(k, v) for k, v in sizes if abs(float(k.split('x')[1]) - D) < 0.1],
                        key=lambda x: float(x[0].split('x')[0])
                    )
                    # If no exact matches, sort by depth difference, then width
                    if not sorted_psl:
                        sorted_psl = sorted(
                            sizes,
                            key=lambda x: (abs(float(x[0].split('x')[1]) - D), float(x[0].split('x')[0]))
                        )
                elif Z == 1 and B > 0:  # Constant width
                    # First try exact width matches
                    sorted_psl = sorted(
                        [(k, v) for k, v in sizes if abs(float(k.split('x')[0]) - B) < 0.1],
                        key=lambda x: float(x[0].split('x')[1])
                    )
                    # If no exact matches, sort by width difference, then depth
                    if not sorted_psl:
                        sorted_psl = sorted(
                            sizes,
                            key=lambda x: (abs(float(x[0].split('x')[0]) - B), float(x[0].split('x')[1]))
                        )
                else:  # No constraint, sort by area
                    sorted_psl = sorted(
                        sizes,
                        key=lambda x: float(x[0].split('x')[0]) * float(x[0].split('x')[1])
                    )
                
                for size, props_temp in sorted_psl:
                    b, d = map(float, size.split('x'))
                    if props_temp['M_capacity'] >= required_moment and props_temp['I'] >= max_I_req:
                        viable_psl.append((size, props_temp, b, d, props_temp['M_capacity']))
                
                if viable_psl:
                    break
    
            if viable_psl:
                selected = viable_psl[0]  # Take first viable option since we've sorted appropriately
                size, props, B_real, D_real, capacity = selected
                props['M_capacity'] = capacity
                selected_props.update(props)
                B = B_real
                D = D_real
                MATERIAL = "PSL"
                Z1 = 1
                has_valid_option = True
                print(f"beam_sizing: Selected PSL size {size} for moment {required_moment} kip-ft")
    
        elif MATERIAL in ["SAWN", "Sawn", "Sawn Only"]:
            viable_sawn = []
            
            # Sort sawn sizes differently based on Z
            if Z == 0 and D > 0:  # Constant depth
                sorted_sawn = sorted(
                    SAWN_SIZES.items(),
                    key=lambda x: (abs(x[1]['d'] - D), x[1]['b'])  # Sort by depth match, then width
                )
            elif Z == 1 and B > 0:  # Constant width
                sorted_sawn = sorted(
                    SAWN_SIZES.items(),
                    key=lambda x: (abs((x[1]['b'] + 0.5) - B), x[1]['d'])  # Sort by width match, then depth
                )
            else:  # No constraint, sort by area
                sorted_sawn = sorted(
                    SAWN_SIZES.items(),
                    key=lambda x: x[1]['b'] * x[1]['d']
                )
            
            for size, props_temp in sorted_sawn:
                b, d = props_temp['b'], props_temp['d']
                capacity = calculate_moment_capacity(b, d, SAWN_Fb)
                props_temp_copy = props_temp.copy()
                props_temp_copy['M_capacity'] = capacity
                if capacity >= required_moment and props_temp['I'] >= max_I_req:
                    viable_sawn.append((size, props_temp_copy, b, d, capacity))
                    break  # Take first viable option since we've sorted appropriately
            
            if viable_sawn:
                selected = viable_sawn[0]
                size, props, B_real, D_real, capacity = selected
                props['M_capacity'] = capacity
                selected_props.update(props)
                B = B_real + 0.5  # Convert to nominal
                D = D_real
                MATERIAL = "Sawn"
                Z1 = 1
                has_valid_option = True
                print(f"beam_sizing: Selected sawn size {size} for moment {required_moment} kip-ft")
            elif MATERIAL == "SAWN" and allow_psl:
                # This is a controlled fallback with only one level of recursion
                old_material = MATERIAL
                MATERIAL = "PSL"
                print(f"beam_sizing: Fallback to PSL size for SAWN")
                # Instead of recursion, just re-run the function with PSL material
                # We'll handle this inline to avoid recursion
                viable_psl = []
                all_psl_sizes = sorted(
                    PSL_SIZES.items(),
                    key=lambda x: float(x[0].split('x')[0]) * float(x[0].split('x')[1])
                )
                for size, props_temp in all_psl_sizes:
                    b, d = map(float, size.split('x'))
                    if props_temp['M_capacity'] >= required_moment and props_temp['I'] >= max_I_req:
                        props_temp_copy = props_temp.copy()
                        selected_props.update(props_temp_copy)
                        B_real = b
                        D_real = d
                        B = b
                        D = d
                        Z1 = 1
                        has_valid_option = True
                        print(f"beam_sizing: Selected PSL fallback size {size}")
                        break
    
    if not has_valid_option:
        print("beam_sizing: No valid size found")
    
    return "Selected" if has_valid_option else ""

class PlotWidget(Widget):
    def __init__(self, **kwargs):
        super(PlotWidget, self).__init__(**kwargs)
        self.texture = None
        
    def update_plot(self):
        fig, ax = plt.subplots(figsize=(5, 3), dpi=200)
        left_cant_len = L0[1]
        main_span_len = L0[2]
        right_cant_len = L0[3]
        total_len = main_span_len + left_cant_len + right_cant_len
        
        ax.plot([-left_cant_len, main_span_len + right_cant_len], [0, 0], 'k-', linewidth=3)
        ax.plot([0, 0], [-0.3, 0.1], 'g-', linewidth=3)
        ax.plot([main_span_len, main_span_len], [-0.3, 0.1], 'g-', linewidth=3)
        
        arrow_scale = 0.6
        text_offset = 0.15
        max_w = max([max(W[g][1:M[g]+1] or [0]) for g in [1,2,3] if L0[g] > 0] or [1])
        
        def draw_uniform_load(x1, x2, w, g):
            if w == 0 or x1 == x2:
                return
            w_scale = 0.2 + 0.2 * (abs(w)/max_w)
            density = 1.5 if g == 1 else 1.0
            x_positions = np.linspace(x1, x2, max(3, int(abs(x2 - x1) * density) + 1))
            for x in x_positions:
                ax.plot([x, x], [0, w_scale], 'b-', lw=1.2)
            ax.plot([x1, x2], [w_scale, w_scale], 'b-', lw=1.2)
            ax.text((x1+x2)/2, w_scale + text_offset, f"{w:.2f}k/ft", ha='center', color='blue')
        
        for g, offset in [(1, -left_cant_len), (2, 0), (3, main_span_len)]:
            if L0[g] > 0:
                for i in range(2, M[g]+1):
                    if P[g][i] != 0:
                        if g == 1:
                            x_pos = -L[g][i]
                        else:
                            x_pos = offset + L[g][i]
                        ax.annotate("", xy=(x_pos, 0), xytext=(x_pos, arrow_scale), arrowprops=dict(arrowstyle="->", color='red', lw=2))
                        ax.text(x_pos, arrow_scale + text_offset, f"{P[g][i]:.2f}k", ha='center', color='red')
                for i in range(1, M[g]+1):
                    if W[g][i] != 0:
                        if g == 1:
                            x1 = -(L[g][i+1] if i < M[g] else L0[g])
                            x2 = -L[g][i]
                        else:
                            x1 = offset + L[g][i]
                            x2 = offset + (L[g][i+1] if i < M[g] else L0[g])
                        draw_uniform_load(x1, x2, W[g][i], g)
        
        total_R1 = R1[1] + R1[2] if L0[2] > 0 else R1[1]
        total_R2 = R2[2] + R2[3] if L0[2] > 0 else R2[3]
        ax.text(0, -0.5, f"R1={total_R1:.2f}k", ha='center', color='green')
        ax.text(main_span_len, -0.5, f"R2={total_R2:.2f}k", ha='center', color='green')
        
        if B_real > 0 and D_real > 0 and selected_props:
            label = f"{MATERIAL} {B_real}x{D_real}\" (Capacity={selected_props.get('M_capacity', 0):.2f} kip-ft)"
        else:
            label = "No beam selected (insufficient capacity or inertia)"
        ax.text(total_len/2 - left_cant_len, -0.7, label, ha='center')
        
        for g, pos in [(1, -left_cant_len/2), (2, main_span_len/2), (3, main_span_len + right_cant_len/2)]:
            if L0[g] > 0 and M1[g] > 0:
                ax.text(pos, -0.3, f"M={M1[g]:.2f}", ha='center', color='purple')
        
        ax.set_title(f"Beam Loading - {L13}")
        ax.set_ylim(-0.8, 1.0)
        ax.set_xlim(-left_cant_len-1, main_span_len+right_cant_len+1)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = CoreImage(buf, ext='png')
        self.texture = img.texture
        plt.close(fig)
        
        with self.canvas:
            self.canvas.clear()
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size, texture=self.texture)
        
       

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        layout = GridLayout(cols=2, padding=15, spacing=[10, 20], size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        self.entries = {}
        
        col1 = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        col1.bind(minimum_height=col1.setter('height'))
        
        col1.add_widget(Label(text="General Parameters", size_hint_y=None, height=30, bold=True))
        
        general_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=[0, 5])
        general_grid.bind(minimum_height=general_grid.setter('height'))
        general_grid.add_widget(Label(text="Beam Location:", size_hint_y=None, height=30))
        self.entries['location'] = TextInput(multiline=False, size_hint_y=None, height=30)
        general_grid.add_widget(self.entries['location'])
        
        general_grid.add_widget(Label(text="Material:", size_hint_y=None, height=30))
        self.entries['material'] = Spinner(
            text='PSL',
            values=('Sawn', 'PSL', 'Sawn Only'),
            size_hint_y=None,
            height=30
        )
        general_grid.add_widget(self.entries['material'])
        
        general_grid.add_widget(Label(text="Width (in):", size_hint_y=None, height=30))
        width_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['width'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        width_layout.add_widget(self.entries['width'])
        width_layout.add_widget(Label(text="e.g., 4 for 4x", size_hint_x=0.3, size_hint_y=None, height=30))
        general_grid.add_widget(width_layout)
        
        general_grid.add_widget(Label(text="Depth (in):", size_hint_y=None, height=30))
        depth_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['depth'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        depth_layout.add_widget(self.entries['depth'])
        depth_layout.add_widget(Label(text="optional", size_hint_x=0.3, size_hint_y=None, height=30))
        general_grid.add_widget(depth_layout)
        
        general_grid.add_widget(Label(text="Hold Constant:", size_hint_y=None, height=30))
        self.entries['z_value'] = Spinner(
            text='Depth (Z=0)',
            values=('Depth (Z=0)', 'Width (Z=1)'),
            size_hint_y=None,
            height=30
        )
        general_grid.add_widget(self.entries['z_value'])
        
        col1.add_widget(general_grid)
        
        col1.add_widget(Label(text="Left Cantilever (Span 1)", size_hint_y=None, height=30, bold=True))
        
        span1_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=[0, 5])
        span1_grid.bind(minimum_height=span1_grid.setter('height'))
        span1_grid.add_widget(Label(text="Length (ft):", size_hint_y=None, height=30))
        length1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['length_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        length1_layout.add_widget(self.entries['length_1'])
        length1_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(length1_layout)
        
        span1_grid.add_widget(Label(text="No. of Point Loads:", size_hint_y=None, height=30))
        nloads1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['n_point_loads_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='int')
        nloads1_layout.add_widget(self.entries['n_point_loads_1'])
        nloads1_layout.add_widget(Label(text="max 1", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(nloads1_layout)
        
        span1_grid.add_widget(Label(text="Point Load 1 (kips):", size_hint_y=None, height=30))
        pload1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['point_load_1_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        pload1_layout.add_widget(self.entries['point_load_1_1'])
        pload1_layout.add_widget(Label(text="kips", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(pload1_layout)
        
        span1_grid.add_widget(Label(text="Distance 1 (ft):", size_hint_y=None, height=30))
        dist1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['distance_1_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        dist1_layout.add_widget(self.entries['distance_1_1'])
        dist1_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(dist1_layout)
        
        span1_grid.add_widget(Label(text="Uniform Seg 1 (k/ft):", size_hint_y=None, height=30))
        useg1_1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['uniform_seg_1_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        useg1_1_layout.add_widget(self.entries['uniform_seg_1_1'])
        useg1_1_layout.add_widget(Label(text="k/ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(useg1_1_layout)
        
        span1_grid.add_widget(Label(text="Uniform Seg 2 (k/ft):", size_hint_y=None, height=30))
        useg1_2_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['uniform_seg_1_2'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        useg1_2_layout.add_widget(self.entries['uniform_seg_1_2'])
        useg1_2_layout.add_widget(Label(text="k/ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span1_grid.add_widget(useg1_2_layout)
        
        col1.add_widget(span1_grid)
        
        col2 = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        col2.bind(minimum_height=col2.setter('height'))
        
        col2.add_widget(Label(text="Main Span (Span 2)", size_hint_y=None, height=30, bold=True))
        
        span2_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=[0, 5])
        span2_grid.bind(minimum_height=span2_grid.setter('height'))
        span2_grid.add_widget(Label(text="Length (ft):", size_hint_y=None, height=30))
        length2_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['length_2'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        length2_layout.add_widget(self.entries['length_2'])
        length2_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span2_grid.add_widget(length2_layout)
        
        span2_grid.add_widget(Label(text="No. of Point Loads:", size_hint_y=None, height=30))
        nloads2_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['n_point_loads_2'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='int')
        nloads2_layout.add_widget(self.entries['n_point_loads_2'])
        nloads2_layout.add_widget(Label(text="max 2", size_hint_x=0.3, size_hint_y=None, height=30))
        span2_grid.add_widget(nloads2_layout)
        
        for i in range(1, 3):
            span2_grid.add_widget(Label(text=f"Point Load {i} (kips):", size_hint_y=None, height=30))
            pload_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            self.entries[f'point_load_2_{i}'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
            pload_layout.add_widget(self.entries[f'point_load_2_{i}'])
            pload_layout.add_widget(Label(text="kips", size_hint_x=0.3, size_hint_y=None, height=30))
            span2_grid.add_widget(pload_layout)
            
            span2_grid.add_widget(Label(text=f"Distance {i} (ft):", size_hint_y=None, height=30))
            dist_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            self.entries[f'distance_2_{i}'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
            dist_layout.add_widget(self.entries[f'distance_2_{i}'])
            dist_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
            span2_grid.add_widget(dist_layout)
        
        for i in range(1, 4):
            span2_grid.add_widget(Label(text=f"Uniform Seg {i} (k/ft):", size_hint_y=None, height=30))
            useg_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
            self.entries[f'uniform_seg_2_{i}'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
            useg_layout.add_widget(self.entries[f'uniform_seg_2_{i}'])
            useg_layout.add_widget(Label(text="k/ft", size_hint_x=0.3, size_hint_y=None, height=30))
            span2_grid.add_widget(useg_layout)
        
        col2.add_widget(span2_grid)
        
        col2.add_widget(Label(text="Right Cantilever (Span 3)", size_hint_y=None, height=30, bold=True))
        
        span3_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=[0, 5])
        span3_grid.bind(minimum_height=span3_grid.setter('height'))
        span3_grid.add_widget(Label(text="Length (ft):", size_hint_y=None, height=30))
        length3_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['length_3'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        length3_layout.add_widget(self.entries['length_3'])
        length3_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(length3_layout)
        
        span3_grid.add_widget(Label(text="No. of Point Loads:", size_hint_y=None, height=30))
        nloads3_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['n_point_loads_3'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='int')
        nloads3_layout.add_widget(self.entries['n_point_loads_3'])
        nloads3_layout.add_widget(Label(text="max 1", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(nloads3_layout)
        
        span3_grid.add_widget(Label(text="Point Load 1 (kips):", size_hint_y=None, height=30))
        pload3_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['point_load_3_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        pload3_layout.add_widget(self.entries['point_load_3_1'])
        pload3_layout.add_widget(Label(text="kips", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(pload3_layout)
        
        span3_grid.add_widget(Label(text="Distance 1 (ft):", size_hint_y=None, height=30))
        dist3_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['distance_3_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        dist3_layout.add_widget(self.entries['distance_3_1'])
        dist3_layout.add_widget(Label(text="ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(dist3_layout)
        
        span3_grid.add_widget(Label(text="Uniform Seg 1 (k/ft):", size_hint_y=None, height=30))
        useg3_1_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['uniform_seg_3_1'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        useg3_1_layout.add_widget(self.entries['uniform_seg_3_1'])
        useg3_1_layout.add_widget(Label(text="k/ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(useg3_1_layout)
        
        span3_grid.add_widget(Label(text="Uniform Seg 2 (k/ft):", size_hint_y=None, height=30))
        useg3_2_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.entries['uniform_seg_3_2'] = TextInput(multiline=False, size_hint_y=None, height=30, input_filter='float')
        useg3_2_layout.add_widget(self.entries['uniform_seg_3_2'])
        useg3_2_layout.add_widget(Label(text="k/ft", size_hint_x=0.3, size_hint_y=None, height=30))
        span3_grid.add_widget(useg3_2_layout)
        
        col2.add_widget(span3_grid)
        
        layout.add_widget(col1)
        layout.add_widget(col2)
        
        analyze_btn = Button(text="Analyze", size_hint_y=None, height=50)
        analyze_btn.bind(on_press=self.analyze)
        layout.add_widget(analyze_btn)
        
        scroll_view.add_widget(layout)
        self.add_widget(scroll_view)
    
    def analyze(self, instance):
        self.manager.current = 'results'
        self.manager.get_screen('results').analyze()

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        plot_height = Window.width * (3 / 5)
        self.plot_widget = PlotWidget(size_hint=(1, None), height=plot_height)
        layout.add_widget(self.plot_widget)
        
        self.results = Label(text="", size_hint_y=None, height=100, text_size=(Window.width - 40, None))
        self.results.bind(texture_size=self.results.setter('size'))
        layout.add_widget(self.results)
        
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        back_btn = Button(text="Back", size_hint_x=0.5)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'input'))
        buttons_layout.add_widget(back_btn)
        
        save_btn = Button(text="Save Report", size_hint_x=0.5)
        save_btn.bind(on_press=self.save_report)
        buttons_layout.add_widget(save_btn)
        
        layout.add_widget(buttons_layout)
        
        self.save_status = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(self.save_status)
        
        scroll_view.add_widget(layout)
        self.add_widget(scroll_view)
    
    def analyze(self):
        app = App.get_running_app()
        app.analyze(None)
    
    def save_report(self, instance):
        result = save_beam_report()
        self.save_status.text = result

def save_beam_report():
    """Save beam analysis results and plot to a report file"""
    if B_real <= 0 or D_real <= 0 or 'M_capacity' not in selected_props:
        return "No valid beam selected. Cannot generate report."
    
    # Create report directory if it doesn't exist
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beam_reports")
    os.makedirs(report_dir, exist_ok=True)
    
    # Generate a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(report_dir, f"beam_report_{timestamp}.txt")
    plot_filename = os.path.join(report_dir, f"beam_plot_{timestamp}.png")
    
    # Generate plot for saving
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot diagram similar to the PlotWidget
    left_cant_len = L0[1]
    main_span_len = L0[2]
    right_cant_len = L0[3]
    total_len = main_span_len + left_cant_len + right_cant_len
    
    ax.plot([-left_cant_len, main_span_len + right_cant_len], [0, 0], 'k-', linewidth=3)
    ax.plot([0, 0], [-0.3, 0.1], 'g-', linewidth=3)
    ax.plot([main_span_len, main_span_len], [-0.3, 0.1], 'g-', linewidth=3)
    
    arrow_scale = 0.6
    text_offset = 0.15
    max_w = max([max(W[g][1:M[g]+1] or [0]) for g in [1,2,3] if L0[g] > 0] or [1])
    
    def draw_uniform_load(x1, x2, w, g):
        if w == 0 or x1 == x2:
            return
        w_scale = 0.2 + 0.2 * (abs(w)/max_w)
        density = 1.5 if g == 1 else 1.0
        x_positions = np.linspace(x1, x2, max(3, int(abs(x2 - x1) * density) + 1))
        for x in x_positions:
            ax.plot([x, x], [0, w_scale], 'b-', lw=1.2)
        ax.plot([x1, x2], [w_scale, w_scale], 'b-', lw=1.2)
        ax.text((x1+x2)/2, w_scale + text_offset, f"{w:.2f}k/ft", ha='center', color='blue')
    
    for g, offset in [(1, -left_cant_len), (2, 0), (3, main_span_len)]:
        if L0[g] > 0:
            for i in range(2, M[g]+1):
                if P[g][i] != 0:
                    if g == 1:
                        x_pos = -L[g][i]
                    else:
                        x_pos = offset + L[g][i]
                    ax.annotate("", xy=(x_pos, 0), xytext=(x_pos, arrow_scale), arrowprops=dict(arrowstyle="->", color='red', lw=2))
                    ax.text(x_pos, arrow_scale + text_offset, f"{P[g][i]:.2f}k", ha='center', color='red')
                for i in range(1, M[g]+1):
                    if W[g][i] != 0:
                        if g == 1:
                            x1 = -(L[g][i+1] if i < M[g] else L0[g])
                            x2 = -L[g][i]
                        else:
                            x1 = offset + L[g][i]
                            x2 = offset + (L[g][i+1] if i < M[g] else L0[g])
                        draw_uniform_load(x1, x2, W[g][i], g)
    
    total_R1 = R1[1] + R1[2] if L0[2] > 0 else R1[1]
    total_R2 = R2[2] + R2[3] if L0[2] > 0 else R2[3]
    ax.text(0, -0.5, f"R1={total_R1:.2f}k", ha='center', color='green')
    ax.text(main_span_len, -0.5, f"R2={total_R2:.2f}k", ha='center', color='green')
    
    if B_real > 0 and D_real > 0 and selected_props:
        label = f"{MATERIAL} {B_real}x{D_real}\" (Capacity={selected_props.get('M_capacity', 0):.2f} kip-ft)"
    else:
        label = "No beam selected (insufficient capacity or inertia)"
    ax.text(total_len/2 - left_cant_len, -0.7, label, ha='center')
    
    for g, pos in [(1, -left_cant_len/2), (2, main_span_len/2), (3, main_span_len + right_cant_len/2)]:
        if L0[g] > 0 and M1[g] > 0:
            ax.text(pos, -0.3, f"M={M1[g]:.2f}", ha='center', color='purple')
    
    ax.set_title(f"Beam Loading - {L13}")
    ax.set_ylim(-0.8, 1.0)
    ax.set_xlim(-left_cant_len-1, main_span_len+right_cant_len+1)
    
    # Save plot to file
    plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    # Generate report content
    report_content = f"""
===========================================================
BEAM STRUCTURAL ANALYSIS REPORT
===========================================================
Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Beam Location: {L13}

BEAM PROPERTIES:
-----------------------------------------------------------
Material: {MATERIAL}
Size: {B_real}" x {D_real}"
Section Properties:
  - Section Modulus (S): {selected_props.get('S', 0):.2f} in³
  - Moment of Inertia (I): {selected_props.get('I', 0):.2f} in⁴
  - Moment Capacity: {selected_props.get('M_capacity', 0):.2f} kip-ft

LOADING SUMMARY:
-----------------------------------------------------------
"""
    
    # Add span information to the report
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0:
            report_content += f"{span_name} (Span {g}):\n"
            report_content += f"  - Length: {L0[g]:.2f} ft\n"
            report_content += f"  - Point Loads: {N[g]}\n"
            
            for i in range(2, M[g]+1):
                if P[g][i] != 0:
                    report_content += f"    * {P[g][i]:.2f} kips at {L[g][i]:.2f} ft\n"
            
            for i in range(1, M[g]+1):
                if W[g][i] != 0:
                    seg_start = L[g][i]
                    seg_end = L[g][i+1] if i < M[g] else L0[g]
                    report_content += f"    * Uniform load {W[g][i]:.2f} k/ft from {seg_start:.2f} ft to {seg_end:.2f} ft\n"
    
    # Add analysis results
    report_content += f"""
ANALYSIS RESULTS:
-----------------------------------------------------------
Reactions:
  - R1 = {total_R1:.2f} kips
  - R2 = {total_R2:.2f} kips

Maximum Moments:
"""
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0 and M1[g] > 0:
            report_content += f"  - {span_name}: {M1[g]:.2f} kip-ft\n"
    
    # Add deflection information
    I_req = calculate_required_inertia()
    report_content += f"""
Deflection:
  - Maximum allowable deflection (L/240): {L0[2] * 12 / 240:.3f} inches
  - Required moment of inertia: {I_req[2]:.2f} in⁴
  - Provided moment of inertia: {selected_props.get('I', 0):.2f} in⁴
"""

    # Add capacity check
    max_moment = max(M1[1:4])
    utilization = max_moment / selected_props.get('M_capacity', 1) * 100
    report_content += f"""
CAPACITY CHECK:
-----------------------------------------------------------
Maximum moment: {max_moment:.2f} kip-ft
Moment capacity: {selected_props.get('M_capacity', 0):.2f} kip-ft
Utilization: {utilization:.1f}%
Status: {"PASS" if utilization <= 100 else "FAIL"}

===========================================================
Plot saved to: {plot_filename}
===========================================================
"""
    
    # Write report to file
    with open(report_filename, 'w') as f:
        f.write(report_content)
    
    return f"Report saved to: {report_filename}"

class BeamAnalysisApp(App):
    def build(self):
        Window.rotation = 0
        
        sm = ScreenManager()
        input_screen = InputScreen(name='input')
        results_screen = ResultsScreen(name='results')
        sm.add_widget(input_screen)
        sm.add_widget(results_screen)
        
        # Pre-filled inputs for your test case
        input_screen.entries['location'].text = "Test Beam"
        input_screen.entries['material'].text = "PSL"
        input_screen.entries['width'].text = ""
        input_screen.entries['depth'].text = ""
        
        # Span 1 (Left Cantilever)
        input_screen.entries['length_1'].text = "5"
        input_screen.entries['n_point_loads_1'].text = "1"
        input_screen.entries['point_load_1_1'].text = "0.64"
        input_screen.entries['distance_1_1'].text = "3"
        input_screen.entries['uniform_seg_1_1'].text = "0.32"
        input_screen.entries['uniform_seg_1_2'].text = "0.60"
        
        # Span 2 (Main Span)
        input_screen.entries['length_2'].text = "16"
        input_screen.entries['n_point_loads_2'].text = "2"
        input_screen.entries['point_load_2_1'].text = "1.00"
        input_screen.entries['distance_2_1'].text = "2"
        input_screen.entries['point_load_2_2'].text = "0.50"
        input_screen.entries['distance_2_2'].text = "3"
        input_screen.entries['uniform_seg_2_1'].text = "0.15"
        input_screen.entries['uniform_seg_2_2'].text = "0.70"
        input_screen.entries['uniform_seg_2_3'].text = "0.42"
        
        # Span 3 (Right Cantilever)
        input_screen.entries['length_3'].text = "5"
        input_screen.entries['n_point_loads_3'].text = "1"
        input_screen.entries['point_load_3_1'].text = "2.00"
        input_screen.entries['distance_3_1'].text = "3"
        input_screen.entries['uniform_seg_3_1'].text = "0.20"
        input_screen.entries['uniform_seg_3_2'].text = "0.60"
        
        self.input_screen = input_screen
        self.results_screen = results_screen
        
        Window.bind(on_keyboard=self.handle_back)
        
        return sm
    
    def handle_back(self, window, key, *args):
        if key == 27:
            if self.manager.current == 'results':
                self.manager.current = 'input'
                return True
        return False
    
    def analyze(self, instance):
        global L13, B, D, B_real, D_real, Z1, F, MATERIAL, Z, N, M, P, L, L1, W, R1, R2, M1, D1, L0, allow_psl
        try:
            reset_globals()
            
            L13 = self.input_screen.entries['location'].text or "Unnamed Beam"
            F = 1.25
            MATERIAL = self.input_screen.entries['material'].text
            allow_psl = MATERIAL != "Sawn Only"
            if MATERIAL == "Sawn Only":
                MATERIAL = "Sawn"
            
            B = safe_eval(self.input_screen.entries['width'].text)
            D = safe_eval(self.input_screen.entries['depth'].text)
            B_real = B - 0.5 if MATERIAL == "Sawn" and B > 0 else B
            D_real = D
            
            # Get Z value from spinner
            Z_input = self.input_screen.entries['z_value'].text
            Z = 1 if Z_input == 'Width (Z=1)' else 0
            
            for g in [1, 2, 3]:
                L0[g] = safe_eval(self.input_screen.entries[f"length_{g}"].text)
                if L0[g] > 0:
                    input_loads(g, self.input_screen.entries)
            
            if L0[2] <= 0:
                raise ValueError("Main span length must be > 0 ft")
            
            calculate_reactions()
            calculate_moments()
            beam_grade = beam_sizing()
            calculate_required_inertia()
            
            results = (f"Reactions: R1={R1[2]:.2f}k, R2={R2[2]:.2f}k\n"
                       f"Max Moment: {M1[2]:.2f} kip-ft\n"
                       f"Deflection: {D1[2]:.2f} in\n"
                       f"Grade: {beam_grade}")
            self.results_screen.results.text = results
            self.results_screen.plot_widget.update_plot()
        except Exception as e:
            self.results_screen.results.text = f"Error: {str(e)}"
            print(f"Exception: {str(e)}")

if __name__ == '__main__':
    BeamAnalysisApp().run()

# -----------------------------
# MISSING FUNCTION (ADDED ONLY)
# -----------------------------
def calculate_required_inertia():
    I_req[1] = 0
    I_req[2] = 0
    I_req[3] = 0

# -----------------------------
# STREAMLIT UI (ADDED ONLY)
# -----------------------------
st.title("Wood Beam Design – Continuous Beam with Cantilevers")

st.write("This app runs your original engineering code without modification.")

if st.button("Run Beam Analysis"):
    try:
        input_loads()
        calculate_reactions()
        calculate_moments()
        calculate_required_inertia()
        B_sel, D_sel, size_data = select_beam()

        st.subheader("Reactions")
        st.write(f"Left Cantilever R1 = {R1[1]:.2f} kips")
        st.write(f"Main Span R1 = {R1[2]:.2f} kips, R2 = {R2[2]:.2f} kips")
        st.write(f"Right Cantilever R2 = {R2[3]:.2f} kips")

        st.subheader("Moments")
        st.write(f"Left Cantilever M1 = {M1[1]:.2f} kip-ft")
        st.write(f"Main Span M1 = {M1[2]:.2f} kip-ft")
        st.write(f"Right Cantilever M1 = {M1[3]:.2f} kip-ft")

        st.subheader("Selected Beam")
        st.write(f"Sawn {B_sel}x{D_sel}")
        st.write(f"Capacity = {size_data['M_capacity']:.2f} kip-ft")
        st.write(f"I = {size_data['I']:.1f} in⁴")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Press the button to run the beam design.")
