#!/usr/bin/env python3
"""
AI Agent Controller v0 -- parametric clamshell shell (CadQuery)

    pip install cadquery trimesh manifold3d matplotlib numpy
    python3 shell.py                 # build everything into ./out
    python3 shell.py --no-preview    # skip the PNG renders (faster)

Every dimension lives in the P = dict(...) block below. Values marked VERIFY
are datasheet/listing guesses -- measure the real part with calipers, edit the
number, rerun. The script prints a fit report (also saved to out/fit_report.txt)
that tells you whether everything still fits and how far the lid opens.

Coordinates (closed device, mm):
  x  left(-) / right(+), centred
  y  0 at the front edge, increasing toward the hinge
  z  0 at the bottom of the base
Hinge axis runs along x at y = L + R, z = H (the base/lid parting plane).

Parts (exported in print orientation):
  base_bottom   floor + hinge band + base knuckles + component cradles   (floor down)
  base_shell    deck + walls, key wells, stick well, grille              (deck down)
  lid_back      lid walls + outer plate + lid knuckles                   (outer face down)
  lid_bezel     screen-side frame with display window                    (screen face down)
  stick_cap     flat wide thumbstick cap                                 (top face down)
"""
import math
import os
import sys

import cadquery as cq

# =============================================================================
# PARAMETERS  (mm)
# =============================================================================
P = dict(
    # ---- overall -------------------------------------------------------------
    W=150.0,          # width (x)
    L=80.0,           # depth of the main body (front edge -> hinge band)
    H=24.0,           # base height (driven by the thumbstick, see fit report)
    T=13.0,           # lid thickness
    wall=2.0, floor=2.0, deck=2.0,
    corner_r=8.0,     # front corner radius (plan view)
    edge_r=1.0,       # small round on the visible outer edges

    # ---- hinge (printed barrel, wires run through the hollow centre) --------
    R=6.5,            # barrel radius (band is 2R deep)
    hinge_clear=0.4,  # radial clearance knuckle <-> body
    hinge_gap=0.4,    # axial gap between neighbouring knuckles
    knuckle_end_w=5.0,
    knuckle_mid_w=14.0,
    bore_d=5.5,       # wire tunnel along the axis (13 x 28 AWG fits)
    chan_d=5.0,       # radial wire channels into base/lid

    # ---- fasteners (M2 socket cap + M2 heat-set inserts) --------------------
    screw_len=6.0,
    screw_head_d=4.4, screw_head_cb=2.4, screw_clear_d=2.3,
    insert_hole_d=3.2,   # VERIFY: use the hole size your insert kit recommends
    insert_depth=5.0,
    boss_d=6.2,
    floor_pad=1.5,       # extra floor thickness under each bottom screw

    # ---- keys: 3 x Kailh Choc v1 + MBK 1u -----------------------------------
    key_x=(-50.0, -31.0, -12.0), key_y=17.0,
    keycap_w=17.5, keycap_d=16.5,  # MBK 1u
    keycap_clear=0.4,
    key_stack=6.0,       # VERIFY: plate top -> keycap top (Choc v1 + MBK)
    key_recess=0.5,      # keycap top sits this far below the deck
    key_plate_t=1.3,     # Choc clips want a 1.2-1.3 plate
    key_hole=13.8,       # Choc v1 plate cutout
    key_skirt=1.6,

    # ---- thumbstick: KY-023 / "PS2 joystick" module -------------------------
    stick_x=46.0, stick_y=28.5,
    cap_d=24.0, cap_t=2.4, cap_hub_d=8.0, cap_hub_h=2.0, cap_recess=0.5,
    js_pcb_w=34.0, js_pcb_d=26.0, js_pcb_t=1.6,   # VERIFY
    js_floor_pocket=1.2,  # module PCB sits in a pocket in the floor
    js_standoff=0.0,      # raise the module if your stick is shorter
    js_pivot_h=9.5,       # VERIFY: PCB bottom -> stick pivot centre
    js_dome_top_h=17.5,   # VERIFY: PCB bottom -> top of the moving dome
    js_dome_r=8.0,        # VERIFY: dome radius
    js_body_w=16.5, js_body_h=12.5,  # VERIFY: fixed metal frame
    js_shaft_d=4.2,       # VERIFY: stick shaft diameter (cap socket)
    js_shaft_tip_h=27.0,  # VERIFY: PCB bottom -> shaft tip with stock cap removed
    js_tilt=25.0,         # VERIFY: max tilt each way (deg)
    well_clear=1.0, well_wall=1.6,

    # ---- grille / speaker / mics --------------------------------------------
    grille=(-66.0, 14.0, 45.0, 69.0),   # x0, x1, y0, y1
    grille_hole_d=1.8, grille_pitch=3.4,
    spk_x=-46.0, spk_y=56.0, spk_d=40.0, spk_t=5.4,  # 40 mm 4 ohm 2 W
    spk_ring_h=3.2,
    mic_xy=((-14.0, 57.0), (8.0, 57.0)),
    mic_d=14.0,          # VERIFY: INMP441 module PCB diameter
    mic_ring_h=2.5,

    # ---- electronics bays ----------------------------------------------------
    esp_L=66.0, esp_W=26.0,   # VERIFY: dual USB-C N16R8 board outline (official DevKitC-1 is 63 x 26)
    esp_y=64.5,               # board centre (y); USB end against the left wall
    esp_under=5.5,            # header plastic + pins trimmed to 3 mm
    esp_pcb_t=1.6, esp_top=3.2,
    esp_port_dy=(-6.5, 6.5),  # VERIFY: USB-C port centres relative to board centre
    esp_slot=(27.0, 7.5),     # opening covering both ports (y, z)
    bat=(52.0, 34.2, 8.5),    # bay fits a 503450 or an 803040 LiPo
    bat_x0=-3.0, bat_y0=43.6,
    tp_L=28.0, tp_W=17.0, tp_y=38.5, tp_pad=2.0, tp_pcb_t=1.0,  # TP4056 USB-C
    tp_slot=(12.5, 7.0),
    buck=(17.0, 11.0, 3.0), buck_xy=(-30.0, 33.0),   # Pololu S7V8F3
    amp=(17.8, 19.3, 11.0), amp_xy=(50.6, 57.5),     # MAX98357A + terminal
    sw_y=50.0, sw_z=12.0,     # SS12D00G3 slide switch on the right wall
    sw_body=(8.8, 3.8, 3.8), sw_slot=(5.0, 2.2),     # VERIFY

    # ---- lid / display: LCDWIKI MSP4031 4.0" ST7796 + cap touch -------------
    bezel_t=2.0, back_t=2.0,
    disp_pcb=(108.0, 60.88),          # module outline (landscape: x, y)
    disp_glass_L=94.57,               # glass length
    disp_header_side=-1,              # pin-header strip on the -x end (LED goes top-right)
    disp_stack=5.45,                  # glass + touch + PCB
    disp_view=(83.82, 55.98),         # touch visual area
    disp_view_dxy=(0.0, 0.0),         # VERIFY: window offset from glass centre
    disp_cy=40.0,
    led_xy=(61.0, 10.0), led_pocket=10.6, led_hole_d=2.0,
)

