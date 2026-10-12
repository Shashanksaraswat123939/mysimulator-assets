"""Pit lane, garages, gantries, boards, flags, barriers and trackside furniture. Original designs; team text uses the
fictional team names only."""
import math

from lib import V, box, cyl, empty, lathe, mat, rod, sphere, text3d, tyre
from pit import build_tool_trolley

ASPH = (0.07, 0.07, 0.075)
CONC = (0.5, 0.5, 0.5)
WHITE = (0.9, 0.9, 0.88)
YEL = (0.9, 0.7, 0.03)


def build_garage(team, loc=(0, 0, 0), rot_z=0.0, parent=None, w=6.6, d=8.0, h=3.6):
    """Open-fronted pit garage (front toward +Y), team-coloured back wall and roof sign."""
    tid = team["id"]
    root = empty("Garage_" + tid, loc, (0, 0, rot_z), parent)
    wall = mat("GarageWall_" + tid, team["a"], 0.6)
    trim = mat("GarageTrim_" + tid, team["b"], 0.5)
    conc = mat("Concrete", CONC, 0.9)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    screen = mat("Screen", (0.05, 0.3, 0.5), 0.2, 0.0, (0.1, 0.5, 0.8), 2.0)
    floor = mat("GarageFloor", (0.22, 0.22, 0.24), 0.45)
    box("Floor", (w, d, 0.05), (0, 0, 0.025), floor, parent=root)
    box("BackWall", (w, 0.2, h), (0, -d / 2, h / 2), wall, parent=root)
    box("SideWall_L", (0.2, d, h), (-w / 2, 0, h / 2), conc, parent=root)
    box("SideWall_R", (0.2, d, h), (w / 2, 0, h / 2), conc, parent=root)
    box("Roof", (w + 0.4, d + 0.4, 0.2), (0, 0, h + 0.1), conc, parent=root)
    box("Fascia", (w + 0.4, 0.15, 0.9), (0, d / 2 + 0.2, h - 0.2), wall, parent=root)
    box("Fascia_Stripe", (w + 0.4, 0.16, 0.12), (0, d / 2 + 0.2, h - 0.75), trim, parent=root)
    text3d("Sign", team["name"].upper(), 0.38, (0, d / 2 + 0.285, h - 0.2), (math.pi / 2, 0, 0), mat("SignText_" + tid, (0.95, 0.95, 0.95), 0.5), parent=root)
    box("Back_Stripe", (w - 0.4, 0.02, 0.5), (0, -d / 2 + 0.12, 1.0), trim, parent=root)
    for i, x in enumerate((-1.6, 0.0, 1.6)):
        box("Monitor_%d" % i, (1.1, 0.04, 0.65), (x, -d / 2 + 0.14, 2.3), dark, parent=root)
        box("Monitor_Screen_%d" % i, (1.0, 0.01, 0.55), (x, -d / 2 + 0.17, 2.3), screen, parent=root)
    build_tool_trolley((w / 2 - 0.6, -d / 2 + 0.7, 0), math.pi, root, team)
    build_tool_trolley((-w / 2 + 0.6, -d / 2 + 0.7, 0), math.pi, root, team)
    return root


