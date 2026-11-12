# More README charts (static SVG, light + dark, English + Japanese), same style as make_charts.py:
#   vibe_qps_*      VIBE yahoo-minilm-384, best QPS at recall@100 >= 0.90 / 0.95 / 0.99, Xeon and 9950X panels
#                   (the five graph / quantized-graph entries; LoRANN and ScaNN are in the README table)
#   vibe_build_*    VIBE yahoo, Xeon: one-core build time of the index behind each algorithm's best point at recall >= 0.95
# Values are copied from the measurement records (one run each). Run: python tools/make_charts_more.py -> docs/img/*.svg
import os

from make_charts import FONT, THEME, OUT, esc, fmt, nice_max, rounded_top

# ---- VIBE QPS ------------------------------------------------------------------------------------------------
VQ = {
    "xeon":  {"graph": [9669, 7934, 5336], "partitioned": [7383, 6287, 2969], "glass": [8844, 6575, 4854],
              "symphonyqg": [7066, 6001, 3789], "ngtqg": [6887, 4916, 3266]},
    "9950x": {"graph": [19267, 16074, 10900], "partitioned": [18126, 13642, 5802], "glass": [15010, 11811, 8861],
              "symphonyqg": [12476, 10527, 6784], "ngtqg": [11497, 8256, 5339]},
}
VQ_SERIES = ["graph", "partitioned", "glass", "symphonyqg", "ngtqg"]   # fixed slot order
VQ_TEXT = {
    "en": {"names": {"graph": "KCI-Vec graph", "partitioned": "KCI-Vec partitioned", "glass": "glass",
                     "symphonyqg": "SymphonyQG", "ngtqg": "NGT-QG"},
           "panels": {"xeon": "Intel Xeon 8375C (AWS r6id.4xlarge)", "9950x": "AMD Ryzen 9 9950X"},
           "groups": ["recall@100 ≥ 0.90", "≥ 0.95", "≥ 0.99"], "yaxis": "queries / s (1 core)",
           "title": "VIBE, yahoo-minilm-384 (embeddings, k = 100) — best QPS at each recall (higher is better)",
           "foot": "Author's own measurements, one run each, not independently verified. Others measured 1–2 days earlier on the same machine. Each panel has its own scale."},
    "ja": {"names": {"graph": "KCI-Vec グラフ方式", "partitioned": "KCI-Vec 区分け方式", "glass": "glass",
                     "symphonyqg": "SymphonyQG", "ngtqg": "NGT-QG"},
           "panels": {"xeon": "Intel Xeon 8375C (AWS r6id.4xlarge)", "9950x": "AMD Ryzen 9 9950X"},
           "groups": ["recall@100 ≥ 0.90", "≥ 0.95", "≥ 0.99"], "yaxis": "1 秒あたりの検索数 (1 コア)",
           "title": "VIBE、yahoo-minilm-384 (埋め込み、k=100) — 各 recall での最良 QPS (高いほど速い)",
           "foot": "開発者自身の計測、各 1 回、第三者の確認はまだありません。相手は 1〜2 日前に同じ機械で計測。パネルごとに目盛りが違います。"},
}

# ---- VIBE build time -----------------------------------------------------------------------------------------
# (key, seconds) — the index of each algorithm's best point at recall@100 >= 0.95, AWS r6id, one core
VB = [("graph", 249), ("lorann", 258), ("scann", 313), ("partitioned", 366), ("glass", 394), ("symphonyqg", 438),
      ("pag", 899), ("ngtqg", 3884)]
