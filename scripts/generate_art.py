#!/usr/bin/env python3
"""Generate the Nord-themed generative SVG assets used in README.md.

Every image is computed from a small mathematical system (no external
image services, no rasterisation): a De Jong strange attractor, a Rule 90
cellular automaton, a Koch-curve L-system, and a Fourier-epicycle drawing
of a lemniscate. Pure standard library (math, cmath) - no third-party deps.

Run with: python3 scripts/generate_art.py
Writes SVGs into assets/svg/.
"""

import cmath
import math
import os

# --- Nord palette (https://www.nordtheme.com) -----------------------------
NORD0, NORD1, NORD2, NORD3 = "#2E3440", "#3B4252", "#434C5E", "#4C566A"
NORD4, NORD5, NORD6 = "#D8DEE9", "#E5E9F0", "#ECEFF4"
NORD7, NORD8, NORD9, NORD10 = "#8FBCBB", "#88C0D0", "#81A1C1", "#5E81AC"
NORD11, NORD12, NORD13, NORD14, NORD15 = (
    "#BF616A", "#D08770", "#EBCB8B", "#A3BE8C", "#B48EAD",
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "svg")


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def write(name, svg):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        f.write(svg)
    print(f"wrote {path} ({len(svg) / 1024:.1f} KiB)")


# ---------------------------------------------------------------------------
# 1. De Jong strange attractor -> header banner
# ---------------------------------------------------------------------------
def generate_de_jong():
    a, b, c, d = 1.4, -2.3, 2.4, -2.1
    n_points = 4500
    warmup = 20

    x, y = 0.1, 0.1
    pts = []
    for i in range(n_points + warmup):
        x, y = math.sin(a * y) - math.cos(b * x), math.sin(c * x) - math.cos(d * y)
        if i >= warmup:
            pts.append((x, y))

    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    pts.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))

    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
    miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)

    width, height, pad = 920, 260, 24
    avail_w, avail_h = width - 2 * pad, height - 2 * pad
    # Independent x/y scale: this is a point cloud, not a rigid shape, so
    # stretching it to fill the banner reads as intentional, not distorted.
    scale_x = avail_w / (maxx - minx)
    scale_y = avail_h / (maxy - miny)
    off_x = pad - minx * scale_x
    off_y = pad - miny * scale_y

    n_bands = 6
    band_colors = [NORD10, NORD9, NORD8, NORD7, NORD15, NORD14]
    band_radius = [0.9, 1.0, 1.05, 1.15, 1.3, 1.4]
    band_opacity = [0.4, 0.45, 0.5, 0.55, 0.75, 0.8]

    chunk = math.ceil(len(pts) / n_bands)
    groups = []
    for b_i in range(n_bands):
        band_pts = pts[b_i * chunk: (b_i + 1) * chunk]
        if not band_pts:
            continue
        circles = []
        for (px, py) in band_pts:
            sx = off_x + px * scale_x
            sy = off_y + py * scale_y
            circles.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{band_radius[b_i]}"/>')
        begin = b_i * 0.35
        groups.append(
            f'<g fill="{band_colors[b_i]}" fill-opacity="{band_opacity[b_i]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
            f'dur="1.1s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            + "".join(circles) + "</g>"
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="De Jong attractor, generative art header">
<defs>
<radialGradient id="bg" cx="50%" cy="45%" r="75%">
<stop offset="0%" stop-color="{NORD1}"/>
<stop offset="100%" stop-color="{NORD0}"/>
</radialGradient>
</defs>
<rect width="{width}" height="{height}" fill="url(#bg)"/>
{"".join(groups)}
</svg>'''
    write("de-jong-header.svg", svg)


# ---------------------------------------------------------------------------
# 2. Rule 90 cellular automaton -> section divider
# ---------------------------------------------------------------------------
def generate_rule90():
    cell = 4
    w_cells = 230
    h_rows = 17
    seeds = [23, 69, 115, 161, 207]

    row = [0] * w_cells
    for s in seeds:
        row[s] = 1
    rows = [row]
    for _ in range(h_rows - 1):
        prev = rows[-1]
        nxt = [0] * w_cells
        for i in range(1, w_cells - 1):
            nxt[i] = prev[i - 1] ^ prev[i + 1]
        rows.append(nxt)

    width, height = w_cells * cell, h_rows * cell
    rects = []
    for r_i, r in enumerate(rows):
        color = lerp_color(NORD8, NORD10, r_i / (h_rows - 1))
        for i, v in enumerate(r):
            if v:
                rects.append(
                    f'<rect x="{i * cell}" y="{r_i * cell}" width="{cell}" height="{cell}" fill="{color}"/>'
                )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Rule 90 cellular automaton divider">
<rect width="{width}" height="{height}" fill="{NORD1}"/>
<g opacity="0">
<animate attributeName="opacity" from="0" to="1" begin="0.1s" dur="1s" fill="freeze"/>
{"".join(rects)}
</g>
</svg>'''
    write("rule90-divider.svg", svg)


# ---------------------------------------------------------------------------
# 3. Koch curve L-system -> small ornament
# ---------------------------------------------------------------------------
def generate_lsystem_koch():
    axiom = "F"
    rules = {"F": "F+F--F+F"}
    iterations = 4
    angle_deg = 60

    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(ch, ch) for ch in s)

    x, y, heading = 0.0, 0.0, 0.0
    pts = [(x, y)]
    for ch in s:
        if ch == "F":
            x += math.cos(math.radians(heading))
            y += math.sin(math.radians(heading))
            pts.append((x, y))
        elif ch == "+":
            heading += angle_deg
        elif ch == "-":
            heading -= angle_deg

    minx, maxx = min(p[0] for p in pts), max(p[0] for p in pts)
    miny, maxy = min(p[1] for p in pts), max(p[1] for p in pts)
    bbox_w, bbox_h = maxx - minx, maxy - miny

    target_w, pad = 300, 20
    scale = target_w / bbox_w
    canvas_w = target_w + 2 * pad
    canvas_h = bbox_h * scale + 2 * pad

    d_parts = []
    for i, (px, py) in enumerate(pts):
        sx = pad + (px - minx) * scale
        sy = pad + (py - miny) * scale
        d_parts.append(f'{"M" if i == 0 else "L"}{sx:.2f},{sy:.2f}')
    d = " ".join(d_parts)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}" role="img" aria-label="Koch curve L-system ornament">
