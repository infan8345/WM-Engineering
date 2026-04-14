# Wood & Steel Beam Design Tools

Structural engineering design tools for beam analysis, steel moment frame design, and detailed load calculations. Built with Python and Kivy for an interactive GUI experience.

These tools follow **AISC 360-16**, **AISC 341-16**, **ASCE 7-16**, and **CBC 2022** design codes — commonly used in residential and commercial building design in the United States.

## Features

- **Steel Moment Frame Analysis** — Seismic design with AISC steel sections (W-shapes), interaction checks, and RBS connection design
- **Wood Beam Design** — Uniform and point load analysis for simply supported beams
- **Detailed Beam Calculations** — Step-by-step shear and moment diagrams with zero-shear point detection
- **LaTeX Report Generation** — Export professional calculation reports
- **Interactive GUI** — Built with Kivy for real-time visualization of frame deflections and load diagrams

## Screenshots

> Run the app and add screenshots here showing the GUI in action.

## Project Files

| File | Description |
|------|-------------|
| `steel_moment_frame.py` | Steel moment frame seismic design app (Kivy GUI) with AISC W-shape database, deflection analysis, interaction checks, and LaTeX export |
| `wood_beam_app.py` | Wood beam design app (Kivy GUI) for residential/commercial beam sizing |
| `beam_analysis.py` | Detailed beam calculations with shear/moment diagrams and matplotlib plots |
| `beam_calcs_with_graph.py` | Enhanced beam calculator with built-in graphing |
| `beam_calcs_no_graph.py` | Lightweight beam calculator without graphing dependencies |

## Requirements

- Python 3.8+
- Kivy (for GUI applications)
- NumPy (for structural calculations)
- Matplotlib (for plotting shear/moment diagrams)

## Installation

```bash
# Clone the repository
git clone https://github.com/wminn1034-stack/Wood-beam-design.git
cd Wood-beam-design

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Steel Moment Frame Analysis
```bash
python steel_moment_frame.py
```
- Select column and beam W-shapes from the AISC database
- Input frame dimensions (width, height)
- Apply lateral (seismic) and gravity loads
- Click **Analyze Frame** to see results
- Click **Save LaTeX Report** to export calculations

### Detailed Beam Analysis
```bash
python beam_analysis.py
```
- Analyzes simply supported beams with point loads and uniform loads
- Calculates reactions, shear diagram, and moment diagram
- Finds zero-shear points to determine maximum moment
- Generates publication-quality diagrams

## Design Codes Referenced

- **AISC 360-16** — Specification for Structural Steel Buildings
- **AISC 341-16** — Seismic Provisions for Structural Steel Buildings
- **ASCE 7-16** — Minimum Design Loads for Buildings
- **CBC 2022** — California Building Code
- **NDS** — National Design Specification for Wood Construction

## Example Output

```
DETAILED BEAM ANALYSIS
Span Length: 16.0 ft
Point Loads: P1 = 1.0 kips at x = 2.0 ft, P2 = 0.5 kips at x = 5.0 ft
Uniform Loads: w1 = 0.15 k/ft, w2 = 0.7 k/ft, w3 = 0.42 k/ft

Reactions: R1 = 4.11 kips, R2 = 5.01 kips
Maximum Moment: 15.234 kip-ft at x = 8.523 ft
```

## Contributing

Contributions are welcome! If you'd like to add new beam types, load cases, or design code support, feel free to open a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**wenchung minn** — Structural Engineer & Developer

---

*Built for engineers who code, and coders who build.*
