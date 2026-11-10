# Make the README charts (static SVG, light + dark, English + Japanese) from the measured values in the README table.
# Grouped columns, one panel per machine (each panel its own scale), solid part = the lowest of the repeated runs,
# lighter part above = the spread up to the highest run. Run: python tools/make_charts.py  -> docs/img/*.svg
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "img")

# (low, high) per recall threshold 0.90 / 0.95 / 0.99; None = not measured on that machine
DATA = {
    "xeon": {
        "graph":       [(16253, 16253), (9851, 9851), (4414, 4414)],
        "partitioned": [(12331, 14725), (8694, 10493), (3302, 4138)],
        "qsgngt":      [(16339, 16809), (10282, 10618), (3408, 3789)],
        "scann":       [(4438, 4508), (2190, 2219), (783, 794)],
        "hnswlib":     None,
    },
    "9950x": {
        "graph":       [(36951, 36951), (21800, 21800), (9440, 9440)],
        "partitioned": [(34670, 34670), (24321, 24321), (9747, 9747)],
        "qsgngt":      [(27678, 27678), (15089, 15089), (6099, 6099)],
        "scann":       [(15611, 15611), (8195, 8195), (3085, 3085)],
        "hnswlib":     [(4268, 4268), (1898, 1898), (685, 685)],
    },
}
SERIES = ["graph", "partitioned", "qsgngt", "scann", "hnswlib"]   # fixed categorical order = slot order

TEXT = {
    "en": {
        "names": {"graph": "KCI-Vec graph", "partitioned": "KCI-Vec partitioned", "qsgngt": "qsgngt 5.0.0",
                  "scann": "ScaNN 1.4.2", "hnswlib": "hnswlib 0.8.0"},
        "panels": {"xeon": "Intel Xeon 8375C (AWS r6id.4xlarge)", "9950x": "AMD Ryzen 9 9950X"},
        "groups": ["recall@10 ≥ 0.90", "≥ 0.95", "≥ 0.99"],
        "yaxis": "queries / s (1 core)",
        "spread": "lighter part: spread over repeated runs",
        "missing": "hnswlib: not measured on this machine",
        "title": "glove-100-angular, official ANN-Benchmarks harness — best QPS at each recall (higher is better)",
        "foot": "Author's own measurements, not independently verified. Each panel has its own scale.",
    },
    "ja": {
        "names": {"graph": "KCI-Vec グラフ方式", "partitioned": "KCI-Vec 区分け方式", "qsgngt": "qsgngt 5.0.0",
                  "scann": "ScaNN 1.4.2", "hnswlib": "hnswlib 0.8.0"},
        "panels": {"xeon": "Intel Xeon 8375C (AWS r6id.4xlarge)", "9950x": "AMD Ryzen 9 9950X"},
        "groups": ["recall@10 ≥ 0.90", "≥ 0.95", "≥ 0.99"],
        "yaxis": "1 秒あたりの検索数 (1 コア)",
        "spread": "淡い部分: 繰り返した計測の幅",
        "missing": "hnswlib: この機械では未計測",
        "title": "glove-100-angular、公式 ANN-Benchmarks の手順 — 各 recall での最良 QPS (高いほど速い)",
        "foot": "開発者自身の計測で、第三者の確認はまだありません。パネルごとに目盛りが違います。",
    },
}
THEME = {
    "light": {"surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781", "grid": "#e1e0d9",
              "axis": "#c3c2b7", "series": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]},
    "dark":  {"surface": "#1a1a19", "ink": "#f0efec", "ink2": "#c3c2b7", "muted": "#898781", "grid": "#2c2c2a",
              "axis": "#383835", "series": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"]},
}
FONT = 'system-ui, -apple-system, &quot;Segoe UI&quot;, &quot;Hiragino Sans&quot;, &quot;Yu Gothic UI&quot;, sans-serif'

W, H = 960, 500
PANEL_W, TOP, PLOT_H = 440, 142, 250
LEFT0 = [60, 540]
BAR, GAP = 18, 2


def nice_max(v):
    for step in (1000, 2000, 2500, 5000, 10000):
        if v / step <= 5:
            return (int(v / step) + 1) * step, step
    return v, v / 5


def fmt(n):
    return f"{n:,}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rounded_top(x, y, w, h, r=4):
    """column with a 4px rounded data-end, square at the baseline"""
    r = min(r, h, w / 2)
    if h <= 0:
        return ""
    return (f"M{x:.1f},{y + h:.1f} L{x:.1f},{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
            f"L{x + w - r:.1f},{y:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} L{x + w:.1f},{y + h:.1f} Z")


