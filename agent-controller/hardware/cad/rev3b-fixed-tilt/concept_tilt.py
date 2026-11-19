#!/usr/bin/env python3
"""
Agent controller rev 3b -- the fixed-tilt option: concept model + renders.

Same base and controller as rev 3. The hinged lid is replaced by a rigid wedge at
the back of the base that holds the screen at 60 degrees. Nothing folds.

This is an OPTION to compare with the folding lid, not the chosen design.
NOT print-ready: part sizes come from datasheets and listings.

It reuses the rev 3 script for the controller, the shared parts and the renderer.

Run:  xvfb-run -a python3 concept_tilt.py     -> PNGs and overlaps.txt in ./out
"""
import math
import os
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rev3-pivot"))
import concept as base  # noqa: E402
from concept import (COL, H, LID, OPEN_DEG, PART_COL, SHELLS, SPK, USB_X, DEV_X0, DEV_X1, W, Y0, Y1,  # noqa: E402
                     T, anc, block_parts, box, cyl_y, cyl_z, dock_parts, key_parts, lid_open, mesh,
                     rbox, render, screen_ui, swing, tr)

OUT = os.path.join(HERE, "out")

# ----------------------------------------------------------------------------- dims
TILT = 60.0                                  # screen angle from the desk
FACE = 68.0                                  # length of the tilted face
YA = 62.0                                    # where the face meets the base top
C, S = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
YB, ZT = YA + FACE * C, H + FACE * S         # top edge of the face: y 96, z 80.9
SPK_T = (SPK[0], 63.0)                       # speaker, moved forward under the front strip


def face(wp):
    """Flat part (x, distance up the face, -depth behind the face) -> its place on the tilted face."""
    return wp.rotate((0, 0, 0), (1, 0, 0), TILT).translate((0, YA, H))


# closed-lid coordinates of rev 3 -> flat face coordinates -> world (reuses the rev 3 display parts)
FLAT = trimesh.transformations.translation_matrix([0, 100.4, H]) @ \
    trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])
ONFACE = trimesh.transformations.translation_matrix([0, YA, H]) @ \
    trimesh.transformations.rotation_matrix(math.radians(TILT), [1, 0, 0]) @ FLAT
NORMAL = np.array([0.0, -S, C])              # out of the screen, toward you


