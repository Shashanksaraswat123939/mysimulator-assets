"""Original open-wheel racing car with active-aero hinge pivots and a team livery. Not a copy of any real car."""
import math

from lib import V, box, cyl, empty, loft, mat, rod, sphere, text3d, tyre
from teams import COMPOUNDS


def build_f1(team, number=1, loc=(0, 0, 0), rot_z=0.0, compound="medium", front_flap=0.0, rear_flap=0.0, helmet=True, parent=None):
    """front_flap / rear_flap: radians the movable flaps are opened (0 = closed/cornering, ~0.35 = open/straight-line)."""
    tid = team["id"]
    root = empty("F1_" + tid, loc, (0, 0, rot_z), parent)
    A = mat("L_%s_A" % tid, team["a"], 0.25, 0.25, coat=1.0)
    B = mat("L_%s_B" % tid, team["b"], 0.3, 0.1, coat=1.0)
    C = mat("L_%s_C" % tid, team["c"], 0.35, 0.0)
    carbon = mat("Carbon", (0.015, 0.015, 0.017), 0.35, 0.3)
    rubber = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    metal = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    ring = mat("Compound_" + compound, COMPOUNDS[compound], 0.6)
    helm = mat("L_%s_Helmet" % tid, team["helmet"], 0.2, 0.0, coat=1.0)
    led = mat("TailLight", (1, 0.02, 0.02), 0.3, 0.0, (1, 0.02, 0.02), 6.0)

    # --- survival cell, nose and engine cover (one lofted body) ---
    body_sections = [(-2.40, 0.20, 0.35, 0.55), (-1.60, 0.28, 0.22, 0.75), (-0.60, 0.34, 0.15, 0.78), (0.20, 0.30, 0.12, 0.62),
                     (0.90, 0.24, 0.12, 0.45), (1.60, 0.12, 0.10, 0.27), (2.10, 0.08, 0.10, 0.22)]
    loft("Body", body_sections, A, 0.0, 0.5, root)
    loft("Body_Stripe", [(y, w * 0.28, zt - 0.02, zt + 0.014) for (y, w, zb, zt) in body_sections], B, 0.0, 0.3, root, subsurf=0)
    # --- sidepods ---
    for s, nm in ((1, "R"), (-1, "L")):
        loft("Sidepod_" + nm, [(0.45, 0.16, 0.12, 0.38), (-0.30, 0.26, 0.12, 0.50), (-1.20, 0.22, 0.12, 0.42), (-1.90, 0.10, 0.15, 0.30)], A, s * 0.55, 0.5, root)
        box("Sidepod_Livery_" + nm, (0.012, 0.55, 0.14), (s * 0.815, -0.35, 0.30), C, parent=root)
        box("Sidepod_Livery2_" + nm, (0.012, 0.28, 0.10), (s * 0.80, -1.05, 0.28), B, parent=root)
        box("Sidepod_Inlet_" + nm, (0.20, 0.02, 0.2), (s * 0.55, 0.46, 0.26), dark, parent=root)
    # --- floor, diffuser, beam wing ---
    box("Floor", (1.62, 3.4, 0.035), (0, -0.1, 0.075), carbon, bevel=0.01, parent=root)
    box("Splitter", (1.0, 0.3, 0.025), (0, 1.55, 0.06), carbon, bevel=0.005, parent=root)
    box("Diffuser", (1.15, 0.75, 0.03), (0, -2.15, 0.2), carbon, rot=(0.28, 0, 0), bevel=0.005, parent=root)
    box("BeamWing", (1.0, 0.24, 0.02), (0, -2.38, 0.34), carbon, parent=root)
    # --- cockpit, airbox, halo, helmet ---
    box("Cockpit", (0.38, 0.75, 0.012), (0, 0.15, 0.628), dark, parent=root)
    box("Airbox_Inlet", (0.2, 0.04, 0.2), (0, -0.3, 0.7), dark, parent=root)
    if helmet:
        sphere("Helmet", 0.125, (0, 0.04, 0.70), helm, (1, 1.1, 1.0), root)
        box("Visor", (0.18, 0.06, 0.06), (0, 0.15, 0.71), dark, parent=root)
    pts = [(-0.2, -0.1, 0.72), (-0.2, 0.3, 0.86), (0, 0.58, 0.80), (0.2, 0.3, 0.86), (0.2, -0.1, 0.72)]
    for i in range(len(pts) - 1):
        rod("Halo_%d" % i, pts[i], pts[i + 1], 0.02, carbon, root)
    rod("Halo_Pylon", (0, 0.58, 0.80), (0, 0.62, 0.55), 0.025, carbon, root)
    for s, nm in ((1, "R"), (-1, "L")):
        rod("Mirror_Stalk_" + nm, (s * 0.25, 0.5, 0.58), (s * 0.5, 0.55, 0.64), 0.012, carbon, root)
        box("Mirror_" + nm, (0.15, 0.05, 0.09), (s * 0.55, 0.56, 0.65), A, bevel=0.01, parent=root)
    box("TailLight", (0.10, 0.02, 0.06), (0, -2.42, 0.42), led, parent=root)
    cyl("Exhaust", 0.045, 0.22, (0, -2.45, 0.5), metal, "Y", 16, parent=root)
    # --- numbers ---
    text3d("Number_Nose", str(number), 0.20, (0, 1.12, 0.395), (0, 0, math.pi / 2), C, parent=root)
    text3d("Number_Cover", str(number), 0.26, (0, -1.35, 0.805), (0, 0, math.pi / 2), C, parent=root)
    # --- front wing (main plane + two hinged flaps per side) ---
    box("FrontWing_Main", (1.8, 0.36, 0.022), (0, 2.28, 0.085), A, bevel=0.004, parent=root)
    for s, nm in ((1, "R"), (-1, "L")):
        for k, (z, ch) in enumerate(((0.15, 0.24), (0.215, 0.20))):
            hinge = empty("FrontFlap_%s%d" % (nm, k + 1), (s * 0.47, 2.34 - 0.0, z), (front_flap * (k + 1) * 0.6, 0, 0), root)
            box("FrontFlap_%s%d_Blade" % (nm, k + 1), (0.86, ch, 0.014), (0, -ch / 2, 0), B if k else A, bevel=0.003, parent=hinge)
        box("FrontWing_Endplate_" + nm, (0.022, 0.44, 0.27), (s * 0.91, 2.28, 0.19), B, bevel=0.006, parent=root)
        box("FrontWing_Pylon_" + nm, (0.035, 0.45, 0.09), (s * 0.08, 1.95, 0.1), carbon, parent=root)
    # --- rear wing (main plane, hinged upper flap, endplates) ---
    box("RearWing_Main", (1.1, 0.3, 0.026), (0, -2.30, 0.68), A, bevel=0.004, parent=root)
    hinge = empty("RearFlap", (0, -2.46, 0.93), (rear_flap, 0, 0), root)
    box("RearFlap_Blade", (1.1, 0.24, 0.018), (0, 0.12, 0), B, bevel=0.004, parent=hinge)
    box("RearWing_Pylon", (0.08, 0.14, 0.22), (0, -2.30, 0.55), carbon, parent=root)
    for s, nm in ((1, "R"), (-1, "L")):
        box("RearWing_Endplate_" + nm, (0.022, 0.52, 0.72), (s * 0.56, -2.33, 0.72), B, bevel=0.006, parent=root)
        text3d("RearWing_Tag_" + nm, team["short"], 0.11, (s * 0.574, -2.33, 0.86), (math.pi / 2, 0, s * math.pi / 2), C, parent=root)
    # --- wheels, tyres (compound band), suspension ---
    for s, sn in ((1, "R"), (-1, "L")):
        for front in (True, False):
            r, w, y = (0.335, 0.30, 1.65) if front else (0.35, 0.37, -1.70)
            x = s * (0.81 if front else 0.83)
            tag = ("F" if front else "R") + sn
            tyre("Tyre_" + tag, r, w, (x, y, r), rubber, "X", root)
            cyl("TyreBand_" + tag, r * 0.93, w + 0.004, (x, y, r), ring, "X", 36, parent=root)
            cyl("Rim_" + tag, r * 0.6, w + 0.012, (x, y, r), metal, "X", 28, parent=root)
            cyl("WheelCover_" + tag, r * 0.5, w + 0.022, (x, y, r), carbon, "X", 28, parent=root)
            hub = V((x - s * w * 0.5, y, r))
            for i, (dy, dz) in enumerate(((0.12, 0.05), (-0.12, 0.05), (0.0, -0.12))):
                rod("Susp_%s_%d" % (tag, i), (s * 0.18, y + dy * 1.3, 0.28 + dz), hub + V((0, dy * 0.2, dz * 0.4)), 0.013, carbon, root)
    return root
