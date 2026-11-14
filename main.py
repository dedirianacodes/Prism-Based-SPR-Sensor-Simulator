#!/usr/bin/env python3
"""
Kretschmann SPR Sensor Simulator — entry point.

    python main.py            # launch the desktop GUI
    python main.py --selftest # run the physics checks without a GUI
"""
import sys


def selftest() -> int:
    """Headless sanity checks of the TMM engine against textbook results."""
    import numpy as np
    from spr.simulation import Layer, SensorConfig, simulate
    from spr.tmm import reflectance_p

    ok = True

    def check(label, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("Transfer-matrix engine")
    # 1. Normal-incidence Fresnel reflectance of a bare glass/air interface
    R = reflectance_p([1.5, 1.0], [], np.array([0.0]), 633.0)[0]
    check(f"Fresnel R(0°) glass/air = {R:.5f} (expected 0.04000)", abs(R - 0.04) < 1e-9)
    # 2. Brewster angle: R_p = 0
    thb = np.degrees(np.arctan(1.0 / 1.5))
    R = reflectance_p([1.5, 1.0], [], np.array([thb]), 633.0)[0]
    check(f"R_p at Brewster angle {thb:.3f}° = {R:.2e} (expected 0)", R < 1e-20)
    # 3. Total internal reflection beyond the critical angle (lossless)
    R = reflectance_p([1.5, 1.0], [], np.array([60.0]), 633.0)[0]
    check(f"TIR R(60°) = {R:.6f} (expected 1)", abs(R - 1) < 1e-12)
    # 4. A zero-thickness layer must not change anything
    th = np.linspace(40, 85, 50)
    a = reflectance_p([1.515, 0.18 + 3.43j, 1.333], [50], th, 633)
    b = reflectance_p([1.515, 0.18 + 3.43j, 1.45, 1.333], [50, 0.0], th, 633)
    check("zero-thickness layer is transparent to the TMM", np.allclose(a, b))

    print("\nKretschmann benchmark: BK7 / Au (Johnson & Christy) 50 nm / water, λ = 632.8 nm")
    r = simulate(SensorConfig())
    print(f"  θ_res = {r.dip.theta_res:.3f}°, R_min = {r.dip.r_min:.4f}, "
          f"FWHM = {r.dip.fwhm:.3f}°, S = {r.sensitivity:.1f} °/RIU, FOM = {r.fom:.1f} /RIU")
    check("θ_res within literature range 71.5°–73°", 71.5 < r.dip.theta_res < 73.0)
    check("deep dip (R_min < 0.05)", r.dip.r_min < 0.05)
    check("sensitivity in literature range 120–180 °/RIU", 120 < r.sensitivity < 180)

    print("\nAll checks passed." if ok else "\nSOME CHECKS FAILED.")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    from spr.gui import run
    sys.exit(run())