<path d="{d}" fill="none" stroke="{NORD14}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000">
<animate attributeName="stroke-dashoffset" from="1000" to="0" dur="1.7s" fill="freeze"
calcMode="spline" keySplines="0.3 0 0.2 1"/>
</path>
</svg>'''
    write("lsystem-koch.svg", svg)


# ---------------------------------------------------------------------------
# 4. Fourier epicycles tracing a lemniscate -> footer signature
# ---------------------------------------------------------------------------
def generate_fourier_epicycles():
    n_samples = 240
    n_epicycles = 10
    period = 8  # seconds per loop

    def lemniscate(t):
        return complex(math.cos(t), math.sin(t) * math.cos(t))

    ts = [2 * math.pi * n / n_samples for n in range(n_samples)]
    z = [lemniscate(t) for t in ts]

    coeffs = {}
    for k in range(-15, 16):
        c = sum(z[n] * cmath.exp(-1j * k * ts[n]) for n in range(n_samples)) / n_samples
        coeffs[k] = c

    chosen = sorted((k for k in coeffs if k != 0), key=lambda k: -abs(coeffs[k]))[:n_epicycles]
    chosen.sort(key=lambda k: -abs(coeffs[k]))  # largest radius first (outermost)

    reach = sum(abs(coeffs[k]) for k in chosen)
    canvas = 380
    center = canvas / 2
    scale = (center - 40) / reach

    epis = [(k, abs(coeffs[k]) * scale, math.degrees(cmath.phase(coeffs[k]))) for k in chosen]

    def build(idx):
        if idx == len(epis):
            return f'<circle cx="0" cy="0" r="4.5" fill="{NORD14}"><animate attributeName="r" values="4.5;5.5;4.5" dur="1.6s" repeatCount="indefinite"/></circle>'
        k, r, phase = epis[idx]
        to_deg = phase + 360 * k
        inner = build(idx + 1)
        return (
            f'<g><animateTransform attributeName="transform" type="rotate" '
            f'from="{phase:.2f}" to="{to_deg:.2f}" dur="{period}s" repeatCount="indefinite"/>'
            f'<circle cx="0" cy="0" r="{r:.2f}" fill="none" stroke="{NORD3}" stroke-opacity="0.4" stroke-width="1"/>'
            f'<line x1="0" y1="0" x2="{r:.2f}" y2="0" stroke="{NORD4}" stroke-opacity="0.3" stroke-width="1"/>'
            f'<g transform="translate({r:.2f},0)">{inner}</g></g>'
        )

    chain = build(0)

    # Reconstructed curve from the same truncated coefficient set, so the
    # traced path matches exactly what the epicycle chain draws.
    recon = []
    for n in range(n_samples + 1):
        t = ts[n % n_samples]
        s = sum(coeffs[k] * cmath.exp(1j * k * t) for k in chosen)
        recon.append((center + s.real * scale, center + s.imag * scale))
    trace_d = " ".join(f'{"M" if i == 0 else "L"}{px:.2f},{py:.2f}' for i, (px, py) in enumerate(recon))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas} {canvas}" role="img" aria-label="Fourier epicycles drawing a lemniscate, looping">
<rect width="{canvas}" height="{canvas}" fill="none"/>
<path d="{trace_d}" fill="none" stroke="{NORD8}" stroke-opacity="0.15" stroke-width="2"/>
<path d="{trace_d}" fill="none" stroke="{NORD8}" stroke-width="2.5" stroke-linecap="round"
pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000">
<animate attributeName="stroke-dashoffset" from="1000" to="0" dur="{period}s" repeatCount="indefinite"/>
</path>
<g transform="translate({center:.2f},{center:.2f})">
{chain}
</g>
</svg>'''
    write("fourier-epicycles-footer.svg", svg)


if __name__ == "__main__":
    generate_de_jong()
    generate_rule90()
    generate_lsystem_koch()
    generate_fourier_epicycles()