def tilt_parts():
    P = {}
    P["base_floor"] = rbox(-W / 2, W / 2, Y0, Y1, 0, 2.0, 3)

    sh = rbox(-W / 2, W / 2, Y0, Y1, 2.0, H, 3)
    sh = sh.cut(rbox(-W / 2 + 2, W / 2 - 2, Y0 + 2.4, Y1 - 2, 1.9, H - 2.0, 1))
    sh = sh.cut(box(-60, 60, YA + 2.6, Y1 - 2, H - 2.5, H + 1))             # open up into the wedge
    grooves = None
    for i in range(8):                                                       # ribbed front strip
        y = 45.0 + i * 2.0
        g = box(-56, 56, y, y + 1.0, H - 0.7, H + 0.2)
        dy = (y + 0.5) - SPK_T[1]
        if abs(dy) < 17.5:
            half = math.sqrt(18.0 ** 2 - dy ** 2)
            g = g.union(box(SPK_T[0] - half, SPK_T[0] + half, y, y + 1.0, H - 2.2, H + 0.2))
        grooves = g if grooves is None else grooves.union(g)
    sh = sh.cut(grooves)
    for ux in USB_X:
        sh = sh.cut(box(ux - 4.7, ux + 4.7, Y1 - 3, Y1 + 1, 11.6, 15.6))
    sh = sh.cut(box(DEV_X0 - 1, DEV_X1 + 1, Y0 + 0.8, Y0 + 3, 2.0, 16.5))
    sh = sh.cut(box(-30.0, -14.0, Y0 - 1, Y0 + 3, 7.5, 14.5))
    for mx in (-47.0, 3.0):
        sh = sh.cut(cyl_y(mx, Y0 + 0.1, Y0 + 3, 11.0, 3.15))
    sh = sh.cut(cyl_z(52.0, 47.5, H - 3, H + 1, 1.2))
    P["base_shell"] = sh

    prof = [(YA, H), (YB, ZT), (Y1, ZT), (Y1, H)]
    wd = cq.Workplane("YZ").polyline(prof).close().extrude(W).translate((-W / 2, 0, 0))
    inner = cq.Workplane("YZ").polyline(prof).close().offset2D(-2.0).extrude(W - 4).translate((-W / 2 + 2, 0, 0))
    wd = wd.cut(inner)
    wd = wd.cut(box(-60, 60, YA + 2.6, Y1 - 2, H - 0.1, H + 2.2))            # open down into the base
    wd = wd.cut(face(box(-63, 63, -2, FACE + 2, -1.25, 3)))                  # seat for the screen frame
    wd = wd.cut(face(box(-55, 55, 2.6, 65.4, -3, 1)))                        # opening for the display
    for i in range(7):                                                       # sound and air slots, back
        z = 34.0 + i * 5.0
        wd = wd.cut(box(-34, 18, Y1 - 3, Y1 + 1, z, z + 1.6))
    P["tilt_shell"] = wd
    bz = box(-W / 2, W / 2, 0.8, FACE, -1.2, 0).cut(box(-42.2, 42.2, 5.8, 62.2, -2, 1))
    P["tilt_bezel"] = face(bz)

    D = dock_parts()
    for k in ("contacts_base", "dock_magnet_L", "dock_magnet_R", "dock_board", "amp", "dock_led"):
        P[k] = D[k]
    P["speaker"] = cyl_z(SPK_T[0], SPK_T[1], H - 2.0 - 5.6, H - 2.1, 20.0)
    return P


def display_parts():
    """Display, screen and header in rev 3's closed-lid coordinates; ONFACE puts them on the tilted face."""
    D = dock_parts()
    z0 = H
    P = {"display": D["display"], "screen": D["screen"]}
    P["display_header"] = box(-54.0, -51.4, 48.2, 83.8, z0 + 6.65, z0 + 9.15)          # straight pins, plastic base
    P["display_plugs"] = box(-53.9, -51.5, 48.6, 83.4, z0 + 9.15, z0 + 23.15)          # plug-on wires, 14 mm tall
    return P


