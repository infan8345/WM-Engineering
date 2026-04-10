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
    allowable_deflection = [0] * 4
    
    for i in range(1, 4):
        allowable_deflection[i] = L0[i] * ft_to_in / 240 if L0[i] > 0 else 0
    
    for g in [1, 2, 3]:
        if L0[g] > 0:
            span_length = L0[g] * ft_to_in
            delta_sum = 0
            
            if g == 2:  # Main span
                # For simplicity, approximate as uniformly loaded beam
                total_load = sum(P[g][i] for i in range(2, M[g]+1)) * kip_to_lb
                for i in range(1, M[g]+1):
                    total_load += W[g][i] * L1[g][i] * kip_to_lb
                
                w_eq = total_load / span_length  # Convert to uniform load (lb/in)
                
                # Calculate deflection for simply supported beam with uniform load
                delta_sum = (5 * w_eq * span_length**4) / (384 * E)
                
                # Calculate required inertia based on allowable deflection
                if allowable_deflection[g] > 0:
                    I_req[g] = delta_sum / (allowable_deflection[g])
                
                # Calculate actual deflection
                if selected_props and 'I' in selected_props and selected_props['I'] > 0:
                    actual_I = selected_props['I']
                    D1[g] = (delta_sum / actual_I)
                else:
                    D1[g] = 0
                
            else:  # Cantilever spans
                # Point loads
                for i in range(2, M[g]+1):
                    P_i = P[g][i] * kip_to_lb
                    a = L[g][i] * ft_to_in  # Distance from support
                    delta_sum += (P_i * a**3) / 3
                
                # Uniform loads
                for i in range(1, M[g]+1):
                    w = W[g][i] * kip_to_lb / ft_to_in  # Convert to lb/in
                    seg_len = L1[g][i] * ft_to_in
                    start_pos = L[g][i] * ft_to_in
                    end_pos = start_pos + seg_len
                    
                    # For cantilever with uniform load
                    delta_contrib = (w * seg_len**4) / 8
                    delta_sum += delta_contrib
                
                # Calculate required inertia based on allowable deflection
                if allowable_deflection[g] > 0:
                    I_req[g] = delta_sum / (E * allowable_deflection[g])
                
                # Calculate actual deflection
                if selected_props and 'I' in selected_props and selected_props['I'] > 0:
                    actual_I = selected_props['I']
                    D1[g] = (delta_sum / (E * actual_I))
                else:
                    D1[g] = 0
    
    print(f"DEBUG: Required I values: Span 1 = {I_req[1]:.2f}, Span 2 = {I_req[2]:.2f}, Span 3 = {I_req[3]:.2f}")
    print(f"DEBUG: Allowable deflection: Span 1 = {allowable_deflection[1]:.4f}, Span 2 = {allowable_deflection[2]:.4f}, Span 3 = {allowable_deflection[3]:.4f}")
    print(f"DEBUG: Delta sum values: Span 1 = {delta_sum if g == 1 else 'N/A'}, Span 2 = {delta_sum if g == 2 else 'N/A'}, Span 3 = {delta_sum if g == 3 else 'N/A'}")
    
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

