"""Build the profile README's SVG cards in dark and light versions.

Writes to assets/:
  toolkit-{dark,light}.svg         the Toolkit card (edit TOOLKIT below)
  platform-{dark,light}.svg        the connected platform diagram (edit PLATFORM below)
  card-<project>-{dark,light}.svg  the project cards (edit PROJECTS below)

Run from anywhere with Python 3.9+ (no dependencies):
  python3 scripts/build_assets.py

Icons live in scripts/icons/; see scripts/icons/README.md for sources and licences.
"""
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = Path(__file__).resolve().parent / "icons"

# Same palette as assets/banner-{dark,light}.svg
THEMES = {
    "dark":  dict(bg="#101412", grid="#1f2722", line="#354039", node="#191f1b", accent="#c4f279",
                  text="#f1f4ed", muted="#b1bcb3", chip="#191f1b", border="#354039"),
    "light": dict(bg="#f6f8f3", grid="#e3e9df", line="#c9d3c4", node="#ffffff", accent="#4d7a12",
                  text="#101412", muted="#4a554d", chip="#ffffff", border="#c9d3c4"),
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# (label, icon file in scripts/icons without .svg)
TOOLKIT = [
    ("WAREHOUSE & TRANSFORM", [("Snowflake", "snowflake"), ("BigQuery", "bigquery"), ("dbt", "dbt"),
                               ("Spark", "spark"), ("SQL", "sql"), ("Python", "python"), ("Go", "go")]),
    ("ORCHESTRATION & INGESTION", [("Airflow", "airflow"), ("Prefect", "prefect"), ("Temporal", "temporal"), ("Kafka", "kafka"),
                                   ("Fivetran", "fivetran")]),
    ("CLOUD & INFRASTRUCTURE", [("AWS", "aws"), ("GCP", "gcp"), ("Azure", "azure"), ("Terraform", "terraform"),
                                ("Docker", "docker"), ("Kubernetes", "kubernetes"), ("GitHub Actions", "githubactions")]),
    ("AI", [("OpenAI", "openai"), ("Anthropic", "anthropic"), ("Gemini", "gemini"),
            ("Structured outputs", "structured"), ("Agent orchestration", "agents"),
            ("Citation validation", "citations")]),
]

PROJECTS = {
    "fieldnotes": dict(
        title="Fieldnotes",
        eyebrow="FEATURED · AGENTIC AI",
        desc=["A research assistant that plans, collects sources",
              "and writes a brief where every citation is",
              "checked against the stored source text."],
        chips=["Multi-model agents", "Citation checks", "Zero dependencies"],
        lang=("Python", "#3572A5"),
        motif="doc",
        alt="Fieldnotes: an agentic research assistant with checked citations",
    ),
    "pipeline-dojo": dict(
        title="pipeline-dojo",
        eyebrow="IN PROGRESS · LEARNING",
        desc=["An interactive guide to data engineering: short",
              "lessons, then SQL, Python and data modelling",
              "exercises, checked right in the browser."],
        chips=["SQL", "Python", "Data modelling", "DSA"],
        lang=("TypeScript", "#3178c6"),
        motif="pipe",
        alt="pipeline-dojo: an interactive, in-browser guide to data engineering",
    ),
}


# The connected platform, in build order: (eyebrow, name, two description lines, status)
PLATFORM = [
    ("01 · DATA PLATFORM", "Tributary", ["CDC → Kafka → Flink →", "Iceberg, Trino and dbt"], "in progress"),
    ("02 · FEATURE STORE", "Pantry", ["Offline from Iceberg,", "online via Go + Redis"], "planned"),
    ("03 · MLOPS", "Slipway", ["Train, register, deploy;", "monitor drift live"], "planned"),
    ("04 · API GATEWAY", "Switchboard", ["Routing, rate limits", "and observability"], "planned"),
]
# What flows along each arrow between neighbours, then the two longer links
FLOWS = ["Iceberg", "features", "models"]
TOP_LINK = (0, 2, "live CDC stream → drift monitoring")  # Tributary → Slipway, drawn above
BOTTOM_LINK = (1, 3, "online features")                  # Pantry → Switchboard, drawn below


def text_width(s, size):
    """Rough width of s in a sans-serif font; good enough for sizing chips."""
    em = 0
    for ch in s:
        if ch in "iltfjrI.,:·' ()":
            em += .30
        elif ch in "mwMW":
            em += .85
        elif ch.isupper() or ch.isdigit():
            em += .66
        else:
            em += .54
    return em * size


def icon(name, x, y, size, color):
    """Inline scripts/icons/<name>.svg, recoloured to a single colour."""
    src = (ICONS / f"{name}.svg").read_text()
    view_box = re.search(r'viewBox="([^"]+)"', src).group(1)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
    inner = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', inner)
    # Outline icons carry their stroke styling on the root element; keep it.
    stroked = 'stroke="currentColor"' in src.split(">", 1)[0]
    root_attrs = ('fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
                  if stroked else 'fill="currentColor"')
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{view_box}" '
            f'color="{color}" {root_attrs}>{inner}</svg>')