def build_pit_lane(n_boxes=11, box_w=7.0, loc=(0, 0, 0), parent=None):
    """Pit lane strip along X: working lane next to the boxes, fast lane beyond, painted lines, pit wall and numbers.
    Boxes face +Y toward the lane. Returns root; box centres are at x = (i - (n-1)/2) * box_w."""
    root = empty("PitLane", loc, (0, 0, 0), parent)
    asph = mat("PitAsphalt", ASPH, 0.8)
    white = mat("PaintWhite", WHITE, 0.7)
    yel = mat("PaintYellow", YEL, 0.7)
    red = mat("PaintRed", (0.7, 0.05, 0.04), 0.7)
    conc = mat("Concrete", CONC, 0.9)
    length = n_boxes * box_w + 20
    box("Lane", (length, 14.0, 0.04), (0, 7.0 + 0.0, 0.0), asph, parent=root)
    box("Line_BoxEdge", (length, 0.15, 0.005), (0, 0.1, 0.045), white, parent=root)
    box("Line_Working", (length, 0.15, 0.005), (0, 5.0, 0.045), yel, parent=root)
    box("Line_Fast", (length, 0.15, 0.005), (0, 9.0, 0.045), white, parent=root)
    box("Line_WallEdge", (length, 0.2, 0.005), (0, 13.8, 0.045), red, parent=root)
    for i in range(n_boxes):
        x = (i - (n_boxes - 1) / 2) * box_w
        box("BoxMark_L_%d" % i, (0.12, 5.2, 0.005), (x - box_w / 2 + 0.2, 2.6, 0.045), white, parent=root)
        box("BoxMark_Stop_%d" % i, (box_w - 1.5, 0.12, 0.005), (x, 4.6, 0.045), yel, parent=root)
        text3d("BoxNo_%d" % (i + 1), str(i + 1), 0.9, (x, 3.2, 0.05), (0, 0, 0), white, extrude=0.001, parent=root)
    text3d("Limit_Paint", "80", 1.4, (-length / 2 + 6, 7.0, 0.05), (0, 0, math.pi / 2), white, extrude=0.001, parent=root)
    box("PitWall", (length, 0.6, 1.0), (0, 14.4, 0.5), conc, parent=root)
    box("PitWall_Cap", (length, 0.7, 0.08), (0, 14.4, 1.04), mat("WallCap", (0.8, 0.8, 0.8), 0.5), parent=root)
    return root


def build_signal_gantry(n_boxes=11, box_w=7.0, loc=(0, 0, 0), parent=None):
    """Overhead gantry above the working lane with a red/green signal per box."""
    root = empty("SignalGantry", loc, (0, 0, 0), parent)
    steel = mat("Metal", (0.55, 0.55, 0.58), 0.35, 1.0)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    red = mat("SignalRed", (1, 0.02, 0.02), 0.3, 0.0, (1, 0.02, 0.02), 8.0)
    green = mat("SignalGreen", (0.05, 1, 0.1), 0.3, 0.0, (0.05, 1, 0.1), 8.0)
    length = n_boxes * box_w
    box("Beam", (length, 0.3, 0.3), (0, 0, 5.2), steel, parent=root)
    for x in (-length / 2, length / 2):
        box("Post_%d" % (x > 0), (0.3, 0.3, 5.2), (x, 0, 2.6), steel, parent=root)
    for i in range(n_boxes):
        x = (i - (n_boxes - 1) / 2) * box_w
        box("Signal_%d" % i, (0.5, 0.12, 1.0), (x, -0.2, 4.4), dark, parent=root)
        cyl("Signal_Red_%d" % i, 0.14, 0.04, (x, -0.28, 4.7), red, "Y", 18, parent=root)
        cyl("Signal_Green_%d" % i, 0.14, 0.04, (x, -0.28, 4.25), green, "Y", 18, parent=root)
    return root


