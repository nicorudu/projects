#!/usr/bin/env python3
"""
Agent controller rev 3 -- concept model + renders.

Three bodies: lid (screen), base (speaker, dock board), controller (key section +
pivoting joystick block). Every part sits where the blueprint puts it, so the
renders show the finished look and the x-ray views show the fit.

NOT print-ready. Part sizes come from datasheets and listings; nothing is printed
before the real parts are measured (plan, milestone M7a).

Coordinates (mm): x left(-)/right(+), centred on the device.
y = 0 at the controller's front face (toward you), increasing toward the back.
z = 0 at the desk.

Run:  python3 concept.py          -> writes PNGs and overlaps.txt to ./out
"""
import math
import os

import cadquery as cq
import numpy as np
import trimesh

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ----------------------------------------------------------------------------- dims
W = 124.0                       # width of every body
H = 22.0                        # height of base and controller
CD = 40.0                       # controller depth (y 0..40)
BD = 72.0                       # base depth (y 40..112)
Y0, Y1 = CD, CD + BD            # base front / back
LID_D, LID_T = 82.0, 10.0
LID_Y0 = Y1 - LID_D             # 30: the closed lid overhangs the controller by 10
OPEN_DEG = 105.0
JX = 18.0                       # joint between key section (left) and joystick block (right)
PIV = (JX, 4.0)                 # pivot axis (x, y)
KN_R = 6.0                      # knuckle radius
SX, SY = 40.0, 20.0             # stick centre
PLATE_X = (-48.0, -22.2, 3.6)   # key plate centres: Cancel, Send, Voice
PLATE_W, PLATE_D = 25.2, 36.2
SW_Y = 13.0                     # switch centre under each plate (plates hinge at the rear)
DEV_X0, DEV_X1 = 32.8, 58.8     # dock board, right side of the base
USB_X = (40.3, 51.3)            # its two USB-C sockets
DEV_Y0, DEV_Y1 = Y1 - 2.0 - 69.0, Y1 - 2.0
SPK = (-8.0, 78.0)              # speaker centre


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


# ----------------------------------------------------------------------------- base + lid (closed position)
def dock_parts():
    P = {}
    P["base_floor"] = rbox(-W / 2, W / 2, Y0, Y1, 0, 2.0, 3)

    sh = rbox(-W / 2, W / 2, Y0, Y1, 2.0, H, 3)
    sh = sh.cut(rbox(-W / 2 + 2, W / 2 - 2, Y0 + 2.4, Y1 - 2, 1.9, H - 2.0, 1))
    # ribbed top: blind grooves left to right, open slots over the speaker only
    grooves = None
    for i in range(29):
        y = 46.0 + i * 2.0
        g = box(-56, 56, y, y + 1.0, H - 0.7, H + 0.2)
        dy = (y + 0.5) - SPK[1]
        if abs(dy) < 17.5:
            half = math.sqrt(18.0 ** 2 - dy ** 2)
            g = g.union(box(SPK[0] - half, SPK[0] + half, y, y + 1.0, H - 2.2, H + 0.2))
        grooves = g if grooves is None else grooves.union(g)
    sh = sh.cut(grooves)
    for ux in USB_X:                                              # two USB-C ports, back wall
        sh = sh.cut(box(ux - 4.7, ux + 4.7, Y1 - 3, Y1 + 1, 11.6, 15.6))
    sh = sh.cut(box(DEV_X0 - 1, DEV_X1 + 1, Y0 + 0.8, Y0 + 3, 2.0, 16.5))  # pocket for the board's front end
    sh = sh.cut(box(-30.0, -14.0, Y0 - 1, Y0 + 3, 7.5, 14.5))            # charge contact window
    for mx in (-47.0, 3.0):
        sh = sh.cut(cyl_y(mx, Y0 + 0.1, Y0 + 3, 11.0, 3.15))             # docking magnet pockets
    sh = sh.cut(cyl_z(52.0, 47.5, H - 3, H + 1, 1.2))                    # status light window
    sh = sh.cut(cyl_z(-57.0, 50.0, H - 2.3, H - 0.25, 3.15))             # lid magnet pocket
    for x0, x1 in ((-54.8, -45.4), (45.4, 54.8)):                        # room for the lid's knuckles
        sh = sh.cut(cyl_x(x0, x1, Y1, H, 4.4))
    for x0, x1 in ((-62, -55), (55, 62)):                                # hinge lugs at the back corners
        sh = sh.union(cyl_x(x0, x1, Y1, H, 4.0))
    for x0, x1 in ((-63, -45), (45, 63)):
        sh = sh.cut(cyl_x(x0, x1, Y1, H, 1.1))
    P["base_shell"] = sh

    P["contacts_base"] = box(-29.5, -14.5, Y0, Y0 + 6.0, 8.0, 14.0)
    P["dock_magnet_L"] = cyl_y(-47.0, Y0 + 0.15, Y0 + 2.15, 11.0, 3.0)
    P["dock_magnet_R"] = cyl_y(3.0, Y0 + 0.15, Y0 + 2.15, 11.0, 3.0)
    P["lid_magnet_base"] = cyl_z(-57.0, 50.0, H - 2.25, H - 0.3, 3.0)

    dev = box(DEV_X0, DEV_X1, DEV_Y0, DEV_Y1, 10.5, 12.1)                # board, pins down
    dev = dev.union(box(DEV_X0 + 4, DEV_X1 - 4, DEV_Y0 + 1, DEV_Y0 + 26.5, 12.1, 15.3))   # radio module
    for ux in USB_X:
        dev = dev.union(box(ux - 4.5, ux + 4.5, DEV_Y1 - 6.5, DEV_Y1 + 1.3, 12.1, 15.3))      # USB-C sockets
    for px in (DEV_X0 + 0.3, DEV_X1 - 2.8):
        dev = dev.union(box(px, px + 2.5, DEV_Y0 + 6, DEV_Y1 - 6, 2.3, 10.5))             # header pins
    P["dock_board"] = dev
    P["speaker"] = cyl_z(SPK[0], SPK[1], H - 2.0 - 5.6, H - 2.1, 20.0)
    P["amp"] = box(-58.0, -40.2, 80.0, 99.3, 2.0, 13.0)
    P["dock_led"] = box(47.3, 56.7, 42.8, 52.2, 17.3, 18.9)

    # ---- lid, closed: screen faces down onto the base
    z0 = H
    bz = rbox(-W / 2, W / 2, LID_Y0, Y1, z0, z0 + 1.2, 3)
    bz = bz.cut(box(-42.2, 42.2, 38.2, 94.6, z0 - 1, z0 + 2))
    for x0, x1 in ((-63, -45.6), (45.6, 63)):
        bz = bz.cut(cyl_x(x0, x1, Y1, H, 4.4))
    bz = bz.cut(cyl_z(-57.0, 50.0, z0 + 0.1, z0 + 2, 3.15))
    P["lid_bezel"] = bz
    bk = rbox(-W / 2, W / 2, LID_Y0, Y1, z0 + 1.2, z0 + LID_T, 3)
    bk = soft(bk, 1.2)
    bk = bk.cut(rbox(-W / 2 + 2, W / 2 - 2, LID_Y0 + 2, Y1 - 2, z0 + 1.1, z0 + LID_T - 2, 2))
    for x0, x1 in ((-63, -54.6), (54.6, 63)):
        bk = bk.cut(cyl_x(x0, x1, Y1, H, 4.4))
    for x0, x1 in ((-54.2, -46), (46, 54.2)):
        bk = bk.union(cyl_x(x0, x1, Y1, H, 4.0))
    for x0, x1 in ((-63, -45), (45, 63)):
        bk = bk.cut(cyl_x(x0, x1, Y1, H, 1.1))
    bk = bk.cut(cyl_z(-57.0, 50.0, z0 + 0.1, z0 + 2.3, 3.15))
    P["lid_back"] = bk
    P["display"] = box(-54, 54, 36.0, 96.8, z0 + 1.2, z0 + 1.2 + 5.45)
    P["screen"] = box(-42.0, 42.0, 38.4, 94.4, z0 + 1.1, z0 + 1.2)
    P["lid_magnet_lid"] = cyl_z(-57.0, 50.0, z0 + 0.15, z0 + 2.15, 3.0)
    P["hinge_pin1"] = cyl_x(-62.0, -46.0, Y1, H, 1.0)
    P["hinge_pin2"] = cyl_x(46.0, 62.0, Y1, H, 1.0)
    return P