VB_TEXT = {
    "en": {"names": {"graph": "KCI-Vec graph", "partitioned": "KCI-Vec partitioned", "glass": "glass", "symphonyqg": "SymphonyQG",
                     "ngtqg": "NGT-QG", "pag": "PAG", "scann": "ScaNN", "lorann": "LoRANN"},
           "title": "VIBE, yahoo-minilm-384, Intel Xeon 8375C — time to build the index (1 core, shorter is better)",
           "sub": "For each algorithm, the index behind its fastest setting at recall@100 ≥ 0.95",
           "unit": " s", "xaxis": "seconds",
           "foot": "Author's own measurements, one run each, not independently verified."},
    "ja": {"names": {"graph": "KCI-Vec グラフ方式", "partitioned": "KCI-Vec 区分け方式", "glass": "glass", "symphonyqg": "SymphonyQG",
                     "ngtqg": "NGT-QG", "pag": "PAG", "scann": "ScaNN", "lorann": "LoRANN"},
           "title": "VIBE、yahoo-minilm-384、Intel Xeon 8375C — 索引を作る時間 (1 コア、短いほど良い)",
           "sub": "それぞれ、recall@100 ≥ 0.95 でいちばん速かった設定の索引",
           "unit": " 秒", "xaxis": "秒",
           "foot": "開発者自身の計測、各 1 回、第三者の確認はまだありません。"},
}

W, H = 960, 500
PANEL_W, TOP, PLOT_H = 440, 142, 250
LEFT0 = [60, 540]
BAR, GAP = 18, 2


