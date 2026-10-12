"""Pit crew (jointed, rig-ready) and pit equipment. Original low-poly design; joints are empties so animation can drive
rotation_euler later or an armature can be added without remodelling."""
import math

from lib import V, box, cyl, empty, lathe, mat, rod, sphere, text3d, tyre, tyre_profile
from teams import COMPOUNDS

THIGH, SHIN, HIP_Z = 0.42, 0.42, 0.91

ROLES = {
    # role: (helmet colour, pose)
    "front_jack": ((0.95, 0.95, 0.95), "jack"),
    "rear_jack": ((0.95, 0.95, 0.95), "jack"),
    "gunner": ((0.95, 0.75, 0.05), "gun"),
    "carrier": ((0.9, 0.35, 0.05), "carry"),
    "wing": ((0.2, 0.6, 0.9), "wing"),
    "stabiliser": ((0.5, 0.5, 0.55), "stand"),
    "extinguisher": ((0.85, 0.05, 0.05), "stand"),
    "lollipop": ((0.1, 0.8, 0.2), "lollipop"),
    "engineer": ((0.1, 0.1, 0.12), "stand"),
}

POSES = {
    #          shoulder_l, elbow_l, shoulder_r, elbow_r, hip, knee
    "stand": (0.12, 0.25, 0.12, 0.25, 0.0, 0.0),
    "gun": (1.25, 0.35, 1.25, 0.35, 1.25, -1.95),
    "carry": (1.15, 0.7, 1.15, 0.7, 0.15, -0.1),
    "jack": (0.95, 0.5, 0.95, 0.5, 0.35, -0.5),
    "wing": (0.9, 0.3, 0.9, 0.3, 0.9, -1.3),
    "lollipop": (0.3, 0.2, 2.7, 0.2, 0.0, 0.0),
}


def _ground_drop(hip, knee):
    return HIP_Z - THIGH * math.cos(hip) - (SHIN + 0.07) * math.cos(hip + knee) - (HIP_Z - THIGH - SHIN - 0.07)


def build_crew(role, team, loc=(0, 0, 0), rot_z=0.0, parent=None, pose=None):
    helmet_col, default_pose = ROLES[role]
    pose = pose or default_pose
    shl, elbl, shr, elbr, hip, knee = POSES[pose]
    root = empty("Crew_%s_%s" % (role, team["id"]), loc, (0, 0, rot_z), parent)
    suit = mat("CrewSuit_" + team["id"], team["a"], 0.75)
    trim = mat("CrewTrim_" + team["id"], team["b"], 0.6)
    glove = mat("CrewGlove", (0.04, 0.04, 0.045), 0.85)
    boot = mat("CrewBoot", (0.02, 0.02, 0.02), 0.8)
    helm = mat("CrewHelmet_" + role, helmet_col, 0.2, 0.0, coat=1.0)
    visor = mat("CrewVisor", (0.01, 0.015, 0.02), 0.05, 0.5)
    drop = _ground_drop(hip, knee)
    body = empty("Body", (0, 0, -drop), (0, 0, 0), root)
    box("Hips", (0.36, 0.22, 0.2), (0, 0, HIP_Z + 0.04), suit, bevel=0.03, parent=body)
    box("Torso", (0.42, 0.24, 0.55), (0, 0, 1.27), suit, bevel=0.05, parent=body)
    box("Chest_Trim", (0.43, 0.25, 0.07), (0, 0, 1.36), trim, parent=body)
    box("Back_Panel", (0.3, 0.02, 0.28), (0, -0.125, 1.25), trim, parent=body)
    cyl("Neck", 0.06, 0.08, (0, 0, 1.58), suit, "Z", 12, parent=body)
    sphere("Helmet", 0.14, (0, 0, 1.74), helm, (1, 1.1, 1.05), body)
    box("Visor", (0.2, 0.08, 0.075), (0, 0.125, 1.75), visor, bevel=0.01, parent=body)
    for s, nm, sh, el in ((1, "L", shl, elbl), (-1, "R", shr, elbr)):
        hipj = empty("Hip_" + nm, (s * 0.1, 0, HIP_Z), (hip, 0, 0), body)
        box("Thigh_" + nm, (0.16, 0.18, THIGH), (0, 0, -THIGH / 2), suit, bevel=0.03, parent=hipj)
        knj = empty("Knee_" + nm, (0, 0, -THIGH), (knee, 0, 0), hipj)
        box("Shin_" + nm, (0.14, 0.16, SHIN), (0, 0, -SHIN / 2), suit, bevel=0.03, parent=knj)
        box("Boot_" + nm, (0.14, 0.28, 0.12), (0, 0.06, -SHIN - 0.01), boot, bevel=0.02, parent=knj)
        shj = empty("Shoulder_" + nm, (s * 0.3, 0, 1.46), (sh, 0, 0), body)
        box("UpperArm_" + nm, (0.12, 0.14, 0.3), (0, 0, -0.15), suit, bevel=0.025, parent=shj)
        elj = empty("Elbow_" + nm, (0, 0, -0.3), (el, 0, 0), shj)
        box("Forearm_" + nm, (0.1, 0.12, 0.27), (0, 0, -0.135), suit, bevel=0.02, parent=elj)
        box("Glove_" + nm, (0.105, 0.125, 0.1), (0, 0, -0.32), glove, bevel=0.02, parent=elj)
    if role == "engineer":
        box("Headset", (0.34, 0.04, 0.04), (0, 0, 1.84), glove, parent=body)
    return root


