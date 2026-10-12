"""Safety car and medical car. Original designs (generic saloon / estate shapes), not copies of real vehicles."""
import math

from lib import box, cyl, empty, loft, mat, sphere, text3d, tyre


def _wheels(root, track, wb, r=0.34, w=0.26):
    rub = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    rim = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * track / 2, sy * wb / 2
            tyre("Tyre_%d%d" % (sx > 0, sy > 0), r, w, (x, y, r), rub, "X", root, 0.62, 32)
            cyl("Rim_%d%d" % (sx > 0, sy > 0), r * 0.62, w + 0.01, (x, y, r), rim, "X", 24, parent=root)


def build_safety_car(loc=(0, 0, 0), rot_z=0.0, parent=None, lights_on=True):
    root = empty("SafetyCar", loc, (0, 0, rot_z), parent)
    paint = mat("SC_Paint", (0.04, 0.35, 0.18), 0.22, 0.2, coat=1.0)
    white = mat("SC_White", (0.9, 0.9, 0.9), 0.3)
    dark = mat("SC_Dark", (0.012, 0.012, 0.015), 0.4)
    glass = mat("SC_Glass", (0.02, 0.04, 0.06), 0.05, 0.0, alpha=0.8)
    amber = mat("SC_Amber", (1, 0.55, 0.02), 0.3, 0.0, (1, 0.55, 0.02), 8.0 if lights_on else 0.2)
    green = mat("SC_Green", (0.1, 1, 0.2), 0.3, 0.0, (0.1, 1, 0.2), 8.0 if lights_on else 0.2)
    led_w = mat("SC_Head", (1, 1, 1), 0.3, 0.0, (1, 1, 1), 5.0)
    led_r = mat("SC_Tail", (1, 0.02, 0.02), 0.3, 0.0, (1, 0.02, 0.02), 5.0)
    loft("Body", [(-2.35, 0.86, 0.32, 0.9), (-1.6, 0.93, 0.28, 0.98), (-0.2, 0.96, 0.26, 1.0), (1.3, 0.94, 0.26, 0.96), (2.2, 0.86, 0.28, 0.74), (2.45, 0.7, 0.3, 0.6)], paint, 0, 0.5, root)
    loft("Cabin", [(-1.15, 0.7, 0.95, 1.22), (-0.6, 0.76, 0.95, 1.38), (0.45, 0.76, 0.95, 1.38), (1.05, 0.7, 0.95, 1.2)], glass, 0, 0.7, root)
    loft("Roof", [(-0.7, 0.72, 1.36, 1.42), (0.5, 0.72, 1.36, 1.42)], paint, 0, 0.4, root, subsurf=0)
    box("Splitter", (1.9, 0.35, 0.05), (0, 2.45, 0.2), dark, bevel=0.01, parent=root)
    box("Rear_Wing", (1.6, 0.34, 0.04), (0, -2.35, 1.12), dark, bevel=0.01, parent=root)
    for x in (-0.55, 0.55):
        box("Wing_Post_%d" % (x > 0), (0.05, 0.1, 0.3), (x, -2.3, 0.97), dark, parent=root)
    box("Stripe_L", (0.012, 3.6, 0.12), (0.97, 0, 0.72), white, parent=root)
    box("Stripe_R", (0.012, 3.6, 0.12), (-0.97, 0, 0.72), white, parent=root)
    box("Bar_Base", (1.5, 0.34, 0.07), (0, -0.05, 1.46), dark, bevel=0.01, parent=root)
    for i, x in enumerate((-0.65, -0.35, -0.05)):
        box("Bar_Amber_%d" % i, (0.27, 0.3, 0.1), (x, -0.05, 1.54), amber, bevel=0.015, parent=root)
    for i, x in enumerate((0.25, 0.55)):
        box("Bar_Green_%d" % i, (0.27, 0.3, 0.1), (x, -0.05, 1.54), green, bevel=0.015, parent=root)
    for s in (1, -1):
        box("Head_%d" % (s > 0), (0.4, 0.05, 0.1), (s * 0.58, 2.35, 0.62), led_w, bevel=0.01, parent=root)
        box("Tail_%d" % (s > 0), (0.4, 0.05, 0.1), (s * 0.58, -2.38, 0.74), led_r, bevel=0.01, parent=root)
    text3d("Hood_Text", "SAFETY CAR", 0.2, (0, 1.4, 0.985), (0, 0, math.pi / 2), white, parent=root)
    _wheels(root, 1.72, 3.0)
    return root


def build_medical_car(loc=(0, 0, 0), rot_z=0.0, parent=None, lights_on=True):
    root = empty("MedicalCar", loc, (0, 0, rot_z), parent)
    paint = mat("MC_Paint", (0.9, 0.9, 0.92), 0.3, 0.1, coat=1.0)
    red = mat("MC_Red", (0.75, 0.04, 0.04), 0.4)
    dark = mat("SC_Dark", (0.012, 0.012, 0.015), 0.4)
    glass = mat("SC_Glass", (0.02, 0.04, 0.06), 0.05, 0.0, alpha=0.8)
    amber = mat("MC_Amber", (1, 0.55, 0.02), 0.3, 0.0, (1, 0.55, 0.02), 8.0 if lights_on else 0.2)
    blue = mat("MC_Blue", (0.05, 0.2, 1), 0.3, 0.0, (0.05, 0.2, 1), 8.0 if lights_on else 0.2)
    loft("Body", [(-2.5, 0.88, 0.32, 1.7), (-1.0, 0.92, 0.28, 1.78), (0.8, 0.92, 0.28, 1.4), (1.8, 0.88, 0.3, 0.95), (2.3, 0.8, 0.32, 0.8)], paint, 0, 0.35, root)
    loft("Windscreen", [(1.0, 0.76, 1.05, 1.32), (1.55, 0.72, 0.95, 1.12)], glass, 0, 0.5, root, subsurf=0)
    box("Stripe_L", (0.012, 4.0, 0.2), (0.935, -0.1, 0.9), red, parent=root)
    box("Stripe_R", (0.012, 4.0, 0.2), (-0.935, -0.1, 0.9), red, parent=root)
    box("Cross_Back", (0.7, 0.012, 0.7), (0, -2.52, 1.2), red, parent=root)
    box("Cross_Back_V", (0.22, 0.014, 0.7), (0, -2.52, 1.2), paint, parent=root)
    box("Cross_Back_H", (0.7, 0.014, 0.22), (0, -2.52, 1.2), paint, parent=root)
    box("Bar_Base", (1.6, 0.3, 0.07), (0, 0.6, 1.82), dark, bevel=0.01, parent=root)
    for i, x in enumerate((-0.7, -0.4, -0.1, 0.2, 0.5)):
        box("Bar_%d" % i, (0.27, 0.26, 0.1), (x, 0.6, 1.9), blue if i % 2 else amber, bevel=0.015, parent=root)
    text3d("Side_Text", "MEDICAL", 0.24, (0.936, -0.1, 1.25), (math.pi / 2, 0, math.pi / 2), red, parent=root)
    _wheels(root, 1.74, 3.1, 0.36, 0.28)
    return root