TCOL = dict(PART_COL)
TCOL.update({"tilt_shell": "shell", "tilt_bezel": "bezel", "display_plugs": "wire"})
TSHELLS = set(SHELLS) | {"tilt_shell", "tilt_bezel"}
HIDDEN_OK = ("green_cap", "slide_switch", "contacts_base", "contacts_ctrl", "mic1", "mic2", "dock_magnet_L",
             "dock_magnet_R", "ctrl_magnet_L", "ctrl_magnet_R", "xiao_usb", "hinge_pin1", "hinge_pin2")


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(base.OUT, exist_ok=True)
    print("building ...")
    tilt = {k: mesh(v) for k, v in tilt_parts().items()}
    tilt.update({k: T(mesh(v), ONFACE) for k, v in display_parts().items()})
    key = {k: mesh(v) for k, v in key_parts().items()}
    blk = {k: mesh(v) for k, v in block_parts().items()}
    ui = {k: (T(mesh(v), ONFACE), c) for k, (v, c) in screen_ui().items()}
    fold = {k: mesh(v) for k, v in dock_parts().items()}          # the folding version, for the comparison
    ui_fold = {k: (mesh(v), c) for k, (v, c) in screen_ui().items()}
    I = np.eye(4)

    # ---------- overlap check
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
    skip = ("wires_key", "wires_block")
    a = overlaps({k: v for k, v in {**tilt, **key, **blk}.items() if k not in skip})
    b = overlaps({k: v for k, v in {**tilt, **key, **{k: T(v, swing()) for k, v in blk.items()}}.items()
                  if k not in skip})
    report = ["OVERLAPS, fixed tilt, block in line (expected: none)"] + [f"  {x} x {y}: {v} mm3" for x, y, v in a] + \
             ["OVERLAPS, fixed tilt, block swung out 90 deg (expected: none)"] + \
             [f"  {x} x {y}: {v} mm3" for x, y, v in b]
    print("\n".join(report))
    with open(os.path.join(OUT, "overlaps.txt"), "w") as fh:
        fh.write("\n".join(report) + "\n")

    # ---------- scenes
    def add(out, k, m, xray, table=TCOL, shells=TSHELLS):
        rgb = COL[table[k]]
        if xray and k in shells:
            out.append((m, rgb, 0.13 if k != "screen" else 0.25))
        elif xray and k in ("switch_plate", "battery_guard", "stick_shelf"):
            out.append((m, rgb, 0.30))
        elif not xray and k not in shells and k not in HIDDEN_OK:
            return
        else:
            out.append((m, rgb))

    def scene(swing_deg=0.0, xray=False, M=I, hide=()):
        out = []
        SM = swing(swing_deg) if swing_deg else I
        for k, m in tilt.items():
            if k not in hide:
                add(out, k, T(m, M), xray)
        for k, m in key.items():
            add(out, k, T(m, M), xray)
        for k, m in blk.items():
            add(out, k, T(m, M @ SM), xray)
        if not xray:
            out += [(T(m, M), COL[c]) for m, c in ui.values()]
        return out

    def scene_fold(M=I):
        out = []
        LM = lid_open(OPEN_DEG)
        for k, m in fold.items():
            add(out, k, T(T(m, LM) if k in LID else m, M), False, PART_COL, SHELLS)
        for k, m in {**key, **blk}.items():
            add(out, k, T(m, M), False, PART_COL, SHELLS)
        out += [(T(T(m, LM), M), COL[c]) for m, c in ui_fold.values()]
        return out

    print("rendering ...")
    p = lambda n: os.path.join(OUT, n)  # noqa: E731
    f = (0, 52, 34)
    render(scene(), (-150, -250, 185), f, p("01-tilt-device.png"), zoom=1.16,
           title="Fixed-tilt option", sub="The screen sits at 60 degrees and never folds. 124 x 112 mm on the desk, 81 mm tall.")
    render(scene(swing_deg=90), (150, -255, 200), (5, 40, 30), p("02-tilt-block-swung-out.png"), zoom=1.1,
           title="Fixed tilt, desktop position", sub="The controller is unchanged: the joystick block still swings out.")
    render(scene(), (190, 330, 170), (0, 60, 34), p("03-tilt-back.png"), zoom=1.2,
           title="Fixed tilt, from behind", sub="Flat back: sound and air slots, and two USB-C sockets at the bottom.")
    both = scene_fold(tr(-74, 0, 0)) + scene(M=tr(74, 0, 0))
    render(both, (0, -420, 250), (0, 50, 30), p("04-compare.png"), size=(2100, 1150), zoom=1.35,
           title="Folding lid (left) and fixed tilt (right)",
           sub="Same base, same controller, same footprint. Folding: 104 mm tall open, 35 closed. Fixed: 81 mm, always.")

    # x-ray, labelled
    xs = scene(xray=True)
    lab = [
        ('4" display + touch, fixed at 60 degrees', anc(tilt["display"], "c")),
        ("Display pins stay straight; wires plug on", anc(tilt["display_plugs"], "c")),
        ("Wedge housing, open into the base", (40, Y1 - 6, ZT - 4)),
        ("Speaker under the front strip", anc(tilt["speaker"])),
        ("Amplifier (MAX98357A)", anc(tilt["amp"])),
        ("Dock board (ESP32-S3), pins down", (46, 92, 12.1)),
        ("Dock status light", anc(tilt["dock_led"])),
        ("Charge contacts (base + controller)", (-22, Y0, 14)),
        ("Docking magnets", anc(tilt["dock_magnet_L"])),
        ("Controller: same as the folding version", (-20, 3, 8)),
    ]
    render(xs, (-150, -250, 185), f, p("05-tilt-xray.png"), size=(2100, 1500), zoom=1.16, labels=lab, margin=430,
           title="Fixed tilt, x-ray", sub="Shells see-through. Concept sizes, not print-ready.")

    # x-ray from the side
    lab = [
        ("Screen face, 60 degrees", (W / 2, YA + 34 * C, H + 34 * S)),
        ("Display module", (W / 2, YA + 50 * C + 4 * S, H + 50 * S - 4 * C)),
        ("Plug-on wires", (W / 2, YA + 34 * C + 17 * S, H + 34 * S - 17 * C)),
        ("Free space in the wedge", (W / 2, 102, 68)),
        ("Dock board", (W / 2, 80, 12)),
        ("Speaker", (W / 2, 63, 17)),
        ("USB-C", (W / 2, Y1, 13.6)),
        ("Controller", (W / 2, 20, 11)),
    ]
    render(xs, (500, 56, 40), (0, 56, 40), p("06-tilt-xray-side.png"), size=(2100, 1300), zoom=1.25, labels=lab,
           margin=420, parallel=True, title="Fixed tilt, x-ray from the right side",
           sub="You are on the left. The back is flat and vertical.")

    # exploded base + wedge
    ex = {
        "base_floor": tr(0, 0, -44), "dock_board": tr(0, 0, -6), "amp": tr(0, 0, -6), "speaker": tr(0, 0, 12),
        "dock_led": tr(0, 0, 34), "contacts_base": tr(0, -22, 0), "dock_magnet_L": tr(0, -22, 0),
        "dock_magnet_R": tr(0, -22, 0), "base_shell": tr(0, 0, 70), "tilt_shell": tr(0, 26, 104),
        "display": tr(0, 26, 176), "display_header": tr(0, 26, 176), "display_plugs": tr(0, 26, 176),
        "screen": tr(0, 26, 236), "tilt_bezel": tr(0, 26, 236),
    }
    DM = {k: T(m, ex[k]) for k, m in tilt.items()}
    items = [(DM[k], COL[TCOL[k]]) for k in DM]
    lab = [
        ("Screen frame", anc(DM["tilt_bezel"], "c")),
        ('4" ST7796 display with touch', anc(DM["display"], "c")),
        ("Straight pins with plug-on wires", anc(DM["display_plugs"], "c")),
        ("Wedge housing: one rigid printed part", (-W / 2, Y1 + 26 - 8, H + 30 + 104)),
        ("Base shell: ribbed front strip, open at the back", (-20, 50, H + 70)),
        ("Status light (WS2812B)", anc(DM["dock_led"])),
        ("Speaker, 40 mm, facing up", anc(DM["speaker"])),
        ("Amplifier (MAX98357A)", anc(DM["amp"])),
        ("Dock board: ESP32-S3 DevKitC-1", (46, 80, 6.1)),
        ("Charge contacts, half without pins", anc(DM["contacts_base"], "front")),
        ("Docking magnets x 2", anc(DM["dock_magnet_R"], "front")),
        ("Bottom plate, 4 x M2 screws", (-30, 60, -42)),
    ]
    render(items, (-250, -330, 250), (0, 76, 100), p("07-tilt-exploded.png"), size=(2100, 2300), zoom=1.1,
           labels=lab, margin=470, title="Fixed tilt: base and screen housing, exploded",
           sub="No hinge, no lid magnets, no pin bending.")
    print("done ->", OUT)


if __name__ == "__main__":
    main()