# what the screen shows (thin slabs on the glass; they turn with the lid)
def screen_ui():
    U = {}
    zt, zb = H + 1.1, H + 1.04
    U["ui_header"] = (box(-40.5, 40.5, 39.6, 45.2, zb, zt), "ui_bar")
    rows = (("ui_blue", 47.2), ("ui_amber", 59.0), ("ui_green", 70.8), ("ui_grey", 82.6))
    for i, (c, y) in enumerate(rows):
        U[f"ui_row{i}"] = (box(-40.5, 40.5, y, y + 10.2, zb, zt), "ui_row")
        U[f"ui_dot{i}"] = (cyl_z(-36.0, y + 5.1, zb - 0.03, zt, 1.9), c)
        U[f"ui_word{i}"] = (box(-31.5, -17.5, y + 3.9, y + 6.3, zb - 0.03, zt), c)
        U[f"ui_title{i}"] = (box(-13.5, 14.0 + 6 * (i % 3), y + 3.9, y + 6.3, zb - 0.03, zt), "ui_text")
    sel = box(-41.3, 41.3, 58.2, 70.0, zb - 0.01, zt).cut(box(-40.5, 40.5, 59.0, 69.2, zb - 0.1, zt + 0.1))
    U["ui_select"] = (sel, "ui_amber")
    return U