def svg(lang, mode):
    t, th = TEXT[lang], THEME[mode]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{esc(t["title"])}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" rx="8" fill="{th["surface"]}"/>',
         f'<text x="24" y="34" font-size="15" font-weight="600" fill="{th["ink"]}">{esc(t["title"])}</text>']
    # legend (always present, >= 2 series), one row
    lx = 24
    for i, k in enumerate(SERIES):
        o.append(f'<rect x="{lx}" y="52" width="12" height="12" rx="3" fill="{th["series"][i]}"/>')
        o.append(f'<text x="{lx + 18}" y="62.5" font-size="13" fill="{th["ink2"]}">{esc(t["names"][k])}</text>')
        lx += 18 + 8.2 * len(t["names"][k]) * (1.55 if lang == "ja" and k in ("graph", "partitioned") else 1.0) + 22
    o.append(f'<rect x="24" y="76" width="12" height="12" rx="3" fill="{th["series"][0]}" fill-opacity="{0.35 if mode == 'light' else 0.45}"/>')
    o.append(f'<text x="42" y="86.5" font-size="12" fill="{th["muted"]}">{esc(t["spread"])}</text>')

    for p, mach in enumerate(("xeon", "9950x")):
        x0 = LEFT0[p]
        d = DATA[mach]
        present = [k for k in SERIES if d[k] is not None]
        vmax = max(hi for k in present for (_, hi) in d[k])
        ymax, step = nice_max(vmax)
        base = TOP + PLOT_H
        sy = lambda v: base - v / ymax * PLOT_H
        o.append(f'<text x="{x0}" y="{TOP - 12}" font-size="13" font-weight="600" fill="{th["ink"]}">{esc(t["panels"][mach])}</text>')
        # grid + ticks
        v = 0
        while v <= ymax + 1:
            y = sy(v)
            o.append(f'<line x1="{x0 + 40}" x2="{x0 + PANEL_W - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="{th["grid"] if v else th["axis"]}" stroke-width="1"/>')
            o.append(f'<text x="{x0 + 34}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{th["muted"]}" '
                     f'style="font-variant-numeric: tabular-nums">{fmt(int(v))}</text>')
            v += step
        o.append(f'<text x="{x0 - 22}" y="{TOP + PLOT_H / 2:.1f}" font-size="11" fill="{th["muted"]}" text-anchor="middle" '
                 f'transform="rotate(-90 {x0 - 22} {TOP + PLOT_H / 2:.1f})">{esc(t["yaxis"])}</text>')
        # groups
        gw = (PANEL_W - 60) / 3
        for g in range(3):
            n = len(present)
            cluster = n * BAR + (n - 1) * GAP
            gx = x0 + 45 + g * gw + (gw - cluster) / 2
            for j, k in enumerate(present):
                i = SERIES.index(k)
                lo, hi = d[k][g]
                bx = gx + j * (BAR + GAP)
                col = th["series"][i]
                name = t["names"][k]
                tip = f"{name} — {t['panels'][mach]}, {t['groups'][g]}: " + (fmt(lo) if lo == hi else f"{fmt(lo)}–{fmt(hi)}")
                if hi > lo:   # spread: lighter part from the low run to the high run, rounded end on top
                    o.append(f'<path d="{rounded_top(bx, sy(hi), BAR, sy(lo) - sy(hi) + 4)}" fill="{col}" fill-opacity="{0.35 if mode == 'light' else 0.45}"><title>{esc(tip)}</title></path>')
                    o.append(f'<rect x="{bx:.1f}" y="{sy(lo):.1f}" width="{BAR}" height="{base - sy(lo):.1f}" fill="{col}"><title>{esc(tip)}</title></rect>')
                else:
                    o.append(f'<path d="{rounded_top(bx, sy(lo), BAR, base - sy(lo))}" fill="{col}"><title>{esc(tip)}</title></path>')
                if k == "graph":   # selective direct label: KCI-Vec graph only, above the tallest column of the group
                    gtop = max(d[q][g][1] for q in present)
                    o.append(f'<text x="{bx + BAR / 2:.1f}" y="{sy(gtop) - 6:.1f}" font-size="11" font-weight="600" text-anchor="middle" '
                             f'fill="{th["ink"]}" style="font-variant-numeric: tabular-nums">{fmt(lo)}</text>')
            o.append(f'<text x="{x0 + 45 + g * gw + gw / 2:.1f}" y="{base + 20}" font-size="12" text-anchor="middle" fill="{th["ink2"]}">{esc(t["groups"][g])}</text>')
        if d["hnswlib"] is None:
            o.append(f'<text x="{x0 + 45}" y="{base + 42}" font-size="11" fill="{th["muted"]}">{esc(t["missing"])}</text>')
    o.append(f'<text x="24" y="{H - 18}" font-size="11.5" fill="{th["muted"]}">{esc(t["foot"])}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for lang in ("en", "ja"):
        for mode in ("light", "dark"):
            p = os.path.join(OUT, f"glove100_qps_{lang}_{mode}.svg")
            open(p, "w", encoding="utf-8", newline="\n").write(svg(lang, mode))
            print("wrote", p)
