"""
LaTeX / PDF calculation-report generation for the two-bay moment frame
analyzer.

build_latex(ctx)  -> str          (complete .tex source)
compile_pdf(tex, figs) -> (bytes|None, str)   (PDF bytes or None + log)
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def esc(s) -> str:
    """Escape LaTeX special characters in dynamic text."""
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("#", r"\#"), ("_", r"\_"), ("$", r"\$"),
                 ("^", r"\^{}"), ("~", r"\~{}")]:
        s = s.replace(a, b)
    return s


TEMPLATE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{graphicx}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}

\title{@@title@@}
\author{Two-Bay Moment Frame Analyzer (preliminary screening)}
\date{@@date@@}

\begin{document}
\maketitle

\textbf{Not for construction.} This is an automated preliminary
screening calculation. Final design requires review, completion, and
approval by a licensed structural engineer.

\section{Frame Model}
\begin{itemize}
@@geometry_items@@
\end{itemize}

The lateral system is one two-bay moment frame: three columns with
@@base@@ bases and rigid beam--column joints, analyzed by the 2D
Euler--Bernoulli direct-stiffness method (linear elastic; no P--Delta
or stiffness reduction). Members: B1 = left beam (J4--J5), B2 = right
beam (J5--J6); C1, C2, C3 = left, center, right columns (bases J1--J3,
tops J4--J6).

\section{Loads}
\subsection{Vertical (line loads on each beam)}
\begin{center}
\begin{tabular}{lcl}
\toprule
Load & Value (kip/ft) & Basis \\
\midrule
Dead $w_D$ & @@wD@@ & @@wD_basis@@ \\
Live $w_L$ & @@wL@@ & @@wL_basis@@ \\
Wind uplift $w_{W\uparrow}$ & @@wup@@ & @@wind_basis@@ \\
Wind downward $w_{W\downarrow}$ & @@wdn@@ & @@wind_basis@@ \\
\bottomrule
\end{tabular}
\end{center}

\subsection{Lateral}
\begin{itemize}
  \item Wind: $H_W$ = @@Hwind@@ kip (@@Hwind_basis@@).
  \item Seismic: $V$ = @@Vseis@@ kip (@@seis_basis@@).
  \item Application: @@latdist@@.
\end{itemize}

\section{Load Combinations (LRFD, ASCE 7)}
\begin{itemize}
@@combo_items@@
\end{itemize}

\section{Design Envelope}
Capacities: beam $\phi M_n$ = @@phiMnb@@ kip-ft (@@beam@@, compact and
braced assumed); column $\phi M_n$ = @@phiMnc@@ kip-ft, $\phi_c P_n$ =
@@phiPn@@ kip ($KL/r$ = @@KLr@@), $\phi_t P_n$ = @@phiTn@@ kip
(@@col@@, $F_y$ = @@Fy@@ ksi). Column interaction per AISC 360 H1 using
envelope $P$ and $M$ (conservative screening).

\begin{center}
\begin{tabular}{llrrrrrr}
\toprule
Member & Type & $|M|_{\max}$ & $|V|_{\max}$ & $P_{c,\max}$ &
$P_{t,\max}$ & $\phi M_n$ & DCR \\
 & & (kip-ft) & (kip) & (kip) & (kip) & (kip-ft) & \\
\midrule
@@env_rows@@
\bottomrule
\end{tabular}
\end{center}

Governing combination (beam flexure): \textbf{@@govcombo@@}.

\section{Results for Governing Combination}
\subsection{Support Reactions}
\begin{center}
\begin{tabular}{lrrr}
\toprule
Joint & $F_x$ (kip) & $F_y$ (kip) & $M$ (kip-ft) \\
\midrule
@@reaction_rows@@
\bottomrule
\end{tabular}
\end{center}

Reactions are forces exerted by the frame on the foundation: negative
$F_y$ = downward (gravity), positive $F_y$ = net uplift; positive $M$ =
counterclockwise.

\subsection{Member-End Forces (local sign convention)}
\begin{center}
\begin{tabular}{llrrr}
\toprule
Member & End & $N$ (kip) & $V$ (kip) & $M$ (kip-ft) \\
\midrule
@@force_rows@@
\bottomrule
\end{tabular}
\end{center}

@@figures@@

\section{Wind Drift and Serviceability (ASCE 7 Appendix C)}
ASCE 7 Appendix C treats wind drift as a serviceability issue and does
not prescribe one universal mandatory drift limit. Selected screening
limit: @@driftlabel@@ (@@allow@@ in for the @@Hin@@-in frame).

\begin{center}
\begin{tabular}{lllll}
\toprule
Combination & Dir & $\Delta_{\max}$ (in) & Ratio & Check \\
\midrule
@@drift_rows@@
\bottomrule
\end{tabular}
\end{center}

Elastic gross-section drift. Foundation rotation, anchor/base-plate
flexibility, connection flexibility, and second-order effects increase
real drift and are not included.

\section{Qualifications}
\begin{enumerate}
  \item Preliminary screening only; not a complete structural design.
  \item Beam lateral-torsional buckling, flange/web local buckling,
        connection design, anchorage, and foundation design are not
        included.
  \item Verify glass-guard manufacturer allowable support displacement
        where applicable.
\end{enumerate}

\end{document}
"""