def frame(w, h, t, alt, body):
    """Shared card background: rounded panel, grid and fade, as in the banner."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(alt)}">
  <title>{escape(alt)}</title>
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{t['grid']}" stroke-width="1"/></pattern>
    <linearGradient id="fade" x1="0" x2="1">
      <stop offset="0" stop-color="{t['bg']}"/><stop offset=".6" stop-color="{t['bg']}" stop-opacity=".93"/><stop offset="1" stop-color="{t['bg']}" stop-opacity=".2"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="{t['bg']}"/>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="url(#grid)"/>
  <rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="url(#fade)" stroke="{t['border']}" stroke-width="2"/>
  <g font-family="{FONT}">
{body}
  </g>
</svg>
'''


def toolkit(t):
    w, pad, row_h, top = 1280, 48, 96, 44
    h = top + row_h * len(TOOLKIT) + 20
    parts = []
    for r, (label, tools) in enumerate(TOOLKIT):
        y = top + r * row_h
        parts.append(f'<rect x="{pad}" y="{y + 4}" width="10" height="10" rx="2" fill="{t["accent"]}"/>'
                     f'<text x="{pad + 20}" y="{y + 14}" fill="{t["accent"]}" font-size="15" font-weight="600" letter-spacing="2.2">{escape(label)}</text>')
        x = pad
        for name, icon_name in tools:
            chip_w = round(16 + 22 + 9 + text_width(name, 19) + 18)
            parts.append(f'<rect x="{x}" y="{y + 28}" width="{chip_w}" height="40" rx="20" fill="{t["chip"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
                         + icon(icon_name, x + 16, y + 37, 22, t["accent"])
                         + f'<text x="{x + 47}" y="{y + 54}" fill="{t["text"]}" font-size="19">{escape(name)}</text>')
            x += chip_w + 12
        if x - 12 > w - pad:
            raise SystemExit(f"Toolkit row {label!r} is too wide ({x - 12}px > {w - pad}px); shorten or move a tool.")
    alt = "Toolkit. " + " ".join(
        f"{label.capitalize().replace('Ai', 'AI')}: {', '.join(n for n, _ in tools)}." for label, tools in TOOLKIT)
    return frame(w, h, t, alt, "\n".join(parts))


def motif(kind, t):
    """Small line-and-node graphic in the top-right corner of a project card."""
    line, node, accent, bg = t["line"], t["node"], t["accent"], t["bg"]
    box = lambda x, y, w=32, h=22: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{node}" stroke="{accent}" stroke-width="2"/>'
    dot = lambda x, y, r=6: f'<circle cx="{x}" cy="{y}" r="{r}" fill="{accent}"/>'
    path = lambda d: f'<path d="{d}" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    shapes = {
        "doc": f'''<rect x="0" y="0" width="64" height="80" rx="8" fill="{node}" stroke="{line}" stroke-width="2"/>
    <g stroke="{line}" stroke-width="3" stroke-linecap="round"><path d="M14 20H50"/><path d="M14 32H50"/><path d="M14 44H38"/></g>
    {dot(56, 70, 16)}<path d="M48 70l6 6 10-11" fill="none" stroke="{bg}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>''',
        "pipe": path("M4 24H40V56H76") + box(-20, 12, 36, 24) + box(58, 44, 36, 24) + dot(40, 56),
    }
    return f'<g transform="translate(520 40)">\n    {shapes[kind]}\n  </g>'


def project_card(p, t):
    w, h = 640, 320
    chips, x = [], 40
    for c in p["chips"]:
        chip_w = round(text_width(c, 15) + 30)
        chips.append(f'<rect x="{x}" y="242" width="{chip_w}" height="32" rx="16" fill="{t["chip"]}" stroke="{t["border"]}"/>'
                     f'<text x="{x + chip_w / 2}" y="263" text-anchor="middle" fill="{t["muted"]}" font-size="15">{escape(c)}</text>')
        x += chip_w + 10
    if x - 10 > w - 40:
        raise SystemExit(f"Chips on the {p['title']} card are too wide; shorten or remove one.")
    desc = "".join(f'<text x="40" y="{164 + i * 28}" fill="{t["muted"]}" font-size="20">{escape(line)}</text>'
                   for i, line in enumerate(p["desc"]))
    lang, color = p["lang"]
    body = f'''  {motif(p['motif'], t)}
    <text x="40" y="66" fill="{t['accent']}" font-size="15" font-weight="600" letter-spacing="2.2">{escape(p['eyebrow'])}</text>
    <text x="38" y="118" fill="{t['text']}" font-size="46" font-weight="600" letter-spacing="-1.2">{escape(p['title'])}</text>
    {desc}
    {''.join(chips)}
    <circle cx="46" cy="294" r="6" fill="{color}"/>
    <text x="60" y="299" fill="{t['muted']}" font-size="15">{escape(lang)}</text>'''
    return frame(w, h, t, p["alt"], body)


def platform(t):
    w, pad, node_w, node_h, top = 1280, 48, 236, 200, 110
    gap = (w - 2 * pad - len(PLATFORM) * node_w) / (len(PLATFORM) - 1)
    h = top + node_h + 120
    xs = [pad + i * (node_w + gap) for i in range(len(PLATFORM))]
    centre = lambda i: xs[i] + node_w / 2
    arrow = lambda x, y, down: (f'<path d="M{x - 7} {y - 9 if down else y + 9}L{x} {y}L{x + 7} {y - 9 if down else y + 9}" '
                                f'fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
    parts = []

    def label_pill(x, y, text):
        lw = text_width(text, 15) + 28
        return (f'<rect x="{x - lw / 2}" y="{y - 15}" width="{lw}" height="30" rx="15" fill="{t["bg"]}" stroke="{t["border"]}"/>'
                f'<text x="{x}" y="{y + 5}" text-anchor="middle" fill="{t["muted"]}" font-size="15">{escape(text)}</text>')

    # long links first so nodes and pills sit on top of them
    for (a, b, text), above in ((TOP_LINK, True), (BOTTOM_LINK, False)):
        y0 = top - 6 if above else top + node_h + 6
        bend = -70 if above else 70
        parts.append(f'<path d="M{centre(a)} {y0}C{centre(a)} {y0 + bend} {centre(b)} {y0 + bend} {centre(b)} {y0}" '
                     f'fill="none" stroke="{t["line"]}" stroke-width="2" stroke-dasharray="6 6"/>')
        parts.append(arrow(centre(b), y0, above))
        parts.append(label_pill((centre(a) + centre(b)) / 2, y0 + bend * .75, text))

    for i, (eyebrow, name, desc, status) in enumerate(PLATFORM):
        x, active = xs[i], status == "in progress"
        for line in desc:
            if text_width(line, 17) > node_w - 48:
                raise SystemExit(f"Platform text {line!r} is too wide for its box; shorten it.")
        parts.append(f'<rect x="{x}" y="{top}" width="{node_w}" height="{node_h}" rx="12" fill="{t["node"]}" '
                     f'stroke="{t["accent"] if active else t["border"]}" stroke-width="2"/>'
                     f'<text x="{x + 24}" y="{top + 38}" fill="{t["accent"]}" font-size="13" font-weight="600" letter-spacing="1.8">{escape(eyebrow)}</text>'
                     f'<text x="{x + 23}" y="{top + 80}" fill="{t["text"]}" font-size="32" font-weight="600" letter-spacing="-.8">{escape(name)}</text>'
                     + "".join(f'<text x="{x + 24}" y="{top + 112 + j * 23}" fill="{t["muted"]}" font-size="17">{escape(l)}</text>'
                               for j, l in enumerate(desc)))
        label = status.upper()
        pw = text_width(label, 12) + 22 + label.count(" ") * 4 + len(label) * 1.4
        parts.append(f'<rect x="{x + 24}" y="{top + 152}" width="{pw}" height="26" rx="13" '
                     + (f'fill="{t["accent"]}"/>' if active else f'fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
                     + f'<text x="{x + 24 + pw / 2}" y="{top + 169}" text-anchor="middle" font-size="12" font-weight="600" letter-spacing="1.4" '
                     f'fill="{t["bg"] if active else t["muted"]}">{label}</text>')
        if i < len(PLATFORM) - 1:
            x1, x2, y = x + node_w + 8, xs[i + 1] - 8, top + node_h / 2
            parts.append(f'<path d="M{x1} {y}H{x2}" stroke="{t["line"]}" stroke-width="2"/>'
                         f'<path d="M{x2 - 9} {y - 7}L{x2} {y}L{x2 - 9} {y + 7}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
                         f'<text x="{(x1 + x2) / 2}" y="{y - 12}" text-anchor="middle" fill="{t["muted"]}" font-size="14">{escape(FLOWS[i])}</text>')

    alt = ("The platform, in build order: " + "; ".join(
        f"{n} ({', '.join(d).replace(',,', ',')}, {st})" for _, n, d, st in PLATFORM)
        + f". Arrows: Tributary to Pantry ({FLOWS[0]}), Pantry to Slipway ({FLOWS[1]}), Slipway to Switchboard ({FLOWS[2]});"
        + f" Tributary also feeds Slipway ({TOP_LINK[2]}) and Pantry serves Switchboard ({BOTTOM_LINK[2]}).")
    return frame(w, h, t, alt, "\n".join(parts))


def main():
    for theme, t in THEMES.items():
        (ASSETS / f"toolkit-{theme}.svg").write_text(toolkit(t))
        (ASSETS / f"platform-{theme}.svg").write_text(platform(t))
        for slug, p in PROJECTS.items():
            (ASSETS / f"card-{slug}-{theme}.svg").write_text(project_card(p, t))
    print(f"Wrote toolkit, platform diagram and {len(PROJECTS)} project cards (dark + light) to {ASSETS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