def vibe_qps(lang, mode):
    t, th = VQ_TEXT[lang], THEME[mode]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="{esc(t["title"])}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" rx="8" fill="{th["surface"]}"/>',
         f'<text x="24" y="34" font-size="15" font-weight="600" fill="{th["ink"]}">{esc(t["title"])}</text>']
    lx = 24
    for i, k in enumerate(VQ_SERIES):
        name = t["names"][k]
        o.append(f'<rect x="{lx}" y="52" width="12" height="12" rx="3" fill="{th["series"][i]}"/>')
        o.append(f'<text x="{lx + 18}" y="62.5" font-size="13" fill="{th["ink2"]}">{esc(name)}</text>')
        wide = sum(1.9 if ord(c) > 0x2E80 else 1.0 for c in name)
        lx += 18 + 7.6 * wide + 22
    for p, mach in enumerate(("xeon", "9950x")):
        x0, d = LEFT0[p], VQ[mach]
        ymax, step = nice_max(max(max(v) for v in d.values()) * 1.08)   # headroom for the value label
        base = TOP + PLOT_H
        sy = lambda v: base - v / ymax * PLOT_H
        o.append(f'<text x="{x0}" y="{TOP - 12}" font-size="13" font-weight="600" fill="{th["ink"]}">{esc(t["panels"][mach])}</text>')
        v = 0
        while v <= ymax + 1:
            y = sy(v)
            o.append(f'<line x1="{x0 + 40}" x2="{x0 + PANEL_W - 10}" y1="{y:.1f}" y2="{y:.1f}" stroke="{th["grid"] if v else th["axis"]}" stroke-width="1"/>')
            o.append(f'<text x="{x0 + 34}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{th["muted"]}" style="font-variant-numeric: tabular-nums">{fmt(int(v))}</text>')
            v += step
        o.append(f'<text x="{x0 - 22}" y="{TOP + PLOT_H / 2:.1f}" font-size="11" fill="{th["muted"]}" text-anchor="middle" '
                 f'transform="rotate(-90 {x0 - 22} {TOP + PLOT_H / 2:.1f})">{esc(t["yaxis"])}</text>')
        gw = (PANEL_W - 60) / 3
        for g in range(3):
            n = len(VQ_SERIES)
            cluster = n * BAR + (n - 1) * GAP
            gx = x0 + 45 + g * gw + (gw - cluster) / 2
            for j, k in enumerate(VQ_SERIES):
                val = d[k][g]
                bx = gx + j * (BAR + GAP)
                tip = f"{t['names'][k]} — {t['panels'][mach]}, {t['groups'][g]}: {fmt(val)}"
                o.append(f'<path d="{rounded_top(bx, sy(val), BAR, base - sy(val))}" fill="{th["series"][j]}"><title>{esc(tip)}</title></path>')
                if k == "graph":   # selective direct label: KCI-Vec graph only, above the tallest column of the group
                    gtop = max(d[q][g] for q in VQ_SERIES)
                    o.append(f'<text x="{bx + BAR / 2:.1f}" y="{sy(gtop) - 6:.1f}" font-size="11" font-weight="600" text-anchor="middle" '
                             f'fill="{th["ink"]}" style="font-variant-numeric: tabular-nums">{fmt(val)}</text>')
            o.append(f'<text x="{x0 + 45 + g * gw + gw / 2:.1f}" y="{base + 20}" font-size="12" text-anchor="middle" fill="{th["ink2"]}">{esc(t["groups"][g])}</text>')
    o.append(f'<text x="24" y="{H - 18}" font-size="11.5" fill="{th["muted"]}">{esc(t["foot"])}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def vibe_build(lang, mode):
    """horizontal bars, one measure; KCI-Vec rows in the first slot color, the others in a neutral (emphasis, not identity)"""
    t, th = VB_TEXT[lang], THEME[mode]
    BW, BH = 960, 400
    LX, RX, TY, ROW, BAR_H = 190, 880, 96, 30, 18
    xmax, step = 4000, 1000
    sx = lambda v: LX + v / xmax * (RX - LX)
    neutral = "#b4b2a9" if mode == "light" else "#5f5e5a"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}" role="img" '
         f'aria-label="{esc(t["title"])}" font-family="{FONT}">',
         f'<rect width="{BW}" height="{BH}" rx="8" fill="{th["surface"]}"/>',
         f'<text x="24" y="34" font-size="15" font-weight="600" fill="{th["ink"]}">{esc(t["title"])}</text>',
         f'<text x="24" y="56" font-size="12" fill="{th["ink2"]}">{esc(t["sub"])}</text>']
    bottom = TY + ROW * len(VB)
    v = 0
    while v <= xmax:
        x = sx(v)
        o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{TY - 8}" y2="{bottom}" stroke="{th["grid"] if v else th["axis"]}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{bottom + 16}" font-size="11" text-anchor="middle" fill="{th["muted"]}" style="font-variant-numeric: tabular-nums">{fmt(v)}</text>')
        v += step
    o.append(f'<text x="{(LX + RX) / 2:.1f}" y="{bottom + 34}" font-size="11" text-anchor="middle" fill="{th["muted"]}">{esc(t["xaxis"])}</text>')
    for r, (k, secs) in enumerate(VB):
        y = TY + r * ROW + (ROW - BAR_H) / 2
        kci = k in ("graph", "partitioned")
        col = th["series"][0 if k == "graph" else 1] if kci else neutral
        w = sx(secs) - LX
        r4 = min(4, w / 2)
        path = (f"M{LX},{y:.1f} L{LX + w - r4:.1f},{y:.1f} Q{LX + w:.1f},{y:.1f} {LX + w:.1f},{y + r4:.1f} "
                f"L{LX + w:.1f},{y + BAR_H - r4:.1f} Q{LX + w:.1f},{y + BAR_H:.1f} {LX + w - r4:.1f},{y + BAR_H:.1f} L{LX},{y + BAR_H:.1f} Z")
        tip = f"{t['names'][k]}: {fmt(secs)}{t['unit']}"
        o.append(f'<text x="{LX - 10}" y="{y + BAR_H - 4:.1f}" font-size="12.5" text-anchor="end" '
                 f'fill="{th["ink"] if kci else th["ink2"]}" font-weight="{600 if kci else 400}">{esc(t["names"][k])}</text>')
        o.append(f'<path d="{path}" fill="{col}"><title>{esc(tip)}</title></path>')
        o.append(f'<text x="{LX + w + 6:.1f}" y="{y + BAR_H - 4:.1f}" font-size="11.5" fill="{th["ink2"]}" '
                 f'style="font-variant-numeric: tabular-nums">{fmt(secs)}{esc(t["unit"])}</text>')
    o.append(f'<text x="24" y="{BH - 16}" font-size="11.5" fill="{th["muted"]}">{esc(t["foot"])}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for lang in ("en", "ja"):
        for mode in ("light", "dark"):
            for name, fn in (("vibe_qps", vibe_qps), ("vibe_build", vibe_build)):
                p = os.path.join(OUT, f"{name}_{lang}_{mode}.svg")
                open(p, "w", encoding="utf-8", newline="\n").write(fn(lang, mode))
                print("wrote", p)