# fastener positions
BASE_SCREWS = [(-68.0, 7.0), (15.0, 6.0), (68.0, 7.0)]
LID_SCREWS = [(-69.0, 20.0), (-69.0, 66.0), (69.0, 20.0), (69.0, 66.0)]

MEASURE = [
    ("js_pivot_h / js_dome_top_h / js_shaft_tip_h", "thumbstick heights above the module PCB bottom -- these set H"),
    ("js_shaft_d", "thumbstick shaft diameter (cap socket)"),
    ("js_pcb_w / js_pcb_d", "thumbstick module PCB outline"),
    ("key_stack", "Choc switch + MBK cap: plate top to keycap top"),
    ("esp_L / esp_W / esp_port_dy", "ESP32 board outline and USB-C port centres"),
    ("disp_pcb / disp_view_dxy", "display PCB outline and where the visible area sits"),
    ("mic_d", "INMP441 module diameter"),
    ("bat", "battery length x width x thickness"),
    ("insert_hole_d", "hole size your M2 insert kit asks for"),
    ("sw_body / sw_slot", "slide switch body and handle"),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


# =============================================================================
# geometry helpers
# =============================================================================
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r, edges="front"):
    b = box(x0, x1, y0, y1, z0, z1)
    if r > 0:
        if edges == "front":
            b = b.edges("|Z").edges("<Y").fillet(r)
        else:
            b = b.edges("|Z").fillet(r)
    return b


def cbox(cx, cy, w, d, z0, z1, r=0.0):
    b = box(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0, z1)
    if r > 0:
        b = b.edges("|Z").fillet(r)
    return b


def cyl_z(x, y, z0, z1, r):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def cyl_x(x0, x1, y, z, r):
    return cq.Workplane("YZ").workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


def revolve_rz(pts, cx, cy):
    """Revolve a closed (r, z) polygon around the vertical axis through (cx, cy)."""
    return (cq.Workplane("XZ").polyline(pts).close()
            .revolve(360, (0, 0, 0), (0, 1, 0)).translate((cx, cy, 0)))


def fillet_where(wp, r, pred):
    """Fillet only the edges for which pred(bbox) is true; keep the shape if OCC refuses."""
    try:
        edges = [e for e in wp.edges().vals() if pred(e.BoundingBox())]
        if not edges:
            return wp
        return cq.Workplane("XY").add(wp.val().fillet(r, edges))
    except Exception as exc:  # noqa: BLE001
        print(f"   (edge round skipped: {exc})")
        return wp


