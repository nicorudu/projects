"""Rev 3 layout drawing: top views (in line, block swung out) and a side view.

Design targets from docs/agent-controller-v0-blueprint.md (rev 3). Not print CAD:
the print model is made after the parts are measured (milestone M7a).

    python layout.py [output_folder]
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

# ---- design targets (mm) ----------------------------------------------------
W = 124            # width of base and controller
BASE_D = 72        # base depth
CTRL_D = 40        # controller depth
KEY_W = 80         # key section width
BLOCK_W = W - KEY_W
H = 22             # base and controller height
LID_D, LID_T = 82, 13
PLATE_W, PLATE_D, GAP = 25.5, 36, 0.8
DISH, CAP = 31, 26
OPEN_DEG = 105

INK, SOFT, FILL, BLOCK, ACCENT, GREEN = "#1b1f24", "#6b7280", "#eef0f3", "#dfe3e8", "#2563eb", "#22a55a"


def body(ax, xy, w, h, fc=FILL, **kw):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0,rounding_size=2.5", fc=fc, ec=INK, lw=1.4, **kw))


def dim(ax, p0, p1, text, off=(0, 0), ha="center", va="center"):
    ax.annotate("", p0, p1, arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1))
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], text, color=ACCENT, fontsize=8.5, ha=ha, va=va)


def note(ax, xy, xytext, text, ha="left"):
    ax.annotate(text, xy, xytext, fontsize=8.5, color=INK, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=SOFT, lw=0.8))


def base_top(ax):
    body(ax, (0, CTRL_D), W, BASE_D)
    for y in range(CTRL_D + 8, CTRL_D + BASE_D - 14, 3):          # ribs
        ax.plot([5, W - 5], [y, y], color="#c3c8d0", lw=0.8)
    ax.add_patch(Rectangle((4, CTRL_D + BASE_D - 9), W - 8, 5, fc="#cfd4db", ec=INK, lw=1))   # hinge bar
    ax.text(W / 2, CTRL_D + BASE_D / 2 + 2, "BASE\nribbed top · speaker under", ha="center", va="center", fontsize=9, color=INK)
    for x in (15, 65):                                             # dock magnets
        ax.add_patch(Circle((x, CTRL_D + 2.5), 2, fc=SOFT, ec="none"))
    ax.add_patch(Rectangle((34, CTRL_D + 0.6), 12, 3.6, fc="#c9a227", ec=INK, lw=0.8))        # contacts


def keys(ax):
    body(ax, (0, 0), KEY_W, CTRL_D)
    x = (KEY_W - 3 * PLATE_W - 2 * GAP) / 2
    for label in ("CANCEL", "SEND", "VOICE"):
        ax.add_patch(FancyBboxPatch((x, 2), PLATE_W, PLATE_D, boxstyle="round,pad=0,rounding_size=1.2", fc="white", ec=INK, lw=1))
        ax.text(x + PLATE_W / 2, 2 + PLATE_D / 2, label, ha="center", va="center", fontsize=7.5, color=INK)
        x += PLATE_W + GAP


def block(ax, swung):
    """Joystick block. Local frame: x 0..BLOCK_W to the right, y 0..CTRL_D back; pivot at local (0, 0)."""
    def T(px, py):
        if swung:                       # rotate 90 deg clockwise about the pivot
            px, py = py, -px
        return KEY_W + px, py
    ax.add_patch(Polygon([T(0, 0), T(BLOCK_W, 0), T(BLOCK_W, CTRL_D), T(0, CTRL_D)], closed=True, fc=BLOCK, ec=INK, lw=1.4))
    c = T(BLOCK_W / 2 - 1, CTRL_D / 2)
    ax.add_patch(Circle(c, DISH / 2, fc="#cfd4db", ec=INK, lw=1))
    ax.add_patch(Circle(c, CAP / 2, fc="white", ec=INK, lw=1))
    for a in range(0, 360, 90):                                   # ticks
        r0, r1 = DISH / 2 + 1, DISH / 2 + 3
        ax.plot([c[0] + r0 * math.cos(math.radians(a)), c[0] + r1 * math.cos(math.radians(a))],
                [c[1] + r0 * math.sin(math.radians(a)), c[1] + r1 * math.sin(math.radians(a))], color=INK, lw=1)
    g = T(BLOCK_W - 5.5, 5.5)
    ax.add_patch(Circle(g, 2.6, fc=GREEN, ec=INK, lw=0.8))
    for my in (11, 29):                                           # mic grilles on the end face
        a, b = T(BLOCK_W, my - 5), T(BLOCK_W, my + 5)
        ax.plot([a[0], b[0]], [a[1], b[1]], color=ACCENT, lw=4, solid_capstyle="round")
    ax.add_patch(Circle((KEY_W, 0), 4.75, fc="white", ec=INK, lw=1.2))    # pivot pin
    ax.add_patch(Circle((KEY_W, 0), 3, fc=INK, ec="none"))
    return c, g, T


def top_view(ax, swung):
    base_top(ax)
    keys(ax)
    c, g, T = block(ax, swung)
    ax.set_aspect("equal")
    ax.set_xlim(-34, W + 42)
    ax.set_ylim(-70, CTRL_D + BASE_D + 14)
    ax.axis("off")
    ax.text(W / 2, CTRL_D + BASE_D + 9, "back (USB-C cable)", ha="center", fontsize=8.5, color=SOFT)
    ax.text(KEY_W / 2, -62, "front (you)", ha="center", fontsize=8.5, color=SOFT)
    note(ax, (KEY_W, 0), (KEY_W - 30, -16), "pivot pin\n(wires inside)", ha="right")
    if swung:
        note(ax, (40, CTRL_D + 2.4), (-30, CTRL_D + 26), "charge\ncontacts", ha="left")
        note(ax, (15, CTRL_D + 2.5), (-30, CTRL_D + 6), "magnet", ha="left")
        ax.set_title("Desktop: joystick block swung out 90°", fontsize=11, color=INK, pad=4)
        m = T(BLOCK_W, CTRL_D / 2)
        note(ax, m, (m[0] + 12, m[1] - 14), "2 mics,\nfacing you")
        note(ax, g, (g[0] - 26, g[1] - 4), "green\nbutton", ha="right")
        note(ax, c, (c[0] + 30, c[1] + 8), "stick cap")
        ax.text(KEY_W + BLOCK_W / 2, CTRL_D / 2, "gap", ha="center", va="center", fontsize=8.5, color=SOFT)
    else:
        ax.set_title("In line: docked, or handheld", fontsize=11, color=INK, pad=4)
        note(ax, (W, CTRL_D / 2), (W + 8, CTRL_D / 2 + 16), "2 mics on\nthe end face")
        note(ax, g, (W + 8, -10), "green button")
        note(ax, c, (c[0] + 4, -24), "stick cap,\nno click", ha="center")
        dim(ax, (0, -34), (KEY_W, -34), f"key section {KEY_W}", off=(0, -5))
        dim(ax, (KEY_W, -34), (W, -34), f"block {BLOCK_W}", off=(0, -5))
        dim(ax, (0, -48), (W, -48), f"{W} mm wide", off=(0, -5))
        dim(ax, (-9, 0), (-9, CTRL_D), f"{CTRL_D}", off=(-7, 0))
        dim(ax, (-9, CTRL_D), (-9, CTRL_D + BASE_D), f"{BASE_D}", off=(-7, 0))


def side_view(ax):
    ax.add_patch(Rectangle((0, 0), BASE_D, H, fc=FILL, ec=INK, lw=1.4))
    ax.add_patch(Rectangle((BASE_D, 0), CTRL_D, H, fc=BLOCK, ec=INK, lw=1.4))
    ax.text(BASE_D / 2, H / 2, "base", ha="center", va="center", fontsize=9)
    ax.text(BASE_D + CTRL_D / 2, H / 2, "controller", ha="center", va="center", fontsize=9)
    ax.add_patch(Rectangle((0, H), LID_D, LID_T, fc="none", ec=SOFT, lw=1, ls="--"))          # lid closed
    ax.text(LID_D / 2, H + LID_T / 2, "lid, closed", ha="center", va="center", fontsize=8, color=SOFT)
    a = math.radians(OPEN_DEG)                                                                 # lid open, leaning back
    hx, hy = 3, H
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = [(hx, hy), (hx + LID_D * ux, hy + LID_D * uy), (hx + LID_D * ux + LID_T * nx, hy + LID_D * uy + LID_T * ny), (hx + LID_T * nx, hy + LID_T * ny)]
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.4))
    ax.text(hx + LID_D * 0.5 * ux + LID_T * 0.5 * nx, hy + LID_D * 0.5 * uy + LID_T * 0.5 * ny, "screen", ha="center", va="center", fontsize=8.5, rotation=OPEN_DEG - 180)
    dim(ax, (0, -7), (BASE_D + CTRL_D, -7), f"{BASE_D + CTRL_D} mm deep", off=(0, -5))
    dim(ax, (BASE_D + CTRL_D + 7, 0), (BASE_D + CTRL_D + 7, H), f"{H}", off=(6, 0))
    dim(ax, (BASE_D + CTRL_D + 24, 0), (BASE_D + CTRL_D + 24, H + LID_T), f"{H + LID_T} closed", off=(5, 0), ha="left")
    ax.text(-4, H * 0.5, "USB-C", ha="right", va="center", fontsize=8.5, color=SOFT)
    ax.text(BASE_D + CTRL_D + 4, H + 44, "you →", ha="left", va="center", fontsize=8.5, color=SOFT)
    ax.set_aspect("equal")
    ax.set_xlim(-55, BASE_D + CTRL_D + 62)
    ax.set_ylim(-20, 108)
    ax.axis("off")
    ax.set_title(f"Side view: lid opens to {OPEN_DEG}°", fontsize=11, color=INK, pad=4)


def main(out: Path):
    fig = plt.figure(figsize=(15, 6.2), dpi=160)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.15, 1], wspace=0.02)
    top_view(fig.add_subplot(gs[0]), swung=False)
    top_view(fig.add_subplot(gs[1]), swung=True)
    side_view(fig.add_subplot(gs[2]))
    fig.suptitle("AI Agent Controller — rev 3 layout (design targets, mm)", fontsize=13, color=INK, y=0.98)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "rev3-layout.png", bbox_inches="tight", facecolor="white")
    print("wrote", out / "rev3-layout.png")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out"))
