#!/usr/bin/env python3
"""
Agent controller rev 2 -- concept model + renders (dock + detachable controller bar).

NOT print-ready: shells are simple and component sizes come from datasheets /
listings. Purpose: show where everything goes. Print CAD comes after caliper
measurements.

Coordinates (mm): x left(-)/right(+) centred on the dock, y 0 = dock front edge,
increasing toward the back, z 0 = desk.
"""
import math
import os

import cadquery as cq
import numpy as np
import trimesh

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ----------------------------------------------------------------------------- dims
# dock
BW, BD, BH = 124.0, 112.0, 20.0          # base
WALL = 2.0
TRAY_Y1 = 36.0                            # controller tray depth (open at front)
LID_D, LID_T = 82.0, 10.0                  # display lid
LID_Y0 = BD - LID_D                       # 30
OPEN_DEG = 105.0
# controller bar
CL, CW, CH = 100.0, 34.0, 18.0
CX0, CY0, CZ0 = -CL / 2, 1.0, 2.0         # docked position of the bar's local origin
KEY_X = (14.0, 33.0, 52.0)                # key centres along the bar
STICK_X = 82.0


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r):
    b = box(x0, x1, y0, y1, z0, z1)
    return b.edges("|Z").fillet(r) if r > 0 else b


def cyl_z(x, y, z0, z1, r):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def cyl_y(x, y0, y1, z, r):
    return cq.Workplane("XZ").workplane(offset=-y0).center(x, z).circle(r).extrude(-(y1 - y0))


def cyl_x(x0, x1, y, z, r):
    return cq.Workplane("YZ").workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


def soft(wp, r, sel=">Z"):
    try:
        return wp.faces(sel).edges().fillet(r)
    except Exception:  # noqa: BLE001
        return wp


# ----------------------------------------------------------------------------- dock parts
def dock_parts():
    P = {}
    # floor plate
    P["dock_floor"] = rbox(-BW / 2, BW / 2, 0, BD, 0, 2.0, 6)
    # upper shell: hollow body, open-front tray, ribbed grille, USB slot
    up = rbox(-BW / 2, BW / 2, 0, BD, 2.0, BH, 6)
    up = soft(up, 1.2)
    up = up.cut(rbox(-BW / 2 + WALL, BW / 2 - WALL, TRAY_Y1 + 2, BD - WALL, 2.0 - 0.1, BH - 2.0, 4))
    up = up.cut(box(-(CL / 2 + 1.0), CL / 2 + 1.0, -1, TRAY_Y1, 2.0, BH + 1))      # tray
    for i in range(22):                                                         # ribbed grille
        x = -22 + i * 3.6
        up = up.cut(box(x, x + 1.6, 54, 104, BH - 2.5, BH + 1))
    up = up.cut(box(-42.5, -33.5, BD - 3, BD + 1, 11.0, 15.0))                  # USB-C (native)
    # hinge knuckles on the base
    up = up.cut(cyl_x(-45, 45, BD, BH, 4.5))                                   # room for lid knuckle
    for x0, x1 in ((-60, -46), (46, 60)):
        up = up.union(cyl_x(x0, x1, BD, BH, 4.0))
    up = up.cut(box(15.5, 31.5, TRAY_Y1 - 1, TRAY_Y1 + 3, 6.5, 13.5))            # pogo female window
    for mx in (-35.0, 42.0):
        up = up.cut(cyl_y(mx, TRAY_Y1 - 1, TRAY_Y1 + 3, 10.0, 3.15))            # magnet pockets
    P["dock_shell"] = up
    # pogo female + magnets in the tray back wall
    P["pogo_female"] = box(16.0, 31.0, TRAY_Y1 - 0.2, TRAY_Y1 + 6, 7.0, 13.0)
    P["dock_magnet_L"] = cyl_y(-35.0, TRAY_Y1 - 0.2, TRAY_Y1 + 2, 10.0, 3.0)
    P["dock_magnet_R"] = cyl_y(42.0, TRAY_Y1 - 0.2, TRAY_Y1 + 2, 10.0, 3.0)
    # electronics
    P["esp32_devkit"] = box(-51, -25, 40, 109, 10.5, 12.1).union(box(-46, -30, 55, 80, 12.1, 15.3)) \
        .union(box(-42, -34, 103, 109.5, 12.1, 15.3))
    P["speaker"] = cyl_z(2.0, 80.0, BH - 2.0 - 5.4, BH - 2.05, 20.0)
    P["amp"] = box(30, 47.8, 45, 64.3, 2.0, 13.0)
    # hinge knuckles on the lid + lid parts (closed position)
    z0 = BH
    bezel = rbox(-BW / 2, BW / 2, LID_Y0, BD, z0, z0 + 2.0, 6)
    bezel = bezel.cut(box(-42.2, 42.2, 71 - 28.2, 71 + 28.2, z0 - 1, z0 + 3))
    bezel = bezel.cut(cyl_x(-45, 45, BD, BH, 4.05))
    for x0, x1 in ((-61, -45.5), (45.5, 61)):
        bezel = bezel.cut(cyl_x(x0, x1, BD, BH, 4.5))
    P["lid_bezel"] = bezel
    back = rbox(-BW / 2, BW / 2, LID_Y0, BD, z0 + 2.0, z0 + LID_T, 6)
    back = soft(back, 1.5)
    back = back.cut(rbox(-BW / 2 + 2, BW / 2 - 2, LID_Y0 + 2, BD - 2, z0 + 1.9, z0 + LID_T - 2, 4))
    for x0, x1 in ((-61, -45.5), (45.5, 61)):
        back = back.cut(cyl_x(x0, x1, BD, BH, 4.5))
    back = back.union(cyl_x(-44, 44, BD, BH, 4.0)).cut(box(-45, 45, BD - 5, BD + 5, BH - 5, BH + 2.0))
    P["lid_back"] = back
    P["display"] = box(-54, 54, 71 - 30.4, 71 + 30.4, z0 + 2.0, z0 + 2.0 + 5.45)
    P["screen"] = box(-41.9, 41.9, 71 - 28, 71 + 28, z0 + 1.9, z0 + 2.0)
    P["dock_led"] = box(52, 58, 34, 40, z0 + 2.0, z0 + 3.6)
    return P