def U(*parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


# =============================================================================
# derived values
# =============================================================================
def derive(p):
    d = {}
    d["ya"] = p["L"] + p["R"]                 # hinge axis y
    d["za"] = p["H"]                          # hinge axis z
    d["Rk"] = p["R"] - p["hinge_clear"]       # knuckle radius
    d["band_top"] = p["H"] - p["R"] - p["hinge_clear"]
    hw, ke, km, g = p["W"] / 2, p["knuckle_end_w"], p["knuckle_mid_w"], p["hinge_gap"]
    d["base_zones"] = [(-hw, -hw + ke), (-km / 2, km / 2), (hw - ke, hw)]
    d["lid_zones"] = [(-hw + ke + g, -km / 2 - g), (km / 2 + g, hw - ke - g)]
    d["x_wire_lid"] = -km / 2 - g - 5.0
    # thumbstick stack
    js_bot = p["floor"] - p["js_floor_pocket"] + p["js_standoff"]
    d["js_bot"] = js_bot
    d["js_pivot_z"] = js_bot + p["js_pivot_h"]
    d["cap_top"] = p["H"] - p["cap_recess"]
    d["cap_bot"] = d["cap_top"] - p["cap_t"]
    d["hub_bot"] = d["cap_bot"] - p["cap_hub_h"]
    d["dome_top"] = js_bot + p["js_dome_top_h"]
    d["shaft_tip_stock"] = js_bot + p["js_shaft_tip_h"]
    d["shaft_trim"] = d["shaft_tip_stock"] - d["cap_bot"] + 0.2  # tip just below cap face
    # swept envelope of the cap when tilted
    zp = d["js_pivot_z"]
    prof = [(p["cap_d"] / 2, d["cap_top"]), (p["cap_d"] / 2, d["cap_bot"]),
            (p["cap_hub_d"] / 2, d["cap_bot"]), (p["cap_hub_d"] / 2, d["hub_bot"])]
    sw = []
    n = 30
    for i in range(n + 1):
        t = math.radians(p["js_tilt"]) * i / n
        for r, z in prof:
            h = z - zp
            sw.append((r * math.cos(t) + h * math.sin(t), -r * math.sin(t) + h * math.cos(t) + zp))
    d["swept"] = sw
    r_p = max(r for r, _ in sw) + p["well_clear"]
    frame_r = p["js_body_w"] / math.sqrt(2)          # half-diagonal of the fixed frame
    r_h = max(p["js_dome_r"], frame_r) + p["well_clear"]
    z_f = min(z - p["well_clear"] + (r_p - r) for r, z in sw if r >= r_h)
    z_f = min(z_f, p["H"])
    d["well_rp"], d["well_rh"], d["well_zf"] = r_p, r_h, z_f
    d["well_zfb"] = z_f - (r_p - r_h)
    # key well
    d["kw_w"] = p["keycap_w"] + 2 * p["keycap_clear"]
    d["kw_d"] = p["keycap_d"] + 2 * p["keycap_clear"]
    d["kp_top"] = p["H"] - p["key_stack"] - p["key_recess"]
    d["kp_bot"] = d["kp_top"] - p["key_plate_t"]
    # display placement
    gl, pl = p["disp_glass_L"], p["disp_pcb"][0]
    if p["disp_header_side"] < 0:
        d["disp_x0"], d["disp_x1"] = gl / 2 - pl, gl / 2
    else:
        d["disp_x0"], d["disp_x1"] = -gl / 2, -gl / 2 + pl
    d["disp_y0"] = p["disp_cy"] - p["disp_pcb"][1] / 2
    d["disp_y1"] = p["disp_cy"] + p["disp_pcb"][1] / 2
    d["lid_in_z0"] = p["H"] + p["bezel_t"]
    d["lid_in_z1"] = p["H"] + p["T"] - p["back_t"]
    d["disp_back_z"] = d["lid_in_z0"] + p["disp_stack"]
    # esp32 placement (USB end against the left wall)
    d["esp_x0"] = -p["W"] / 2 + p["wall"]
    d["esp_x1"] = d["esp_x0"] + p["esp_L"]
    d["esp_port_z"] = p["floor"] + p["esp_under"] + p["esp_pcb_t"] + 1.6
    d["tp_port_z"] = p["floor"] + p["tp_pad"] + p["tp_pcb_t"] + 1.6
    return d


D = derive(P)


# =============================================================================
# hinge pieces shared by base and lid
# =============================================================================
def wire_cut_base(p, d):
    """Tunnel: base interior -> back wall -> band -> up into the middle base knuckle -> axis bore."""
    ya, za = d["ya"], d["za"]
    yc = ya - p["chan_d"] / 2 - 0.6  # keep the vertical channel inside the front half of the knuckle
    c = cyl_x(-p["knuckle_mid_w"] / 2 - 0.1, p["bore_d"] / 2, ya, za, p["bore_d"] / 2)
    c = c.union(cyl_z(0.0, yc, 9.0, za, p["chan_d"] / 2))
    c = c.union(box(-3.0, 3.0, p["L"] - p["wall"] - 1.0, yc + p["chan_d"] / 2 - 0.5, 9.0, 14.0))
    return c


def wire_cut_lid(p, d):
    ya, za = d["ya"], d["za"]
    yc = ya - p["chan_d"] / 2 - 0.6
    x_r = -p["knuckle_mid_w"] / 2 - p["hinge_gap"]
    xc = d["x_wire_lid"]
    c = cyl_x(x_r - 9.0, x_r + 0.1, ya, za, p["bore_d"] / 2)
    c = c.union(cyl_z(xc, yc, za, d["lid_in_z1"] - 0.5, p["chan_d"] / 2))
    c = c.union(box(xc - 2.5, xc + 2.5, p["L"] - p["wall"] - 1.0, yc + p["chan_d"] / 2 - 0.5,
                    d["lid_in_z1"] - 5.0, d["lid_in_z1"] - 0.5))
    return c


# =============================================================================
# BASE
# =============================================================================
def build_base_shell(p, d):
    W, L, H = p["W"], p["L"], p["H"]
    hw, t = W / 2, p["wall"]
    deck_bot = H - p["deck"]

    outer = rbox(-hw, hw, 0, L, p["floor"], H, p["corner_r"])
    outer = fillet_where(outer, p["edge_r"] * 1.2,
                         lambda bb: abs(bb.zmin - H) < 1e-3 and abs(bb.zmax - H) < 1e-3 and bb.ymax < L - 1e-3)
    cavity = rbox(-hw + t, hw - t, t, L - t, p["floor"] - 1, deck_bot, p["corner_r"] - t)
    shell = outer.cut(cavity)

    # --- key wells: window + skirt + integral 1.3 mm plate ---------------------
    kw_w, kw_d = d["kw_w"], d["kw_d"]
    sk = p["key_skirt"]
    for kx in p["key_x"]:
        shell = shell.union(cbox(kx, p["key_y"], kw_w + 2 * sk, kw_d + 2 * sk, d["kp_bot"], H, 2.0 + sk))
    for kx in p["key_x"]:
        shell = shell.cut(cbox(kx, p["key_y"], kw_w, kw_d, d["kp_top"], H + 1, 1.2))
        shell = shell.cut(cbox(kx, p["key_y"], p["key_hole"], p["key_hole"], d["kp_bot"] - 1, d["kp_top"] + 0.01))

    # --- thumbstick well: vertical skirt + 45 deg funnel (prints deck-down) -----
    rp, rh, zf, zfb, tw = d["well_rp"], d["well_rh"], d["well_zf"], d["well_zfb"], p["well_wall"]
    body_pts = [(rh, zfb), (rp, zf), (rp, H), (rp + tw, H),
                (rp + tw, zf - 0.414 * tw), (rh, zfb - 1.414 * tw)]
    if zf >= H - 1e-6:
        body_pts = [(rh, zfb), (rp, zf), (rp + tw, H), (rh, zfb - 1.414 * tw)]
    shell = shell.union(revolve_rz(body_pts, p["stick_x"], p["stick_y"]))
    cav_pts = [(0, H + 2), (rp, H + 2), (rp, zf), (rh, zfb), (rh, zfb - 20), (0, zfb - 20)]
    shell = shell.cut(revolve_rz(cav_pts, p["stick_x"], p["stick_y"]))

    # --- speaker ring + mic rings under the deck --------------------------------
    sr = p["spk_d"] / 2 + 0.3
    ring = cyl_z(p["spk_x"], p["spk_y"], deck_bot - p["spk_ring_h"], deck_bot + 0.01, sr + 1.6).cut(
        cyl_z(p["spk_x"], p["spk_y"], deck_bot - p["spk_ring_h"] - 1, deck_bot + 0.02, sr))
    for a in (90, 210, 330):  # crush ribs for a press fit
        cx = p["spk_x"] + (sr - 0.2) * math.cos(math.radians(a))
        cy = p["spk_y"] + (sr - 0.2) * math.sin(math.radians(a))
        ring = ring.union(cyl_z(cx, cy, deck_bot - p["spk_ring_h"], deck_bot, 0.6))
    shell = shell.union(ring)
    mr = p["mic_d"] / 2 + 0.25
    for mx, my in p["mic_xy"]:
        shell = shell.union(cyl_z(mx, my, deck_bot - p["mic_ring_h"], deck_bot + 0.01, mr + 1.2).cut(
            cyl_z(mx, my, deck_bot - p["mic_ring_h"] - 1, deck_bot + 0.02, mr)))

    # --- grille: one field of holes over speaker + both mics --------------------
    gx0, gx1, gy0, gy1 = p["grille"]
    pitch, hd = p["grille_pitch"], p["grille_hole_d"]
    pts, row, y = [], 0, gy0 + 2.0
    while y <= gy1 - 2.0 + 1e-6:
        x = gx0 + 2.0 + (pitch / 2 if row % 2 else 0)
        while x <= gx1 - 2.0 + 1e-6:
            pts.append((x, y))
            x += pitch
        y += pitch * math.sqrt(3) / 2
        row += 1
    holes = (cq.Workplane("XY").workplane(offset=deck_bot - 0.5)
             .pushPoints(pts).circle(hd / 2).extrude(p["deck"] + 1))
    shell = shell.cut(holes)
    d["grille_n"] = len(pts)

    # --- bosses for the floor screws -------------------------------------------
    z_boss_bot = p["floor"] + p["floor_pad"]
    for bx, by in BASE_SCREWS:
        shell = shell.union(cyl_z(bx, by, z_boss_bot, deck_bot + 0.01, p["boss_d"] / 2))
        shell = shell.cut(cyl_z(bx, by, z_boss_bot - 0.1, z_boss_bot + p["insert_depth"], p["insert_hole_d"] / 2))

    # --- back wall tongues (hook into the band) --------------------------------
    for x0, x1 in ((-60.0, -20.0), (20.0, 60.0)):
        shell = shell.union(box(x0, x1, L - 0.01, L + 1.8, p["floor"], p["floor"] + 2.5))

    # --- slide switch pocket on the right wall ---------------------------------
    bx_w, bx_d, bx_h = p["sw_body"]
    xw = hw - t
    blk = box(xw - bx_d - 2.0, xw + 0.01, p["sw_y"] - bx_w / 2 - 2.0, p["sw_y"] + bx_w / 2 + 2.0,
              p["sw_z"] - bx_h / 2, deck_bot + 0.01)
    blk = blk.cut(box(xw - bx_d, xw + 0.02, p["sw_y"] - bx_w / 2, p["sw_y"] + bx_w / 2,
                      p["sw_z"] - bx_h / 2 - 1, p["sw_z"] + bx_h / 2))
    shell = shell.union(blk)
    sl_y, sl_z = p["sw_slot"]
    shell = shell.cut(box(xw - 0.5, hw + 1, p["sw_y"] - sl_y / 2, p["sw_y"] + sl_y / 2,
                          p["sw_z"] - sl_z / 2, p["sw_z"] + sl_z / 2))

    # --- left wall: ESP32 USB-C + TP4056 charge port ---------------------------
    def wall_slot(yc, zc, wy, hz):
        s = box(-hw - 1, -hw + t + 0.5, yc - wy / 2, yc + wy / 2, zc - hz / 2, zc + hz / 2)
        return s.edges("|X").fillet(min(wy, hz) / 2 - 0.05)
    shell = shell.cut(wall_slot(p["esp_y"], d["esp_port_z"], *p["esp_slot"]))
    shell = shell.cut(wall_slot(p["tp_y"], d["tp_port_z"], *p["tp_slot"]))

    # --- wire pass through the back wall ---------------------------------------
    shell = shell.cut(wire_cut_base(p, d))
    return shell


def build_base_bottom(p, d):
    W, L, H, R = p["W"], p["L"], p["H"], p["R"]
    hw, t, f = W / 2, p["wall"], p["floor"]
    ya, za, Rk = d["ya"], d["za"], d["Rk"]

    floor = rbox(-hw, hw, 0, L + 1.0, 0, f, p["corner_r"])
    floor = fillet_where(floor, p["edge_r"],
                         lambda bb: abs(bb.zmin) < 1e-3 and abs(bb.zmax) < 1e-3 and bb.ymax < L - 1e-3)
    band = box(-hw, hw, L, L + 2 * R, 0, d["band_top"])
    base = floor.union(band)

    # base knuckles + their fill (front half only, so the lid can swing past)
    for x0, x1 in d["base_zones"]:
        base = base.union(box(x0, x1, L, ya, d["band_top"] - 0.01, za))
        base = base.union(cyl_x(x0, x1, ya, za, Rk))

    # pivot screws: counterbore + clearance through the end knuckles
    for (x0, x1), side in ((d["base_zones"][0], -1), (d["base_zones"][2], +1)):
        outer = x0 if side < 0 else x1
        inner = x1 if side < 0 else x0
        if side < 0:
            base = base.cut(cyl_x(outer - 1, outer + p["screw_head_cb"], ya, za, p["screw_head_d"] / 2))
            base = base.cut(cyl_x(outer - 1, inner + 0.1, ya, za, p["screw_clear_d"] / 2))
        else:
            base = base.cut(cyl_x(outer - p["screw_head_cb"], outer + 1, ya, za, p["screw_head_d"] / 2))
            base = base.cut(cyl_x(inner - 0.1, outer + 1, ya, za, p["screw_clear_d"] / 2))

    # slots in the band that take the shell's back-wall tongues
    for x0, x1 in ((-60.0, -20.0), (20.0, 60.0)):
        base = base.cut(box(x0 - 0.3, x1 + 0.3, L - 0.1, L + 2.1, f - 0.01, f + 2.8))

    # screw pads + counterbores from underneath
    for bx, by in BASE_SCREWS:
        base = base.union(cyl_z(bx, by, f - 0.01, f + p["floor_pad"], p["boss_d"] / 2))
        base = base.cut(cyl_z(bx, by, -1, p["screw_head_cb"], p["screw_head_d"] / 2))
        base = base.cut(cyl_z(bx, by, -1, f + p["floor_pad"] + 1, p["screw_clear_d"] / 2))

    # ---- component cradles -------------------------------------------------------
    def corner_ls(x0, x1, y0, y1, h, which=("fl", "fr", "bl", "br"), arm=5.0, th=1.2, c=0.3):
        out = []
        xa, xb, ya_, yb = x0 - c, x1 + c, y0 - c, y1 + c
        spec = {"fl": (xa, ya_, +1, +1), "fr": (xb, ya_, -1, +1), "bl": (xa, yb, +1, -1), "br": (xb, yb, -1, -1)}
        for k in which:
            cx, cy, sx, sy = spec[k]
            out.append(box(min(cx, cx - sx * th), max(cx, cx - sx * th), min(cy - sy * th, cy + sy * arm), max(cy - sy * th, cy + sy * arm), f - 0.01, f + h))
            out.append(box(min(cx, cx + sx * arm), max(cx, cx + sx * arm), min(cy, cy - sy * th), max(cy, cy - sy * th), f - 0.01, f + h))
        return out

    # ESP32: centre rail between the header rows + end stop
    e0, e1, ey = d["esp_x0"], d["esp_x1"], p["esp_y"]
    base = base.union(box(e0 + 8, e1 - 8, ey - 3, ey + 3, f - 0.01, f + p["esp_under"]))
    base = base.union(box(e1 + 0.3, e1 + 2.0, ey - 6, ey + 6, f - 0.01, f + p["esp_under"] + p["esp_pcb_t"] + 1.0))

    # battery
    bL, bW, bT = p["bat"]
    bx0, by0 = p["bat_x0"], p["bat_y0"]
    for s in corner_ls(bx0, bx0 + bL, by0, by0 + bW, 4.0, which=("fl",)):
        base = base.union(s)
    base = base.union(box(bx0 + 8, bx0 + 24, by0 - 1.5, by0 - 0.3, f - 0.01, f + 4.0))

    # thumbstick module: floor pocket + corner locators
    sx, sy = p["stick_x"], p["stick_y"]
    jw, jd = p["js_pcb_w"], p["js_pcb_d"]
    base = base.cut(cbox(sx, sy, jw + 0.6, jd + 0.6, f - p["js_floor_pocket"], f + 0.01))
    for s in corner_ls(sx - jw / 2, sx + jw / 2, sy - jd / 2, sy + jd / 2, 3.0 + p["js_standoff"]):
        base = base.union(s)
    if p["js_standoff"] > 0:
        for ox in (-jw / 2 + 3, jw / 2 - 3):
            for oy in (-jd / 2 + 3, jd / 2 - 3):
                base = base.union(cyl_z(sx + ox, sy + oy, f - p["js_floor_pocket"], d["js_bot"], 2.0))

    # TP4056: raised pad so the port clears the floor seam, plus an end stop
    tx0 = -hw + t
    base = base.union(box(tx0, tx0 + p["tp_L"], p["tp_y"] - p["tp_W"] / 2, p["tp_y"] + p["tp_W"] / 2,
                          f - 0.01, f + p["tp_pad"]))
    base = base.union(box(tx0 + p["tp_L"] + 0.3, tx0 + p["tp_L"] + 1.8, p["tp_y"] - 5, p["tp_y"] + 5,
                          f - 0.01, f + p["tp_pad"] + p["tp_pcb_t"] + 1.5))

    # amplifier
    aw, ad, _ = p["amp"]
    ax, ay = p["amp_xy"]
    for s in corner_ls(ax, ax + aw, ay, ay + ad, 3.0, which=("fl", "fr")):
        base = base.union(s)

    # wire tunnel
    base = base.cut(wire_cut_base(p, d))
    return base


# =============================================================================
# LID
# =============================================================================
def build_lid_bezel(p, d):
    W, L, H = p["W"], p["L"], p["H"]
    hw = W / 2
    z0, z1 = H, H + p["bezel_t"]
    bez = rbox(-hw, hw, 0, L, z0, z1, p["corner_r"])
    bez = fillet_where(bez, p["edge_r"],
                       lambda bb: abs(bb.zmin - z0) < 1e-3 and abs(bb.zmax - z0) < 1e-3 and bb.ymax < L - 1e-3)

    # display locating frame (glass rests on the bezel's inner face)
    c = 0.3
    x0, x1, y0, y1 = d["disp_x0"] - c, d["disp_x1"] + c, d["disp_y0"] - c, d["disp_y1"] + c
    fr = box(x0 - 1.2, x1 + 1.2, y0 - 1.2, y1 + 1.2, z1 - 0.01, z1 + 3.0).cut(box(x0, x1, y0, y1, z1 - 1, z1 + 4))
    bez = bez.union(fr)

    # visible window
    vw, vh = p["disp_view"]
    gcx = p["disp_view_dxy"][0]  # glass is centred on x = 0
    gcy = p["disp_cy"] + p["disp_view_dxy"][1]
    win = cbox(gcx, gcy, vw + 0.4, vh + 0.4, z0 - 1, z1 + 1, 1.5)
    bez = bez.cut(win)
    # chamfer-like step so the window edge looks thin from the front
    bez = bez.cut(cbox(gcx, gcy, vw + 2.4, vh + 2.4, z0 - 1, z0 + 0.6, 2.5))

    # status LED: light hole + pocket walls
    lx, ly = p["led_xy"]
    lp = p["led_pocket"]
    bez = bez.union(cbox(lx, ly, lp + 2.0, lp + 2.0, z1 - 0.01, z1 + 2.5).cut(cbox(lx, ly, lp, lp, z1 - 1, z1 + 3)))
    bez = bez.cut(cyl_z(lx, ly, z0 - 1, z1 + 1, p["led_hole_d"] / 2))

    # screw bosses with inserts (screws come from the lid back)
    boss_top = d["lid_in_z1"] - p["floor_pad"]
    for bx, by in LID_SCREWS:
        bez = bez.union(cyl_z(bx, by, z1 - 0.01, boss_top, p["boss_d"] / 2))
        bez = bez.cut(cyl_z(bx, by, boss_top - p["insert_depth"], boss_top + 0.1, p["insert_hole_d"] / 2))
    return bez


def build_lid_back(p, d):
    W, L, H, T, R = p["W"], p["L"], p["H"], p["T"], p["R"]
    hw, t = W / 2, p["wall"]
    ya, za, Rk = d["ya"], d["za"], d["Rk"]
    z0, ztop = H + p["bezel_t"], H + T

    outer = rbox(-hw, hw, 0, L, z0, ztop, p["corner_r"])
    outer = fillet_where(outer, p["edge_r"] * 1.5,
                         lambda bb: abs(bb.zmin - ztop) < 1e-3 and abs(bb.zmax - ztop) < 1e-3 and bb.ymax < L - 1e-3)
    cavity = rbox(-hw + t, hw - t, t, L - t, z0 - 1, d["lid_in_z1"], p["corner_r"] - t)
    lid = outer.cut(cavity)

    # fill behind the main body up to the hinge axis; full depth only over lid knuckles
    lid = lid.union(box(-hw, hw, L - 0.01, ya, za + R + p["hinge_clear"], ztop))
    for x0, x1 in d["lid_zones"]:
        lid = lid.union(box(x0, x1, L, ya, za, za + R + p["hinge_clear"] + 0.01))
        lid = lid.union(cyl_x(x0, x1, ya, za, Rk))

    # inserts for the two friction pivots
    (a0, a1), (b0, b1) = d["lid_zones"]
    lid = lid.cut(cyl_x(a0 - 0.1, a0 + p["insert_depth"], ya, za, p["insert_hole_d"] / 2))
    lid = lid.cut(cyl_x(b1 - p["insert_depth"], b1 + 0.1, ya, za, p["insert_hole_d"] / 2))

    # screw pads + counterbores (heads on the outer face)
    for bx, by in LID_SCREWS:
        lid = lid.union(cyl_z(bx, by, d["lid_in_z1"] - p["floor_pad"], d["lid_in_z1"] + 0.01, p["boss_d"] / 2))
        lid = lid.cut(cyl_z(bx, by, ztop - p["screw_head_cb"], ztop + 1, p["screw_head_d"] / 2))
        lid = lid.cut(cyl_z(bx, by, d["lid_in_z1"] - p["floor_pad"] - 1, ztop + 1, p["screw_clear_d"] / 2))

    # pads that hold the display PCB against the bezel (add 0.5 mm foam)
    pz0 = d["disp_back_z"] + 0.3
    for px in (-p["disp_glass_L"] / 2 + 7, p["disp_glass_L"] / 2 - 7):
        for py in (d["disp_y0"] + 5, d["disp_y1"] - 5):
            lid = lid.union(cbox(px, py, 6, 6, pz0, d["lid_in_z1"] + 0.01))

    lid = lid.cut(wire_cut_lid(p, d))
    return lid


def build_stick_cap(p, d):
    """Built in place (assembly position)."""
    sx, sy = p["stick_x"], p["stick_y"]
    r = p["cap_d"] / 2
    cap = cyl_z(sx, sy, d["cap_bot"], d["cap_top"], r)
    try:
        cap = cap.faces(">Z").edges().chamfer(0.6)
    except Exception:  # noqa: BLE001
        pass
    cap = cap.union(cyl_z(sx, sy, d["hub_bot"], d["cap_bot"] + 0.01, p["cap_hub_d"] / 2))
    cap = cap.cut(cyl_z(sx, sy, d["hub_bot"] - 1, d["cap_top"] - 0.8, p["js_shaft_d"] / 2 + 0.1))
    return cap


# =============================================================================
# reference components (for checks + STEP context)
# =============================================================================
def build_refs(p, d):
    f, H = p["floor"], p["H"]
    refs = {}
    e0, e1, ey = d["esp_x0"], d["esp_x1"], p["esp_y"]
    zb = f + p["esp_under"]
    refs["esp32"] = box(e0, e1, ey - p["esp_W"] / 2, ey + p["esp_W"] / 2, zb, zb + p["esp_pcb_t"] + p["esp_top"])
    bL, bW, bT = p["bat"]
    refs["battery"] = box(p["bat_x0"], p["bat_x0"] + bL, p["bat_y0"], p["bat_y0"] + bW, f, f + bT)
    deck_bot = H - p["deck"]
    refs["speaker"] = cyl_z(p["spk_x"], p["spk_y"], deck_bot - p["spk_t"], deck_bot - 0.05, p["spk_d"] / 2)
    for i, (mx, my) in enumerate(p["mic_xy"]):
        refs[f"mic{i+1}"] = cyl_z(mx, my, deck_bot - 2.2, deck_bot - 0.3, p["mic_d"] / 2)
    tx0 = -p["W"] / 2 + p["wall"]
    refs["tp4056"] = box(tx0, tx0 + p["tp_L"], p["tp_y"] - p["tp_W"] / 2, p["tp_y"] + p["tp_W"] / 2,
                         f + p["tp_pad"], f + p["tp_pad"] + p["tp_pcb_t"] + 3.3)
    bw, bd, bh = p["buck"]
    refs["buck_boost"] = cbox(p["buck_xy"][0], p["buck_xy"][1], bw, bd, f, f + bh)
    aw, ad, ah = p["amp"]
    refs["amp"] = box(p["amp_xy"][0], p["amp_xy"][0] + aw, p["amp_xy"][1], p["amp_xy"][1] + ad, f, f + ah)
    xw = p["W"] / 2 - p["wall"]
    sw_w, sw_d, sw_h = p["sw_body"]
    refs["slide_switch"] = box(xw - sw_d + 0.2, xw - 0.1, p["sw_y"] - sw_w / 2 + 0.2, p["sw_y"] + sw_w / 2 - 0.2,
                               p["sw_z"] - sw_h / 2 + 0.2, p["sw_z"] + sw_h / 2 - 0.2)
    # thumbstick module (PCB + fixed frame + moving dome)
    sx, sy, jb = p["stick_x"], p["stick_y"], d["js_bot"]
    js = cbox(sx, sy, p["js_pcb_w"], p["js_pcb_d"], jb, jb + p["js_pcb_t"])
    js = js.union(cbox(sx, sy, p["js_body_w"], p["js_body_w"], jb + p["js_pcb_t"] - 0.01, jb + p["js_body_h"]))
    dome = cq.Workplane("XY").sphere(p["js_dome_r"]).translate((sx, sy, d["js_pivot_z"]))
    dome = dome.intersect(box(sx - 20, sx + 20, sy - 20, sy + 20, jb + p["js_body_h"] - 0.5, d["dome_top"]))
    refs["thumbstick"] = js.union(dome)
    # keys (switch top housing + keycap, at rest)
    for i, kx in enumerate(p["key_x"]):
        sw = cbox(kx, p["key_y"], 15.0, 15.0, d["kp_top"], d["kp_top"] + 3.0)
        kc = cbox(kx, p["key_y"], p["keycap_w"], p["keycap_d"], d["kp_top"] + 3.0, d["kp_top"] + p["key_stack"], 1.5)
        refs[f"key{i+1}"] = sw.union(kc)
    # display stack + LED
    refs["display"] = box(d["disp_x0"], d["disp_x1"], d["disp_y0"], d["disp_y1"], d["lid_in_z0"], d["disp_back_z"])
    lx, ly = p["led_xy"]
    refs["led"] = cbox(lx, ly, 9.5, 9.5, d["lid_in_z0"] + 0.05, d["lid_in_z0"] + 2.0)
    return refs


# =============================================================================
# export + checks
# =============================================================================
def to_mesh(wp, tol=0.05):
    import trimesh
    path = os.path.join(OUT, "_tmp.stl")
    cq.exporters.export(wp, path, tolerance=tol, angularTolerance=0.15)
    m = trimesh.load(path)
    os.remove(path)
    return m


def to_manifold(mesh):
    import numpy as np
    import manifold3d as mf
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
                               tri_verts=np.asarray(mesh.faces, dtype=np.uint32)))


