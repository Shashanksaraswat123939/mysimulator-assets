"""Shared Blender helpers for My Simulator original assets. Pure data-API (bmesh), no selection-dependent operators,
so scripts run identically headless on a CI runner. Units: metres. Convention: +Y forward, +Z up, X = car/crew right.
Everything here is original geometry; no third-party meshes or textures are used."""
import math
import os
import sys
import traceback

import bmesh
import bpy
import mathutils

V = mathutils.Vector


# ---------------------------------------------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgba, rough=0.5, metal=0.0, emit=None, emit_strength=0.0, coat=0.0, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba if len(rgba) == 4 else (*rgba, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat and "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "BLENDED"
    if emit:
        b.inputs["Emission Color"].default_value = emit if len(emit) == 4 else (*emit, 1.0)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def _finish(name, bm, material, loc, rot, smooth, bevel, parent):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    if material is not None:
        me.materials.append(material)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        mod = o.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
    if parent is not None:
        o.parent = parent
    return o


def box(name, size, loc, material, rot=(0, 0, 0), bevel=0.0, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=V(size), verts=bm.verts)
    return _finish(name, bm, material, loc, rot, bevel > 0, bevel, parent)


def cyl(name, r, depth, loc, material, axis="Z", segs=28, r2=None, bevel=0.0, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    rot = {"Z": (0, 0, 0), "X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0)}[axis]
    return _finish(name, bm, material, loc, rot, True, bevel, parent)


def sphere(name, r, loc, material, scale=(1, 1, 1), parent=None, segs=24):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(8, segs // 2), radius=r)
    bmesh.ops.scale(bm, vec=V(scale), verts=bm.verts)
    return _finish(name, bm, material, loc, (0, 0, 0), True, 0.0, parent)


def rod(name, a, b, r, material, parent=None, segs=10):
    """Cylinder between two points."""
    a, b = V(a), V(b)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=d.length)
    o = _finish(name, bm, material, (a + b) / 2, (0, 0, 0), True, 0.0, parent)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def loft(name, sections, material, xoff=0.0, rr=0.5, parent=None, subsurf=1, smooth=True):
    """Rounded-rectangle rings along +Y. sections = [(y, half_width, z_bottom, z_top), ...]."""
    bm = bmesh.new()
    rings = []
    for (y, w, zb, zt) in sections:
        c = max(0.001, min(w, (zt - zb) / 2) * rr)
        pts = [(-w + c, zt), (w - c, zt), (w, zt - c), (w, zb + c), (w - c, zb), (-w + c, zb), (-w, zb + c), (-w, zt - c)]
        rings.append([bm.verts.new((xoff + x, y, z)) for (x, z) in pts])
    n = 8
    for i in range(len(rings) - 1):
        for j in range(n):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % n], rings[i + 1][(j + 1) % n], rings[i + 1][j]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _finish(name, bm, material, (0, 0, 0), (0, 0, 0), smooth, 0.0, parent)
    if subsurf:
        m = o.modifiers.new("Subsurf", "SUBSURF")
        m.levels = subsurf
        m.render_levels = subsurf
    return o


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    link(e)
    e.location = loc
    e.rotation_euler = rot
    if parent is not None:
        e.parent = parent
    return e


def text3d(name, body, size, loc, rot, material, extrude=0.004, parent=None, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    tmp = bpy.data.objects.new(name + "_c", cu)
    link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp, do_unlink=True)
    o = bpy.data.objects.new(name, me)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    me.materials.append(material)
    if parent is not None:
        o.parent = parent
    return o


def tree(root):
    out = [root]
    for c in root.children_recursive:
        out.append(c)
    return out


def hide_helpers(root):
    pass


# --------------------------------------------------------------------------------------------------------- bounds
def bounds(root):
    pts = []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in tree(root):
        if o.type == "MESH":
            ev = o.evaluated_get(dg)
            pts += [ev.matrix_world @ V(c) for c in ev.bound_box]
    if not pts:
        return V((-1, -1, 0)), V((1, 1, 1))
    mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


# ------------------------------------------------------------------------------------------------------- render
def setup_render(w=1280, h=720, samples=32):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "AgX"
    except Exception:
        pass
    return sc


def studio(root=None, floor=True, size=60.0, floor_rgba=(0.18, 0.18, 0.19, 1)):
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.32, 0.36, 0.42, 1)
    bg.inputs["Strength"].default_value = 0.9
    if floor:
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
        o = _finish("Floor", bm, mat("Floor_Studio", floor_rgba, 0.55), (0, 0, 0), (0, 0, 0), False, 0.0, None)
        return o


