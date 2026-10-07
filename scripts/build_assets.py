"""Build the profile README's SVG cards in dark and light versions.

Writes to assets/:
  toolkit-{dark,light}.svg         the Toolkit card (edit TOOLKIT below)
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
                               ("Spark", "spark"), ("SQL", "sql"), ("Python", "python")]),
    ("ORCHESTRATION & INGESTION", [("Airflow", "airflow"), ("Prefect", "prefect"), ("Kafka", "kafka"),
                                   ("Fivetran", "fivetran")]),
    ("CLOUD & INFRASTRUCTURE", [("AWS", "aws"), ("GCP", "gcp"), ("Azure", "azure"), ("Terraform", "terraform"),
                                ("Docker", "docker"), ("GitHub Actions", "githubactions")]),
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
    "tributary": dict(
        title="Tributary",
        eyebrow="PLANNED · STREAMING",
        desc=["Change data capture from Postgres into Kafka,",
              "then real-time processing: windowed aggregates,",
              "joins and replayable, reliable sinks."],
        chips=["Debezium", "Kafka", "Postgres", "Python"],
        lang=("Python", "#3572A5"),
        motif="merge",
        alt="Tributary (planned): change data capture and real-time stream processing",
    ),
    "strongroom": dict(
        title="Strongroom",
        eyebrow="PLANNED · DATA WAREHOUSE",
        desc=["A Data Vault 2.0 warehouse in dbt: hubs, links",
              "and satellites with full history, plus a",
              "business vault and marts for analytics."],
        chips=["dbt", "Data Vault 2.0", "DuckDB", "Snowflake"],
        lang=("SQL", "#e38c00"),
        motif="vault",
        alt="Strongroom (planned): a Data Vault 2.0 warehouse built with dbt",
    ),
    "assay": dict(
        title="Assay",
        eyebrow="PLANNED · DATA QUALITY",
        desc=["Declarative data quality checks that catch bad",
              "data before it lands, with readable reports",
              "and row-level quarantine."],
        chips=["YAML checks", "DuckDB", "Airflow"],
        lang=("Python", "#3572A5"),
        motif="filter",
        alt="Assay (planned): a declarative data quality framework",
    ),
    "trellis": dict(
        title="Trellis",
        eyebrow="PLANNED · ORCHESTRATION",
        desc=["An ETL engine where pipelines are dependency",
              "graphs: parallel runs, retries, resumable",
              "state and partition backfills."],
        chips=["DAG engine", "Backfills", "SQLite"],
        lang=("Python", "#3572A5"),
        motif="dag",
        alt="Trellis (planned): a graph-based ETL engine",
    ),
    "pantry": dict(
        title="Pantry",
        eyebrow="PLANNED · MLOPS",
        desc=["A feature store: define a feature once, serve",
              "it offline for point-in-time training sets",
              "and online for low-latency inference."],
        chips=["Point-in-time joins", "Redis", "FastAPI"],
        lang=("Python", "#3572A5"),
        motif="shelves",
        alt="Pantry (planned): a feature store for offline training and online serving",
    ),
    "slipway": dict(
        title="Slipway",
        eyebrow="PLANNED · MLOPS",
        desc=["Gated CI/CD for ML models: tracked training,",
              "a model registry, canary deploys, and drift",
              "monitoring once models are live."],
        chips=["MLflow", "GitHub Actions", "Drift (PSI/KS)"],
        lang=("Python", "#3572A5"),
        motif="cycle",
        alt="Slipway (planned): MLOps CI/CD with drift monitoring",
    ),
    "switchboard": dict(
        title="Switchboard",
        eyebrow="PLANNED · BACKEND",
        desc=["Microservices behind one API gateway, with",
              "auth, rate limiting, contract tests and",
              "end-to-end tracing."],
        chips=["FastAPI", "Redis", "OpenTelemetry"],
        lang=("Python", "#3572A5"),
        motif="fanout",
        alt="Switchboard (planned): a microservices and API gateway platform",
    ),
}


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
        "merge": path("M0 10C40 10 40 44 70 44") + path("M0 78C40 78 40 44 70 44") + path("M70 44H96") + dot(70, 44) + box(-12, 0, 24, 20) + box(-12, 68, 24, 20),
        "vault": path("M44 40L6 8M44 40L84 8M44 40L6 76M44 40L84 76") + box(-10, -2) + box(68, -2) + box(-10, 66) + box(68, 66) + dot(44, 40, 11),
        "filter": path("M4 8H84L54 44V74L34 84V44Z") + dot(74, 72, 14) + f'<path d="M67 72l5 5 9-10" fill="none" stroke="{bg}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        "dag": path("M12 44L48 12M12 44L48 76M48 12L84 44M48 76L84 44") + dot(12, 44) + box(32, 2) + box(32, 66) + dot(84, 44, 8),
        "shelves": "".join(box(x, y, 36, 22) for x, y in [(0, 6), (44, 6), (0, 36), (0, 66), (44, 66)]) + f'<rect x="44" y="36" width="36" height="22" rx="5" fill="{accent}"/>',
        "cycle": path("M44 8A36 36 0 0 1 80 44") + path("M44 80A36 36 0 0 1 8 44")
                 + f'<path d="M73 37l7 9 7-9M1 51l7-9 7 9" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
                 + box(28, 33, 32, 22) + dot(44, 8, 4) + dot(44, 80, 4),
        "fanout": path("M16 44H40M40 44L68 8M40 44H68M40 44L68 80") + box(-20, 33, 36, 22) + dot(40, 44) + box(64, -3) + box(64, 33) + box(64, 69),
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


def main():
    for theme, t in THEMES.items():
        (ASSETS / f"toolkit-{theme}.svg").write_text(toolkit(t))
        for slug, p in PROJECTS.items():
            (ASSETS / f"card-{slug}-{theme}.svg").write_text(project_card(p, t))
    print(f"Wrote toolkit and {len(PROJECTS)} project cards (dark + light) to {ASSETS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