# ----------------------------------------------------------------------------- controller parts (local)
def controller_parts():
    P = {}
    split = 9.0
    body = rbox(0, CL, 0, CW, 0, CH, 5)
    body = soft(body, 1.0)
    inner = rbox(1.6, CL - 1.6, 1.6, CW - 1.6, 1.5, CH - 2.0, 3.5)
    shell = body.cut(inner)
    # key windows, stick recess, LED hole, mic grilles, ports
    for kx in KEY_X:
        shell = shell.cut(rbox(kx - 9.2, kx + 9.2, 17 - 8.7, 17 + 8.7, CH - 3, CH + 1, 1.2))
    shell = shell.cut(cyl_z(STICK_X, 17.0, CH - 2.2, CH + 1, 14.0))
    shell = shell.cut(cyl_z(STICK_X, 17.0, CH - 4, CH + 1, 6.0))
    shell = shell.cut(cyl_z(92.0, 29.5, CH - 3, CH + 1, 1.2))
    for yc in (10.0, 24.0):
        for dy in (-2.4, 0, 2.4):
            for dz in (-2.4, 0, 2.4):
                shell = shell.cut(cyl_x(CL - 3, CL + 1, yc + dy, 9.0 + dz, 0.6))
    shell = shell.cut(box(-1, 3, 12.5, 21.5, 1.4, 5.5))       # XIAO USB-C (flashing)
    shell = shell.cut(box(65.5, 81.5, CW - 3, CW + 1, 5.5, 12.5))  # pogo male window
    for mx in (15.0, 92.0):
        shell = shell.cut(cyl_y(mx, CW - 3, CW + 1, 10.0, 3.15))   # magnet pockets
    shell = shell.cut(box(5.5, 10.5, -1, 3, 8.0, 10.0))       # slide switch slot (front face)
    P["ctrl_bottom"] = shell.intersect(box(-5, CL + 5, -5, CW + 5, -1, split))
    P["ctrl_top"] = shell.intersect(box(-5, CL + 5, -5, CW + 5, split, CH + 5))
    # inside
    P["xiao"] = box(2.0, 23.0, 8.25, 25.75, 1.5, 3.0).union(box(5, 20, 10, 24, 3.0, 4.6)) \
        .union(box(0.8, 8.0, 12.9, 21.1, 1.6, 4.8))
    P["battery"] = box(24.0, 64.0, 2.0, 32.0, 1.5, 9.5)
    P["tp4056"] = box(67.0, 95.0, 8.5, 25.5, 1.5, 3.0).union(box(75, 81, 14, 20, 3.0, 4.2))
    P["stick"] = box(STICK_X - 8.5, STICK_X + 8.5, 17 - 8.5, 17 + 8.5, 6.0, 12.5) \
        .union(cyl_z(STICK_X, 17.0, 12.5, 14.5, 6.5)).union(cyl_z(STICK_X, 17.0, 14.5, CH - 1.6, 2.0))
    P["stick_cap"] = soft(cyl_z(STICK_X, 17.0, CH - 1.6, CH + 0.4, 11.0), 0.8)
    for i, kx in enumerate(KEY_X):
        P[f"switch{i+1}"] = box(kx - 7.5, kx + 7.5, 17 - 7.5, 17 + 7.5, 11.8, CH - 0.5)
        P[f"keycap{i+1}"] = soft(rbox(kx - 8.75, kx + 8.75, 17 - 8.25, 17 + 8.25, CH - 0.5, CH + 1.8, 1.5), 0.6)
    for i, yc in enumerate((10.0, 24.0)):
        P[f"mic{i+1}"] = cyl_x(CL - 3.4, CL - 1.8, yc, 9.0, 6.5)
    P["ctrl_led"] = box(88.0, 96.0, 25.5, 32.0, CH - 4.0, CH - 2.3)
    P["slide_switch"] = box(3.6, 12.4, 1.6, 5.4, 7.2, 10.8)
    P["pogo_male"] = box(66.0, 81.0, CW - 6.0, CW + 0.3, 6.0, 12.0)
    P["ctrl_magnet_L"] = cyl_y(15.0 - 0.0, CW - 2.0, CW + 0.2, 10.0, 3.0)
    P["ctrl_magnet_R"] = cyl_y(92.0, CW - 2.0, CW + 0.2, 10.0, 3.0)
    return P


