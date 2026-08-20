"""
2D Euler-Bernoulli moment-frame analysis (direct stiffness method).

Geometry: one level of beams supported by columns with fixed or pinned bases.
Bay lengths may differ; column tops are assumed level (single frame height).

Units (internal): kip, inch, ksi.

Sign conventions used for output:
- Beam moments: sagging positive.
- Beam shear: positive upward on the left face of a cut.
- Column moments: reported as member-end magnitudes with sign relative to
  local member axis (base -> top).
- Axial: tension positive.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


# --------------------------------------------------------------------------
# Section database (common W-shapes):  A (in^2), Ix (in^4), Zx (in^3)
# --------------------------------------------------------------------------
W_SHAPES = {
    "W8x10": (2.96, 30.8, 8.87),
    "W8x13": (3.84, 39.6, 11.4),
    "W10x12": (3.54, 53.8, 12.6),
    "W10x15": (4.41, 68.9, 16.0),
    "W10x19": (5.62, 96.3, 21.6),
    "W10x22": (6.49, 118.0, 26.0),
    "W10x26": (7.61, 144.0, 31.3),
    "W10x30": (8.84, 170.0, 36.6),
    "W12x14": (4.16, 88.6, 17.4),
    "W12x16": (4.71, 103.0, 20.1),
    "W12x19": (5.57, 130.0, 24.7),
    "W12x22": (6.48, 156.0, 29.3),
    "W12x26": (7.65, 204.0, 37.2),
    "W12x30": (8.79, 238.0, 43.1),
    "W12x35": (10.3, 285.0, 51.2),
    "W12x40": (11.7, 307.0, 57.0),
    "W14x22": (6.49, 199.0, 33.2),
    "W14x26": (7.69, 245.0, 40.2),
    "W14x30": (8.85, 291.0, 47.3),
    "W14x34": (10.0, 340.0, 54.6),
    "W16x26": (7.68, 301.0, 44.2),
    "W16x31": (9.12, 375.0, 54.0),
    "W16x36": (10.6, 448.0, 64.0),
}


@dataclass
class MemberResult:
    name: str
    kind: str                      # "beam" or "column"
    n1: int
    n2: int
    length: float                  # in
    end_forces: np.ndarray = field(default=None)  # local [N1,V1,M1,N2,V2,M2]
    x: np.ndarray = field(default=None)           # stations along member (in)
    M: np.ndarray = field(default=None)           # internal moment (kip-in)
    V: np.ndarray = field(default=None)           # internal shear (kip)
    N: np.ndarray = field(default=None)           # internal axial (kip)
    defl_v: np.ndarray = field(default=None)      # local transverse defl (in)
    defl_u: np.ndarray = field(default=None)      # local axial defl (in)


@dataclass
class AnalysisResult:
    case_name: str
    disp: np.ndarray                              # global displacement vector
    reactions: dict                               # node -> [Fx, Fy, M]
    members: list                                 # list[MemberResult]
    top_drift: float                              # max |ux| at top joints (in)
    node_xy: list                                 # node coordinates


# --------------------------------------------------------------------------
# Core element formulation
# --------------------------------------------------------------------------
def _element(E, A, I, x1, y1, x2, y2):
    """Return (k_global 6x6, k_local 6x6, T, L, c, s)."""
    L = math.hypot(x2 - x1, y2 - y1)
    c, s = (x2 - x1) / L, (y2 - y1) / L
    k = np.array([
        [A * E / L,            0,             0, -A * E / L,            0,             0],
        [0,  12 * E * I / L**3,  6 * E * I / L**2, 0, -12 * E * I / L**3,  6 * E * I / L**2],
        [0,   6 * E * I / L**2,  4 * E * I / L,    0,  -6 * E * I / L**2,  2 * E * I / L],
        [-A * E / L,           0,             0,  A * E / L,            0,             0],
        [0, -12 * E * I / L**3, -6 * E * I / L**2, 0,  12 * E * I / L**3, -6 * E * I / L**2],
        [0,   6 * E * I / L**2,  2 * E * I / L,    0,  -6 * E * I / L**2,  4 * E * I / L],
    ])
    T = np.array([
        [c, s, 0, 0, 0, 0],
        [-s, c, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, c, s, 0],
        [0, 0, 0, -s, c, 0],
        [0, 0, 0, 0, 0, 1],
    ])
    return T.T @ k @ T, k, T, L, c, s


def _udl_fixed_end(w, L):
    """Consistent fixed-end force vector (local) for UDL w [kip/in] acting
    downward (global -Y) on a horizontal member.  Local +v is global +Y for a
    left-to-right member, so local load intensity q = -w.

    Returns fef such that element nodal forces = k_local*d_local + fef.
    Sign convention: fixed-end moments that the support exerts on the member.
    """
    q = -w
    return np.array([0.0,
                     q * L / 2.0,
                     q * L ** 2 / 12.0,
                     0.0,
                     q * L / 2.0,
                     -q * L ** 2 / 12.0])


# --------------------------------------------------------------------------
# Model assembly
# --------------------------------------------------------------------------
def build_model(bay_lengths_in, height_in, beam_AI, col_AI, base="fixed"):
    """Assemble nodes/elements for a two-bay frame.

    bay_lengths_in : [L1, L2]  (in)
    height_in      : scalar or [h1, h2, h3] column heights (in)
    beam_AI        : (A, I) or [(A,I), (A,I)] per beam
    col_AI         : (A, I) or [(A,I), (A,I), (A,I)] per column
    Returns dict with nodes, elements, dof maps.
    """
    L1, L2 = bay_lengths_in
    if np.isscalar(height_in):
        heights = [height_in] * 3
    else:
        heights = list(height_in)
    if isinstance(beam_AI, tuple):
        beam_AI = [beam_AI, beam_AI]
    if isinstance(col_AI, tuple):
        col_AI = [col_AI] * 3

    xs = [0.0, L1, L1 + L2]
    nodes = [(xs[i], 0.0) for i in range(3)] + \
            [(xs[i], heights[i]) for i in range(3)]
    # nodes 0,1,2 bases ; 3,4,5 tops
    elements = []
    for i in range(3):  # columns C1..C3  (base -> top)
        elements.append({"n1": i, "n2": i + 3, "A": col_AI[i][0],
                         "I": col_AI[i][1], "kind": "column",
                         "name": f"C{i+1}"})
    elements.append({"n1": 3, "n2": 4, "A": beam_AI[0][0],
                     "I": beam_AI[0][1], "kind": "beam", "name": "B1"})
    elements.append({"n1": 4, "n2": 5, "A": beam_AI[1][0],
                     "I": beam_AI[1][1], "kind": "beam", "name": "B2"})
    return {"nodes": nodes, "elements": elements, "base": base}


def analyze(model, E, w_beams=(0.0, 0.0), H_top=(0.0, 0.0, 0.0),
            case_name="case", n_pts=41):
    """Run one load case.

    w_beams : (w1, w2) downward UDL per beam (kip/in)
    H_top   : (H1, H2, H3) global X point loads at top joints (kip)
    """
    nodes, elements = model["nodes"], model["elements"]
    ndof = 3 * len(nodes)
    K = np.zeros((ndof, ndof))
    F = np.zeros(ndof)
    elem_data = []

    for el in elements:
        n1, n2 = el["n1"], el["n2"]
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        kg, kl, T, L, c, s = _element(E, el["A"], el["I"], x1, y1, x2, y2)
        dofs = [3 * n1, 3 * n1 + 1, 3 * n1 + 2, 3 * n2, 3 * n2 + 1, 3 * n2 + 2]
        for a in range(6):
            for b in range(6):
                K[dofs[a], dofs[b]] += kg[a, b]
        fef = np.zeros(6)
        if el["kind"] == "beam":
            w = w_beams[0] if el["name"] == "B1" else w_beams[1]
            fef = _udl_fixed_end(w, L)
            # equivalent nodal load = -T^T fef
            F[np.array(dofs)] += T.T @ (-fef)
        elem_data.append({"el": el, "kl": kl, "T": T, "L": L,
                          "c": c, "s": s, "fef": fef, "dofs": dofs})

    for j, Hj in enumerate(H_top):            # top joints are nodes 3,4,5
        F[3 * (j + 3)] += Hj

    # supports
    fixed_dofs = []
    for i in range(3):
        fixed_dofs += [3 * i, 3 * i + 1]
        if model["base"] == "fixed":
            fixed_dofs.append(3 * i + 2)
    free = [d for d in range(ndof) if d not in fixed_dofs]

    d = np.zeros(ndof)
    d[np.array(free)] = np.linalg.solve(
        K[np.ix_(free, free)], F[np.array(free)])

    # reactions
    R = K @ d - F
    reactions = {}
    for i in range(3):
        reactions[f"J{i+1}"] = [R[3 * i], R[3 * i + 1],
                                R[3 * i + 2] if model["base"] == "fixed" else 0.0]

    # member results
    members = []
    for ed in elem_data:
        el = ed["el"]
        d_loc = ed["T"] @ d[np.array(ed["dofs"])]
        f_loc = ed["kl"] @ d_loc + ed["fef"]
        L = ed["L"]
        x = np.linspace(0.0, L, n_pts)
        # internal actions from left-segment equilibrium (local axes);
        # f_loc = forces exerted by element on nodes.
        # sagging-positive moment, positive shear upward on left face,
        # tension-positive axial.
        q = 0.0
        if el["kind"] == "beam":
            w = w_beams[0] if el["name"] == "B1" else w_beams[1]
            q = -w                                   # local +v = global +Y
        N = f_loc[0] * np.ones_like(x)
        V = -f_loc[1] + q * x
        M = f_loc[2] - f_loc[1] * x + q * x ** 2 / 2.0
        # local transverse displacement (Hermite) incl. load term via
        # integrating curvature:  v(x) = N1(x)v1 + N2(x)th1 + N3(x)v2 + N4(x)th2 + v_load
        v1, t1, v2, t2 = d_loc[1], d_loc[2], d_loc[4], d_loc[5]
        xi = x / L
        H1 = 1 - 3 * xi ** 2 + 2 * xi ** 3
        H2 = L * (xi - 2 * xi ** 2 + xi ** 3)
        H3 = 3 * xi ** 2 - 2 * xi ** 3
        H4 = L * (-xi ** 2 + xi ** 3)
        v_el = H1 * v1 + H2 * t1 + H3 * v2 + H4 * t2
        # particular (load) deflection for clamped-clamped UDL:
        v_q = q * x ** 2 * (L - x) ** 2 / (24.0 * E * el["I"]) if q != 0 else 0.0
        u_ax = d_loc[0] + (d_loc[3] - d_loc[0]) * xi
        members.append(MemberResult(
            name=el["name"], kind=el["kind"], n1=el["n1"], n2=el["n2"],
            length=L, end_forces=f_loc, x=x,
            M=M, V=V, N=N, defl_v=v_el + v_q, defl_u=u_ax))

    top_ux = [abs(d[3 * n]) for n in (3, 4, 5)]
    return AnalysisResult(case_name=case_name, disp=d, reactions=reactions,
                          members=members, top_drift=max(top_ux),
                          node_xy=nodes)


# --------------------------------------------------------------------------
# Load combinations
# --------------------------------------------------------------------------
DEFAULT_COMBOS = [
    ("1.4D",                    {"D": 1.4}),
    ("1.2D+1.6L",               {"D": 1.2, "L": 1.6}),
    ("1.2D+L+W(down)+W(lat)",   {"D": 1.2, "L": 1.0, "Wdown": 1.0, "Wlat": 1.0}),
    ("0.9D+W(up)+W(lat)",       {"D": 0.9, "Wup": 1.0, "Wlat": 1.0}),
    ("1.2D+E+L",                {"D": 1.2, "E": 1.0, "L": 1.0}),
    ("0.9D+E",                  {"D": 0.9, "E": 1.0}),
]


def combine(results_by_case, combo, combo_name):
    """Linear combination of AnalysisResult objects (linear analysis)."""
    out = None
    for case, factor in combo.items():
        r = results_by_case.get(case)
        if r is None or factor == 0.0:
            continue
        if out is None:
            out = AnalysisResult(
                case_name=combo_name, disp=factor * r.disp,
                reactions={k: [factor * v for v in vals]
                           for k, vals in r.reactions.items()},
                members=[], top_drift=0.0, node_xy=r.node_xy)
            for m in r.members:
                out.members.append(MemberResult(
                    name=m.name, kind=m.kind, n1=m.n1, n2=m.n2,
                    length=m.length, end_forces=factor * m.end_forces,
                    x=m.x, M=factor * m.M, V=factor * m.V, N=factor * m.N,
                    defl_v=factor * m.defl_v, defl_u=factor * m.defl_u))
        else:
            out.disp += factor * r.disp
            for k in out.reactions:
                out.reactions[k] = [a + factor * b for a, b in
                                    zip(out.reactions[k], r.reactions[k])]
            for mo, mr in zip(out.members, r.members):
                mo.end_forces += factor * mr.end_forces
                mo.M += factor * mr.M
                mo.V += factor * mr.V
                mo.N += factor * mr.N
                mo.defl_v += factor * mr.defl_v
                mo.defl_u += factor * mr.defl_u
    if out is None:
        return None
    out.top_drift = max(abs(out.disp[3 * n]) for n in (3, 4, 5))
    return out
