"""Builds, colours, exports (FBX + .blend) and renders every original My Simulator asset.

blender -b --factory-startup --python scripts/build_all.py -- <out_dir> <group> [samples]
Groups: liveries cars crew equipment venue scenes
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402

import lib  # noqa: E402
from lib import V, empty, mat, text3d, tyre  # noqa: E402
from teams import COMPOUNDS, TEAMS  # noqa: E402
import f1car  # noqa: E402
import pit  # noqa: E402
import support  # noqa: E402
import venue  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT, GROUP = ARGS[0], ARGS[1]
SAMPLES = int(ARGS[2]) if len(ARGS) > 2 else 32
for sub in ("previews", "models", "blend"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)
T = {t["id"]: t for t in TEAMS}
AUR = T["aurelia"]
MANIFEST = []

THREE_Q = (("front34", (0.9, 1.1, 0.5)), ("rear34", (-0.9, -1.1, 0.5)))
ONE_Q = (("front34", (0.9, 1.1, 0.5)),)


def materials_of(root):
    names = set()
    for o in lib.tree(root):
        if o.type == "MESH":
            for m in o.data.materials:
                if m:
                    names.add(m.name)
    return sorted(names)


def make(name, group, builder, views=ONE_Q, lens=50, size=60.0, export=True, w=1280, h=720):
    if group != GROUP and GROUP != "all":
        return

    def go():
        lib.reset()
        root = builder()
        n, tris = lib.stats(root)
        rec = dict(name=name, group=group, meshes=n, triangles=tris, materials=materials_of(root), previews=[], fbx=None)
        if export:
            lib.export_fbx(root, os.path.join(OUT, "models", name + ".fbx"))
            rec["fbx"] = "models/%s.fbx" % name
        lib.save_blend(os.path.join(OUT, "blend", name + ".blend"))
        outs = lib.frame_and_render(root, os.path.join(OUT, "previews", name + ".png"), views, lens, w, h, SAMPLES, size)
        rec["previews"] = [os.path.relpath(p, OUT) for p in outs]
        MANIFEST.append(rec)

    ok = lib.run_safely(name, go)
    if not ok:
        MANIFEST.append(dict(name=name, group=group, status="FAILED"))


# ---------------------------------------------------------------------------------------------------- liveries
for t in TEAMS:
    make("f1_" + t["id"], "liveries", lambda t=t: f1car.build_f1(t, t["nums"][0], compound="medium"), THREE_Q + (("side", (1.0, 0.0, 0.18)),), 55)

# active aero states on one car
def _aero_states():
    root = empty("AeroStates")
    for i, (nm, ff, rf) in enumerate((("CORNER_MODE", 0.0, 0.0), ("STRAIGHT_MODE", 0.45, 0.55))):
        c = f1car.build_f1(AUR, 1, (i * 3.4 - 1.7, 0, 0), 0.0, "soft", ff, rf, parent=root)
        text3d("Label_" + nm, nm.replace("_", " "), 0.22, (i * 3.4 - 1.7, 0, 0.002), (0, 0, math.pi / 2), mat("LabelInk", (0.9, 0.9, 0.9), 0.6), parent=root)
    return root


make("f1_active_aero", "liveries", lambda: _aero_states(), (("front34", (0.9, 1.1, 0.5)),), 45, w=1600)


# ---------------------------------------------------------------------------------------------------- cars
make("safety_car", "cars", lambda: support.build_safety_car(), THREE_Q, 50)
make("medical_car", "cars", lambda: support.build_medical_car(), THREE_Q, 50)

# ---------------------------------------------------------------------------------------------------- crew
ROLE_ORDER = ["front_jack", "rear_jack", "gunner", "carrier", "wing", "stabiliser", "extinguisher", "lollipop", "engineer"]


def _crew_lineup():
    root = empty("CrewLineup")
    for i, r in enumerate(ROLE_ORDER):
        pit.build_crew(r, AUR, ((i - 4) * 1.15, 0, 0), 0.0, root)
        text3d("Tag_" + r, r.replace("_", " "), 0.12, ((i - 4) * 1.15, -0.9, 0.002), (0, 0, 0), mat("LabelInk", (0.9, 0.9, 0.9), 0.6), parent=root)
    return root


make("crew_lineup", "crew", _crew_lineup, (("front", (0.0, 1.0, 0.25)), ("front34", (0.9, 1.1, 0.4))), 50, w=1800, h=700)
for tid in ("vantor", "helios", "obsidian"):
    make("crew_" + tid, "crew", lambda tid=tid: pit.build_crew("gunner", T[tid]), (("front34", (0.9, 1.1, 0.4)),), 60)


def _crew_pose_gallery():
    root = empty("CrewPoses")
    for i, p in enumerate(("stand", "gun", "carry", "jack", "wing", "lollipop")):
        pit.build_crew("gunner", AUR, ((i - 2.5) * 1.3, 0, 0), 0.0, root, pose=p)
        text3d("Tag_" + p, p, 0.13, ((i - 2.5) * 1.3, -0.9, 0.002), (0, 0, 0), mat("LabelInk", (0.9, 0.9, 0.9), 0.6), parent=root)
    return root


make("crew_pose_gallery", "crew", _crew_pose_gallery, (("front", (0.0, 1.0, 0.25)),), 50, w=1800, h=700)

# ---------------------------------------------------------------------------------------------------- equipment
make("jack_front", "equipment", lambda: pit.build_jack(True), ONE_Q, 55)
make("jack_rear", "equipment", lambda: pit.build_jack(False), ONE_Q, 55)
make("wheel_gun", "equipment", lambda: pit.build_wheel_gun(), ONE_Q, 60)
make("tyre_trolley", "equipment", lambda: pit.build_tyre_trolley(), ONE_Q, 55)
make("tool_trolley", "equipment", lambda: pit.build_tool_trolley(team=AUR), ONE_Q, 55)
make("fire_extinguisher", "equipment", lambda: pit.build_extinguisher(), ONE_Q, 60)


def _tyre_compounds():
    root = empty("Compounds")
    for i, c in enumerate(COMPOUNDS):
        pit.build_tyre_stack(c, 4, ((i - 2) * 0.95, 0, 0), 0.0, root)
        text3d("Tag_" + c, c.upper(), 0.14, ((i - 2) * 0.95, -0.55, 0.002), (0, 0, 0), mat("LabelInk", (0.9, 0.9, 0.9), 0.6), parent=root)
    return root


make("tyre_compounds", "equipment", _tyre_compounds, (("front34", (0.6, 1.1, 0.45)),), 45, w=1700)


def _boards():
    root = empty("Boards")
    for i, (txt, bd, ink) in enumerate((("BOX", (0.95, 0.95, 0.95), (0.02, 0.02, 0.02)), ("STOP", (0.8, 0.04, 0.04), (0.95, 0.95, 0.95)),
                                        ("P1", (0.05, 0.12, 0.6), (0.95, 0.95, 0.95)), ("+2.4", (0.9, 0.7, 0.02), (0.02, 0.02, 0.02)))):
        pit.build_pit_board(txt, bd, ink, ((i - 1.5) * 0.9, 0, 0), 0.0, root)
    return root


make("pit_boards", "equipment", _boards, (("front", (0.0, 1.0, 0.3)),), 45, w=1500)

# ---------------------------------------------------------------------------------------------------- venue
make("garage_aurelia", "venue", lambda: venue.build_garage(AUR), (("front34", (0.6, 1.2, 0.35)),), 40, size=80)
make("garage_vantor", "venue", lambda: venue.build_garage(T["vantor"]), (("front34", (0.6, 1.2, 0.35)),), 40, size=80)
make("signal_gantry", "venue", lambda: venue.build_signal_gantry(3), (("front34", (0.5, -1.2, 0.3)),), 40, size=80)
make("speed_sign", "venue", lambda: venue.build_speed_sign(80), (("front34", (0.5, 1.2, 0.3)),), 55)
make("start_lights", "venue", lambda: venue.build_start_lights(), (("front34", (0.5, -1.3, 0.3)),), 40, size=80)
make("overtake_board_on", "venue", lambda: venue.build_overtake_board(active=True), (("front34", (0.45, 1.2, 0.3)),), 50)
make("overtake_board_off", "venue", lambda: venue.build_overtake_board(active=False), (("front34", (0.45, 1.2, 0.3)),), 50)


def _flags():
    root = empty("Flags")
    kinds = ["green", "yellow", "double_yellow", "red", "blue", "white", "black", "black_white", "black_orange", "yellow_red_stripes", "chequered"]
    for i, k in enumerate(kinds):
        venue.build_flag(k, ((i - 5) * 1.0, 0, 0), 0.0, root)
        text3d("Tag_" + k, k.replace("_", " "), 0.07, ((i - 5) * 1.0 + 0.35, -0.2, 0.002), (0, 0, 0), mat("LabelInk", (0.9, 0.9, 0.9), 0.6), parent=root)
    return root


make("flags_set", "venue", _flags, (("front", (0.0, 1.0, 0.2)),), 45, w=1900, h=620)
make("marshal_post", "venue", lambda: venue.build_marshal_post(), (("front34", (0.6, 1.2, 0.35)),), 45, size=80)
make("tyre_wall", "venue", lambda: venue.build_tyre_wall(), (("front34", (0.5, 1.2, 0.35)),), 45, size=80)
make("armco", "venue", lambda: venue.build_armco(), (("front34", (0.5, 1.2, 0.3)),), 45, size=80)
make("catch_fence", "venue", lambda: venue.build_catch_fence(), (("front34", (0.5, 1.2, 0.3)),), 40, size=80)
make("kerb", "venue", lambda: venue.build_kerb(), (("front34", (0.5, 1.2, 0.5)),), 40, size=80)
make("grandstand", "venue", lambda: venue.build_grandstand(), (("front34", (0.6, 1.3, 0.4)),), 40, size=120)


def _lane3():
    root = empty("PitLane3")
    venue.build_pit_lane(3, 7.0, (0, 0, 0), root)
    for i, t in enumerate(TEAMS[:3]):
        venue.build_garage(t, ((i - 1) * 7.0, -4.0, 0), 0.0, root)
    venue.build_signal_gantry(3, 7.0, (0, 5.0, 0), root)
    return root


make("pit_lane_segment", "venue", _lane3, (("front34", (0.35, 1.25, 0.45)),), 40, size=200)

# ---------------------------------------------------------------------------------------------------- scenes
LAB = lambda: mat("LabelInk", (0.9, 0.9, 0.9), 0.6)  # noqa: E731


def _team_grid():
    root = empty("TeamGrid")
    for i, t in enumerate(TEAMS):
        row, col = divmod(i, 6)
        x, y = (col - 2.5) * 3.2, -row * 7.0
        f1car.build_f1(t, t["nums"][0], (x, y, 0), 0.0, "medium", parent=root)
        text3d("Name_" + t["id"], t["name"], 0.2, (x, y - 3.4, 0.002), (0, 0, 0), LAB(), parent=root)
    return root


make("team_grid", "scenes", _team_grid, (("front34", (0.4, 1.2, 0.8)), ("top", (0.0, 0.4, 1.7))), 50, size=200, w=1920, h=900)


def _pit_lane_all():
    root = empty("PitLaneAll")
    n = len(TEAMS)
    venue.build_pit_lane(n, 7.0, (0, 0, 0), root)
    venue.build_signal_gantry(n, 7.0, (0, 5.0, 0), root)
    for i, t in enumerate(TEAMS):
        x = (i - (n - 1) / 2) * 7.0
        venue.build_garage(t, (x, -4.0, 0), 0.0, root)
        f1car.build_f1(t, t["nums"][0], (x, 2.6, 0), -math.pi / 2, "soft", parent=root)
    for s in (-1, 1):
        venue.build_speed_sign(80, (s * (n * 7.0 / 2 + 6), 9.5, 0), 0.0, root)
    return root


make("pit_lane_all_teams", "scenes", _pit_lane_all, (("front34", (0.25, 1.2, 0.6)), ("top", (0.0, 0.3, 1.8))), 40, size=400, w=1920, h=900, export=False)


def _face(fx, fy):
    return math.atan2(-fx, fy)


def _pit_stop():
    t = AUR
    world = empty("PitStopWorld")
    venue.build_pit_lane(1, 9.0, (0, 0, 0), world)
    venue.build_garage(t, (0, -4.0, 0), 0.0, world, w=8.5)
    sr = empty("PitStop", (0, 2.6, 0), (0, 0, -math.pi / 2), world)
    f1car.build_f1(t, 1, (0, 0, 0), 0.0, "medium", parent=sr)
    rub = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    band = mat("Compound_soft", COMPOUNDS["soft"], 0.6)
    for sx in (1, -1):
        for y, nm in ((1.65, "F"), (-1.70, "R")):
            gx = sx * 1.75
            g = pit.build_crew("gunner", t, (gx, y, 0), _face(-sx, 0), sr)
            pit.build_wheel_gun((0, 0.72, 0.45), 0.0, g)
            c = pit.build_crew("carrier", t, (sx * 2.7, y, 0), _face(-sx, 0), sr)
            tyre("NewTyre_%s%d" % (nm, sx > 0), 0.35, 0.3, (0, 0.5, 1.02), rub, "Y", c)
            lib.cyl("NewTyreBand_%s%d" % (nm, sx > 0), 0.325, 0.304, (0, 0.5, 1.02), band, "Y", 36, parent=c)
    pit.build_jack(True, (0, 2.9, 0), math.pi, sr)
    pit.build_crew("front_jack", t, (0, 4.1, 0), math.pi, sr)
    pit.build_jack(False, (0, -3.2, 0), 0.0, sr)
    pit.build_crew("rear_jack", t, (0, -4.4, 0), 0.0, sr)
    for sx in (1, -1):
        pit.build_crew("wing", t, (sx * 1.1, 3.1, 0), _face(-sx * 0.3, -1), sr)
        pit.build_crew("stabiliser", t, (sx * 0.9, -3.3, 0), _face(-sx * 0.2, 1), sr)
    pit.build_crew("extinguisher", t, (-4.0, 2.4, 0), _face(1, 0), sr)
    pit.build_extinguisher((-3.4, 2.7, 0.0), 0.0, sr)
    pit.build_crew("lollipop", t, (1.2, 6.2, 0), math.pi, sr)
    pit.build_pit_board("BOX", (0.95, 0.95, 0.95), (0.02, 0.02, 0.02), (1.7, 5.7, 0), math.pi, sr)
    pit.build_crew("engineer", t, (4.2, -0.5, 0), _face(-1, 0), sr)
    pit.build_tyre_stack("soft", 4, (-4.6, -1.2, 0), 0.0, sr)
    pit.build_tyre_stack("medium", 4, (-4.6, 1.2, 0), 0.0, sr)
    pit.build_tyre_trolley((4.6, 2.2, 0), math.pi / 2, sr)
    return sr


make("pit_stop_aurelia", "scenes", _pit_stop, (("front34", (0.95, 1.1, 0.55)), ("rear34", (-0.95, -1.1, 0.55)), ("top", (0.0, 0.25, 1.8))), 38, size=200, w=1920, h=1000)

with open(os.path.join(OUT, "manifest_%s.json" % GROUP), "w") as f:
    json.dump(MANIFEST, f, indent=1)
print("GROUP_DONE", GROUP, len(MANIFEST))