# ----------------------------------------------------------------------------- controller, docked + in line
def key_parts():
    P = {}
    body = rbox(-W / 2, JX, 0, CD, 0, H, 3)
    body = body.cut(box(-W / 2 + 1.2, JX - 1.6, 1.4, CD - 2.0, 1.5, H + 1))          # open top for the plates
    body = body.cut(cyl_z(PIV[0], PIV[1], 11.0, H + 1, KN_R + 0.3))                  # room for the block's ear
    body = body.union(cyl_z(PIV[0], PIV[1], 0, 11.0, KN_R))                          # lower knuckle
    body = body.union(cyl_z(PIV[0], PIV[1], 11.0, 20.4, 4.75))                       # pivot pin
    body = body.cut(cyl_z(PIV[0], PIV[1], 1.5, H + 1, 3.0))                          # 6 mm wire bore
    body = body.cut(box(PIV[0] - 8, PIV[0], PIV[1] - 2.2, PIV[1] + 2.2, 1.5, 6.5))   # wires enter the bore
    body = body.cut(box(-W / 2 - 1, -W / 2 + 2, 6.9, 16.3, 2.3, 5.3))                # XIAO USB-C
    body = body.cut(box(-W / 2 - 1, -W / 2 + 2, 28.6, 32.0, 11.2, 13.6))             # slide switch slot
    body = body.cut(box(-30.0, -14.0, CD - 3, CD + 1, 7.5, 14.5))                    # contact window
    for mx in (-47.0, 3.0):
        body = body.cut(cyl_y(mx, CD - 2.3, CD - 0.05, 11.0, 3.15))                  # docking magnets
    body = body.cut(cyl_x(JX - 2.2, JX + 1, 28.0, 11.0, 2.0))                        # pivot sensor stem
    body = body.cut(cyl_x(JX - 2.25, JX - 0.05, 35.0, 6.0, 3.15))                    # joint magnet
    P["key_body"] = body

    sp = box(-W / 2 + 1.3, JX - 1.7, 3.0, 24.0, 13.0, 14.2)                          # switch plate
    for cx in PLATE_X:
        sp = sp.cut(box(cx - 7.0, cx + 7.0, SW_Y - 7.0, SW_Y + 7.0, 12, 15))
    sp = sp.cut(cyl_z(PIV[0], PIV[1], 12, 15, KN_R + 0.6))
    P["switch_plate"] = sp
    for i, cx in enumerate(PLATE_X):
        s = box(cx - 6.9, cx + 6.9, SW_Y - 6.9, SW_Y + 6.9, 12.0, 14.2)
        s = s.union(box(cx - 7.5, cx + 7.5, SW_Y - 7.5, SW_Y + 7.5, 14.2, 17.0))
        s = s.union(box(cx - 2.9, cx + 2.9, SW_Y - 1.6, SW_Y + 1.6, 17.0, 20.0))    # stem
        s = s.union(box(cx - 0.5, cx + 0.5, SW_Y + 5.2, SW_Y + 6.2, 10.5, 12.0))    # trimmed pins
        s = s.union(box(cx + 4.5, cx + 5.5, SW_Y + 3.2, SW_Y + 4.2, 10.5, 12.0))
        P[f"switch{i+1}"] = s
        pl = rbox(cx - PLATE_W / 2, cx + PLATE_W / 2, 1.6, 1.6 + PLATE_D, 20.0, H, 1.5)
        pl = soft(pl, 0.5)
        pl = pl.cut(cyl_z(PIV[0], PIV[1], 19, H + 1, KN_R + 0.6))                   # Voice plate clears the pivot
        P[f"plate{i+1}"] = pl
    P["battery_guard"] = box(-32.0, 10.0, 3.0, 24.0, 9.7, 10.3)
    P["battery"] = rbox(-31.0, 9.0, 3.0, 33.0, 1.5, 9.5, 1.5)
    xi = box(-60.6, -39.6, 2.2, 20.0, 1.5, 2.7).union(box(-54.0, -42.0, 4.0, 18.2, 2.7, 4.3))
    P["xiao"] = xi
    P["xiao_usb"] = box(-61.9, -54.6, 7.3, 15.9, 2.7, 4.9)                           # USB-C socket
    P["charger"] = box(-60.6, -32.6, 20.6, 37.8, 1.5, 3.1).union(box(-52, -44, 26, 32, 3.1, 4.4))
    P["slide_switch"] = box(-60.7, -56.3, 26.0, 34.6, 10.0, 14.7).union(box(-63.6, -60.7, 29.0, 31.6, 11.5, 13.3))
    P["contacts_ctrl"] = box(-29.5, -14.5, CD - 6.0, CD, 8.0, 14.0)
    P["ctrl_magnet_L"] = cyl_y(-47.0, CD - 2.2, CD - 0.1, 11.0, 3.0)
    P["ctrl_magnet_R"] = cyl_y(3.0, CD - 2.2, CD - 0.1, 11.0, 3.0)
    P["pivot_sensor"] = box(JX - 5.4, JX - 1.9, 25.0, 31.0, 8.0, 14.0).union(cyl_x(JX - 1.9, JX - 0.02, 28.0, 11.0, 1.7))
    P["joint_magnet_key"] = cyl_x(JX - 2.2, JX - 0.1, 35.0, 6.0, 3.0)
    P["wires_key"] = cyl_x(PIV[0] - 30.0, PIV[0], PIV[1], 4.0, 1.9).union(cyl_z(PIV[0], PIV[1], 4.0, 17.6, 1.9))
    return P