def build_speed_sign(limit=80, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("SpeedSign_%d" % limit, loc, (0, 0, rot_z), parent)
    pole = mat("Pole", (0.15, 0.15, 0.17), 0.4, 0.8)
    wh = mat("SignWhite", WHITE, 0.5)
    red = mat("SignRed", (0.8, 0.04, 0.04), 0.5)
    ink = mat("SignInk", (0.02, 0.02, 0.02), 0.6)
    rod("Pole", (0, 0, 0), (0, 0, 2.6), 0.04, pole, root)
    cyl("Face_Red", 0.5, 0.04, (0, 0.03, 2.6), red, "Y", 36, parent=root)
    cyl("Face_White", 0.37, 0.05, (0, 0.04, 2.6), wh, "Y", 36, parent=root)
    text3d("Limit", str(limit), 0.34, (0, 0.07, 2.6), (math.pi / 2, 0, 0), ink, parent=root)
    return root


def build_start_lights(loc=(0, 0, 0), rot_z=0.0, parent=None, lit=5):
    root = empty("StartLights", loc, (0, 0, rot_z), parent)
    steel = mat("Metal", (0.55, 0.55, 0.58), 0.35, 1.0)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    on = mat("LightOn", (1, 0.02, 0.02), 0.3, 0.0, (1, 0.02, 0.02), 10.0)
    off = mat("LightOff", (0.12, 0.01, 0.01), 0.4)
    box("Gantry", (14.0, 0.5, 0.5), (0, 0, 7.0), steel, parent=root)
    for x in (-7.0, 7.0):
        box("Post_%d" % (x > 0), (0.5, 0.5, 7.0), (x, 0, 3.5), steel, parent=root)
    for i in range(5):
        x = (i - 2) * 1.5
        box("Pod_%d" % i, (0.9, 0.3, 1.9), (x, -0.4, 6.1), dark, parent=root)
        for k, z in enumerate((6.65, 6.1, 5.55)):
            cyl("Lamp_%d_%d" % (i, k), 0.22, 0.05, (x, -0.58, z), on if i < lit else off, "Y", 20, parent=root)
    return root


def build_overtake_board(loc=(0, 0, 0), rot_z=0.0, parent=None, active=True):
    """LED board that shows the overtake-mode state: amber 'OVERTAKE' with a state bar, plus a trackside zone sign."""
    root = empty("OvertakeBoard", loc, (0, 0, rot_z), parent)
    pole = mat("Pole", (0.15, 0.15, 0.17), 0.4, 0.8)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    amber = mat("LED_Amber", (1, 0.55, 0.02), 0.3, 0.0, (1, 0.55, 0.02), 7.0 if active else 0.4)
    green = mat("LED_Green", (0.1, 1, 0.2), 0.3, 0.0, (0.1, 1, 0.2), 6.0 if active else 0.3)
    for x in (-1.3, 1.3):
        box("Post_%d" % (x > 0), (0.12, 0.12, 2.2), (x, 0, 1.1), pole, parent=root)
    box("Panel", (3.2, 0.14, 1.5), (0, 0, 2.6), dark, bevel=0.02, parent=root)
    text3d("Title", "OVERTAKE", 0.42, (0, 0.085, 2.95), (math.pi / 2, 0, 0), amber, extrude=0.01, parent=root)
    text3d("State", "MODE ON" if active else "MODE OFF", 0.3, (0, 0.085, 2.4), (math.pi / 2, 0, 0), green if active else amber, extrude=0.01, parent=root)
    for i in range(10):
        box("Bar_%d" % i, (0.25, 0.04, 0.12), (-1.3 + i * 0.29, 0.085, 2.0), green if (active and i < 7) else dark, parent=root)
    return root


def build_flag(kind, loc=(0, 0, 0), rot_z=0.0, parent=None):
    """Marshal flag on a pole. kinds: green yellow double_yellow red blue white black black_white black_orange
    yellow_red_stripes chequered."""
    root = empty("Flag_" + kind, loc, (0, 0, rot_z), parent)
    pole = mat("Pole", (0.15, 0.15, 0.17), 0.4, 0.8)
    rod("Pole", (0, 0, 0), (0, 0, 2.2), 0.018, pole, root)
    cols = {
        "green": (0.05, 0.6, 0.1), "yellow": (0.9, 0.7, 0.02), "red": (0.8, 0.03, 0.03), "blue": (0.03, 0.15, 0.8),
        "white": (0.9, 0.9, 0.9), "black": (0.02, 0.02, 0.02),
    }
    ky = {"double_yellow": "yellow", "black_white": "black", "black_orange": "black", "yellow_red_stripes": "yellow", "chequered": "white"}
    base = cols[ky.get(kind, kind)]
    cloth = mat("Cloth_" + ky.get(kind, kind), base, 0.8)
    wx, wz = 0.7, 0.5
    cx, cz = wx / 2 + 0.02, 2.0
    if kind == "chequered":
        blk = mat("Cloth_black", cols["black"], 0.8)
        nx, nz = 8, 6
        for i in range(nx):
            for j in range(nz):
                box("Sq_%d_%d" % (i, j), (wx / nx, 0.01, wz / nz), (0.02 + (i + 0.5) * wx / nx, 0, 2.2 - 0.02 - (j + 0.5) * wz / nz), blk if (i + j) % 2 == 0 else cloth, parent=root)
    elif kind == "double_yellow":
        box("Cloth_0", (wx, 0.01, wz * 0.48), (cx, 0, 2.2 - 0.02 - wz * 0.24), cloth, parent=root)
        box("Cloth_1", (wx, 0.01, wz * 0.48), (cx, 0, 2.2 - 0.02 - wz * 0.76), cloth, parent=root)
    elif kind == "black_white":
        box("Cloth", (wx, 0.01, wz), (cx, 0, cz), mat("Cloth_white", cols["white"], 0.8), parent=root)
        box("Tri", (wx * 0.75, 0.012, wz * 0.75), (cx, 0, cz), cloth, rot=(0, 0.9, 0), parent=root)
    elif kind == "black_orange":
        box("Cloth", (wx, 0.01, wz), (cx, 0, cz), cloth, parent=root)
        cyl("Disc", 0.17, 0.012, (cx, 0.0, cz), mat("Cloth_orange", (0.95, 0.4, 0.02), 0.7), "Y", 28, parent=root)
    elif kind == "yellow_red_stripes":
        red = mat("Cloth_red", cols["red"], 0.8)
        for i in range(7):
            box("Stripe_%d" % i, (wx, 0.01, wz / 7), (cx, 0, 2.2 - 0.02 - (i + 0.5) * wz / 7), cloth if i % 2 == 0 else red, parent=root)
    else:
        box("Cloth", (wx, 0.01, wz), (cx, 0, cz), cloth, parent=root)
    return root


def build_marshal_post(loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("MarshalPost", loc, (0, 0, rot_z), parent)
    wall = mat("PostWall", (0.85, 0.85, 0.85), 0.7)
    roof = mat("PostRoof", (0.6, 0.05, 0.05), 0.6)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    amber = mat("LED_Amber", (1, 0.55, 0.02), 0.3, 0.0, (1, 0.55, 0.02), 6.0)
    box("Floor", (2.6, 2.2, 0.15), (0, 0, 0.075), mat("Concrete", CONC, 0.9), parent=root)
    for x in (-1.2, 1.2):
        box("Post_%d" % (x > 0), (0.1, 0.1, 2.2), (x, 0.9, 1.25), wall, parent=root)
    box("BackWall", (2.6, 0.1, 2.0), (0, -0.95, 1.15), wall, parent=root)
    box("Roof", (2.9, 2.5, 0.12), (0, 0, 2.4), roof, rot=(0.08, 0, 0), parent=root)
    box("Bench", (1.8, 0.4, 0.08), (0, -0.6, 0.55), dark, parent=root)
    box("LightPanel", (1.0, 0.1, 0.7), (0, 1.0, 2.0), dark, parent=root)
    for i, c in enumerate((0, 1, 2, 3)):
        cyl("Lamp_%d" % i, 0.1, 0.04, (-0.36 + i * 0.24, 1.07, 2.0), amber, "Y", 16, parent=root)
    return root


def build_tyre_wall(rows=3, cols=8, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("TyreWall", loc, (0, 0, rot_z), parent)
    rub = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    wcol = mat("Tyre_White", (0.9, 0.9, 0.9), 0.7)
    bcol = mat("Tyre_Blue", (0.05, 0.1, 0.7), 0.7)
    for r in range(rows):
        for c in range(cols):
            x = (c - (cols - 1) / 2) * 0.62 + (0.31 if r % 2 else 0)
            tyre("Tyre_%d_%d" % (r, c), 0.33, 0.34, (x, 0, 0.17 + r * 0.34), rub, "Y", root, 0.45, 20)
    box("Strap", (cols * 0.62, 0.02, 0.04), (0, -0.18, 0.3), mat("Strap", (0.8, 0.5, 0.05), 0.6), parent=root)
    return root


def build_armco(length=12.0, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("Armco", loc, (0, 0, rot_z), parent)
    steel = mat("Armco", (0.62, 0.64, 0.66), 0.35, 1.0)
    n = int(length / 2.0)
    for i in range(n + 1):
        box("Post_%d" % i, (0.08, 0.1, 0.8), (i * 2.0 - length / 2, 0, 0.4), steel, parent=root)
    box("Rail", (length, 0.05, 0.3), (0, 0.06, 0.62), steel, bevel=0.01, parent=root)
    box("Rail_Ridge", (length, 0.07, 0.06), (0, 0.07, 0.62), steel, parent=root)
    return root


def build_catch_fence(length=14.0, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("CatchFence", loc, (0, 0, rot_z), parent)
    steel = mat("Metal", (0.55, 0.55, 0.58), 0.35, 1.0)
    mesh = mat("FenceMesh", (0.3, 0.3, 0.32), 0.5, 0.0, alpha=0.35)
    n = int(length / 3.5)
    for i in range(n + 1):
        rod("Post_%d" % i, (i * 3.5 - length / 2, 0, 0), (i * 3.5 - length / 2, 0, 6.0), 0.05, steel, root)
    box("Mesh", (length, 0.01, 5.0), (0, 0, 3.4), mesh, parent=root)
    rod("TopWire", (-length / 2, 0, 6.0), (length / 2, 0, 6.0), 0.015, steel, root)
    return root


def build_kerb(length=10.0, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("Kerb", loc, (0, 0, rot_z), parent)
    red = mat("Kerb_Red", (0.75, 0.04, 0.03), 0.6)
    wh = mat("Kerb_White", WHITE, 0.6)
    n = int(length / 0.8)
    for i in range(n):
        box("Seg_%d" % i, (0.8, 1.1, 0.06), ((i + 0.5) * 0.8 - length / 2, 0, 0.03), red if i % 2 == 0 else wh, bevel=0.01, parent=root)
    return root


def build_grandstand(rows=10, width=24.0, loc=(0, 0, 0), rot_z=0.0, parent=None, team=None):
    root = empty("Grandstand", loc, (0, 0, rot_z), parent)
    conc = mat("Concrete", CONC, 0.9)
    seat = mat("Seat_Blue", (0.05, 0.12, 0.55), 0.6)
    seat2 = mat("Seat_White", (0.85, 0.85, 0.88), 0.6)
    roof = mat("StandRoof", (0.7, 0.7, 0.72), 0.5, 0.2)
    steel = mat("Metal", (0.55, 0.55, 0.58), 0.35, 1.0)
    for r in range(rows):
        box("Step_%d" % r, (width, 0.9, 0.45), (0, r * 0.9, 0.225 + r * 0.45), conc, parent=root)
        for i in range(int(width / 0.7)):
            box("Seat_%d_%d" % (r, i), (0.5, 0.35, 0.4), (-width / 2 + 0.4 + i * 0.7, r * 0.9 - 0.15, 0.62 + r * 0.45), seat if (i + r) % 5 else seat2, bevel=0.03, parent=root)
    top = rows * 0.45 + 3.0
    for x in (-width / 2, width / 2):
        rod("Pillar_%d" % (x > 0), (x, rows * 0.9 - 0.4, 0), (x, rows * 0.9 - 0.4, top), 0.12, steel, root)
    box("Roof", (width + 1, rows * 0.9 + 1.5, 0.15), (0, rows * 0.45, top), roof, rot=(-0.12, 0, 0), parent=root)
    return root
