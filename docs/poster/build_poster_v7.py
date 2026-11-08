"""Build poster_v7.html: a visual-first version of the Group 8 poster.

All numbers come from the report (docs/Report/Report-process-Mining-2026-11-06.qmd)
or are recomputed from data/output/alignment_encodings.csv.
Run:  python docs/poster/build_poster_v7.py   (from the project root)
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "poster" / "poster_v7.html"

BLUE, ORANGE, MAROON, GREY, INK, MUTED = "#2f6f8f", "#d9622b", "#6b2e2a", "#a9a79f", "#1b1b1b", "#555"
FONT = 'font-family="Segoe UI, Arial, Helvetica, sans-serif"'

# ---------------------------------------------------------------- data
rows = list(csv.DictReader(open(ROOT / "data/output/alignment_encodings.csv")))
tt = [float(r["throughput_time"]) for r in rows]
N = len(tt)
hist = [0] * 31  # 2-day bins, last bin = 60+ days
for v in tt:
    hist[min(int(v // 2), 30)] += 1
n_fast = sum(v <= 14 for v in tt)
n_slow = N - n_fast
dev_cols = [c for c in rows[0] if c.startswith(("log_move", "model_move"))]


def share(col):
    return sum(float(r[col]) > 0 for r in rows) / N


any_dev = sum(any(float(r[c]) > 0 for c in dev_cols) for r in rows) / N
prevalence = [
    ("Any deviation", any_dev),
    ("Offer returned", share("log_move_O-Returned")),
    ("Offer refused", share("log_move_O-Refused")),
    ("Application denied", share("log_move_A-Denied")),
    ("Extra pause of call", share("log_move_W-Call-after-offers-suspend")),
]
assert N == 3093 and n_fast == 1501 and n_slow == 1592


# ---------------------------------------------------------------- charts
def histogram():
    W, H = 900, 360
    x0, x1, base, top = 70, 880, 282, 66
    bw = (x1 - x0) / len(hist)
    ymax = 420
    s = [f'<svg viewBox="0 0 {W} {H}" {FONT}>']
    for y in (0, 200, 400):
        yy = base - (base - top) * y / ymax
        s.append(f'<line x1="{x0}" x2="{x1}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#e4e1dc" stroke-width="2"/>')
        s.append(f'<text x="{x0-10}" y="{yy+9:.1f}" font-size="26" fill="{MUTED}" text-anchor="end">{y}</text>')
    for i, h in enumerate(hist):
        hh = (base - top) * h / ymax
        col = BLUE if i < 7 else ORANGE
        s.append(f'<rect x="{x0+i*bw+1.5:.1f}" y="{base-hh:.1f}" width="{bw-3:.1f}" height="{hh:.1f}" fill="{col}"/>')
    cx = x0 + 7 * bw
    s.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{top-30}" y2="{base}" stroke="{INK}" stroke-width="4" stroke-dasharray="12 8"/>')
    s.append(f'<text x="{cx+12:.1f}" y="{top-8}" font-size="28" font-weight="700" fill="{INK}">14 days</text>')
    # class labels
    s.append(f'<text x="{x0+3.5*bw:.1f}" y="{top-36}" font-size="34" font-weight="800" fill="{BLUE}" text-anchor="middle">fast</text>')
    s.append(f'<text x="{x0+3.5*bw:.1f}" y="{top-4}" font-size="28" font-weight="700" fill="{BLUE}" text-anchor="middle">{n_fast:,}</text>')
    s.append(f'<text x="{x0+19*bw:.1f}" y="{top+40}" font-size="34" font-weight="800" fill="{ORANGE}" text-anchor="middle">slow  {n_slow:,}</text>')
    for d in (0, 14, 30, 45):
        xx = x0 + d / 2 * bw
        s.append(f'<text x="{xx:.1f}" y="{base+34}" font-size="26" fill="{MUTED}" text-anchor="middle">{d}</text>')
    s.append(f'<text x="{x1-bw/2:.1f}" y="{base+34}" font-size="26" fill="{MUTED}" text-anchor="middle">60+</text>')
    s.append(f'<text x="{(x0+x1)/2:.1f}" y="{base+72}" font-size="28" fill="{INK}" text-anchor="middle">days from application to denial (up to 260)</text>')
    s.append(f'<line x1="{x0}" x2="{x1}" y1="{base}" y2="{base}" stroke="{INK}" stroke-width="3"/>')
    s.append("</svg>")
    return "".join(s)


def case_strip():
    """Simplified denied-loan case, with the follow-up call paused."""
    W, H = 700, 226
    nodes = [("Apply", 62), ("Offer sent", 240), ("Follow-up call", 450), ("Denied", 638)]
    s = [f'<svg viewBox="0 0 {W} {H}" {FONT}>']
    s.append(f'<defs><marker id="ah" markerUnits="userSpaceOnUse" markerWidth="22" markerHeight="22" refX="18" refY="11" orient="auto"><path d="M0,0 L22,11 L0,22 z" fill="{MAROON}"/></marker></defs>')
    for (_, xa), (_, xb) in zip(nodes, nodes[1:]):
        s.append(f'<line x1="{xa+62}" x2="{xb-60}" y1="80" y2="80" stroke="{MAROON}" stroke-width="5" marker-end="url(#ah)"/>')
    for label, x in nodes:
        last = label == "Denied"
        fill = MAROON if last else "#fff"
        s.append(f'<circle cx="{x}" cy="80" r="56" fill="{fill}" stroke="{MAROON}" stroke-width="5"/>')
        tc = "#fff" if last else MAROON
        if label == "Apply":  # document
            s.append(f'<rect x="{x-20}" y="52" width="40" height="54" rx="4" fill="none" stroke="{tc}" stroke-width="5"/>')
            for dy in (66, 78, 90):
                s.append(f'<line x1="{x-11}" x2="{x+11}" y1="{dy}" y2="{dy}" stroke="{tc}" stroke-width="4"/>')
        elif label == "Offer sent":  # envelope
            s.append(f'<rect x="{x-30}" y="58" width="60" height="42" rx="4" fill="none" stroke="{tc}" stroke-width="5"/>')
            s.append(f'<polyline points="{x-30},60 {x},84 {x+30},60" fill="none" stroke="{tc}" stroke-width="5"/>')
        elif label == "Follow-up call":  # pause symbol
            s.append(f'<rect x="{x-20}" y="54" width="13" height="52" rx="3" fill="{tc}"/>')
            s.append(f'<rect x="{x+7}" y="54" width="13" height="52" rx="3" fill="{tc}"/>')
        else:  # cross
            s.append(f'<path d="M{x-22},58 L{x+22},102 M{x+22},58 L{x-22},102" stroke="{tc}" stroke-width="9" stroke-linecap="round"/>')
        s.append(f'<text x="{x}" y="180" font-size="29" font-weight="700" fill="{INK}" text-anchor="middle">{label}</text>')
    s.append(f'<text x="450" y="216" font-size="27" fill="{ORANGE}" font-weight="700" text-anchor="middle">often paused</text>')
    s.append("</svg>")
    return "".join(s)


ICONS = {
    "input": f'''<svg viewBox="0 0 120 90"><rect x="6" y="8" width="44" height="60" rx="4" fill="none" stroke="{MAROON}" stroke-width="5"/>
      <line x1="15" x2="41" y1="24" y2="24" stroke="{MAROON}" stroke-width="4"/><line x1="15" x2="41" y1="36" y2="36" stroke="{MAROON}" stroke-width="4"/><line x1="15" x2="41" y1="48" y2="48" stroke="{MAROON}" stroke-width="4"/>
      <circle cx="68" cy="58" r="11" fill="none" stroke="{MAROON}" stroke-width="5"/><rect x="85" y="47" width="14" height="22" fill="{MAROON}"/><circle cx="110" cy="58" r="7" fill="none" stroke="{MAROON}" stroke-width="4"/>
      <line x1="79" x2="85" y1="58" y2="58" stroke="{MAROON}" stroke-width="4"/><line x1="99" x2="103" y1="58" y2="58" stroke="{MAROON}" stroke-width="4"/></svg>''',
    "kpi": f'''<svg viewBox="0 0 120 90"><circle cx="60" cy="46" r="36" fill="none" stroke="{MAROON}" stroke-width="6"/>
      <line x1="60" x2="60" y1="46" y2="22" stroke="{MAROON}" stroke-width="6" stroke-linecap="round"/><line x1="60" x2="78" y1="46" y2="56" stroke="{MAROON}" stroke-width="6" stroke-linecap="round"/></svg>''',
    "align": f'''<svg viewBox="0 0 120 90"><g fill="#ddd" stroke="{MAROON}" stroke-width="3">
      <rect x="6" y="14" width="24" height="24"/><rect x="34" y="14" width="24" height="24" fill="{ORANGE}"/><rect x="62" y="14" width="24" height="24"/><rect x="90" y="14" width="24" height="24"/>
      <rect x="6" y="50" width="24" height="24"/><rect x="62" y="50" width="24" height="24" fill="{BLUE}"/><rect x="90" y="50" width="24" height="24"/></g>
      <text x="46" y="70" font-size="22" font-weight="800" fill="{MAROON}" text-anchor="middle" {FONT}>&#187;</text></svg>''',
    "tree": f'''<svg viewBox="0 0 120 90"><rect x="40" y="4" width="40" height="24" rx="5" fill="{MAROON}"/>
      <path d="M60,28 V40 M30,40 H90 M30,40 V54 M90,40 V54" stroke="{MAROON}" stroke-width="5" fill="none"/>
      <rect x="8" y="54" width="44" height="28" rx="5" fill="{BLUE}"/><rect x="68" y="54" width="44" height="28" rx="5" fill="{ORANGE}"/></svg>''',
    "rules": f'''<svg viewBox="0 0 120 90"><g stroke-width="5" stroke-linecap="round">
      <circle cx="18" cy="22" r="7" fill="{BLUE}"/><line x1="36" x2="108" y1="22" y2="22" stroke="{MAROON}"/>
      <circle cx="18" cy="46" r="7" fill="{ORANGE}"/><line x1="36" x2="96" y1="46" y2="46" stroke="{MAROON}"/>
      <circle cx="18" cy="70" r="7" fill="{GREY}"/><line x1="36" x2="88" y1="70" y2="70" stroke="{MAROON}"/></g></svg>''',
}


def f1_dots():
    """Dot plot: F1 of 4 runs vs the all-slow guess (axis 0.60-0.75)."""
    W, H = 740, 258
    x0, x1 = 40, 710
    lo, hi = 0.60, 0.75
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    seeds = [0.712, 0.661, 0.662, 0.716]
    s = [f'<svg viewBox="0 0 {W} {H}" {FONT}>']
    y = 138
    s.append(f'<line x1="{x0}" x2="{x1}" y1="{y}" y2="{y}" stroke="#d8d4ce" stroke-width="4"/>')
    for v, anchor in ((lo, "start"), (hi, "end")):
        s.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{y-8}" y2="{y+8}" stroke="{MUTED}" stroke-width="3"/>')
        s.append(f'<text x="{X(v):.1f}" y="{y+38}" font-size="26" fill="{MUTED}" text-anchor="{anchor}">{v:.2f}</text>')
    s.append(f'<text x="{(x0+x1)/2}" y="{y+112}" font-size="27" fill="{INK}" text-anchor="middle">F1 score for slow cases (higher is better)</text>')
    xb, xm = X(0.680), X(0.688)
    s.append(f'<line x1="{xb:.1f}" x2="{xb:.1f}" y1="10" y2="{y+34}" stroke="{GREY}" stroke-width="6" stroke-dasharray="14 8"/>')
    s.append(f'<text x="{xb-14:.1f}" y="32" font-size="27" fill="{MUTED}" text-anchor="end">Guess "every case slow"</text>')
    s.append(f'<text x="{xb-14:.1f}" y="66" font-size="32" font-weight="800" fill="{MUTED}" text-anchor="end">0.680</text>')
    # +0.008 bracket
    by = 98
    s.append(f'<path d="M{xb:.1f},{by} H{xm:.1f} M{xb:.1f},{by-9} v18 M{xm:.1f},{by-9} v18" stroke="{ORANGE}" stroke-width="4" fill="none"/>')
    for v in seeds:
        s.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="17" fill="{BLUE}" fill-opacity="0.7"/>')
    for cx, rules in ((X(0.6615), "11-14 rules"), (X(0.714), "2 rules")):
        s.append(f'<text x="{cx:.1f}" y="{y+46}" font-size="25" fill="{BLUE}" font-weight="700" text-anchor="middle">2 runs</text>')
        s.append(f'<text x="{cx:.1f}" y="{y+71}" font-size="25" fill="{BLUE}" text-anchor="middle">{rules}</text>')
    s.append(f'<path d="M{xm:.1f},{y-28} l16,28 l-16,28 l-16,-28 z" fill="{MAROON}"/>')
    s.append(f'<text x="{xm+22:.1f}" y="{y-34}" font-size="30" font-weight="800" fill="{MAROON}">Tree average 0.688</text>')
    s.append("</svg>")
    return "".join(s)


def leaf_bars():
    """Main finding: share slow per tree leaf, against the 51.5 % base rate."""
    W, H = 1460, 206
    x0, x1 = 360, 1180
    X = lambda p: x0 + p * (x1 - x0)
    leaves = [("No", "389 cases", 0.159), ("Yes", "2,704 cases", 0.566)]
    s = [f'<svg viewBox="0 0 {W} {H}" {FONT}>']
    for i, (ans, n, p) in enumerate(leaves):
        y = 10 + i * 84
        s.append(f'<text x="10" y="{y+48}" font-size="40" font-weight="800" fill="{INK}">{ans}</text>')
        s.append(f'<text x="100" y="{y+48}" font-size="32" fill="{INK}">{n}</text>')
        s.append(f'<rect x="{x0}" y="{y}" width="{X(1-p)-x0:.1f}" height="70" fill="{BLUE}"/>')
        s.append(f'<rect x="{X(1-p):.1f}" y="{y}" width="{x1-X(1-p):.1f}" height="70" fill="{ORANGE}"/>')
        s.append(f'<text x="{x1+18}" y="{y+50}" font-size="42" font-weight="800" fill="{ORANGE}">{round(p*100)}% slow</text>')
        s.append(f'<text x="{x0+16}" y="{y+48}" font-size="30" font-weight="700" fill="#fff">{round((1-p)*100)}% fast</text>')
    xb = X(1 - 0.515)
    s.append(f'<line x1="{xb:.1f}" x2="{xb:.1f}" y1="2" y2="176" stroke="{INK}" stroke-width="4" stroke-dasharray="12 8"/>')
    s.append(f'<text x="{xb:.1f}" y="203" font-size="27" fill="{INK}" text-anchor="middle">all cases: 51.5% slow</text>')
    s.append("</svg>")
    return "".join(s)


def prevalence_bars():
    W, H = 860, 258
    x0, x1 = 330, 760
    s = [f'<svg viewBox="0 0 {W} {H}" {FONT}>']
    for i, (lab, p) in enumerate(prevalence):
        y = 6 + i * 46
        col = MAROON if i == 0 else "#b07a72"
        s.append(f'<text x="{x0-14}" y="{y+29}" font-size="28" font-weight="{800 if i == 0 else 400}" fill="{INK}" text-anchor="end">{lab}</text>')
        s.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="36" fill="#eee"/>')
        s.append(f'<rect x="{x0}" y="{y}" width="{(x1-x0)*p:.1f}" height="36" fill="{col}"/>')
        s.append(f'<text x="{x1+12}" y="{y+29}" font-size="29" font-weight="800" fill="{INK}">{round(p*100)}%</text>')
    s.append(f'<text x="{x0}" y="{H-4}" font-size="25" fill="{MUTED}">share of the 3,093 cases with this deviation</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- page
HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Poster Group 8: Conformance Checking for Process Improvement</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@page {{ size: 420mm 594mm; margin: 0; }}
:root{{--ink:{INK};--muted:{MUTED};--maroon:{MAROON};--blue:{BLUE};--orange:{ORANGE};--line:#cfc9c2}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#fff}}
body{{font-family:"Segoe UI",Arial,Helvetica,sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.poster{{width:420mm;height:594mm;margin:0 auto;overflow:hidden;display:flex;flex-direction:column;
  padding:26px 38px 12px;gap:7px;font-size:32px;line-height:1.2}}
svg{{display:block;width:100%;height:auto}}
/* header */
.head{{display:grid;grid-template-columns:0.75fr 4fr 0.95fr;gap:16px;align-items:center;border-bottom:6px solid var(--maroon);padding-bottom:12px}}
.head .course{{font-weight:700;font-size:27px;color:var(--maroon)}}
.head h1{{font-size:46px;text-align:center;line-height:1.05;white-space:nowrap}}
.head .who{{text-align:center;font-size:29px;margin-top:8px}}
.head img{{height:78px;max-width:100%;justify-self:end;display:block;margin-left:auto}}
/* sections */
section{{border:3px solid var(--line);border-radius:12px;display:flex;flex-direction:column}}
section>h2{{background:var(--maroon);color:#fff;font-size:40px;text-align:center;padding:2px 10px;border-radius:9px 9px 0 0}}
.body{{padding:12px 24px;flex:1;display:flex;flex-direction:column;gap:10px;justify-content:space-around}}
.grow{{flex:1 0 auto}}
h3{{font-size:34px;color:var(--maroon);line-height:1.1}}
.big{{font-size:44px;font-weight:800;line-height:1.1}}
.q{{font-size:38px;font-weight:800;line-height:1.12;color:var(--ink)}}
.q em{{font-style:normal;color:var(--orange)}}
.sub{{font-size:29px;color:var(--muted)}}
/* s1 */
.s1g{{display:grid;grid-template-columns:0.95fr 1.05fr;gap:30px;align-items:center}}
/* s2 */
.pipe{{display:grid;grid-template-columns:repeat(5,1fr);gap:0;align-items:stretch}}
.st{{position:relative;text-align:center;padding:0 14px}}
.st+.st::before{{content:"";position:absolute;left:-16px;top:40px;border:16px solid transparent;border-left:22px solid var(--maroon)}}
.st svg{{height:70px;width:auto;margin:0 auto 6px}}
.st b{{display:block;font-size:33px;color:var(--maroon)}}
.st span{{display:block;font-size:28px;line-height:1.15}}
.st .n{{display:inline-block;width:42px;height:42px;border-radius:50%;background:var(--maroon);color:#fff;font-size:28px;line-height:42px;margin-right:6px}}
.alg{{display:grid;grid-template-columns:auto 1fr;gap:26px;align-items:center;border-top:3px solid var(--line);padding-top:14px}}
table.al{{border-collapse:separate;border-spacing:6px}}
.al td{{background:#eee;text-align:center;padding:6px 12px;font-size:29px;border-radius:6px;white-space:nowrap}}
.al td.k{{background:none;font-weight:800;text-align:right;color:var(--maroon)}}
.al td.lm{{background:var(--orange);color:#1b1b1b;font-weight:800}}
.al td.gap{{background:#fff;box-shadow:inset 0 0 0 3px var(--orange);font-weight:800}}
.al td.ok{{background:#dfe9df}}
.al td.mm{{background:var(--blue);color:#fff;font-weight:800}}
.al td.gapm{{background:#fff;box-shadow:inset 0 0 0 3px var(--blue);font-weight:800}}
.legend{{display:flex;flex-direction:column;gap:12px;font-size:29px}}
.chip{{display:inline-block;border-radius:6px;padding:0 10px;font-weight:800}}
.chip.lm{{background:var(--orange)}} .chip.mm{{background:var(--blue);color:#fff}}
/* s3 */
.ev{{display:grid;grid-template-columns:0.82fr 1.18fr;gap:30px}}
.ev>div+div{{border-left:3px solid var(--line);padding-left:28px}}
.res{{display:grid;grid-template-columns:1fr 1fr;gap:14px;font-size:27px;white-space:nowrap}}
.res>div{{border:2px solid var(--line);border-radius:10px;padding:8px 10px;text-align:center}}
.res b{{display:block;font-size:42px;font-weight:800;line-height:1.05}}
.check{{display:grid;grid-template-columns:auto 2px 1fr;align-items:center;gap:22px;margin-top:auto;padding-top:20px}}
.verdict{{font-size:34px;font-weight:800;line-height:1.15;white-space:nowrap;color:var(--ink)}}
.verdict svg{{width:44px;height:44px;display:inline-block;vertical-align:-6px;margin-right:4px}}
.vline{{align-self:stretch;background:var(--line)}}
.ev>div:first-child{{display:flex;flex-direction:column}}
.tick{{width:84px;height:84px;flex:none}}
.toy{{width:100%;margin:18px 0 0;display:block}}
.finding{{border-top:3px solid var(--line);padding-top:14px}}
.take{{background:var(--maroon);color:#fff;border-radius:10px;padding:10px 18px;font-size:34px;font-weight:700;text-align:center}}
/* s4 */
.s4g{{display:grid;grid-template-columns:1.12fr 0.88fr;gap:30px;align-items:center}}
.fw{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px}}
.fw div{{border:3px solid var(--maroon);border-radius:10px;padding:6px 10px;font-size:27px;font-weight:700;line-height:1.15;text-align:center;display:flex;align-items:center;justify-content:center;min-height:62px}}
footer{{font-size:24px;color:var(--muted);border-top:3px solid var(--line);padding-top:6px;white-space:nowrap;overflow:hidden}}
</style>
</head>
<body>
<div class="poster">

<header class="head">
  <div class="course">JM0211<br>Process Mining</div>
  <div>
    <h1>Conformance Checking for Process Improvement</h1>
    <div class="who"><b>Group 8:</b> Rick de Rijk, Thom Verzantvoort, Stefan Vonk, Tycho van Rooij</div>
  </div>
  <img src="figures/jads_logo.png" alt="JADS logo">
</header>

<section>
  <h2>Motivation and Scientific Background</h2>
  <div class="body">
    <div class="s1g">
      <div>
        <div class="sub" style="text-align:center;white-space:nowrap">BPI 2017 &middot; Dutch bank &middot; <b>3,093 denied loans</b></div>
        {case_strip()}
        <div class="q">Which deviations from the process go with <em>slow</em> denials?</div>
      </div>
      <div>{histogram()}</div>
    </div>
  </div>
</section>

<section>
  <h2>Explanation of Conceptual Approach</h2>
  <div class="body">
    <div class="pipe">
      <div class="st">{ICONS['input']}<b>Input</b><span>event log + Petri net</span></div>
      <div class="st">{ICONS['kpi']}<b><span class="n">1</span>KPI</b><span>days per case</span></div>
      <div class="st">{ICONS['align']}<b><span class="n">2</span>Align</b><span>count deviations</span></div>
      <div class="st">{ICONS['tree']}<b><span class="n">3</span>Tree</b><span>slow vs fast</span></div>
      <div class="st">{ICONS['rules']}<b>Output</b><span>rules + cases</span></div>
    </div>
    <div class="alg">
      <table class="al">
        <tr><td class="k">Case</td><td>Call paused</td><td class="gap">Call paused</td><td class="gapm">&gt;&gt;</td><td>Denied</td></tr>
        <tr><td class="k">Model</td><td>Call paused</td><td class="gap">&gt;&gt;</td><td class="gapm">Call resumed</td><td>Denied</td></tr>
        <tr><td class="k"></td><td class="ok">&#10003;</td><td class="lm">log move</td><td class="mm">model move</td><td class="ok">&#10003;</td></tr>
      </table>
      <div class="legend">
        <div><span class="chip lm">log move</span> extra step in the case</div>
        <div><span class="chip mm">model move</span> step the case skipped</div>
        <div class="sub">One case &rarr; 108 deviation counts &rarr; tree</div>
      </div>
    </div>
  </div>
</section>

<section class="grow">
  <h2>Evaluation Design and Results</h2>
  <div class="body">
    <div class="ev">
      <div>
        <h3>&#9312; Is it correct?</h3>
        <div class="sub">Toy logs, solved by hand first</div>
        <img class="toy" src="figures/toy_net_parallel.png" alt="Toy Petri net with parallel block and choice">
        <div class="check">
          <div class="verdict"><svg viewBox="0 0 40 40"><path d="M8,21 l8,8 l16,-18" stroke="#3d7a4a" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>Yes,<br>exact match</div>
          <div class="vline"></div>
          <div class="res"><div><b>11 / 11</b>alignments</div><div><b>2 / 2</b>planted rules</div></div>
        </div>
      </div>
      <div>
        <h3>&#9313; Is it useful? Barely better than guessing</h3>
        <div class="sub">4 runs: trained on a random 75%, tested on the other 25%</div>
        {f1_dots()}
      </div>
    </div>
    <div class="finding">
      <h3>Main finding: was the follow-up call paused more often than the model allows?</h3>
      {leaf_bars()}
    </div>
    <div class="take">Correct on the toy logs &middot; but only +0.008 F1 over guessing &rarr; a lead, not proof</div>
  </div>
</section>

<section>
  <h2>Limitations and Future Work</h2>
  <div class="body">
    <div class="s4g">
      <div>
        <h3>Why so weak? Every case deviates</h3>
        {prevalence_bars()}
      </div>
      <div>
        <div class="q" style="font-size:34px">Model too strict: deviations are <em>normal</em>, so they hardly tell slow from fast.</div>
        <div class="fw">
          <div>Net that allows repeated pauses</div>
          <div>Add waiting-time features</div>
          <div>Predict days, not a cutoff</div>
          <div>Also check data (loan amount)</div>
        </div>
      </div>
    </div>
  </div>
</section>

<footer><b>References:</b> Dees, de Leoni, Mannhardt (2017). van der Aalst (2016) Process Mining. Berti et al. (2019) PM4Py. van Dongen (2017).</footer>
</div>
</body>
</html>
"""

OUT.write_text(HTML)
print("wrote", OUT, [(l, round(p, 3)) for l, p in prevalence])