def mvol(m):
    v = m.volume() if callable(getattr(m, "volume", None)) else m.get_volume()
    return float(v)


def fmt_bb(m):
    b = m.bounding_box()
    return "x[{:.1f},{:.1f}] y[{:.1f},{:.1f}] z[{:.1f},{:.1f}]".format(b[0], b[3], b[1], b[4], b[2], b[5])


def rot_lid(m, theta_deg, ya, za):
    """Open the lid by theta (front edge goes up)."""
    a = -math.radians(theta_deg)
    c, s = math.cos(a), math.sin(a)
    # rotation about x through (ya, za): y' = c(y-ya) - s(z-za) + ya ; z' = s(y-ya) + c(z-za) + za
    M = [[1, 0, 0, 0],
         [0, c, -s, ya - c * ya + s * za],
         [0, s, c, za - s * ya - c * za]]
    return m.transform(M)


def rot_about(m, axis_xy, pivot, tilt_deg, direction_deg):
    """Tilt a part about a horizontal axis through pivot, axis perpendicular to direction."""
    import numpy as np
    phi = math.radians(direction_deg)
    k = np.array([-math.sin(phi), math.cos(phi), 0.0])  # rotation axis
    t = math.radians(tilt_deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    Rm = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    pv = np.array(pivot)
    tr = pv - Rm @ pv
    M = [[*Rm[0], tr[0]], [*Rm[1], tr[1]], [*Rm[2], tr[2]]]
    return m.transform(M)


def main():
    os.makedirs(OUT, exist_ok=True)
    preview = "--no-preview" not in sys.argv
    p, d = P, D
    print("building parts ...")
    parts = {
        "base_bottom": build_base_bottom(p, d),
        "base_shell": build_base_shell(p, d),
        "lid_bezel": build_lid_bezel(p, d),
        "lid_back": build_lid_back(p, d),
        "stick_cap": build_stick_cap(p, d),
    }
    refs = build_refs(p, d)

    # ---- STEP: assembly in closed position, parts + reference components -------
    colors = {"base_bottom": (0.80, 0.80, 0.78), "base_shell": (0.86, 0.86, 0.84),
              "lid_bezel": (0.20, 0.20, 0.22), "lid_back": (0.86, 0.86, 0.84), "stick_cap": (0.95, 0.95, 0.93)}
    asm = cq.Assembly(name="agent_controller_v0")
    for k, v in parts.items():
        asm.add(v, name=k, color=cq.Color(*colors[k]))
    for k, v in refs.items():
        asm.add(v, name=f"REF_{k}", color=cq.Color(0.2, 0.5, 0.9, 0.5))
    asm.save(os.path.join(OUT, "agent_controller_v0.step"))
    for k, v in parts.items():
        cq.exporters.export(v, os.path.join(OUT, f"{k}.step"))

    # ---- STL in print orientation ---------------------------------------------
    import trimesh
    H, T = p["H"], p["T"]
    meshes = {k: to_mesh(v) for k, v in parts.items()}
    ref_meshes = {k: to_mesh(v, 0.1) for k, v in refs.items()}
    print_xf = {
        "base_bottom": lambda m: m,
        "base_shell": lambda m: m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])),
        "lid_bezel": lambda m: m,
        "lid_back": lambda m: m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])),
        "stick_cap": lambda m: m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0])),
    }
    rep = []
    rep.append("AGENT CONTROLLER v0 -- FIT REPORT")
    rep.append("=" * 60)
    rep.append(f"outer size closed: {p['W']:.0f} x {p['L'] + 2 * p['R']:.0f} x {p['H'] + p['T']:.1f} mm "
               f"(base {p['H']:.1f} + lid {p['T']:.1f})")
    rep.append("")
    rep.append("PARTS (print orientation)")
    for k, m in meshes.items():
        pm = m.copy()
        print_xf[k](pm)
        pm.apply_translation(-pm.bounds[0] + [0, 0, 0])
        pm.export(os.path.join(OUT, f"{k}.stl"))
        bodies = len(pm.split(only_watertight=False))
        ext = pm.extents
        fits = "fits" if ext[0] <= 220 and ext[1] <= 220 and ext[2] <= 250 else "TOO BIG FOR ENDER 3"
        rep.append(f"  {k:12s} {ext[0]:6.1f} x {ext[1]:5.1f} x {ext[2]:5.1f}  watertight={pm.is_watertight}  "
                   f"bodies={bodies}  vol={pm.volume / 1000:6.1f} cm3  ({fits})")

    # ---- interference checks --------------------------------------------------
    M = {k: to_manifold(m) for k, m in meshes.items()}
    MR = {k: to_manifold(m) for k, m in ref_meshes.items()}
    rep.append("")
    rep.append("CLOSED: part-vs-part overlap (should all be ~0)")
    keys = list(M)
    bad = 0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            x = M[keys[i]] ^ M[keys[j]]
            v = mvol(x)
            if v > 0.5:
                bad += 1
                rep.append(f"  !! {keys[i]} x {keys[j]}: {v:.1f} mm3  bbox {fmt_bb(x)}")
    if not bad:
        rep.append("  ok")
    rep.append("")
    rep.append("CLOSED: component-vs-shell overlap (should all be ~0)")
    bad = 0
    for rk, rm in MR.items():
        for pk, pm in M.items():
            x = rm ^ pm
            v = mvol(x)
            if rk == "speaker" and pk == "base_shell" and v < 8:
                rep.append(f"  speaker press-fit ribs bite {v:.1f} mm3 (intended)")
                continue
            if v > 0.5:
                bad += 1
                rep.append(f"  !! {rk} hits {pk}: {v:.1f} mm3  bbox {fmt_bb(x)}")
    if not bad:
        rep.append("  ok")

    # lid swing
    lid = M["lid_back"] + M["lid_bezel"]
    base = M["base_bottom"] + M["base_shell"]
    stop = None
    for th in range(1, 181):
        v = mvol(rot_lid(lid, th, d["ya"], d["za"]) ^ base)
        if v > 0.5:
            stop = th
            break
    d["stop"] = stop
    rep.append("")
    rep.append(f"LID SWING: opens freely to {stop - 1 if stop else 180} deg "
               f"(hard stop where the lid's back face meets the hinge band)")
    rep.append("  friction comes from the two M2 pivot screws -- tighten until the lid holds its angle")

    # thumbstick tilt sweep
    rep.append("")
    rep.append("THUMBSTICK")
    cap = M["stick_cap"]
    shell_all = M["base_shell"] + M["base_bottom"]
    worst = 0.0
    pivot = (p["stick_x"], p["stick_y"], d["js_pivot_z"])
    for direc in range(0, 360, 45):
        for tilt in (p["js_tilt"] / 2, p["js_tilt"]):
            worst = max(worst, mvol(rot_about(cap, None, pivot, tilt, direc) ^ shell_all))
    rep.append(f"  cap tilt +/-{p['js_tilt']:.0f} deg in 8 directions: worst overlap {worst:.2f} mm3 "
               f"({'ok' if worst < 0.5 else 'COLLIDES'})")
    rep.append(f"  well: opening dia {2 * d['well_rp']:.1f}, funnel from z={d['well_zf']:.1f} down to "
               f"z={d['well_zfb']:.1f} at dia {2 * d['well_rh']:.1f}")
    fr_top = d["js_bot"] + p["js_body_h"]
    piv_to_edge = math.hypot(d["well_rh"], d["well_zfb"] - d["js_pivot_z"])
    rep.append(f"  funnel inner edge is {piv_to_edge - p['js_dome_r']:.1f} mm outside the dome sphere "
               f"({'ok' if piv_to_edge - p['js_dome_r'] > 0.3 else 'TOO CLOSE'})")
    rep.append(f"  cap hub bottom z={d['hub_bot']:.1f}, dome top z={d['dome_top']:.1f}: "
               f"gap {d['hub_bot'] - d['dome_top']:.1f} mm ({'ok' if d['hub_bot'] - d['dome_top'] >= 0.5 else 'TOO TIGHT -- raise H'})")
    rep.append(f"  module frame top z={fr_top:.1f}")
    rep.append(f"  >> with these stick heights: trim ~{max(0.0, d['shaft_trim']):.1f} mm off the shaft, then glue the cap on")
    rep.append("")
    rep.append("KEYS")
    rep.append(f"  plate top z={d['kp_top']:.1f}, keycap top z={d['kp_top'] + p['key_stack']:.1f} "
               f"(deck z={p['H']:.1f})")
    rep.append("")
    rep.append("LID")
    rep.append(f"  display back z={d['disp_back_z']:.2f}, lid inner ceiling z={d['lid_in_z1']:.2f}: "
               f"{d['lid_in_z1'] - d['disp_back_z']:.2f} mm for solder joints -- trim the header pins to ~3 mm")
    rep.append("")
    rep.append(f"GRILLE: {d['grille_n']} holes")
    rep.append("")
    rep.append("FASTENERS: 9 x M2x6 socket cap + 9 x M2 heat-set inserts "
               "(3 base, 4 lid, 2 hinge pivots)")
    rep.append("")
    rep.append("MEASURE THESE WHEN PARTS ARRIVE (edit P, rerun):")
    for k, why in MEASURE:
        rep.append(f"  - {k}: {why}")
    text = "\n".join(rep)
    print(text)
    with open(os.path.join(OUT, "fit_report.txt"), "w") as fh:
        fh.write(text + "\n")

    if preview:
        render_previews(meshes, ref_meshes, d)


