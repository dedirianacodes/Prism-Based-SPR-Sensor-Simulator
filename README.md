# Kretschmann SPR Sensor Simulator (TMM, p-polarisation)

Interactive desktop application for prism-coupled surface plasmon resonance
(SPR) sensors in the Kretschmann configuration. Reflectance is computed with
the 2×2 characteristic-matrix (transfer-matrix) method for TM light, using
optical constants that follow the refractiveindex.info database.

```
spr_simulator/
├── main.py              entry point (GUI, or --selftest)
├── requirements.txt
└── spr/
    ├── materials.py     optical-constant library + refractiveindex.info YAML import / fetch
    ├── tmm.py           TM transfer-matrix engine, R(θ) and |H_y(z)|² field profile
    ├── simulation.py    layer stack model, dip analysis (θ_res, R_min, FWHM), S, sweeps
    └── gui.py           PyQt6 / PySide6 window with embedded Matplotlib canvases
```

## Install and run

Python 3.9 or newer.

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. verify the physics engine (no GUI needed)
python main.py --selftest

# 4. launch the application
python main.py
```

If PyQt6 is unavailable on your platform, `pip install PySide6` instead; the app
detects either binding automatically. On some Linux distributions you may also
need the system package `libxcb-cursor0` for Qt 6.

## The five variation controls

| # | Control | Where |
|---|---------|-------|
| 1 | Glass prism (BK7, Fused Silica, SF10, SF11, LaSFN9, Sapphire) | "① Light source & glass prism" — n(λ) from the Sellmeier formula is shown live |
| 2 | Plasmonic metal (Au, Ag, Cu, Al, plus Cr/Ti adhesion layers) | "② Plasmonic metal" dropdown — n + ik and ε shown live |
| 3 | Film thickness | Metal slider 10–100 nm (1 nm steps) + spinbox (0.1 nm); any layer via the "Selected layer d" slider (0.1 nm steps) or its cell in the table |
| 4 | Multilayer stack | Table with Add / Remove / ▲ / ▼, material per layer, custom n + ik, YAML import, online fetch |
| 5 | Analyte index nₐ | Slider 1.3300–1.4000 (1×10⁻⁴ steps) + spinbox; Δnₐ for sensitivity |

Everything recomputes live (debounced while dragging). The wavelength is
adjustable (presets 632.8, 670, 785, 830, 850, 1064, 1550 nm) and every
material's optical constants are re-evaluated at that λ.

## Outputs

* **Reflectance R(θ)** at nₐ and nₐ + Δn, with θ_c, θ_res marker and FWHM bar.
* **Performance read-out:** θ_res, R_min, FWHM, S = Δθ_res/Δnₐ, Δθ_res, FOM = S/FWHM,
  detection accuracy 1/FWHM, critical angle.
* **Sensor response:** family of R(θ) curves and the θ_res(nₐ) calibration line with linear-fit slope and R².
* **Thickness optimisation:** R_min, θ_res, FWHM and S versus any layer's thickness; the optimum (minimum R_min) is marked.
* **Field profile:** |H_y(z)|²/|H_inc|² through the stack at resonance (near-field enhancement).
* **Dispersion:** n(λ) and k(λ) of every material in the stack, 400–1100 nm.
* **Export:** File → *Export R(θ) data as CSV* (Ctrl+S) writes angle and reflectance columns with a
  header that records the full stack, λ and metrics. *Export current tab data* saves the data
  behind any other tab; *Save current figure* writes PNG/SVG/PDF at 300 dpi.

## Physics

For p-polarisation, each finite layer j (thickness d_j, permittivity ε_j = N_j²) has

```
M_j = [[ cos β_j,          -i sin β_j / q_j ],
       [ -i q_j sin β_j,    cos β_j         ]]

β_j = (2π/λ) d_j √(ε_j − n_p² sin²θ)        q_j = √(ε_j − n_p² sin²θ) / ε_j
```

with the square root taken on the branch Im ≥ 0. For M = M_1 M_2 … M_{N−2},

```
r_p = [(M11 + M12 q_N) q_0 − (M21 + M22 q_N)] / [(M11 + M12 q_N) q_0 + (M21 + M22 q_N)],   R = |r_p|²
```

θ is the internal angle in the prism. θ_res is refined below the grid spacing by a
parabola through the three lowest points. FWHM is measured at half the dip depth,
referenced to the total-internal-reflection shoulder between θ_c and the dip.
S uses a forward difference between nₐ and nₐ + Δnₐ.

`python main.py --selftest` checks the engine against the Fresnel result at normal
incidence, the Brewster angle, TIR, a zero-thickness layer, and the standard
BK7 / Au 50 nm / water benchmark.

## Optical-constant data

| Material | Model | refractiveindex.info record |
|---|---|---|
| BK7, SF10, SF11, LaSFN9 | Sellmeier (formula 2), SCHOTT data sheets | specs/SCHOTT-optical/… |
| Fused silica, SiO₂ film | Sellmeier (formula 1), Malitson 1965 | main/SiO2/Malitson |
| Sapphire, Al₂O₃ film | Sellmeier (formula 1), Malitson 1962 (o-ray) | main/Al2O3/Malitson-o |
| TiO₂ film | DeVore 1951 (o-ray) | main/TiO2/Devore-o |
| Au, Ag | Johnson & Christy 1972 tables (default) | main/Au/Johnson, main/Ag/Johnson |
| Au, Ag, Cu, Al, Cr, Ti | Rakić 1998 Lorentz-Drude model | main/…/Rakic-LD |
| Graphene, MoS₂, WS₂, MoSe₂, BP | literature constants used in SPR papers at ~633 nm | — |

The two metal datasets differ noticeably in the red: for BK7 / Au 50 nm / water at
632.8 nm, Johnson & Christy gives θ_res ≈ 72.3° and FWHM ≈ 5.3°, while the Rakić
Lorentz-Drude fit gives θ_res ≈ 74.8° and FWHM ≈ 9.3°. Most SPR papers use Johnson &
Christy, so it is the default; the Rakić set is the one to use for Cu and Al, and as
a broadband model. The 2D-material constants are valid only near 633 nm, and the
status bar warns when λ leaves any material's data range.

### Using any other refractiveindex.info dataset

* **Fetch online:** *Fetch RII…* (or File menu). Enter shelf / book / page as they
  appear in the site URL, e.g. `?shelf=main&book=Cu&page=Johnson`, or pick a preset.
  Files are cached in `~/.spr_simulator/rii_cache` so later sessions work offline.
* **Import a file:** on the material's page, download the full database record (YAML)
  and use *Import YAML…*. Formulas 1–5 and tabulated n, k and nk are supported.

The new material is placed in the selected layer (or becomes the prism / primary
metal) and appears in every dropdown.

## Presets

The Presets menu loads common structures: Au or Ag on BK7, Cr/Au with a bio-recognition
layer, Ag/Au bimetallic, Au/graphene on SF11, Ag/TiO₂/MoS₂ on SF11, Cu/SiO₂ on SF10,
Al on BK7, and Au with the Rakić model for comparison.