def block_parts():
    P = {}
    X1 = W / 2
    body = rbox(JX, X1, 0, CD, 0, 19.5, 3)
    body = body.cut(box(JX + 1.6, X1 - 1.6, 1.6, CD - 1.6, 1.5, 20))
    body = body.cut(cyl_z(PIV[0], PIV[1], -1, 20, KN_R + 0.3))                       # room for the knuckle
    ear = cyl_z(PIV[0], PIV[1], 11.2, 19.5, KN_R).cut(cyl_z(PIV[0], PIV[1], 10, 21, 4.95))
    ear = ear.cut(box(PIV[0], PIV[0] + 8, PIV[1] - 2.2, PIV[1] + 2.2, 15.4, 20))     # wires leave the bore
    body = body.union(ear)
    for yc in (12.0, 28.0):                                                          # mic grilles, end face
        for dz in (-2.6, 0, 2.6):
            body = body.cut(box(X1 - 3, X1 + 1, yc - 4.0, yc + 4.0, 9.0 + dz - 0.6, 9.0 + dz + 0.6))
    body = body.cut(cyl_x(JX - 0.1, JX + 2.2, 35.0, 6.0, 3.15))                      # joint magnet
    P["block_body"] = body

    top = rbox(JX, X1, 0, CD, 19.5, H, 3)
    top = soft(top, 0.6)
    top = top.union(cyl_z(SX, SY, 16.0, 19.5, 17.0))
    top = top.cut(cyl_z(SX, SY, 17.5, H + 1, 15.5))                                  # 31 mm dish
    top = top.cut(cyl_z(SX, SY, 15, 18, 7.2))                                        # stick comes through
    top = top.cut(cyl_z(PIV[0], PIV[1], 15, H + 1, KN_R + 0.3))
    top = top.cut(cyl_z(56.0, 6.0, 15, H + 1, 2.9))                                  # green button
    top = top.cut(cyl_z(49.5, 4.2, 15, H + 1, 1.0))                                  # status light window
    for ang in (0, 90, 180, 270):                                                    # four tick marks
        a = math.radians(ang)
        cx, cy = SX + 18.0 * math.cos(a), SY + 18.0 * math.sin(a)
        lx, ly = (1.6, 0.45) if ang in (0, 180) else (0.45, 1.6)
        top = top.cut(box(cx - lx, cx + lx, cy - ly, cy + ly, H - 0.5, H + 1))
    P["block_top"] = top
    P["retainer"] = cyl_z(PIV[0], PIV[1], 20.5, H, KN_R)

    P["stick_shelf"] = box(30.0, 50.0, 10.5, 29.5, 7.0, 8.5)
    st = box(SX - 8.5, SX + 8.5, SY - 8.5, SY + 8.5, 8.5, 15.0)
    st = st.union(cyl_z(SX, SY, 15.0, 17.0, 6.5)).union(cyl_z(SX, SY, 17.0, 19.8, 2.0))
    P["stick"] = st
    cap = soft(cyl_z(SX, SY, 19.8, 21.8, 13.0), 0.7)
    cap = cap.cut(cyl_z(SX, SY, 21.4, 22.5, 4.2))
    P["stick_cap"] = cap
    P["green_button"] = box(53.0, 59.0, 3.0, 9.0, 15.5, 19.0).union(cyl_z(56.0, 6.0, 19.0, 20.4, 1.7))
    P["green_cap"] = cyl_z(56.0, 6.0, 20.4, 22.3, 2.6)
    P["ctrl_led"] = box(44.75, 54.25, 1.8, 11.3, 11.0, 12.6)
    P["mic1"] = cyl_x(X1 - 3.2, X1 - 1.6, 12.0, 9.0, 7.0)
    P["mic2"] = cyl_x(X1 - 3.2, X1 - 1.6, 28.0, 9.0, 7.0)
    P["joint_magnet_block"] = cyl_x(JX + 0.05, JX + 2.1, 35.0, 6.0, 3.0)
    P["wires_block"] = cyl_x(PIV[0], PIV[0] + 12.0, PIV[1], 17.6, 1.9)
    return P


# ----------------------------------------------------------------------------- mesh helpers
def mesh(wp, tol=0.06):
    path = os.path.join(OUT, "_t.stl")
    cq.exporters.export(wp, path, tolerance=tol, angularTolerance=0.15)
    m = trimesh.load(path)
    os.remove(path)
    return m


def T(m, M):
    c = m.copy()
    c.apply_transform(M)
    return c


def tr(dx=0, dy=0, dz=0):
    return trimesh.transformations.translation_matrix([dx, dy, dz])


def lid_open(deg=OPEN_DEG):
    return trimesh.transformations.rotation_matrix(-math.radians(deg), [1, 0, 0], [0, Y1, H])


def swing(deg=90.0):
    """Joystick block swung out toward you."""
    return trimesh.transformations.rotation_matrix(-math.radians(deg), [0, 0, 1], [PIV[0], PIV[1], 0])


COL = {
    "shell": (0.90, 0.91, 0.92), "floor": (0.76, 0.77, 0.79), "plate": (0.97, 0.97, 0.98),
    "bezel": (0.10, 0.10, 0.12), "screen": (0.03, 0.04, 0.06), "cap": (0.12, 0.12, 0.14),
    "esp": (0.10, 0.32, 0.22), "xiao": (0.16, 0.50, 0.30), "battery": (0.88, 0.72, 0.26),
    "speaker": (0.24, 0.24, 0.27), "amp": (0.48, 0.30, 0.70), "tp": (0.20, 0.42, 0.85),
    "stick": (0.32, 0.32, 0.36), "switch": (0.84, 0.18, 0.22), "mic": (0.05, 0.62, 0.62),
    "led": (0.98, 0.80, 0.20), "pogo": (0.90, 0.62, 0.12), "magnet": (0.55, 0.57, 0.62),
    "slide": (0.95, 0.45, 0.10), "display": (0.16, 0.32, 0.66), "green": (0.16, 0.78, 0.38),
    "button": (0.20, 0.20, 0.22), "wire": (0.95, 0.35, 0.55), "guard": (0.75, 0.90, 0.95),
    "splate": (0.55, 0.60, 0.68), "pin": (0.60, 0.60, 0.62),
    "ui_bar": (0.10, 0.12, 0.15), "ui_row": (0.07, 0.08, 0.10), "ui_text": (0.86, 0.88, 0.90),
    "ui_blue": (0.30, 0.64, 1.00), "ui_amber": (0.96, 0.77, 0.26), "ui_green": (0.24, 0.86, 0.52),
    "ui_grey": (0.54, 0.56, 0.60),
}
PART_COL = {
    "base_floor": "floor", "base_shell": "shell", "contacts_base": "pogo", "dock_magnet_L": "magnet",
    "dock_magnet_R": "magnet", "lid_magnet_base": "magnet", "dock_board": "esp", "speaker": "speaker",
    "amp": "amp", "dock_led": "led", "lid_bezel": "bezel", "lid_back": "shell", "display": "display",
    "screen": "screen", "lid_magnet_lid": "magnet", "hinge_pin1": "pin", "hinge_pin2": "pin",
    "key_body": "shell", "switch_plate": "splate", "battery_guard": "guard", "battery": "battery",
    "xiao": "xiao", "xiao_usb": "pin", "charger": "tp", "slide_switch": "slide", "contacts_ctrl": "pogo",
    "ctrl_magnet_L": "magnet", "ctrl_magnet_R": "magnet", "pivot_sensor": "button",
    "joint_magnet_key": "magnet", "wires_key": "wire",
    "block_body": "shell", "block_top": "shell", "retainer": "shell", "stick_shelf": "splate",
    "stick": "stick", "stick_cap": "cap", "green_button": "button", "green_cap": "green",
    "ctrl_led": "led", "mic1": "mic", "mic2": "mic", "joint_magnet_block": "magnet", "wires_block": "wire",
}
for _i in (1, 2, 3):
    PART_COL[f"switch{_i}"] = "switch"
    PART_COL[f"plate{_i}"] = "plate"