# =============================================================================
# previews (VTK, off-screen)
# =============================================================================
def _vtk_poly(mesh):
    import numpy as np
    import vtk
    from vtk.util import numpy_support as ns
    pts = vtk.vtkPoints()
    pts.SetData(ns.numpy_to_vtk(np.asarray(mesh.vertices, dtype=np.float64), deep=True))
    f = np.asarray(mesh.faces, dtype=np.int64)
    cells = np.hstack([np.full((len(f), 1), 3, dtype=np.int64), f]).ravel()
    ca = vtk.vtkCellArray()
    ca.SetCells(len(f), ns.numpy_to_vtkIdTypeArray(cells, deep=True))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(ca)
    return pd


def _render(items, cam_pos, focal, up, path, size=(1400, 1000), title=None, zoom=1.0):
    import vtk
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    rw = vtk.vtkRenderWindow()
    rw.SetOffScreenRendering(1)
    rw.SetSize(*size)
    rw.SetMultiSamples(8)
    rw.AddRenderer(ren)
    for mesh, rgb, *rest in items:
        opacity = rest[0] if rest else 1.0
        pd = _vtk_poly(mesh)
        nrm = vtk.vtkPolyDataNormals()
        nrm.SetInputData(pd)
        nrm.SetFeatureAngle(35)
        nrm.SplittingOn()
        nrm.Update()
        mp = vtk.vtkPolyDataMapper()
        mp.SetInputConnection(nrm.GetOutputPort())
        ac = vtk.vtkActor()
        ac.SetMapper(mp)
        pr = ac.GetProperty()
        pr.SetColor(*rgb)
        pr.SetOpacity(opacity)
        pr.SetAmbient(0.25)
        pr.SetDiffuse(0.75)
        pr.SetSpecular(0.15)
        pr.SetSpecularPower(20)
        ren.AddActor(ac)
        if opacity >= 1.0:
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
            ea.GetProperty().SetLineWidth(1.2)
            ea.GetProperty().SetOpacity(0.55)
            ren.AddActor(ea)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*cam_pos)
    cam.SetFocalPoint(*focal)
    cam.SetViewUp(*up)
    ren.ResetCamera()
    cam.Zoom(zoom)
    light = vtk.vtkLight()
    light.SetLightTypeToSceneLight()
    light.SetPosition(-200, -300, 400)
    light.SetFocalPoint(0, 40, 0)
    light.SetIntensity(0.45)
    ren.AddLight(light)
    if title:
        tx = vtk.vtkTextActor()
        tx.SetInput(title)
        tx.GetTextProperty().SetFontSize(26)
        tx.GetTextProperty().SetColor(0.2, 0.2, 0.2)
        tx.SetPosition(24, size[1] - 50)
        ren.AddActor2D(tx)
    rw.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.Update()
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(path)
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()