# ----------------------------------------------------------------------------------------------------- equipment
def build_jack(front=True, loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("Jack_" + ("Front" if front else "Rear"), loc, (0, 0, rot_z), parent)
    frame = mat("Jack_Frame", (0.9, 0.78, 0.04), 0.45, 0.3)
    metal = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    rubber = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    red = mat("Jack_Handle", (0.8, 0.04, 0.04), 0.5)
    box("Base", (0.7, 0.9, 0.07), (0, 0, 0.1), frame, bevel=0.02, parent=root)
    box("Column", (0.14, 0.14, 0.7), (0, -0.25, 0.48), frame, bevel=0.02, parent=root)
    arm = empty("LiftArm", (0, -0.25, 0.8), (0, 0, 0), root)
    box("Arm", (0.1, 1.0, 0.08), (0, 0.45, 0), frame, bevel=0.015, parent=arm)
    cyl("Pad", 0.06, 0.04, (0, 0.95, 0.06), rubber, "Z", 16, parent=arm)
    handle = empty("Handle", (0, -0.3, 0.7), (-0.5, 0, 0), root)
    rod("HandleBar", (0, 0, 0), (0, -1.2, 0.35), 0.022, red, handle)
    for x in (-0.3, 0.3):
        for y in (-0.35, 0.35):
            cyl("Castor", 0.05, 0.05, (x, y, 0.05), rubber, "X", 14, parent=root)
    return root


def build_wheel_gun(loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("WheelGun", loc, (0, 0, rot_z), parent)
    body = mat("Gun_Body", (0.8, 0.1, 0.05), 0.4, 0.2)
    metal = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    grip = mat("Gun_Grip", (0.02, 0.02, 0.02), 0.8)
    cyl("Barrel", 0.075, 0.32, (0, 0.18, 0), body, "Y", 20, bevel=0.01, parent=root)
    cyl("Socket", 0.048, 0.12, (0, 0.4, 0), metal, "Y", 6, parent=root)
    box("Handle", (0.06, 0.08, 0.22), (0, 0.02, -0.15), grip, bevel=0.015, parent=root)
    box("Trigger", (0.02, 0.03, 0.06), (0, 0.08, -0.07), metal, parent=root)
    rod("Hose_0", (0, -0.12, -0.05), (0, -0.4, -0.2), 0.018, grip, root)
    rod("Hose_1", (0, -0.4, -0.2), (0, -0.8, -0.35), 0.018, grip, root)
    return root


def build_tyre_stack(compound="medium", count=4, loc=(0, 0, 0), rot_z=0.0, parent=None, blanket=True):
    root = empty("TyreStack_" + compound, loc, (0, 0, rot_z), parent)
    rub = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    band = mat("Compound_" + compound, COMPOUNDS[compound], 0.6)
    rim = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    blank = mat("Blanket", (0.08, 0.08, 0.09), 0.9)
    for i in range(count):
        z = 0.15 + i * 0.31
        tyre("Tyre_%d" % i, 0.35, 0.3, (0, 0, z), rub, "Z", root)
        cyl("Band_%d" % i, 0.325, 0.304, (0, 0, z), band, "Z", 36, parent=root)
        cyl("Rim_%d" % i, 0.21, 0.31, (0, 0, z), rim, "Z", 28, parent=root)
        if blanket:
            cyl("Blanket_%d" % i, 0.36, 0.05, (0, 0, z + 0.16), blank, "Z", 36, parent=root)
    return root


def build_tyre_trolley(loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("TyreTrolley", loc, (0, 0, rot_z), parent)
    steel = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    rub = mat("Rubber", (0.012, 0.012, 0.012), 0.9)
    box("Deck", (0.8, 0.9, 0.04), (0, 0, 0.18), steel, bevel=0.01, parent=root)
    for x in (-0.4, 0.4):
        rod("Rail_%d" % (x > 0), (x, -0.45, 0.2), (x, -0.45, 1.0), 0.015, steel, root)
        rod("Rail2_%d" % (x > 0), (x, -0.45, 1.0), (x, -0.75, 1.0), 0.015, steel, root)
        for y in (-0.38, 0.38):
            cyl("Castor", 0.07, 0.04, (x, y, 0.07), rub, "X", 14, parent=root)
    return root


def build_pit_board(text="BOX", board=(0.9, 0.9, 0.9), ink=(0.02, 0.02, 0.02), loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("PitBoard_" + text, loc, (0, 0, rot_z), parent)
    pole = mat("Pole", (0.12, 0.12, 0.14), 0.4, 0.8)
    face = mat("Board_" + text, board, 0.6)
    txt = mat("BoardInk_" + text, ink, 0.6)
    rod("Pole", (0, 0, 0), (0, 0, 1.9), 0.014, pole, root)
    box("Face", (0.6, 0.02, 0.45), (0, 0, 1.95), face, bevel=0.005, parent=root)
    text3d("Text", text, 0.2, (0, 0.016, 1.95), (math.pi / 2, 0, 0), txt, parent=root)
    return root


def build_tool_trolley(loc=(0, 0, 0), rot_z=0.0, parent=None, team=None):
    root = empty("ToolTrolley", loc, (0, 0, rot_z), parent)
    col = mat("Trolley_" + (team["id"] if team else "x"), team["a"] if team else (0.5, 0.05, 0.05), 0.4, 0.2)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    steel = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    box("Cabinet", (0.7, 0.5, 0.8), (0, 0, 0.55), col, bevel=0.015, parent=root)
    for i in range(4):
        box("Drawer_%d" % i, (0.62, 0.01, 0.15), (0, 0.255, 0.3 + i * 0.18), dark, parent=root)
        box("DrawerHandle_%d" % i, (0.3, 0.02, 0.015), (0, 0.265, 0.34 + i * 0.18), steel, parent=root)
    box("Top", (0.74, 0.54, 0.03), (0, 0, 0.97), steel, parent=root)
    for x in (-0.3, 0.3):
        cyl("Castor", 0.06, 0.04, (x, 0, 0.06), dark, "X", 12, parent=root)
    return root


def build_extinguisher(loc=(0, 0, 0), rot_z=0.0, parent=None):
    root = empty("Extinguisher", loc, (0, 0, rot_z), parent)
    red = mat("ExtRed", (0.8, 0.03, 0.03), 0.4, 0.2)
    metal = mat("Metal", (0.6, 0.6, 0.62), 0.3, 1.0)
    dark = mat("Dark", (0.01, 0.01, 0.012), 0.6)
    cyl("Tank", 0.09, 0.5, (0, 0, 0.3), red, "Z", 20, bevel=0.01, parent=root)
    cyl("Neck", 0.03, 0.08, (0, 0, 0.58), metal, "Z", 12, parent=root)
    box("Lever", (0.03, 0.14, 0.02), (0, 0.04, 0.63), metal, parent=root)
    rod("Hose", (0, 0.06, 0.58), (0.1, 0.25, 0.4), 0.014, dark, root)
    return root