LID = {"lid_bezel", "lid_back", "display", "screen", "lid_magnet_lid"}
SHELLS = {"base_floor", "base_shell", "lid_bezel", "lid_back", "key_body", "block_body", "block_top",
          "retainer", "plate1", "plate2", "plate3", "stick_cap", "screen"}


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


def render(items, cam, focal, path, size=(1600, 1100), zoom=1.0, labels=None, title=None, sub=None,
           view_up=(0, 0, 1), margin=0, bg=(1, 1, 1), parallel=False):
    """items: list of (mesh, rgb[, opacity]). labels: list of (text, world_xyz)."""
    import vtk
    from PIL import Image, ImageDraw, ImageFont
    W_, H_ = size
    top = 96 if (title or margin) else 0
    RW, RH = W_ - 2 * margin, H_ - top
    ren = vtk.vtkRenderer()
    ren.SetBackground(*bg)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(RW, RH)
    see_through = any(len(it) > 2 and it[2] < 1.0 for it in items)
    if see_through:
        rw.SetAlphaBitPlanes(1)
        rw.SetMultiSamples(0)
        ren.SetUseDepthPeeling(1)
        ren.SetMaximumNumberOfPeels(60)
        ren.SetOcclusionRatio(0.0)
        ren.SetUseFXAA(True)
    else:
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
        pr.SetAmbient(0.50)
        pr.SetDiffuse(0.58)
        pr.SetSpecular(0.20)
        pr.SetSpecularPower(28)
        ren.AddActor(ac)
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
        ea.GetProperty().SetColor(0.12, 0.12, 0.14)
        ea.GetProperty().SetLineWidth(1.1)
        ea.GetProperty().SetOpacity(0.45 if op >= 1.0 else 0.30)
        ren.AddActor(ea)
    c = ren.GetActiveCamera()
    c.SetPosition(*cam)
    c.SetFocalPoint(*focal)
    c.SetViewUp(*view_up)
    if parallel:
        c.ParallelProjectionOn()
    ren.ResetCamera()
    c.Zoom(zoom)
    lt = vtk.vtkLight()
    lt.SetLightTypeToSceneLight()
    lt.SetPosition(-250, -300, 450)
    lt.SetFocalPoint(0, 50, 0)
    lt.SetIntensity(0.45)
    ren.AddLight(lt)
    l2 = vtk.vtkLight()                       # soft light from above, so top faces read as light
    l2.SetLightTypeToSceneLight()
    l2.SetPosition(60, -80, 600)
    l2.SetFocalPoint(0, 50, 0)
    l2.SetIntensity(0.38)
    ren.AddLight(l2)
    rw.Render()
    proj = []
    if labels:
        co = vtk.vtkCoordinate()
        co.SetCoordinateSystemToWorld()
        for text, p in labels:
            co.SetValue(*p)
            x, y = co.GetComputedDoubleDisplayValue(ren)
            proj.append((text, x + margin, (RH - y) + top))
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    from vtk.util import numpy_support as ns
    img = w2i.GetOutput()
    arr = ns.vtk_to_numpy(img.GetPointData().GetScalars()).reshape(RH, RW, -1)[::-1]
    im3 = Image.fromarray(arr[:, :, :3].astype("uint8"))
    im = Image.new("RGB", (W_, H_), tuple(int(255 * v) for v in bg))
    im.paste(im3, (margin, top))
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)
        sfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        tfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except Exception:  # noqa: BLE001
        font = sfont = tfont = ImageFont.load_default()
    if title:
        d.text((30, 18), title, fill=(25, 25, 28), font=tfont)
    if sub:
        d.text((30, 60), sub, fill=(95, 95, 100), font=sfont)
    if proj:
        cx = W_ / 2
        left = sorted([p for p in proj if p[1] < cx], key=lambda t: t[2])
        right = sorted([p for p in proj if p[1] >= cx], key=lambda t: t[2])
        for side, group in (("L", left), ("R", right)):
            if not group:
                continue
            lo, hi = top + 14, H_ - 44
            gap = 36
            n = len(group)
            pos = []
            for _, _, y in group:
                y = max(lo, y - 12)
                if pos and y - pos[-1] < gap:
                    y = pos[-1] + gap
                pos.append(y)
            over = pos[-1] - hi
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
                    lx = W_ - 24 - tw
                    ex = lx - 10
                d.line([(ex, ly + 13), (ax, ay)], fill=(95, 95, 100), width=2)
                d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(35, 35, 38))
                d.text((lx, ly), text, fill=(22, 22, 25), font=font)
    # trim empty rows above and below the picture; the title strip stays
    a = np.asarray(im).astype(int)
    bgv = np.array([int(255 * v) for v in bg])
    rows = np.where((np.abs(a[top:] - bgv).sum(axis=2) > 24).any(axis=1))[0]
    if len(rows):
        r0, r1 = max(top, top + rows[0] - 30), min(H_, top + rows[-1] + 45)
        out = Image.new("RGB", (W_, top + (r1 - r0)), tuple(bgv))
        out.paste(im.crop((0, 0, W_, top)), (0, 0))
        out.paste(im.crop((0, r0, W_, r1)), (0, top))
        im = out
    im.save(path)