def render_previews(meshes, ref_meshes, d):
    import trimesh
    out = os.path.join(OUT, "preview")
    os.makedirs(out, exist_ok=True)

    def opened(m, th=115):
        mm = m.copy()
        mm.apply_transform(trimesh.transformations.rotation_matrix(-math.radians(th), [1, 0, 0], [0, d["ya"], d["za"]]))
        return mm

    def moved(m, dz=0.0, dy=0.0):
        mm = m.copy()
        mm.apply_translation([0, dy, dz])
        return mm

    shell_c = (0.86, 0.86, 0.84)
    bottom_c = (0.80, 0.80, 0.78)
    bezel_c = (0.16, 0.16, 0.18)
    screen_c = (0.05, 0.07, 0.12)
    cap_c = (0.97, 0.96, 0.93)
    comp = {"esp32": (0.10, 0.10, 0.12), "battery": (0.95, 0.78, 0.25), "speaker": (0.25, 0.25, 0.25),
            "mic1": (0.15, 0.45, 0.25), "mic2": (0.15, 0.45, 0.25), "tp4056": (0.15, 0.35, 0.75),
            "buck_boost": (0.15, 0.55, 0.75), "amp": (0.45, 0.25, 0.65), "slide_switch": (0.9, 0.9, 0.9),
            "thumbstick": (0.35, 0.35, 0.38), "key1": (0.80, 0.15, 0.20), "key2": (0.80, 0.15, 0.20),
            "key3": (0.80, 0.15, 0.20), "display": screen_c, "led": (0.2, 0.9, 0.4)}
    M, R = meshes, ref_meshes
    keys = [(R[f"key{i}"], cap_c) for i in (1, 2, 3)]
    f = (0, 40, 15)

    open_items = [(M["base_bottom"], bottom_c), (M["base_shell"], shell_c), (M["stick_cap"], cap_c),
                  (opened(M["lid_back"]), shell_c), (opened(M["lid_bezel"]), bezel_c),
                  (opened(R["display"]), screen_c)] + keys
    _render(open_items, (-170, -230, 230), f, (0, 0, 1), os.path.join(out, "1_open.png"), title="open, 115 deg")
    _render(open_items, (260, f[1], 30), f, (0, 0, 1), os.path.join(out, "3_side.png"), title="right side")
    closed = [(M["base_bottom"], bottom_c), (M["base_shell"], shell_c), (M["lid_back"], shell_c),
              (M["lid_bezel"], bezel_c)]
    _render(closed, (180, 300, 160), f, (0, 0, 1), os.path.join(out, "2_closed_back.png"), title="closed, hinge side")
    _render(closed, (-200, -250, 120), f, (0, 0, 1), os.path.join(out, "2b_closed_front.png"),
            title="closed, front left (USB + charge ports)")
    inside = [(M["base_bottom"], bottom_c)] + [(R[k], comp[k]) for k in R if k not in ("display", "led")]
    _render(inside, (-60, -120, 260), (0, 40, 0), (0, 1, 0), os.path.join(out, "4_inside_base.png"),
            title="inside the base (deck removed)", zoom=1.15)
    under = [(M["base_shell"], shell_c)] + [(R[k], comp[k]) for k in ("speaker", "mic1", "mic2", "slide_switch")] + keys
    _render(under, (0, 40, -300), (0, 40, 10), (0, 1, 0), os.path.join(out, "5_deck_underside.png"),
            title="deck from underneath", zoom=1.15)
    _render([(M["base_shell"], shell_c), (M["stick_cap"], cap_c)] + keys, (0, 40, 300), (0, 40, 10), (0, 1, 0),
            os.path.join(out, "6_deck_top.png"), title="deck, top view", zoom=1.15)
    ex = [(M["base_bottom"], bottom_c), (moved(M["base_shell"], 35), shell_c),
          (moved(M["stick_cap"], 55), cap_c), (moved(M["lid_bezel"], 80), bezel_c),
          (moved(R["display"], 92), screen_c), (moved(M["lid_back"], 120), shell_c)]
    ex += [(moved(R[k], 0), comp[k]) for k in R if k not in ("display", "led") and not k.startswith("key")]
    _render(ex, (-230, -260, 200), (0, 40, 60), (0, 0, 1), os.path.join(out, "7_exploded.png"),
            title="exploded", size=(1400, 1300))

    # contact sheet
    try:
        from PIL import Image
        names = ["1_open.png", "2_closed_back.png", "4_inside_base.png", "6_deck_top.png"]
        ims = [Image.open(os.path.join(out, n)) for n in names]
        w, h = ims[0].size
        sheet = Image.new("RGB", (w * 2, h * 2), "white")
        for i, im in enumerate(ims):
            sheet.paste(im.resize((w, h)), ((i % 2) * w, (i // 2) * h))
        sheet = sheet.resize((w, h))
        sheet.save(os.path.join(out, "overview.png"))
    except Exception as exc:  # noqa: BLE001
        print("contact sheet skipped:", exc)
    print(f"previews -> {out}")


if __name__ == "__main__":
    main()