def light_rig(centre, r):
    for name, off, e in (("key", (1.2, -1.0, 1.1), 1300), ("fill", (-1.2, -0.7, 0.7), 420), ("rim", (0.1, 1.3, 0.9), 700)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = e * (r / 4.0) ** 2
        ld.size = max(1.0, r * 0.6)
        lo = bpy.data.objects.new(name, ld)
        link(lo)
        lo.location = V(centre) + V(off) * r
        lo.rotation_euler = (V(centre) - lo.location).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=45):
    c = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    c.data.lens = lens
    c.data.clip_end = 2000
    link(c)
    c.location = loc
    c.rotation_euler = (V(target) - V(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = c
    return c


def frame_and_render(root, path, views=(("front34", (0.9, 1.1, 0.45)),), lens=50, w=1280, h=720, samples=32, floor_size=60.0):
    setup_render(w, h, samples)
    studio(root, True, floor_size)
    mn, mx = bounds(root)
    centre = (mn + mx) / 2
    diag = (mx - mn).length
    light_rig(centre, max(2.0, diag * 0.9))
    cam = camera(centre + V((1, -1, 0.5)) * diag, centre, lens)
    outs = []
    for tag, d in views:
        dist = diag * 1.15
        cam.location = centre + V(d).normalized() * dist
        cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        p = path if len(views) == 1 else path.replace(".png", "_%s.png" % tag)
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        outs.append(p)
    return outs


# ------------------------------------------------------------------------------------------------------- export
def export_fbx(root, path):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in tree(root):
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True, global_scale=1.0,
                             axis_forward="-Z", axis_up="Y", bake_space_transform=True, path_mode="COPY", embed_textures=False)


def save_blend(path):
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)


def stats(root):
    n = 0
    tris = 0
    for o in tree(root):
        if o.type == "MESH":
            n += 1
            tris += sum(max(1, len(p.vertices) - 2) for p in o.data.polygons)
    return n, tris


def run_safely(name, fn):
    try:
        fn()
        print("ASSET_OK", name)
        return True
    except Exception:
        print("ASSET_FAIL", name)
        traceback.print_exc()
        return False


def lathe(name, profile, material, loc=(0, 0, 0), rot=(0, 0, 0), segs=40, parent=None, smooth=True):
    """Spin a closed (radius, z) profile around the Z axis (tyres, rims, bottles)."""
    bm = bmesh.new()
    n = len(profile)
    rings = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * ca, r * sa, z)) for (r, z) in profile])
    for i in range(segs):
        j = (i + 1) % segs
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((rings[i][k], rings[j][k], rings[j][k2], rings[i][k2]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, material, loc, rot, smooth, 0.0, parent)


def tyre_profile(r, w, rim_r):
    """Rounded tyre cross-section as (radius, z) points; z is the axle direction."""
    hw = w / 2
    s = min(0.05, w * 0.18)
    return [(rim_r, -hw), (r - s, -hw), (r - s * 0.3, -hw + s * 0.35), (r, -hw + s), (r, hw - s), (r - s * 0.3, hw - s * 0.35),
            (r - s, hw), (rim_r, hw)]


def tyre(name, r, w, loc, material, axis="X", parent=None, rim_frac=0.6, segs=40):
    rot = {"Z": (0, 0, 0), "X": (0, math.pi / 2, 0), "Y": (-math.pi / 2, 0, 0)}[axis]
    return lathe(name, tyre_profile(r, w, r * rim_frac), material, loc, rot, segs, parent)