# ----------------------------------------------------------------------------- mesh helpers
def mesh(wp, tol=0.08):
    path = os.path.join(OUT, "_t.stl")
    cq.exporters.export(wp, path, tolerance=tol, angularTolerance=0.2)
    m = trimesh.load(path)
    os.remove(path)
    return m


def T(m, M):
    c = m.copy()
    c.apply_transform(M)
    return c


def tr(dx=0, dy=0, dz=0):
    return trimesh.transformations.translation_matrix([dx, dy, dz])


def rot_z(deg, about=(0, 0, 0)):
    return trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1], about)


def lid_open(deg=OPEN_DEG):
    return trimesh.transformations.rotation_matrix(-math.radians(deg), [1, 0, 0], [0, BD, BH])


COL = {
    "shell": (0.95, 0.95, 0.93), "floor": (0.84, 0.84, 0.82), "bezel": (0.13, 0.13, 0.15),
    "screen": (0.04, 0.06, 0.11), "keycap": (0.98, 0.97, 0.94), "cap": (0.95, 0.95, 0.93),
    "esp": (0.10, 0.10, 0.12), "xiao": (0.20, 0.45, 0.30), "battery": (0.86, 0.72, 0.30),
    "speaker": (0.22, 0.22, 0.24), "amp": (0.45, 0.28, 0.66), "tp": (0.18, 0.38, 0.78),
    "stick": (0.30, 0.30, 0.33), "switch": (0.80, 0.16, 0.20), "mic": (0.10, 0.55, 0.30),
    "led": (0.20, 0.95, 0.45), "pogo": (0.85, 0.66, 0.20), "magnet": (0.55, 0.57, 0.60),
    "slide": (0.95, 0.95, 0.95), "display": (0.15, 0.30, 0.62),
}
DOCK_COL = {"dock_floor": "floor", "dock_shell": "shell", "pogo_female": "pogo", "dock_magnet_L": "magnet",
            "dock_magnet_R": "magnet", "esp32_devkit": "esp", "speaker": "speaker", "amp": "amp",
            "lid_bezel": "bezel", "lid_back": "shell", "display": "display", "screen": "screen", "dock_led": "led"}