def anc(m, where="top"):
    lo, hi = m.bounds
    c = (lo + hi) / 2
    if where == "top":
        return (c[0], c[1], hi[2])
    if where == "front":
        return (c[0], lo[1], c[2])
    if where == "back":
        return (c[0], hi[1], c[2])
    if where == "left":
        return (lo[0], c[1], c[2])
    if where == "right":
        return (hi[0], c[1], c[2])
    return tuple(c)


# ----------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    print("building ...")
    dock = {k: mesh(v) for k, v in dock_parts().items()}
    key = {k: mesh(v) for k, v in key_parts().items()}
    blk = {k: mesh(v) for k, v in block_parts().items()}
    ui = {k: (mesh(v), c) for k, (v, c) in screen_ui().items()}
    I = np.eye(4)

    # ---------- overlap check: lid closed, controller docked, block in line
    import manifold3d as mf

    def mf_of(m):
        return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, dtype=np.float32),
                                   tri_verts=np.asarray(m.faces, dtype=np.uint32)))

    def overlaps(parts, floor=0.5):
        M = {k: mf_of(v) for k, v in parts.items()}
        ks = list(M)
        out = []
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                v = (M[ks[i]] ^ M[ks[j]]).volume()
                if v > floor:
                    out.append((ks[i], ks[j], round(v, 1)))
        return out
    skip = ("wires_key", "wires_block")           # wires are drawn through the pivot bore on purpose
    allp = {**dock, **key, **blk}
    hits = overlaps({k: v for k, v in allp.items() if k not in skip})
    swung = {**{k: v for k, v in dock.items() if k not in LID}, **key, **{k: T(v, swing()) for k, v in blk.items()}}
    hits2 = overlaps({k: v for k, v in swung.items() if k not in skip})
    report = ["OVERLAPS, lid closed + block in line (expected: none)"] + \
             [f"  {a} x {b}: {v} mm3" for a, b, v in hits] + \
             ["OVERLAPS, block swung out 90 deg (expected: none)"] + \
             [f"  {a} x {b}: {v} mm3" for a, b, v in hits2]
    print("\n".join(report))
    with open(os.path.join(OUT, "overlaps.txt"), "w") as fh:
        fh.write("\n".join(report) + "\n")

    # ---------- scene builder
    def scene(open_deg=OPEN_DEG, swing_deg=0.0, xray=False, show_ui=True, ctrl_M=I, hide=()):
        out = []
        LM = lid_open(open_deg)
        SM = swing(swing_deg) if swing_deg else I

        def add(k, m):
            if k in hide:
                return
            rgb = COL[PART_COL[k]]
            if xray and k in SHELLS:
                out.append((m, rgb, 0.13 if k != "screen" else 0.25))
            elif xray and k in ("switch_plate", "battery_guard", "stick_shelf"):
                out.append((m, rgb, 0.30))
            elif not xray and k not in SHELLS and k not in ("green_cap", "hinge_pin1", "hinge_pin2",
                                                             "slide_switch", "contacts_base", "contacts_ctrl",
                                                             "mic1", "mic2", "dock_magnet_L", "dock_magnet_R",
                                                             "ctrl_magnet_L", "ctrl_magnet_R", "xiao_usb"):
                return                                # hidden inside an opaque shell
            else:
                out.append((m, rgb))
        for k, m in dock.items():
            add(k, T(m, LM) if k in LID else m)
        for k, m in key.items():
            add(k, T(m, ctrl_M))
        for k, m in blk.items():
            add(k, T(m, ctrl_M @ SM))
        if show_ui and open_deg > 20 and not xray:
            for k, (m, c) in ui.items():
                out.append((T(m, LM), COL[c]))
        return out

    print("rendering ...")
    p = lambda n: os.path.join(OUT, n)  # noqa: E731
    f = (0, 52, 30)
    # 1. the device as you'd see it on the desk
    render(scene(), (-150, -250, 185), f, p("01-device-open.png"), zoom=1.16,
           title="AI Agent Controller, rev 3", sub="Docked, screen open. About 124 x 112 mm on the desk.")
    # 2. joystick block swung out
    render(scene(swing_deg=90), (150, -255, 200), (5, 40, 28), p("02-block-swung-out.png"), zoom=1.1,
           title="Desktop position", sub="The joystick block swings out 90 degrees. Mics face you.")
    # 3. controller lifted off, held in line
    offM = tr(0, -62, 0)
    render(scene(ctrl_M=offM), (-170, -300, 215), (0, 25, 22), p("03-controller-off-dock.png"), zoom=1.15,
           title="Controller off the dock", sub="Magnets and two spring contacts on the base's front face.")
    # 4. closed
    render(scene(open_deg=0), (-170, -250, 170), (0, 56, 14), p("04-closed.png"), zoom=1.3,
           title="Closed", sub="About 124 x 112 x 32 mm. The lid overhangs the controller by 10 mm.")

    # 5. x-ray, three-quarter view, labelled
    xs = scene(xray=True)
    LM = lid_open()
    lab = [
        ('4" display + touch (in the lid)', anc(T(dock["display"], LM), "c")),
        ("Speaker, 40 mm, under the open slots", anc(dock["speaker"])),
        ("Amplifier (MAX98357A)", anc(dock["amp"])),
        ("Dock board (ESP32-S3), pins down", (47, 92, 12.1)),
        ("Its radio end, next to the controller", (47, 54, 15.3)),
        ("2 x USB-C, back wall", (47, Y1, 13.6)),
        ("Dock status light", anc(dock["dock_led"])),
        ("Lid magnet pair", anc(dock["lid_magnet_base"])),
        ("Charge contacts (base + controller)", (-22, Y0, 14)),
        ("Docking magnets", anc(dock["dock_magnet_L"])),
        ("XIAO ESP32S3, USB-C on the end", anc(key["xiao"])),
        ("Charger (TP4056)", anc(key["charger"])),
        ("Slide power switch", anc(key["slide_switch"], "left")),
        ("Battery, 1000 mAh", (-20, 3, 8)),
        ("3 key switches under the plates", anc(key["switch2"], "front")),
        ("Pivot pin, 10 wires inside", (PIV[0], PIV[1], 12)),
        ("Thumbstick + wide cap", anc(blk["stick"], "front")),
        ("Green button", anc(blk["green_cap"])),
        ("Controller status light", anc(blk["ctrl_led"], "front")),
        ("2 mics, end face", anc(blk["mic1"], "right")),
        ("Pivot sensor button", anc(key["pivot_sensor"])),
    ]
    render(xs, (-150, -250, 185), f, p("05-xray.png"), size=(2100, 1500), zoom=1.12, labels=lab, margin=420,
           title="X-ray: where everything sits", sub="Shells see-through. Concept sizes, not print-ready.")

    # 6. x-ray, straight down, lid removed
    xt = scene(xray=True, hide=LID | {"lid_magnet_lid", "hinge_pin1", "hinge_pin2"})
    lab = [
        ("Dock board (ESP32-S3)", (47, 88, 16)), ("USB-C x 2 (cable to the computer)", (47, Y1, 14)),
        ("Speaker", (SPK[0], SPK[1], 20)), ("Amplifier", (-49, 90, 13)),
        ("Lid magnet", (-58, 50, 21)), ("Dock status light", (52, 47.5, 19)),
        ("Charge contacts", (-22, Y0, 14)), ("Docking magnet", (-47, Y0, 11)), ("Docking magnet ", (3, Y0, 11)),
        ("XIAO ESP32S3 (under the Cancel switch)", (-58.5, 4.0, 3)), ("Charger (TP4056)", (-46, 29, 5)), ("Slide switch", (-62, 30, 12)),
        ("Battery (partly under the switches)", (-11, 28, 9.5)),
        ("Key switches: Cancel, Send, Voice", (-22.2, SW_Y, 20)),
        ("Pivot pin (wires)", (PIV[0], PIV[1], 21)), ("Pivot sensor", (14.5, 28, 14)),
        ("Joint magnets", (18, 35, 9)), ("Thumbstick", (SX, SY, 21)), ("Green button", (56, 6, 22)),
        ("Status light", (49.5, 6.5, 13)), ("Mic 1", (W / 2 - 2, 12, 9)), ("Mic 2", (W / 2 - 2, 28, 9)),
    ]
    render(xt, (0, 56, 400), (0, 56, 0), p("06-xray-top.png"), size=(2100, 1320), zoom=1.3, labels=lab,
           margin=400, view_up=(0, 1, 0), parallel=True,
           title="X-ray from above (lid removed)", sub="Back of the device at the top, you at the bottom.")

    # 7. exploded dock (lid closed, parts lifted straight up)
    ex = {
        "base_floor": tr(0, 0, -44), "dock_board": tr(0, 0, -6), "amp": tr(0, 0, -6), "speaker": tr(0, 0, 12),
        "dock_led": tr(0, 0, 34), "contacts_base": tr(0, -22, 0), "dock_magnet_L": tr(0, -22, 0),
        "dock_magnet_R": tr(0, -22, 0), "lid_magnet_base": tr(0, 0, 50), "base_shell": tr(0, 0, 80),
        "hinge_pin1": tr(-16, 0, 80), "hinge_pin2": tr(16, 0, 80),
        "lid_magnet_lid": tr(0, 0, 112), "lid_bezel": tr(0, 0, 128), "screen": tr(0, 0, 128),
        "display": tr(0, 0, 152), "lid_back": tr(0, 0, 180),
    }
    DM = {k: T(m, ex[k]) for k, m in dock.items()}
    items = [(DM[k], COL[PART_COL[k]]) for k in DM]
    lab = [
        ("Lid back", anc(DM["lid_back"])),
        ('4" ST7796 display with touch, 108 x 61 mm', anc(DM["display"])),
        ("Lid frame + screen window", anc(DM["lid_bezel"], "front")),
        ("Lid magnet", anc(DM["lid_magnet_lid"])),
        ("Hinge pin (M2 screw), one each side", anc(DM["hinge_pin2"], "right")),
        ("Base shell: ribbed top, open slots over the speaker", (-20, 70, H + 80)),
        ("Lid magnet (in the base top)", anc(DM["lid_magnet_base"])),
        ("Status light (WS2812B) under a small window", anc(DM["dock_led"])),
        ("Speaker, 40 mm, 4 ohm, 2 W, facing up", anc(DM["speaker"])),
        ("Amplifier (MAX98357A)", anc(DM["amp"])),
        ("Dock board: ESP32-S3 DevKitC-1, pins down", (47, 80, 6.1)),
        ("USB-C sockets reach through the back wall", (47, Y1, 7.6)),
        ("Charge contacts, half without pins", anc(DM["contacts_base"], "front")),
        ("Docking magnets x 2", anc(DM["dock_magnet_R"], "front")),
        ("Bottom plate, 4 x M2 screws", (-30, 60, -42)),
    ]
    render(items, (-230, -330, 250), (0, 76, 50), p("07-exploded-dock.png"), size=(2100, 1800), zoom=1.12,
           labels=lab, margin=470, title="Lid and base, exploded")

    # 8. exploded controller
    exk = {
        "key_body": tr(0, 0, -30), "battery": tr(0, 0, -6), "xiao": tr(0, 0, -10), "charger": tr(0, 0, -10),
        "battery_guard": tr(0, 0, 4), "switch_plate": tr(0, 0, 16),
        "slide_switch": tr(-16, 0, 0), "contacts_ctrl": tr(0, 18, 0), "ctrl_magnet_L": tr(0, 18, 0),
        "ctrl_magnet_R": tr(0, 18, 0), "pivot_sensor": tr(0, 0, 10), "joint_magnet_key": tr(0, 0, -14),
        "wires_key": tr(0, 0, -6),
    }
    for i in (1, 2, 3):
        exk[f"switch{i}"] = tr(0, 0, 28)
        exk[f"plate{i}"] = tr(0, 0, 54)
    exb = {
        "block_body": tr(26, 0, -30), "block_top": tr(26, 0, 40), "retainer": tr(26, 0, 58),
        "stick_shelf": tr(26, 0, -8), "stick": tr(26, 0, 8), "stick_cap": tr(26, 0, 62),
        "green_button": tr(26, 0, 14), "green_cap": tr(26, 0, 62), "ctrl_led": tr(26, 0, -4),
        "mic1": tr(46, 0, 0), "mic2": tr(46, 0, 0), "joint_magnet_block": tr(26, 0, -14),
        "wires_block": tr(26, 0, 0),
    }
    KM = {k: T(m, exk.get(k, I)) for k, m in key.items()}
    BM = {k: T(m, exb.get(k, I)) for k, m in blk.items()}
    items = [(KM[k], COL[PART_COL[k]]) for k in KM] + [(BM[k], COL[PART_COL[k]]) for k in BM]
    lab = [
        ("Key plates: Cancel / Send / Voice", anc(KM["plate1"])),
        ("Voice plate is notched for the pivot", (15.5, 4.5, H + 54)),
        ("Choc V1 switches, toward the front", anc(KM["switch1"], "front")),
        ("Printed switch plate", (-58, 20, 14.2 + 16)),
        ("Guard sheet between battery and switch pins", (-28, 3, 14.2)),
        ("Battery, 1000 mAh, 8 x 30 x 40 mm", anc(KM["battery"], "front")),
        ("XIAO ESP32S3 (USB-C through the end wall)", anc(KM["xiao"], "front")),
        ("Charger (TP4056)", anc(KM["charger"], "back")),
        ("Slide power switch", anc(KM["slide_switch"], "left")),
        ("Charge contacts, pin half", anc(KM["contacts_ctrl"])),
        ("Docking magnets x 2", anc(KM["ctrl_magnet_L"])),
        ("Key section shell with the hollow pivot pin", (-40, 0, -24)),
        ("10 wires go up the pin", (PIV[0], PIV[1], 2)),
        ("Pivot sensor button", anc(KM["pivot_sensor"])),
        ("Joint magnets x 2", anc(BM["joint_magnet_block"], "front")),
        ("Stick cap, 26 mm", anc(BM["stick_cap"])),
        ("Pivot retainer", anc(BM["retainer"])),
        ("Green button cap", anc(BM["green_cap"])),
        ("Block top: dish, tick marks, light window", (70, 34, H + 40)),
        ("Green button (tactile switch)", anc(BM["green_button"], "front")),
        ("Thumbstick (Adafruit 5628)", anc(BM["stick"], "front")),
        ("Status light (WS2812B)", anc(BM["ctrl_led"], "front")),
        ("2 mics (INMP441) behind the end grilles", anc(BM["mic2"], "right")),
        ("Joystick block shell with the pivot ear", (70, 0, -24)),
    ]
    render(items, (-150, -290, 230), (12, 20, 16), p("08-exploded-controller.png"), size=(2100, 1700),
           zoom=1.1, labels=lab, margin=480, title="Controller, exploded",
           sub="Key section on the left, joystick block on the right.")
    print("done ->", OUT)


if __name__ == "__main__":
    main()