def generate_detailed_text_report():
    """Generate a detailed step-by-step text report including zero shear calculations"""
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beam_reports")
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(report_dir, f"detailed_text_report_{timestamp}.txt")

    # Prepare the report content
    report_content = f"""
{"="*80}
DETAILED BEAM ANALYSIS
{"="*80}
Beam Location: {L13}
Span Length: {L0[2]} ft

Point Loads:
"""
    for i in range(2, M[2]+1):
        if P[2][i] != 0:
            report_content += f"  P{i-1} = {P[2][i]} kips at x = {L[2][i]} ft\n"

    report_content += "\nUniform Loads:\n"
    for i in range(1, M[2]+1):
        if W[2][i] != 0:
            seg_start = L[2][i]
            seg_end = L[2][i+1] if i < M[2] else L0[2]
            report_content += f"  w{i} = {W[2][i]} k/ft from x = {seg_start} ft to x = {seg_end} ft\n"

    report_content += f"""
{"-"*80}
1. CALCULATING REACTIONS:
   Span Length = {L0[2]} ft

   Step 1.1: Calculate moment equilibrium about left support (x=0) to find R2
   Point load contributions to moment:
"""
    # Calculate moment contributions for R2
    sum_moments = 0
    for i in range(2, M[2]+1):
        if P[2][i] != 0:
            moment = P[2][i] * L[2][i]
            sum_moments += moment
            report_content += f"     P{i-1} = {P[2][i]} kips at x = {L[2][i]} ft -> M = {P[2][i]} × {L[2][i]} = {moment:.2f} kip-ft\n"
    
    report_content += "\n   Uniform load contributions to moment:\n"
    for i in range(1, M[2]+1):
        if W[2][i] != 0:
            seg_start = L[2][i]
            seg_end = L[2][i+1] if i < M[2] else L0[2]
            length = seg_end - seg_start
            centroid = seg_start + length/2
            load = W[2][i] * length
            moment = load * centroid
            sum_moments += moment
            report_content += f"     w{i} = {W[2][i]} k/ft from x = {seg_start} to {seg_end} ft\n"
            report_content += f"       Length = {length} ft, Centroid at x = {centroid} ft\n"
            report_content += f"       Total load = {W[2][i]} × {length} = {load:.2f} kips\n"
            report_content += f"       Moment = {load:.2f} × {centroid} = {moment:.2f} kip-ft\n"
    
    # Calculate R2
    R2_calc = sum_moments / L0[2] if L0[2] > 0 else 0
    report_content += f"""
   Sum of moments = {sum_moments:.2f} kip-ft
   R2 = Sum of moments / Span Length = {sum_moments:.2f} / {L0[2]} = {R2_calc:.2f} kips
   
   Step 1.2: Calculate vertical force equilibrium to find R1
   Point load contributions:
"""
    # Calculate sum of loads for R1
    sum_loads = 0
    for i in range(2, M[2]+1):
        if P[2][i] != 0:
            sum_loads += P[2][i]
            report_content += f"     P{i-1} = {P[2][i]} kips\n"
    
    report_content += "\n   Uniform load contributions:\n"
    for i in range(1, M[2]+1):
        if W[2][i] != 0:
            seg_start = L[2][i]
            seg_end = L[2][i+1] if i < M[2] else L0[2]
            length = seg_end - seg_start
            load = W[2][i] * length
            sum_loads += load
            report_content += f"     w{i} = {W[2][i]} k/ft over {length} ft = {load:.2f} kips\n"
    
    # Calculate R1
    R1_calc = sum_loads - R2_calc
    report_content += f"""
   Sum of loads = {sum_loads:.2f} kips
   R1 = Sum of loads - R2 = {sum_loads:.2f} - {R2_calc:.2f} = {R1_calc:.2f} kips

2. CALCULATING SHEAR DIAGRAM:
   
   Step 2.1: Calculate shear at key points
   Starting shear at x = 0: V(0) = R1 = {R1_calc:.2f} kips
"""

    # Calculate shear at key points
    x_points = [0, L0[2]]  # Add supports
    for i in range(2, M[2]+1):
        if P[2][i] != 0:
            x_points.append(L[2][i])  # Add point load positions
    
    # Add uniform load boundaries
    for i in range(1, M[2]+1):
        if W[2][i] != 0:
            seg_start = L[2][i]
            seg_end = L[2][i+1] if i < M[2] else L0[2]
            if seg_start > 0:
                x_points.append(seg_start)
            if seg_end < L0[2]:
                x_points.append(seg_end)
    
    x_points = sorted(list(set(x_points)))  # Remove duplicates and sort
    
    # Create a finer mesh for zero shear detection
    x_fine = np.linspace(0, L0[2], 200)
    shear_values = []
    
    # Calculate shear at each x-value
    for x in x_points:
        # Start with reaction at left support
        shear = R1_calc
        description = []
        
        # Subtract point loads to the left of x
        for i in range(2, M[2]+1):
            if P[2][i] != 0 and L[2][i] < x:
                shear -= P[2][i]
                description.append(f"   At x = {x:.2f} ft: Subtract point load P{i-1} = {P[2][i]:.2f} kips at x = {L[2][i]:.2f} ft -> V = {shear:.2f} kips")
        
        # Subtract uniform loads to the left of x
        for i in range(1, M[2]+1):
            if W[2][i] != 0:
                seg_start = L[2][i]
                seg_end = L[2][i+1] if i < M[2] else L0[2]
                
                if seg_start < x:
                    # If x is within the uniform load region
                    if x <= seg_end:
                        uniform_load_effect = W[2][i] * (x - seg_start)
                        shear -= uniform_load_effect
                        description.append(f"   At x = {x:.2f} ft: Subtract uniform load w{i} = {W[2][i]:.2f} k/ft from x = {seg_start:.2f} to {x:.2f} ft")
                        description.append(f"     Effect = {W[2][i]:.2f} × ({x:.2f} - {seg_start:.2f}) = {uniform_load_effect:.2f} kips -> V = {shear:.2f} kips")
                    
                    # If x is beyond the uniform load region
                    else:
                        uniform_load_effect = W[2][i] * (seg_end - seg_start)
                        shear -= uniform_load_effect
                        description.append(f"   At x = {x:.2f} ft: Subtract uniform load w{i} = {W[2][i]:.2f} k/ft from x = {seg_start:.2f} to {seg_end:.2f} ft")
                        description.append(f"     Effect = {W[2][i]:.2f} × ({seg_end:.2f} - {seg_start:.2f}) = {uniform_load_effect:.2f} kips -> V = {shear:.2f} kips")
        
        shear_values.append((x, shear, description))
    
    # Add shear descriptions to report
    for x, shear, description in shear_values:
        for line in description:
            report_content += line + "\n"
    
    # Find zero-shear points
    zero_shear_points = []
    
    # Calculate shear at fine mesh points
    shear_fine = np.zeros_like(x_fine)
    for i, x in enumerate(x_fine):
        shear = R1_calc
        
        # Subtract point loads to the left of x
        for j in range(2, M[2]+1):
            if P[2][j] != 0 and L[2][j] < x:
                shear -= P[2][j]
        
        # Subtract uniform loads
        for j in range(1, M[2]+1):
            if W[2][j] != 0:
                seg_start = L[2][j]
                seg_end = L[2][j+1] if j < M[2] else L0[2]
                
                if seg_start < x:
                    if x <= seg_end:
                        shear -= W[2][j] * (x - seg_start)
                    else:
                        shear -= W[2][j] * (seg_end - seg_start)
        
        shear_fine[i] = shear
    
    # Find zero crossing
    report_content += "\n   Step 2.2: Find points of zero shear (where shear diagram crosses x-axis)\n"
    
    for i in range(len(x_fine) - 1):
        if shear_fine[i] * shear_fine[i+1] <= 0 and abs(shear_fine[i]) + abs(shear_fine[i+1]) > 0:
            x1, x2 = x_fine[i], x_fine[i+1]
            v1, v2 = shear_fine[i], shear_fine[i+1]
            
            # Linear interpolation to find the exact zero crossing
            if v1 == 0 and v2 == 0:
                zero_x = (x1 + x2) / 2
            else:
                zero_x = x1 - v1 * (x2 - x1) / (v2 - v1) if (v2 - v1) != 0 else x1
            
            zero_shear_points.append(zero_x)
            report_content += f"   Zero shear at x = {zero_x:.3f} ft (between x = {x1:.3f} and x = {x2:.3f} ft)\n"
    
    if not zero_shear_points:
        report_content += "   No zero-shear points found in the span\n"
    
    # Calculate moment at key points including zero shear points
    report_content += f"""
3. CALCULATING MOMENT DIAGRAM:

   Step 3.1: Calculate moment at key points
"""
    
    # Add zero shear points to evaluation points
    x_moment = sorted(list(set(x_points + zero_shear_points)))
    moment_values = []
    
    for x in x_moment:
        # Start with reaction at left support
        moment = R1_calc * x
        report_content += f"\n   At x = {x:.3f} ft:\n"
        report_content += f"     R1 contribution = {R1_calc:.2f} × {x:.3f} = {R1_calc * x:.3f} kip-ft\n"
        
        # Subtract point loads to the left of x
        for i in range(2, M[2]+1):
            if P[2][i] != 0 and L[2][i] < x:
                point_moment = P[2][i] * (x - L[2][i])
                moment -= point_moment
                report_content += f"     P{i-1} = {P[2][i]:.2f} kips at x = {L[2][i]:.3f} ft, effect = -{P[2][i]:.2f} × ({x:.3f} - {L[2][i]:.3f}) = -{point_moment:.3f} kip-ft\n"
        
        # Subtract uniform loads
        for i in range(1, M[2]+1):
            if W[2][i] != 0:
                seg_start = L[2][i]
                seg_end = L[2][i+1] if i < M[2] else L0[2]
                
                if seg_start < x:
                    # If x is within the uniform load region
                    if x <= seg_end:
                        # The uniform load acts from start to x
                        length = x - seg_start
                        centroid = seg_start + length/2
                        load = W[2][i] * length
                        uniform_moment = load * (x - centroid)
                        moment -= uniform_moment
                        report_content += f"     w{i} = {W[2][i]:.2f} k/ft from x = {seg_start:.3f} to {x:.3f} ft\n"
                        report_content += f"       Length = {length:.3f} ft, Centroid at x = {centroid:.3f} ft\n"
                        report_content += f"       Total load = {W[2][i]:.2f} × {length:.3f} = {load:.3f} kips\n"
                        report_content += f"       Effect = -{load:.3f} × ({x:.3f} - {centroid:.3f}) = -{uniform_moment:.3f} kip-ft\n"
                    
                    # If x is beyond the uniform load region
                    else:
                        # The uniform load acts from start to end
                        length = seg_end - seg_start
                        centroid = seg_start + length/2
                        load = W[2][i] * length
                        uniform_moment = load * (x - centroid)
                        moment -= uniform_moment
                        report_content += f"     w{i} = {W[2][i]:.2f} k/ft from x = {seg_start:.3f} to {seg_end:.3f} ft\n"
                        report_content += f"       Length = {length:.3f} ft, Centroid at x = {centroid:.3f} ft\n"
                        report_content += f"       Total load = {W[2][i]:.2f} × {length:.3f} = {load:.3f} kips\n"
                        report_content += f"       Effect = -{load:.3f} × ({x:.3f} - {centroid:.3f}) = -{uniform_moment:.3f} kip-ft\n"
        
        report_content += f"     Total moment at x = {x:.3f} ft: M = {moment:.3f} kip-ft\n"
        moment_values.append((x, moment))
    
    # Find maximum moment
    max_moment = max(moment_values, key=lambda x: x[1])
    max_moment_position = max_moment[0]
    max_moment_value = max_moment[1]
    
    # Check if maximum moment occurs at a zero-shear point
    at_zero_shear = False
    closest_zero_shear = None
    closest_distance = float('inf')
    
    for zero_x in zero_shear_points:
        if abs(zero_x - max_moment_position) < 0.001:  # Threshold for considering "at zero shear"
            at_zero_shear = True
            break
        # Find the closest zero-shear point
        if abs(zero_x - max_moment_position) < closest_distance:
            closest_distance = abs(zero_x - max_moment_position)
            closest_zero_shear = zero_x
    
    report_content += f"""
   Step 3.2: Locate maximum moment
   Maximum moment = {max_moment_value:.3f} kip-ft at x = {max_moment_position:.3f} ft
"""
    
    if at_zero_shear:
        report_content += "   Maximum moment occurs at a zero-shear point, which confirms the theoretical expectation.\n"
    elif zero_shear_points:
        report_content += f"   Note: Closest zero-shear point is at x = {closest_zero_shear:.3f} ft, {closest_distance:.3f} ft away.\n"
        report_content += "   Small difference may be due to calculation precision or load distribution.\n"
    else:
        report_content += "   No zero-shear points found within the span.\n"
    
    # Add deflection information
    required_inertia = calculate_required_inertia()
    report_content += f"""
4. DEFLECTION ANALYSIS:
   Required Moment of Inertia (for L/240):
   - Main Span: {required_inertia[2]:.2f} in⁴
   
   Provided Moment of Inertia: {selected_props.get('I', 0):.2f} in⁴
   
   Maximum Deflection: {max(D1[1:4]):.3f} inches
   Allowable Deflection (L/240): {L0[2] * ft_to_in / 240:.3f} inches

{"="*80}
SUMMARY OF RESULTS:
{"="*80}
Beam Location: {L13}
Beam Size: {MATERIAL} {B_real}x{D_real}
Moment Capacity: {selected_props.get('M_capacity', 0):.2f} kip-ft

Reactions: R1 = {R1_calc:.2f} kips, R2 = {R2_calc:.2f} kips
"""
    
    if zero_shear_points:
        report_content += "\nZero-Shear Points:\n"
        for i, zero_x in enumerate(zero_shear_points):
            report_content += f"  Point {i+1}: x = {zero_x:.3f} ft\n"
    else:
        report_content += "\nNo zero-shear points within the span\n"
    
    report_content += f"\nMaximum Moment: {max_moment_value:.3f} kip-ft at x = {max_moment_position:.3f} ft\n"
    
    # Add theoretical verification
    report_content += "\nTHEORETICAL VERIFICATION:\n"
    report_content += "Maximum moment occurs where shear changes sign (crosses zero).\n"
    
    if at_zero_shear:
        report_content += "This is confirmed by our calculations.\n"
    else:
        report_content += "Note: In this case, the maximum moment might not occur exactly at a zero-shear point due to:\n"
        report_content += "  - The beam may have non-continuous loading\n"
        report_content += "  - Maximum moment may occur at a point load or beam end\n"
        report_content += "  - Numerical approximation in calculations\n"
    
    # Add beam capacity check
    utilization = max_moment_value / selected_props.get('M_capacity', 1) * 100
    report_content += f"""
CAPACITY CHECK:
Maximum moment: {max_moment_value:.2f} kip-ft
Moment capacity: {selected_props.get('M_capacity', 0):.2f} kip-ft
Utilization: {utilization:.1f}%
Status: {"PASS" if utilization <= 100 else "FAIL"}

{"="*80}
"""
    
    # Write to file
    with open(report_filename, 'w', encoding='utf-8') as file:
        file.write(report_content)
    
    return report_filename


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
        
        back_btn = Button(text="Back", size_hint_x=0.2)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'input'))
        buttons_layout.add_widget(back_btn)
        
        detailed_btn = Button(text="Detailed Report", size_hint_x=0.3)
        detailed_btn.bind(on_press=self.generate_detailed_report)
        buttons_layout.add_widget(detailed_btn)
        
        latex_btn = Button(text="LaTeX Report", size_hint_x=0.3)
        latex_btn.bind(on_press=self.generate_latex_report)
        buttons_layout.add_widget(latex_btn)
        
        layout.add_widget(buttons_layout)
        
        self.save_status = Label(text="", size_hint_y=None, height=30)
        layout.add_widget(self.save_status)
        
        scroll_view.add_widget(layout)
        self.add_widget(scroll_view)
    
    def analyze(self):
        app = App.get_running_app()
        app.analyze(None)
    
    def save_report(self, instance):
        try:
            result = save_beam_report()
            self.save_status.text = str(result)  # Ensure result is a string
        except Exception as e:
            self.save_status.text = f"Error generating report: {str(e)}"
    
    def generate_detailed_report(self, instance):
        """Generate a detailed text report with zero shear calculations"""
        try:
            report_file = generate_detailed_text_report()
            self.save_status.text = f"Detailed report saved to:\n{report_file}"
        except Exception as e:
            self.save_status.text = f"Error generating report: {str(e)}"
    
    def generate_latex_report(self, instance):
        """Generate a LaTeX report with detailed analysis matching the text report"""
        try:
        # Generate the basic report and get filenames
           result = save_beam_report()
           latex_filename = None
        for line in result.split('\n'):
            if '.tex' in line:
                parts = line.split()
                for part in parts:
                    if part.endswith('.tex'):
                        latex_filename = part
                        break
            if latex_filename:
                break

        if not latex_filename:
            self.save_status.text = "Error: Could not find LaTeX file in report output"
            return

        # Read the existing LaTeX content
        try:
            with open(latex_filename, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as ex:
            self.save_status.text = f"Error reading LaTeX file {latex_filename}: {str(ex)}"
            return

        # Find insertion point
        insert_pos = content.rfind('\\end{document}')
        if insert_pos < 0:
            self.save_status.text = f"Error: Could not find \\end{{document}} in LaTeX file"
            return

        # Generate detailed analysis similar to the text report
        detailed_text = r"""
\section{Detailed Analysis}
This section provides a detailed step-by-step explanation of the beam analysis, including reaction calculations, shear force analysis, zero-shear points, moment calculations, and deflection analysis.

\subsection{Reaction Calculations}
The support reactions are determined using static equilibrium:
\begin{itemize}
    \item Sum of vertical forces: $\sum F_y = 0$
    \item Sum of moments about a point: $\sum M = 0$
\end{itemize}

For the main span (Span 2, length = """ + f"{L0[2]:.2f}" + r""" ft), we calculate the moment about the left support (x=0) to find $R_2$:

\begin{align*}
\sum M_{x=0} &= 0
\end{align*}

Point load contributions:
"""
        # Point load moment contributions
        sum_moments = 0
        for i in range(2, M[2]+1):
            if P[2][i] != 0:
                moment = P[2][i] * L[2][i]
                sum_moments += moment
                detailed_text += f"\\item $P_{{{i-1}}} = {P[2][i]:.2f}$ kips at $x = {L[2][i]:.2f}$ ft: $M = {P[2][i]:.2f} \\times {L[2][i]:.2f} = {moment:.2f}$ kip-ft\n"

        detailed_text += r"\end{itemize}" + "\n\nUniform load contributions:\n\\begin{itemize}\n"
        for i in range(1, M[2]+1):
            if W[2][i] != 0:
                seg_start = L[2][i]
                seg_end = L[2][i+1] if i < M[2] else L0[2]
                length = seg_end - seg_start
                centroid = seg_start + length/2
                load = W[2][i] * length
                moment = load * centroid
                sum_moments += moment
                detailed_text += f"\\item $w_{{{i}}} = {W[2][i]:.2f}$ k/ft from $x = {seg_start:.2f}$ to ${seg_end:.2f}$ ft:\n"
                detailed_text += f"\\begin{itemize}\n"
                detailed_text += f"\\item Length = {length:.2f} ft\n"
                detailed_text += f"\\item Centroid at $x = {centroid:.2f}$ ft\n"
                detailed_text += f"\\item Total load = ${W[2][i]:.2f} \\times {length:.2f} = {load:.2f}$ kips\n"
                detailed_text += f"\\item Moment = ${load:.2f} \\times {centroid:.2f} = {moment:.2f}$ kip-ft\n"
                detailed_text += r"\end{itemize}" + "\n"

        detailed_text += r"\end{itemize}" + "\n"
        R2_calc = sum_moments / L0[2] if L0[2] > 0 else 0
        R1_calc = (sum(P[2][i] for i in range(2, M[2]+1)) + sum(W[2][i] * L1[2][i] for i in range(1, M[2]+1))) - R2_calc

        detailed_text += f"Total moment about left support: ${sum_moments:.2f}$ kip-ft\n\n"
        detailed_text += f"Reaction at right support: $R_2 = \\frac{{{sum_moments:.2f}}}{{{L0[2]:.2f}}} = {R2_calc:.2f}$ kips\n\n"
        detailed_text += f"Reaction at left support: $R_1 = \\left("
        for i in range(2, M[2]+1):
            if P[2][i] != 0:
                detailed_text += f"{P[2][i]:.2f} + "
        for i in range(1, M[2]+1):
            if W[2][i] != 0:
                detailed_text += f"({W[2][i]:.2f} \\times {L1[2][i]:.2f}) + "
        detailed_text = detailed_text.rstrip(' + ') + f"\\right) - {R2_calc:.2f} = {R1_calc:.2f}$ kips\n"

        # Shear force and zero-shear points
        detailed_text += r"""
\subsection{Shear Force Analysis}
The shear force $V(x)$ at any point is the algebraic sum of all vertical forces to the left of that point.

Shear force function:
\begin{align*}
V(x) &= R_1 - \sum_{i} P_i \cdot H(x - x_i) - \sum_{j} w_j \cdot (x - a_j) \cdot H(x - a_j) \cdot H(b_j - x)
\end{align*}
where $H(x)$ is the Heaviside step function ($H(x) = 0$ for $x < 0$, $H(x) = 1$ for $x \geq 0$).

To find zero-shear points, we evaluate $V(x) = 0$ across the span at fine intervals.
"""
        x_points = [0] + [L[2][i] for i in range(2, M[2]+1) if L[2][i] > 0] + [L0[2]]
        x_fine = list(np.arange(0, L0[2] + 0.01, 0.01))
        shear_fine = [0] * len(x_fine)
        zero_shear_points = []

        for i, x in enumerate(x_fine):
            shear = R1_calc
            for j in range(2, M[2]+1):
                if P[2][j] != 0 and L[2][j] <= x:
                    shear -= P[2][j]
            for j in range(1, M[2]+1):
                seg_start = L[2][j]
                seg_end = L[2][j+1] if j < M[2] else L0[2]
                if seg_start <= x <= seg_end:
                    shear -= W[2][j] * (x - seg_start)
                elif x > seg_end:
                    shear -= W[2][j] * (seg_end - seg_start)
            shear_fine[i] = shear

        detailed_text += r"\subsubsection{Zero-Shear Points}" + "\n"
        for i in range(len(x_fine) - 1):
            if shear_fine[i] * shear_fine[i+1] <= 0 and abs(shear_fine[i]) + abs(shear_fine[i+1]) > 0:
                x1, x2 = x_fine[i], x_fine[i+1]
                v1, v2 = shear_fine[i], shear_fine[i+1]
                if v1 == 0 and v2 == 0:
                    zero_x = (x1 + x2) / 2
                else:
                    zero_x = x1 - v1 * (x2 - x1) / (v2 - v1) if (v2 - v1) != 0 else x1
                zero_shear_points.append(zero_x)
                detailed_text += f"\\item Zero shear at $x = {zero_x:.3f}$ ft (between $x = {x1:.3f}$ and $x = {x2:.3f}$ ft)\n"

        if not zero_shear_points:
            detailed_text += r"\item No zero-shear points found in the span" + "\n"

        # Moment calculations
        detailed_text += r"""
\subsection{Moment Calculations}
The bending moment $M(x)$ is calculated by integrating the shear force or summing moments to the left of each point.

Moment function:
\begin{align*}
M(x) &= R_1 \cdot x - \sum_{i} P_i \cdot (x - x_i) \cdot H(x - x_i) - \sum_{j} \frac{w_j \cdot (x - a_j)^2}{2} \cdot H(x - a_j) \cdot H(b_j - x)
\end{align*}

We evaluate the moment at key points, including load application points and zero-shear points.
"""
        x_moment = sorted(list(set(x_points + zero_shear_points)))
        moment_values = []
        for x in x_moment:
            moment = R1_calc * x
            detailed_text += f"\\subsubsection{{At $x = {x:.3f}$ ft}}\n"
            detailed_text += f"$R_1$ contribution: ${R1_calc:.2f} \\times {x:.3f} = {R1_calc * x:.3f}$ kip-ft\n\n"
            for i in range(2, M[2]+1):
                if P[2][i] != 0 and L[2][i] < x:
                    point_moment = P[2][i] * (x - L[2][i])
                    moment -= point_moment
                    detailed_text += f"Point load $P_{{{i-1}}} = {P[2][i]:.2f}$ kips at $x = {L[2][i]:.3f}$ ft: $M = -{P[2][i]:.2f} \\times ({x:.3f} - {L[2][i]:.3f}) = -{point_moment:.3f}$ kip-ft\n"
            for i in range(1, M[2]+1):
                if W[2][i] != 0:
                    seg_start = L[2][i]
                    seg_end = L[2][i+1] if i < M[2] else L0[2]
                    if seg_start < x:
                        if x <= seg_end:
                            length = x - seg_start
                            centroid = seg_start + length/2
                            load = W[2][i] * length
                            uniform_moment = load * (x - centroid)
                            moment -= uniform_moment
                            detailed_text += f"Uniform load $w_{{{i}}} = {W[2][i]:.2f}$ k/ft from $x = {seg_start:.3f}$ to $x = {x:.3f}$ ft:\n"
                            detailed_text += f"\\begin{{itemize}}\n"
                            detailed_text += f"\\item Length = ${length:.3f}$ ft\n"
                            detailed_text += f"\\item Centroid at $x = {centroid:.3f}$ ft\n"
                            detailed_text += f"\\item Total load = ${W[2][i]:.2f} \\times {length:.3f} = {load:.3f}$ kips\n"
                            detailed_text += f"\\item Effect = $-{load:.3f} \\times ({x:.3f} - {centroid:.3f}) = -{uniform_moment:.3f}$ kip-ft\n"
                            detailed_text += r"\end{itemize}" + "\n"
                        else:
                            length = seg_end - seg_start
                            centroid = seg_start + length/2
                            load = W[2][i] * length
                            uniform_moment = load * (x - centroid)
                            moment -= uniform_moment
                            detailed_text += f"Uniform load $w_{{{i}}} = {W[2][i]:.2f}$ k/ft from $x = {seg_start:.3f}$ to $x = {seg_end:.3f}$ ft:\n"
                            detailed_text += f"\\begin{{itemize}}\n"
                            detailed_text += f"\\item Length = ${length:.3f}$ ft\n"
                            detailed_text += f"\\item Centroid at $x = {centroid:.3f}$ ft\n"
                            detailed_text += f"\\item Total load = ${W[2][i]:.2f} \\times {length:.3f} = {load:.3f}$ kips\n"
                            detailed_text += f"\\item Effect = $-{load:.3f} \\times ({x:.3f} - {centroid:.3f}) = -{uniform_moment:.3f}$ kip-ft\n"
                            detailed_text += r"\end{itemize}" + "\n"
            detailed_text += f"Total moment: $M = {moment:.3f}$ kip-ft\n\n"
            moment_values.append((x, moment))

        # Maximum moment
        max_moment = max(moment_values, key=lambda x: x[1])
        max_moment_position = max_moment[0]
        max_moment_value = max_moment[1]
        at_zero_shear = any(abs(zero_x - max_moment_position) < 0.001 for zero_x in zero_shear_points)
        closest_zero_shear = min(zero_shear_points, key=lambda z: abs(z - max_moment_position)) if zero_shear_points else None
        closest_distance = abs(closest_zero_shear - max_moment_position) if closest_zero_shear else float('inf')

        detailed_text += r"\subsubsection{Maximum Moment}" + "\n"
        detailed_text += f"Maximum moment: ${max_moment_value:.3f}$ kip-ft at $x = {max_moment_position:.3f}$ ft\n\n"
        if at_zero_shear:
            detailed_text += r"Maximum moment occurs at a zero-shear point, confirming theoretical expectations." + "\n"
        elif zero_shear_points:
            detailed_text += f"Closest zero-shear point at $x = {closest_zero_shear:.3f}$ ft, ${closest_distance:.3f}$ ft away.\n"
            detailed_text += r"Small difference may be due to numerical precision or load distribution." + "\n"
        else:
            detailed_text += r"No zero-shear points found in the span." + "\n"

        # Deflection analysis
        required_inertia = calculate_required_inertia()
        max_deflection = max(D1[1:4]) if any(D1[1:4]) else 0
        allowable_deflection = L0[2] * ft_to_in / 240 if L0[2] > 0 else 0

        detailed_text += r"""
\subsection{Deflection Analysis}
\begin{itemize}
    \item Required moment of inertia (L/240): $I_{req} = """ + f"{required_inertia[2]:.2f}" + r"""$ in$^4$
    \item Provided moment of inertia: $I = """ + f"{selected_props.get('I', 0):.2f}" + r"""$ in$^4$
    \item Maximum deflection: $\delta_{max} = """ + f"{max_deflection:.3f}" + r"""$ inches
    \item Allowable deflection (L/240): $\delta_{allow} = """ + f"{allowable_deflection:.3f}" + r"""$ inches
\end{itemize}
"""

        # Capacity check
        utilization = max_moment_value / selected_props.get('M_capacity', 1) * 100
        detailed_text += r"""
\subsection{Capacity Check}
\begin{align*}
M_{max} &= """ + f"{max_moment_value:.2f}" + r""" \text{ kip-ft} \\
M_{capacity} &= """ + f"{selected_props.get('M_capacity', 0):.2f}" + r""" \text{ kip-ft} \\
\text{Utilization} &= \frac{M_{max}}{M_{capacity}} \times 100\% = """ + f"{utilization:.1f}" + r""" \%
\end{align*}

\textbf{Status}: \textcolor{""" + ("green" if utilization <= 100 else "red") + r"""}{""" + ("PASS" if utilization <= 100 else "FAIL") + r"""}
"""

        # Theoretical verification
        detailed_text += r"""
\subsection{Theoretical Verification}
The maximum moment occurs where the shear force is zero, as the derivative of the moment is the shear:
\begin{align*}
\frac{dM(x)}{dx} = V(x)
\end{align*}
At maximum moment, $V(x) = 0$. """
        if at_zero_shear:
            detailed_text += r"This is confirmed by our calculations." + "\n"
        else:
            detailed_text += r"Note: The maximum moment may not occur exactly at a zero-shear point due to:\n"
            detailed_text += r"\begin{itemize}" + "\n"
            detailed_text += r"\item Non-continuous loading" + "\n"
            detailed_text += r"\item Maximum moment at point loads or beam ends" + "\n"
            detailed_text += r"\item Numerical approximation" + "\n"
            detailed_text += r"\end{itemize}" + "\n"

        # Write the enhanced LaTeX content
        new_content = content[:insert_pos] + detailed_text + content[insert_pos:]
        try:
            with open(latex_filename, 'w', encoding='utf-8') as file:
                file.write(new_content)
            self.save_status.text = f"Enhanced LaTeX report saved to:\n{latex_filename}"
        except Exception as ex:
            self.save_status.text = f"Error writing enhanced LaTeX file {latex_filename}: {str(ex)}"
            return

    except Exception as e:
        self.save_status.text = f"Error generating LaTeX report: {str(e)}"
        print(f"Error generating LaTeX report: {str(e)}")

def save_beam_report():
    """Save beam analysis results and plot to a report file"""
    if B_real <= 0 or D_real <= 0 or 'M_capacity' not in selected_props:
        return "Error: No valid beam selected. Cannot generate report."

    # Create report directory if it doesn't exist
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beam_reports")
    os.makedirs(report_dir, exist_ok=True)
    
    # Generate a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(report_dir, f"beam_report_{timestamp}.txt")
    plot_filename = os.path.join(report_dir, f"beam_plot_{timestamp}.png")
    latex_filename = os.path.join(report_dir, f"beam_report_{timestamp}.tex")
    html_filename = os.path.join(report_dir, f"beam_report_{timestamp}.html")
    
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
    try:
        plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        plt.close(fig)
        return f"Error saving plot: {str(e)}"
    
    # Generate report content (text version)
    report_content = f"""===========================================================
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
-----------------------------------------------------------"""
    
    # Add span information to the report
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0:
            report_content += f"\n{span_name} (Span {g}):\n"
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

Maximum Moments:"""
    
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0 and M1[g] > 0:
            report_content += f"\n  - {span_name}: {M1[g]:.2f} kip-ft"
    
    # Add deflection information
    I_req = calculate_required_inertia()
    max_deflection = max(D1[1:4]) if any(D1[1:4]) else 0
    deflection_ratio = int(L0[2]*12/max_deflection) if max_deflection > 0 else 0
    
    report_content += f"""

Deflection:
  - Maximum deflection: {max_deflection:.3f} inches (L/{deflection_ratio})
  - Maximum allowable deflection (L/240): {L0[2] * 12 / 240:.3f} inches
  - Required moment of inertia: {I_req[2]:.2f} in⁴
  - Provided moment of inertia: {selected_props.get('I', 0):.2f} in⁴"""

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
LaTeX report saved to: {latex_filename}
HTML report saved to: {html_filename}
==========================================================="""
    
    # Write text report to file
    try:
        with open(report_filename, 'w', encoding='utf-8') as file:
            file.write(report_content)
        print(f"Text report saved to {report_filename}")
    except Exception as e:
        print(f"Error writing text report: {str(e)}")
        return f"Error writing text report: {str(e)}"



    # In the generate_latex_report() method
    latex_content = r"""
\documentclass[12pt]{article}
\usepackage{graphicx}
\graphicspath{{./beam_reports/}}  # <-- ADD THIS LINE
\begin{document}
...
\end{document}
"""
    
    # When saving the plot
    plot_filename = os.path.join(report_dir, f"beam_plot_{timestamp}.png")  # Keep this line

    # In the LaTeX content
    latex_content += (
        r"\includegraphics[width=0.85\textwidth]{beam_plot_" 
        + f"{timestamp}"  # <-- MUST MATCH plot_filename
        + r".png}"
)
    
    
    # Generate LaTeX report content
    latex_content = r"""\documentclass[12pt]{article}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}  
\graphicspath{{./beam_reports/}}  
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage[margin=1in]{geometry}
\usepackage{fancyhdr}
\usepackage{xcolor}
\usepackage{array}
\usepackage{caption}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[L]{\textbf{Beam Structural Analysis}}
\fancyhead[R]{\today}
\fancyfoot[C]{\thepage}

\begin{document}

\begin{center}
\textbf{\LARGE Beam Structural Analysis Report} \\
\vspace{0.5cm}
\textbf{\large """ + f"{L13}" + r"""} \\
\vspace{0.3cm}
\textbf{Date: """ + f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + r"""}
\end{center}

\section{Beam Properties}

\begin{table}[htbp]
\centering
\caption{Beam Specifications}
\begin{tabular}{>{\raggedright\arraybackslash}p{5cm} >{\raggedleft\arraybackslash}p{5cm}}
\toprule
\textbf{Property} & \textbf{Value} \\
\midrule
Material & """ + f"{MATERIAL}" + r""" \\
Size & """ + f"{B_real}" + r""" in $\times$ """ + f"{D_real}" + r""" in \\
Section Modulus ($S$) & """ + f"{selected_props.get('S', 0):.2f}" + r""" in$^3$ \\
Moment of Inertia ($I$) & """ + f"{selected_props.get('I', 0):.2f}" + r""" in$^4$ \\
Moment Capacity & """ + f"{selected_props.get('M_capacity', 0):.2f}" + r""" kip-ft \\
\bottomrule
\end{tabular}
\end{table}

\section{Loading Summary}"""
    
    # Add span information to the LaTeX report
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0:
            latex_content += r"\subsection{" + f"{span_name} (Span {g})" + r"}" + "\n"
            latex_content += r"Span length: $L = " + f"{L0[g]:.2f}" + r"$ ft\\\\" + "\n"
            
            # Point loads
            has_point_loads = False
            for i in range(2, M[g]+1):
                if P[g][i] != 0:
                    if not has_point_loads:
                        latex_content += r"\subsubsection{Point Loads}" + "\n"
                        latex_content += r"\begin{tabular}{lll}" + "\n"
                        latex_content += r"\textbf{Load} & \textbf{Magnitude} & \textbf{Position} \\" + "\n"
                        has_point_loads = True
                    latex_content += f"$P_{{{g}{i-1}}}$ & {P[g][i]:.2f} kips & {L[g][i]:.2f} ft \\\\" + "\n"
            if has_point_loads:
                latex_content += r"\end{tabular}" + "\n\n"
            
            # Uniform loads
            has_uniform_loads = False
            for i in range(1, M[g]+1):
                if W[g][i] != 0:
                    if not has_uniform_loads:
                        latex_content += r"\subsubsection{Uniform Loads}" + "\n"
                        latex_content += r"\begin{tabular}{llll}" + "\n"
                        latex_content += r"\textbf{Load} & \textbf{Magnitude} & \textbf{Start} & \textbf{End} \\" + "\n"
                        has_uniform_loads = True
                    seg_start = L[g][i]
                    seg_end = L[g][i+1] if i < M[g] else L0[g]
                    latex_content += f"$w_{{{g}{i}}}$ & {W[g][i]:.2f} k/ft & {seg_start:.2f} ft & {seg_end:.2f} ft \\\\" + "\n"
            if has_uniform_loads:
                latex_content += r"\end{tabular}" + "\n\n"
    
    # Add analysis results
    latex_content += r"""
\section{Analysis Results}

\subsection{Reactions}
$R_1 = """ + f"{total_R1:.2f}" + r"""$ kips \\
$R_2 = """ + f"{total_R2:.2f}" + r"""$ kips

\subsection{Maximum Moments}
"""
    for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
        if L0[g] > 0 and M1[g] > 0:
            latex_content += f"{span_name}: $M_{{{g}}} = {M1[g]:.2f}$ kip-ft \\\\\n"
    
    # Add deflection information
    latex_content += r"""
\subsection{Deflection Analysis}
Maximum deflection: $\delta_{max} = """ + f"{max_deflection:.3f}" + r"""$ inches (L/""" + f"{deflection_ratio}" + r""")\\
Maximum allowable deflection ($L/240$): $\delta_{allow} = """ + f"{L0[2] * 12 / 240:.3f}" + r"""$ inches \\
Required moment of inertia: $I_{req} = """ + f"{I_req[2]:.2f}" + r"""$ in$^4$ \\
Provided moment of inertia: $I_{provided} = """ + f"{selected_props.get('I', 0):.2f}" + r"""$ in$^4$ \\
"""

    # Add capacity check
    latex_content += r"""
\section{Capacity Check}
\begin{align}
M_{max} &= """ + f"{max_moment:.2f}" + r""" \text{ kip-ft} \\
M_{capacity} &= """ + f"{selected_props.get('M_capacity', 0):.2f}" + r""" \text{ kip-ft} \\
\text{Utilization} &= \frac{M_{max}}{M_{capacity}} \times 100\% = """ + f"{utilization:.1f}" + r"""\%
\end{align}

\textbf{Status}: \textcolor{""" + ("green" if utilization <= 100 else "red") + r"""}{""" + ("PASS" if utilization <= 100 else "FAIL") + r"""}

\section{Beam Diagram}
\begin{figure}[htbp]
\centering

\includegraphics[width=0.85\textwidth]{beam_plot_""" + f"{timestamp}" + r""".png} 
\caption{Beam Loading Diagram for """ + f"{L13}" + r"""}
\end{figure}

\end{document}"""
    
    
    
    # Write LaTeX report to file
    try:
        with open(latex_filename, 'w', encoding='utf-8') as file:
            file.write(latex_content)
        print(f"LaTeX report saved to {latex_filename}")
    except Exception as e:
        print(f"Error writing LaTeX report: {str(e)}")
        return f"Error writing LaTeX report: {str(e)}"
    
    # Generate HTML report content (stub for completeness, as per original code)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Beam Structural Analysis Report</title>
</head>
<body>
    <h1>Beam Structural Analysis Report</h1>
    <h2>{L13}</h2>
    <p><b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <!-- Add HTML content here -->
</body>
</html>"""
    
    try:
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML report saved to {html_filename}")
    except Exception as e:
        print(f"Error writing HTML report: {str(e)}")
        return f"Error writing HTML report: {str(e)}"
    
    return f"Reports saved:\nText: {report_filename}\nPlot: {plot_filename}\nLaTeX: {latex_filename}\nHTML: {html_filename}"

def generate_word_report():
    import os
    import datetime

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beam_reports")
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(report_dir, f"beam_word_report_{timestamp}.txt")
    plot_filename = os.path.join(report_dir, f"beam_plot_{timestamp}.png")

    # Save the plot (reuse your plotting code)
    # ... (copy your plot code here, or call your plot function)
    # For example:
    # plot_results(selected_props, M1, L0, MATERIAL, B_real, D_real)
    # plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
    # plt.close()

    # Write the word-based report
    with open(report_filename, 'w', encoding='utf-8') as file:
        file.write(f"BEAM STRUCTURAL ANALYSIS REPORT\n")
        file.write(f"{'='*60}\n")
        file.write(f"Beam Location: {L13}\n")
        file.write(f"Material: {MATERIAL}\n")
        file.write(f"Size: {B_real} x {D_real} in\n")
        file.write(f"Section Modulus (S): {selected_props.get('S', 0):.2f} in^3\n")
        file.write(f"Moment of Inertia (I): {selected_props.get('I', 0):.2f} in^4\n")
        file.write(f"Moment Capacity: {selected_props.get('M_capacity', 0):.2f} kip-ft\n\n")

        file.write("LOADING SUMMARY:\n")
        for g, span_name in [(1, "Left Cantilever"), (2, "Main Span"), (3, "Right Cantilever")]:
            if L0[g] > 0:
                file.write(f"{span_name} (Span {g}):\n")
                file.write(f"  - Length: {L0[g]:.2f} ft\n")
                for i in range(2, M[g]+1):
                    if P[g][i] != 0:
                        file.write(f"    * Point Load: {P[g][i]:.2f} kips at {L[g][i]:.2f} ft\n")
                for i in range(1, M[g]+1):
                    if W[g][i] != 0:
                        seg_start = L[g][i]
                        seg_end = L[g][i+1] if i < M[g] else L0[g]
                        file.write(f"    * Uniform load: {W[g][i]:.2f} k/ft from {seg_start:.2f} ft to {seg_end:.2f} ft\n")
        file.write("\n")

        file.write("ANALYSIS RESULTS:\n")
        file.write(f"  - R1 = {R1[2]:.2f} kips\n")
        file.write(f"  - R2 = {R2[2]:.2f} kips\n")
        file.write(f"  - Maximum Moment: {max(M1[1:4]):.2f} kip-ft\n")
        file.write(f"  - Maximum Deflection: {max(D1[1:4]) if any(D1[1:4]) else 0:.3f} inches\n")
        file.write(f"  - Allowable Deflection (L/240): {L0[2] * 12 / 240:.3f} inches\n")
        file.write(f"  - Utilization: {max(M1[1:4]) / selected_props.get('M_capacity', 1) * 100:.1f}%\n")
        file.write(f"  - Status: {'PASS' if max(M1[1:4]) / selected_props.get('M_capacity', 1) <= 1.0 and (max(D1[1:4]) if any(D1[1:4]) else 0) <= L0[2] * 12 / 240 else 'FAIL'}\n\n")

        file.write("DETAILED CALCULUS ANALYSIS:\n")
        file.write("The shear force at any point is calculated as the sum of all vertical forces to the left of that point.\n")
        file.write("To find where the shear is zero, we solve V(x) = 0 for each segment between loads.\n")
        # You can add more step-by-step explanations here, similar to the LaTeX version, but in plain English.

        file.write(f"\nSee the attached plot: {plot_filename}\n")

    return report_filename

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
        if key == 27:  # ESC key
            if self.root.current == 'results':
                self.root.current = 'input'
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
            
            # Find max deflection
            max_deflection = max(D1[1:4]) if any(D1[1:4]) else 0
            allowable_deflection = L0[2] * ft_to_in / 240 if L0[2] > 0 else 0
            
            results = (f"Reactions: R1={R1[2]:.2f}k, R2={R2[2]:.2f}k\n"
                      f"Max Moment: {M1[2]:.2f} kip-ft\n"
                      f"Deflection: {max_deflection:.3f} in (L/{int(L0[2]*12/max_deflection) if max_deflection > 0 else 0})\n"
                      f"Allowable: {allowable_deflection:.3f} in (L/240)\n"
                      f"Grade: {beam_grade}")
            self.results_screen.results.text = results
            self.results_screen.plot_widget.update_plot()
        except Exception as e:
            self.results_screen.results.text = f"Error: {str(e)}"
            print(f"Exception: {str(e)}")

if __name__ == '__main__':
    BeamAnalysisApp().run()