CTRL_COL = {"ctrl_bottom": "floor", "ctrl_top": "shell", "xiao": "xiao", "battery": "battery", "tp4056": "tp",
            "stick": "stick", "stick_cap": "cap", "ctrl_led": "led", "slide_switch": "slide", "pogo_male": "pogo",
            "ctrl_magnet_L": "magnet", "ctrl_magnet_R": "magnet", "mic1": "mic", "mic2": "mic"}
for i in (1, 2, 3):
    CTRL_COL[f"switch{i}"] = "switch"
    CTRL_COL[f"keycap{i}"] = "keycap"
LID = {"lid_bezel", "lid_back", "display", "screen", "dock_led"}


# ----------------------------------------------------------------------------- rendering
def _poly(m):
    import vtk
    from vtk.util import numpy_support as ns
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.asarray(m.vertices, dtype=np.float64), deep=True))
    f = np.asarray(m.faces, dtype=np.int64)
    cells = np.hstack([np.full((len(f), 1), 3, dtype=np.int64), f]).ravel()
    ca = vtk.vtkCellArray()
    ca.SetCells(len(f), ns.numpy_to_vtkIdTypeArray(cells, deep=True))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(ca)
    return pd


def render(items, cam, focal, path, size=(1600, 1100), zoom=1.0, labels=None, title=None, view_up=(0, 0, 1),
           margin=0):
    """items: list of (mesh, rgb[, opacity]). labels: list of (text, world_xyz)."""
    import vtk
    from PIL import Image, ImageDraw, ImageFont
    W, H = size
    RW, RH = W - 2 * margin, H - (80 if margin else 0)
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(RW, RH)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    for it in items:
        m, rgb = it[0], it[1]
        op = it[2] if len(it) > 2 else 1.0
        pd = _poly(m)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(32)
        nrm.SplittingOn()
        nrm.Update()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        ac = vtk.vtkActor()
        ac.SetMapper(mp)
        pr = ac.GetProperty()
        pr.SetColor(*rgb)
        pr.SetOpacity(op)
        pr.SetAmbient(0.40)
        pr.SetDiffuse(0.62)
        pr.SetSpecular(0.18)
        pr.SetSpecularPower(25)
        ren.AddActor(ac)
        if op >= 1.0:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputData(pd)
            fe.BoundaryEdgesOff()
            fe.ManifoldEdgesOff()
            fe.NonManifoldEdgesOff()
            fe.FeatureEdgesOn()
            fe.SetFeatureAngle(35)
            em = vtk.vtkPolyDataMapper()
            em.SetInputConnection(fe.GetOutputPort())
            em.ScalarVisibilityOff()
            ea = vtk.vtkActor()
            ea.SetMapper(em)
            ea.GetProperty().SetColor(0.15, 0.15, 0.15)
            ea.GetProperty().SetLineWidth(1.1)
            ea.GetProperty().SetOpacity(0.45)
            ren.AddActor(ea)
    c = ren.GetActiveCamera()
    c.SetPosition(*cam)
    c.SetFocalPoint(*focal)
    c.SetViewUp(*view_up)
    ren.ResetCamera()
    c.Zoom(zoom)
    lt = vtk.vtkLight()
    lt.SetLightTypeToSceneLight()
    lt.SetPosition(-250, -300, 450)
    lt.SetFocalPoint(0, 50, 0)
    lt.SetIntensity(0.45)
    ren.AddLight(lt)
    rw.Render()
    proj = []
    if labels:
        co = vtk.vtkCoordinate()
        co.SetCoordinateSystemToWorld()
        for text, p in labels:
            co.SetValue(*p)
            x, y = co.GetComputedDoubleDisplayValue(ren)
            proj.append((text, x + margin, (RH - y) + (H - RH)))
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    from vtk.util import numpy_support as ns
    img = w2i.GetOutput()
    arr = ns.vtk_to_numpy(img.GetPointData().GetScalars()).reshape(RH, RW, -1)[::-1]
    im3 = Image.fromarray(arr[:, :, :3].astype("uint8"))
    im = Image.new("RGB", (W, H), "white")
    im.paste(im3, (margin, H - RH))
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        tfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:  # noqa: BLE001
        font = tfont = ImageFont.load_default()
    if title:
        d.text((30, 22), title, fill=(30, 30, 30), font=tfont)
    if proj:
        cx = W / 2
        left = sorted([p for p in proj if p[1] < cx], key=lambda t: t[2])
        right = sorted([p for p in proj if p[1] >= cx], key=lambda t: t[2])
        for side, group in (("L", left), ("R", right)):
            if not group:
                continue
            top, bot = 90, H - 40
            n = len(group)
            ys = [p[2] for p in group]
            # spread labels: keep order, enforce min gap
            gap = 34
            pos = []
            for y in ys:
                y = max(top, y)
                if pos and y - pos[-1] < gap:
                    y = pos[-1] + gap
                pos.append(y)
            over = pos[-1] - bot
            if over > 0:
                pos = [p - over for p in pos]
                for i in range(1, n):
                    if pos[i] - pos[i - 1] < gap:
                        pos[i] = pos[i - 1] + gap
            for (text, ax, ay), ly in zip(group, pos):
                tw = d.textlength(text, font=font)
                if side == "L":
                    lx = 24
                    ex = lx + tw + 10
                else:
                    lx = W - 24 - tw
                    ex = lx - 10
                d.line([(ex, ly + 12), (ax, ay)], fill=(90, 90, 90), width=2)
                d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(40, 40, 40))
                d.text((lx, ly), text, fill=(25, 25, 25), font=font)
    im.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("building ...")
    dock = {k: mesh(v) for k, v in dock_parts().items()}
    ctrl = {k: mesh(v) for k, v in controller_parts().items()}
    dockedM = tr(CX0, CY0, CZ0)

    def col(k, table):
        return COL[table[k]]

    # ---------- overlap check (docked, lid closed)
    import manifold3d as mf

    def mf_of(m):
        return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, dtype=np.float32),
                                   tri_verts=np.asarray(m.faces, dtype=np.uint32)))
    allp = {**{f"D:{k}": v for k, v in dock.items()}, **{f"C:{k}": T(v, dockedM) for k, v in ctrl.items()}}
    M = {k: mf_of(v) for k, v in allp.items()}
    keys = list(M)
    hits = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            v = (M[keys[i]] ^ M[keys[j]]).volume()
            if v > 0.5:
                hits.append((keys[i], keys[j], round(v, 1)))
    report = ["OVERLAPS (closed, docked) -- expected: screen/bezel only"] + \
             [f"  {a} x {b}: {v} mm3" for a, b, v in hits]
    print("\n".join(report))
    with open(os.path.join(OUT, "overlaps.txt"), "w") as fh:
        fh.write("\n".join(report) + "\n")

    # ---------- views
    def dock_items(open_deg=OPEN_DEG, skip=()):
        out = []
        for k, m in dock.items():
            if k in skip:
                continue
            mm = T(m, lid_open(open_deg)) if k in LID else m
            out.append((mm, col(k, DOCK_COL)))
        return out

    def ctrl_items(M, skip=()):
        return [(T(m, M), col(k, CTRL_COL)) for k, m in ctrl.items() if k not in skip]

    hidden_inside_dock = ("esp32_devkit", "speaker", "amp", "display")
    hidden_inside_ctrl = ("xiao", "battery", "tp4056", "stick", "mic1", "mic2", "ctrl_led", "slide_switch",
                          "pogo_male", "ctrl_magnet_L", "ctrl_magnet_R", "switch1", "switch2", "switch3")
    f = (0, 50, 25)
    print("rendering ...")
    # 1. docked, open
    items = dock_items(skip=hidden_inside_dock) + ctrl_items(dockedM, skip=hidden_inside_ctrl)
    render(items, (-190, -260, 230), f, os.path.join(OUT, "1_docked_open.png"), zoom=1.05,
           title="Docked, screen open (~124 x 112 mm footprint)")
    # 2. controller off the dock (lifted forward, turned so the stick is under the right thumb)
    liftM = tr(CX0 + 10, -70, 0) @ trimesh.transformations.rotation_matrix(math.radians(-28), [0, 0, 1], [CL / 2, CW / 2, 0])
    items = dock_items(skip=hidden_inside_dock) + ctrl_items(liftM, skip=hidden_inside_ctrl)
    render(items, (-170, -330, 260), (0, 20, 15), os.path.join(OUT, "2_controller_off_dock.png"), zoom=1.0,
           title="Controller lifted off: dock tray with pogo + magnets visible")
    # 3. closed
    items = dock_items(open_deg=0, skip=hidden_inside_dock) + ctrl_items(dockedM, skip=hidden_inside_ctrl)
    render(items, (-200, -260, 180), (0, 56, 14), os.path.join(OUT, "3_closed.png"), zoom=1.1,
           title="Closed (~124 x 112 x 30 mm)")

    # 4. exploded dock (labelled) -- vertical stack, lid closed
    def anc(m, where="top"):
        lo, hi = m.bounds
        c = (lo + hi) / 2
        if where == "top":
            return (c[0], c[1], hi[2])
        if where == "front":
            return (c[0], lo[1], c[2])
        return tuple(c)
    ex = {
        "dock_floor": tr(0, 0, -40), "dock_shell": tr(0, 0, 70),
        "esp32_devkit": tr(0, 0, 0), "speaker": tr(0, 0, 28), "amp": tr(0, 0, 0),
        "pogo_female": tr(0, -18, 0), "dock_magnet_L": tr(0, -18, 0), "dock_magnet_R": tr(0, -18, 0),
        "lid_bezel": tr(0, 0, 104), "screen": tr(0, 0, 104), "dock_led": tr(0, 0, 116),
        "display": tr(0, 0, 128), "lid_back": tr(0, 0, 156),
    }
    DM = {k: T(m, ex[k]) for k, m in dock.items()}
    items = [(DM[k], col(k, DOCK_COL)) for k in DM]
    lab = [
        ("Lid back (fold-flat hinge at rear)", anc(DM["lid_back"])),
        ('4" ST7796 display + touch', anc(DM["display"])),
        ("Status LED (WS2812B)", anc(DM["dock_led"])),
        ("Bezel + screen window", anc(DM["lid_bezel"], "front")),
        ("Top shell: ribbed speaker grille", (30, 80, BH + 70)),
        ("Controller tray (open front)", (0, TRAY_Y1, 2 + 70 + 9)),
        ("40 mm 4 ohm 2 W speaker", anc(DM["speaker"])),
        ("MAX98357A amp", anc(DM["amp"])),
        ("ESP32-S3 N16R8 DevKitC", anc(DM["esp32_devkit"])),
        ("Native USB-C out the back (to Mac)", (-38, 109.5, 13.7)),
        ("Pogo female (5 V to controller)", anc(DM["pogo_female"], "front")),
        ("2x magnets (hold controller)", anc(DM["dock_magnet_L"], "front")),
        ("Floor plate (M2 screws)", (-30, 25, -38)),
    ]
    render(items, (-250, -330, 230), (0, 56, 40), os.path.join(OUT, "4_exploded_dock.png"), size=(1900, 1650),
           zoom=1.1, labels=lab, title="Dock, exploded", margin=330)

    # 5. exploded controller (labelled), larger scale, local coords
    exc = {
        "ctrl_bottom": tr(0, 0, -22), "ctrl_top": tr(0, 0, 34),
        "xiao": tr(0, 0, -6), "battery": tr(0, 0, 0), "tp4056": tr(0, 0, -6),
        "stick": tr(0, 0, 8), "stick_cap": tr(0, 0, 46),
        "mic1": tr(16, 0, 0), "mic2": tr(16, 0, 0), "ctrl_led": tr(0, 0, 62), "slide_switch": tr(0, -14, 0),
        "pogo_male": tr(48, 16, -4), "ctrl_magnet_L": tr(0, 14, 0), "ctrl_magnet_R": tr(0, 14, 0),
    }
    for i in (1, 2, 3):
        exc[f"switch{i}"] = tr(0, 0, 14)
        exc[f"keycap{i}"] = tr(0, 0, 40)
    CM = {k: T(m, exc.get(k, np.eye(4))) for k, m in ctrl.items()}
    items = [(CM[k], col(k, CTRL_COL)) for k in CM]
    lab = [
        ("Top cover: key windows, stick recess, LED hole", (8, 17, CH + 34)),
        ("3x MBK keycaps", anc(CM["keycap1"])),
        ("Choc V1 switches: Cancel / Voice / Send", anc(CM["switch2"], "front")),
        ("Flat printed stick cap", anc(CM["stick_cap"])),
        ("Joy-Con style stick (Adafruit 5628)", anc(CM["stick"], "front")),
        ("Status LED (WS2812B)", anc(CM["ctrl_led"])),
        ("2x INMP441 mics on the end face", anc(CM["mic2"])),
        ("TP4056 charger", anc(CM["tp4056"], "front")),
        ("Pogo male (charging pins)", anc(CM["pogo_male"])),
        ("Magnets", anc(CM["ctrl_magnet_L"])),
        ("1000 mAh LiPo 803040", anc(CM["battery"], "front")),
        ("XIAO ESP32S3 (USB-C on the end)", anc(CM["xiao"], "front")),
        ("Slide power switch", anc(CM["slide_switch"], "front")),
        ("Bottom shell", (60, 0, -18)),
    ]
    render(items, (-120, -170, 150), (CL / 2, CW / 2, 10), os.path.join(OUT, "5_exploded_controller.png"),
           size=(1900, 1300), zoom=1.15, labels=lab, title="Controller bar, exploded (100 x 34 x 18 mm)",
           margin=360)

    # 6. controller x-ray top view
    see = lambda k: k.startswith("keycap") or k.startswith("switch")  # noqa: E731
    items = [(T(m, np.eye(4)), col(k, CTRL_COL)) for k, m in ctrl.items()
             if k not in ("ctrl_top", "stick_cap") and not see(k)]
    items += [(ctrl[k], col(k, CTRL_COL), 0.28) for k in ctrl if k.startswith("switch")]
    items += [(T(ctrl["ctrl_top"], np.eye(4)), COL["shell"], 0.18)]
    lab = [
        ("XIAO ESP32S3", (12, 17, 5)), ("LiPo 1000 mAh", (44, 6, 9.5)), ("TP4056", (70, 12, 3)),
        ("Stick", (STICK_X, 17, 14)), ("Mic 1", (CL - 2, 10, 9)), ("Mic 2", (CL - 2, 24, 9)),
        ("LED", (92, 29, CH - 2.5)), ("Pogo male", (73.5, CW, 9)), ("Magnet", (15, CW, 10)),
        ("Magnet ", (92, CW, 10)), ("Slide switch", (8, 3, 9)),
        ("3 key switches (outlined)", (KEY_X[1], 17 - 7.5, 16)),
    ]
    render(items, (CL / 2, CW / 2, 300), (CL / 2, CW / 2, 0), os.path.join(OUT, "6_controller_inside_top.png"),
           size=(1900, 1000), zoom=1.0, labels=lab, title="Controller, top view (shell see-through)",
           view_up=(0, 1, 0), margin=300)

    # 7. dock x-ray top view
    items = [(m, col(k, DOCK_COL)) for k, m in dock.items() if k not in LID and k not in ("dock_shell",)]
    items += [(dock["dock_shell"], COL["shell"], 0.15)] + ctrl_items(
        dockedM, skip=("ctrl_top", "stick_cap", "keycap1", "keycap2", "keycap3", "switch1", "switch2", "switch3"))
    items += [(T(ctrl["ctrl_top"], dockedM), COL["shell"], 0.15)]
    lab = [
        ("ESP32-S3 DevKitC", (-38, 75, 15)), ("USB-C to Mac", (-38, BD, 13)), ("Speaker", (2, 80, 16)),
        ("Amp", (39, 55, 13)), ("Pogo female", (23.5, TRAY_Y1 + 3, 13)), ("Magnet", (-35, TRAY_Y1, 10)),
        ("Magnet ", (42, TRAY_Y1, 10)), ("Controller in tray", (-20, 18, 20)),
    ]
    render(items, (0, BD / 2, 350), (0, BD / 2, 0), os.path.join(OUT, "7_dock_inside_top.png"),
           size=(1700, 1300), zoom=1.0, labels=lab, title="Dock + docked controller, top view (shells see-through)",
           view_up=(0, 1, 0), margin=260)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