def _env_rows(df):
    lines = []
    for _, r in df.iterrows():
        lines.append(
            f"{esc(r['Member'])} & {esc(r['Type'])} & "
            f"{r['max |M| (kip-ft)']} & {r['max |V| (kip)']} & "
            f"{r['max P comp (kip)']} & {r['max P tens (kip)']} & "
            f"{r['phiMn (kip-ft)']} & {r['DCR']} \\\\")
    return "\n".join(lines)


def build_latex(ctx: dict) -> str:
    rep = {k: esc(v) for k, v in ctx.items()
           if isinstance(v, (str, int, float))}

    rep["geometry_items"] = "\n".join([
        rf"  \item Bay lengths: {ctx['bay1']:.2f} ft and "
        rf"{ctx['bay2']:.2f} ft (frame length "
        rf"{ctx['bay1'] + ctx['bay2']:.2f} ft)",
        rf"  \item Column height: {ctx['height']:.2f} ft",
        rf"  \item Beam: {esc(ctx['beam'])} ($A$ = {ctx['Ab']:.2f} in$^2$,"
        rf" $I$ = {ctx['Ib']:.0f} in$^4$)",
        rf"  \item Column: {esc(ctx['col'])} ($A$ = {ctx['Ac']:.2f}"
        rf" in$^2$, $I$ = {ctx['Ic']:.0f} in$^4$)",
        rf"  \item $E$ = {ctx['E']:.0f} ksi",
    ])
    rep["combo_items"] = "\n".join(rf"  \item {esc(c)}"
                                   for c in ctx["combos"])
    rep["env_rows"] = _env_rows(ctx["env_df"])
    rep["reaction_rows"] = "\n".join(
        rf"{esc(j)} & {fx:.2f} & {fy:.2f} & {mz:.1f} \\"
        for j, fx, fy, mz in ctx["reactions"])
    rep["force_rows"] = "\n".join(
        rf"{esc(m)} & {esc(e)} & {n:.2f} & {v:.2f} & {mo:.1f} \\"
        for m, e, n, v, mo in ctx["forces"])
    rep["drift_rows"] = "\n".join(
        rf"{esc(c)} & {esc(dr)} & {dl:.3f} & {esc(rt)} & {esc(ch)} \\"
        for c, dr, dl, rt, ch in ctx["drifts"])

    if ctx.get("figures"):
        rep["figures"] = "\n".join(
            "\\begin{figure}[h!]\n\\centering\n"
            f"\\includegraphics[width=0.9\\textwidth]{{{Path(p).name}}}\n"
            f"\\caption{{{esc(cap)}}}\n\\end{{figure}}"
            for p, cap in ctx["figures"])
    else:
        rep["figures"] = ""

    out = TEMPLATE
    for k, v in rep.items():
        out = out.replace(f"@@{k}@@", str(v))
    leftover = [t for t in out.split("@@")[1::2]]
    if leftover:
        raise KeyError(f"Unfilled template tokens: {leftover}")
    return out


def compile_pdf(tex: str, fig_paths: list | None = None,
                engine: str | None = None):
    """Compile LaTeX to PDF. Returns (pdf_bytes or None, log_tail)."""
    engine = engine or shutil.which("pdflatex") or shutil.which("xelatex")
    if not engine:
        return None, "No LaTeX engine (pdflatex/xelatex) found on PATH."
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        (tdp / "report.tex").write_text(tex)
        for f in fig_paths or []:
            shutil.copy(f, tdp / Path(f).name)
        log = ""
        for _ in range(2):
            try:
                p = subprocess.run(
                    [engine, "-interaction=nonstopmode", "report.tex"],
                    cwd=td, capture_output=True, text=True, timeout=180)
                log = (p.stdout or "")[-3000:]
            except subprocess.TimeoutExpired:
                return None, "LaTeX compilation timed out."
        pdf = tdp / "report.pdf"
        if pdf.exists():
            return pdf.read_bytes(), log
        return None, log
