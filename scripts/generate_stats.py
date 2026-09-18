#!/usr/bin/env python3
"""
FloraDB statistics page generator (`FloraDB-public`).

Reads the FULL private snapshot (the private pipeline's floradb_core.sqlite, never the
public sample) and writes a citable, embeddable statistics page:

    stats/index.html          the page (URL /stats/)
    stats/charts/<slug>.svg   one standalone SVG per chart (for <img> embeds elsewhere)
    stats/data.json           every figure on the page, machine-readable

Only aggregates leave the private database -- no row-level data is written. Every
figure states its denominator and source; nothing is estimated (plants without an
ASPCA determination are excluded from the toxicity shares, never guessed).

Re-run after each data refresh, then `python scripts/generate_seo_pages.py` (or add the
/stats/ entry to sitemap.xml by hand), `python scripts/i18n_common.py build` and `... check`.

Usage:
    python scripts/generate_stats.py                 # ../../04_Houseplants_Botanical_FloraDB/floradb_core.sqlite
    python scripts/generate_stats.py --db PATH       # or FLORADB_SQLITE=PATH
"""
import argparse
import datetime as dt
import os
import sqlite3
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats_common import (Site, esc, n, pct, data, svg_hbar, figure, table, section, toc, tiles,  # noqa: E402
                          article_ld, COPY_JS, STATS_CSS, write_outputs)

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "stats"
FIRST_PUBLISHED = "2026-09-18"
DEFAULT_DB = BASE_DIR.parent / "04_Houseplants_Botanical_FloraDB" / "floradb_core.sqlite"

SITE = Site(base_url="https://floradb.dataengineered.io", brand="FloraDB",
            snippet_label="FloraDB houseplant statistics",
            surface="#12140f", surface2="#191c14", ink="#ece7d9", muted="#9a9683", grid="#2a2e22", accent="#9cbf6a",
            font="'Spline Sans', system-ui, -apple-system, 'Segoe UI', sans-serif",
            mono="'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace",
            heading_class="serif")

STATUS_LABELS = {"aspca_verified": "ASPCA-verified", "aspca_genus_inferred": "inferred from the genus", "unknown": "not verified"}
METRICS = [("min_lux_threshold", "Minimum light", "lux"), ("max_lux_threshold", "Maximum light", "lux"),
           ("watering_frequency_days", "Watering interval", "days"), ("min_temp_celsius", "Minimum temperature", "°C"),
           ("max_temp_celsius", "Maximum temperature", "°C"), ("ideal_humidity_percent", "Ideal humidity", "%")]


def num(v):
    """Integer-valued floats print without a decimal part."""
    return n(v) if float(v).is_integer() else f"{v:g}"


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------

def compute(db_path):
    con = sqlite3.connect(str(db_path))

    def q(sql, *a):
        return con.execute(sql, a).fetchall()

    s = {}
    s["snapshot_date"] = q("select max(substr(retrieved_at,1,10)) from data_sources")[0][0]
    s["aspca_date"] = q("select max(substr(retrieved_at,1,10)) from aspca_toxicity")[0][0]
    s["plants"] = q("select count(*) from plants")[0][0]
    s["families"] = q("select count(distinct family_id) from plants")[0][0]
    s["aspca_entries"] = q("select count(*) from aspca_toxicity")[0][0]
    s["species_index"] = q("select count(*) from species_index")[0][0]
    s["enriched"] = q("select count(*) from species_enrichment")[0][0]

    # toxicity in the care core (cat and dog verdicts are stored separately; the page checks they coincide)
    st = Counter()
    for status, cats, dogs, c in q("select toxicity_status, is_toxic_to_cats, is_toxic_to_dogs, count(*) from plants group by 1,2,3"):
        st[(status, cats, dogs)] += c
    s["cats_dogs_differ"] = q("select count(*) from plants where is_toxic_to_cats is not is_toxic_to_dogs")[0][0]
    s["tox_unknown"] = q("select count(*) from plants where is_toxic_to_cats is null and is_toxic_to_dogs is null")[0][0]
    s["tox_known"] = s["plants"] - s["tox_unknown"]
    s["tox_toxic"] = q("select count(*) from plants where is_toxic_to_cats=1 or is_toxic_to_dogs=1")[0][0]
    s["tox_nontoxic"] = q("select count(*) from plants where is_toxic_to_cats=0 and is_toxic_to_dogs=0")[0][0]
    s["tox_toxic_pct"] = pct(s["tox_toxic"], s["tox_known"])
    s["tox_rows"] = [
        ("Toxic, ASPCA-verified", q("select count(*) from plants where toxicity_status='aspca_verified' and (is_toxic_to_cats=1 or is_toxic_to_dogs=1)")[0][0]),
        ("Toxic, inferred from the genus", q("select count(*) from plants where toxicity_status='aspca_genus_inferred' and (is_toxic_to_cats=1 or is_toxic_to_dogs=1)")[0][0]),
        ("Non-toxic, ASPCA-verified", q("select count(*) from plants where toxicity_status='aspca_verified' and is_toxic_to_cats=0 and is_toxic_to_dogs=0")[0][0]),
        ("Non-toxic, inferred from the genus", q("select count(*) from plants where toxicity_status='aspca_genus_inferred' and is_toxic_to_cats=0 and is_toxic_to_dogs=0")[0][0]),
        ("No determination", s["tox_unknown"]),
    ]
    s["tox_rows"] = [(lbl, c) for lbl, c in s["tox_rows"] if c > 0]

    # ASPCA index (all entries, not only houseplants)
    cd = {(c, d): k for c, d, k in q("select toxic_to_cats, toxic_to_dogs, count(*) from aspca_toxicity group by 1,2")}
    s["aspca_both_known"] = sum(k for (c, d), k in cd.items() if c is not None and d is not None)
    s["aspca_both"] = cd.get((1, 1), 0)
    s["aspca_cats_only"] = cd.get((1, 0), 0)
    s["aspca_dogs_only"] = cd.get((0, 1), 0)
    s["aspca_neither"] = cd.get((0, 0), 0)
    s["aspca_either"] = s["aspca_both"] + s["aspca_cats_only"] + s["aspca_dogs_only"]
    s["aspca_either_pct"] = pct(s["aspca_either"], s["aspca_both_known"])
    s["aspca_cats"], s["aspca_cats_known"] = q("select sum(toxic_to_cats), count(toxic_to_cats) from aspca_toxicity")[0]
    s["aspca_dogs"], s["aspca_dogs_known"] = q("select sum(toxic_to_dogs), count(toxic_to_dogs) from aspca_toxicity")[0]
    s["aspca_horses"], s["aspca_horses_known"] = q("select sum(toxic_to_horses), count(toxic_to_horses) from aspca_toxicity")[0]
    s["aspca_families"] = [(f, c, k, t, pct(t, k)) for f, c, k, t in q(
        "select gbif_family, count(*) c, sum(case when toxic_to_cats is not null and toxic_to_dogs is not null then 1 else 0 end) k, "
        "sum(case when toxic_to_cats=1 or toxic_to_dogs=1 then 1 else 0 end) t from aspca_toxicity "
        "where gbif_family is not null group by 1 order by c desc, 1 limit 15")]
    s["aspca_with_family"] = q("select count(*) from aspca_toxicity where gbif_family is not null")[0][0]

    # families in the care core
    s["family_rows"] = [(f, c, pct(c, s["plants"]), k, t) for f, c, k, t in q(
        "select f.name, count(*) c, sum(case when p.is_toxic_to_cats is not null then 1 else 0 end) k, "
        "sum(case when p.is_toxic_to_cats=1 or p.is_toxic_to_dogs=1 then 1 else 0 end) t "
        "from plants p join plant_families f using(family_id) group by f.name order by c desc, f.name limit 15")]
    s["top15_share"] = pct(sum(r[1] for r in s["family_rows"]), s["plants"])

    # light
    light = []
    for lv, c in q("select light_requirement_level, count(*) from plants group by 1 order by 2 desc, 1"):
        rows = q("select min_lux_threshold, max_lux_threshold, watering_frequency_days, ideal_humidity_percent from plants where light_requirement_level=?", lv)
        med = [statistics.median([r[i] for r in rows]) for i in range(4)]
        light.append((lv, c, pct(c, s["plants"]), med[0], med[1], med[2], med[3]))
    s["light_rows"] = light

    # watering
    s["watering_rows"] = [(d, c, pct(c, s["plants"])) for d, c in q("select watering_frequency_days, count(*) from plants group by 1 order by 1")]
    s["watering_median"] = statistics.median([r[0] for r in q("select watering_frequency_days from plants")])
    s["watering_18plus"] = q("select count(*) from plants where watering_frequency_days >= 18")[0][0]
    s["watering_18plus_sun"] = q("select count(*) from plants where watering_frequency_days >= 18 and light_requirement_level='Direct Sun'")[0][0]

    # care medians
    care = []
    for col, label, unit in METRICS:
        vals = [r[0] for r in q(f"select {col} from plants")]
        mode, mode_c = Counter(vals).most_common(1)[0]
        care.append(dict(metric=label, unit=unit, median=statistics.median(vals), mean=round(statistics.mean(vals), 1),
                         min=min(vals), max=max(vals), mode=mode, mode_n=mode_c, mode_pct=pct(mode_c, len(vals))))
    s["care"] = care
    s["humidity_rows"] = [(h, c, pct(c, s["plants"])) for h, c in q("select ideal_humidity_percent, count(*) from plants group by 1 order by 1")]
    s["temp_min_rows"] = [(t, c) for t, c in q("select min_temp_celsius, count(*) from plants group by 1 order by 1")]
    s["temp_max_rows"] = [(t, c) for t, c in q("select max_temp_celsius, count(*) from plants group by 1 order by 1")]
    s["confidence"] = [(k, c, pct(c, s["plants"])) for k, c in q("select care_confidence, count(*) from plants group by 1 order by 2 desc")]
    con.close()
    return s


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------

CSS = """
    :root { --bg-paper: #12140f; --bg-paper-2: #191c14; --text-ink: #ece7d9; --text-muted: #9a9683;
            --rule-color: rgba(236, 231, 217, 0.18); --accent: #9cbf6a; --sepia: #c39a6b; --radius: 6px; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Spline Sans', system-ui, sans-serif; background: var(--bg-paper); color: var(--text-ink); line-height: 1.6; }
    .serif { font-family: 'Fraunces', serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    header { border-bottom: 1px solid var(--rule-color); padding: 20px 0; background: var(--bg-paper-2); }
    .container { max-width: 1000px; margin: 0 auto; padding: 0 24px; }
    .nav-bar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
    .brand { font-family: 'Fraunces', serif; font-size: 1.4rem; font-weight: 700; color: var(--text-ink); text-decoration: none; }
    .brand .accent { color: var(--accent); }
    .btn-link { color: var(--text-ink); text-decoration: none; font-size: 0.9rem; margin-left: 12px; border: 1px solid var(--rule-color); padding: 8px 16px; border-radius: 4px; transition: all 0.2s; }
    .btn-link:hover { background: var(--accent); color: #12140f; border-color: var(--accent); }
    a { color: var(--accent); }
    .stats-wrap { max-width: 1000px; margin: 0 auto; padding: 44px 24px 64px; }
    .stats-wrap h1 { font-family: 'Fraunces', serif; font-size: clamp(2rem, 3.6vw, 2.8rem); line-height: 1.08; margin: 0 0 8px; }
    .stats-wrap h2 { font-size: 1.5rem; margin: 0; }
    .stats-wrap h3 { font-size: 1.05rem; margin: 24px 0 0; }
    .stats-wrap .lede { font-size: 1.05rem; margin-top: 12px; max-width: 76ch; color: var(--text-muted); }
    .crumb { font-size: .8rem; opacity: .6; margin: 0 0 1rem; }
    .eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--sepia); margin-bottom: 10px; }
    .cta-inline { margin-top: 56px; padding: 28px; border: 1px solid var(--rule-color); border-radius: var(--radius); background: var(--bg-paper-2); }
    .cta-inline p { color: var(--text-muted); margin: 8px 0 16px; }
    .btn-primary { display: inline-block; background: var(--accent); color: #12140f; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 12px 20px; text-decoration: none; border-radius: 4px; }
    footer { margin-top: 60px; border-top: 1px solid var(--rule-color); padding: 30px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }
    .safety-strip { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin-top: 12px; opacity: 0.8; }
"""


def build_page(s, charts):
    site = SITE
    snap = s["snapshot_date"]
    src_note = f"Source: FloraDB, floradb.dataengineered.io/stats · snapshot {snap} · CC BY 4.0"
    sections = []

    # 1. pet toxicity (headline)
    tr = s["tox_rows"]
    charts["toxicity-status"] = svg_hbar(site, "Pet toxicity of the care-core houseplants", f"{n(s['plants'])} plants by ASPCA determination",
                                         [(lbl, c, f"{n(c)} ({pct(c, s['plants'])}%)") for lbl, c in tr], src_note, label_w=236)
    coincide = ("In every determined record the cat and dog verdicts coincide." if s["cats_dogs_differ"] == 0
                else f"The cat and dog verdicts differ on {n(s['cats_dogs_differ'])} plants.")
    sections.append(section(
        site, "pet-toxicity", "How many common houseplants are toxic to cats or dogs",
        f"Of the {n(s['tox_known'])} care-core houseplants with an ASPCA determination, <strong>{n(s['tox_toxic'])} ({s['tox_toxic_pct']}%)</strong> are toxic to cats or dogs: "
        f"{n(tr[0][1])} verified against the ASPCA entry for the species and {n(tr[1][1])} inferred from an ASPCA entry for the genus. "
        f"{n(s['tox_nontoxic'])} are recorded as non-toxic. The other {n(s['tox_unknown'])} of {n(s['plants'])} plants have no determination and are excluded from the share, not assumed safe. {coincide}",
        figure(site, "toxicity-status", charts["toxicity-status"], "Pet toxicity of the care-core houseplants", f"{n(s['plants'])} plants, {n(s['tox_known'])} with a determination"),
        table(["Determination", "Plants", "Share of all plants", "Share of determined plants"],
              [(lbl, n(c), f"{pct(c, s['plants'])}%", f"{pct(c, s['tox_known'])}%" if lbl != "No determination" else "excluded") for lbl, c in tr], {1, 2, 3}),
        f"One row per plant in the care core. <em>ASPCA-verified</em>: the species has its own entry in the ASPCA toxic and non-toxic plant index. <em>Inferred from the genus</em>: "
        f"no species entry exists, but every ASPCA entry for the genus carries the same verdict, so it is applied with <code>toxicity_status = aspca_genus_inferred</code>. "
        f"Plants with neither are stored as NULL. Denominator for the headline share: {n(s['tox_known'])} determined plants. ASPCA index crawled {s['aspca_date']}."))

    # 2. ASPCA index
    af = s["aspca_families"]
    charts["aspca-families"] = svg_hbar(site, "Plant families with the most entries in the ASPCA index", f"Top {len(af)} of the families in {n(s['aspca_with_family'])} entries with a GBIF family",
                                        [(f, c, f"{n(c)} · {p}% toxic") for f, c, k, t, p in af], src_note, label_w=150)
    all_toxic = [f for f, c, k, t, p in af if t == k and k > 0]
    none_toxic = [f for f, c, k, t, p in af if t == 0 and k > 0]
    sections.append(section(
        site, "aspca-index", "What the ASPCA plant index says overall",
        f"Across the {n(s['aspca_both_known'])} ASPCA index entries with both a cat and a dog verdict, <strong>{n(s['aspca_either'])} ({s['aspca_either_pct']}%)</strong> are toxic to at least one of them: "
        f"{n(s['aspca_both'])} to both, {n(s['aspca_cats_only'])} to cats only and {n(s['aspca_dogs_only'])} to dogs only. "
        f"{n(s['aspca_horses'])} of the {n(s['aspca_horses_known'])} entries with a horse verdict are toxic to horses. "
        + (f"Among the largest families, every determined entry of {', '.join(data(f) for f in all_toxic)} is toxic; " if all_toxic else "")
        + (f"none of {', '.join(data(f) for f in none_toxic)} is." if none_toxic else ""),
        figure(site, "aspca-families", charts["aspca-families"], "Plant families with the most entries in the ASPCA index", f"top {len(af)} families by entries"),
        table(["Family (GBIF)", "ASPCA entries", "With both verdicts", "Toxic to cats or dogs", "Share toxic"],
              [(f, n(c), n(k), n(t), f"{p}%") for f, c, k, t, p in af], {1, 2, 3, 4})
        + "<h3>Verdicts by animal</h3>"
        + table(["Animal", "Entries with a verdict", "Toxic", "Share toxic"],
                [("Cats", n(s["aspca_cats_known"]), n(s["aspca_cats"]), f"{pct(s['aspca_cats'], s['aspca_cats_known'])}%"),
                 ("Dogs", n(s["aspca_dogs_known"]), n(s["aspca_dogs"]), f"{pct(s['aspca_dogs'], s['aspca_dogs_known'])}%"),
                 ("Horses", n(s["aspca_horses_known"]), n(s["aspca_horses"]), f"{pct(s['aspca_horses'], s['aspca_horses_known'])}%")], {1, 2, 3}),
        f"The full ASPCA toxic and non-toxic plant index as crawled on {s['aspca_date']}: {n(s['aspca_entries'])} entries covering garden, wild and indoor plants, not only houseplants. "
        f"Each entry is matched to the GBIF backbone; the family shown is GBIF's, which merges older names such as Liliaceae and Compositae into current circumscriptions. "
        f"Entries without a GBIF family ({n(s['aspca_entries'] - s['aspca_with_family'])}) are left out of the family table only."))

    # 3. families
    fr = s["family_rows"]
    charts["families"] = svg_hbar(site, "Families with the most plants in the care core", f"Top {len(fr)} of {n(s['families'])} families, {n(s['plants'])} plants",
                                  [(f, c, f"{n(c)} ({p}%)") for f, c, p, k, t in fr], src_note, label_w=150)
    sections.append(section(
        site, "families", "Which plant families the houseplants come from",
        f"{data(fr[0][0])} contributes the most plants to the care core: <strong>{n(fr[0][1])} of {n(s['plants'])} ({fr[0][2]}%)</strong>, and {n(fr[0][4])} of its {n(fr[0][3])} determined plants are toxic to cats or dogs. "
        f"{data(fr[1][0])} follows with {n(fr[1][1])} and {data(fr[2][0])} with {n(fr[2][1])}. The {len(fr)} largest families hold {s['top15_share']}% of the plants; {n(s['families'])} families are represented in all.",
        figure(site, "families", charts["families"], "Families with the most plants in the care core", f"top {len(fr)} of {n(s['families'])} families"),
        table(["Family", "Plants", "Share", "With a determination", "Toxic to cats or dogs"],
              [(f, n(c), f"{p}%", n(k), n(t)) for f, c, p, k, t in fr], {1, 2, 3, 4}),
        "Family per plant is the GBIF backbone family of the accepted name, re-verified against GBIF on each monthly refresh. "
        "The toxicity columns use the same ASPCA determination as the headline section; plants without one count in the family total but not in the toxic column."))

    # 4. light
    lr = s["light_rows"]
    charts["light"] = svg_hbar(site, "Light requirement of the care-core houseplants", f"{n(s['plants'])} plants by light category",
                               [(lv, c, f"{n(c)} ({p}%)") for lv, c, p, *_ in lr], src_note, label_w=150)
    bi = next(r for r in lr if r[0] == "Bright Indirect")
    ds = next((r for r in lr if r[0] == "Direct Sun"), None)
    sections.append(section(
        site, "light", "How much light the houseplants need",
        f"<strong>{data(lr[0][0])}</strong> is the most common light requirement, {n(lr[0][1])} of {n(s['plants'])} plants ({lr[0][2]}%), followed by {data(lr[1][0])} ({n(lr[1][1])}, {lr[1][2]}%) and {data(lr[2][0])} ({n(lr[2][1])}, {lr[2][2]}%). "
        f"The median lux band of a bright-indirect plant is {n(bi[3])} to {n(bi[4])} lux"
        + (f"; of a direct-sun plant {n(ds[3])} to {n(ds[4])} lux, with a median watering interval of {num(ds[5])} days against {num(bi[5])} for bright-indirect plants." if ds else "."),
        figure(site, "light", charts["light"], "Light requirement of the care-core houseplants", f"{n(s['plants'])} plants"),
        table(["Light category", "Plants", "Share", "Median min lux", "Median max lux", "Median watering (days)", "Median humidity (%)"],
              [(lv, n(c), f"{p}%", n(a), n(b), num(w), num(h)) for lv, c, p, a, b, w, h in lr], {1, 2, 3, 4, 5, 6}),
        "Each plant carries one light category and a lux band (min_lux_threshold, max_lux_threshold) taken from the curated care sources listed on the plant's record. "
        "Medians are computed within the category over all its plants. Lux values are indoor reading thresholds, not measured field values."))

    # 5. watering
    wr = s["watering_rows"]
    top_w = max(wr, key=lambda t: t[1])
    charts["watering"] = svg_hbar(site, "Watering interval of the care-core houseplants", f"{n(s['plants'])} plants by interval in days",
                                  [(f"every {d} days", c, f"{n(c)} ({p}%)") for d, c, p in wr], src_note, label_w=130)
    sections.append(section(
        site, "watering", "How often the houseplants are watered",
        f"<strong>{n(top_w[1])} of {n(s['plants'])} plants ({top_w[2]}%)</strong> are on a {top_w[0]}-day watering interval; the median interval is {num(s['watering_median'])} days and the range {wr[0][0]} to {wr[-1][0]} days. "
        f"{n(s['watering_18plus'])} plants ({pct(s['watering_18plus'], s['plants'])}%) go 18 days or longer between waterings, {n(s['watering_18plus_sun'])} of them direct-sun plants.",
        figure(site, "watering", charts["watering"], "Watering interval of the care-core houseplants", f"{n(s['plants'])} plants"),
        table(["Interval (days)", "Plants", "Share"], [(str(d), n(c), f"{p}%") for d, c, p in wr], {1, 2}),
        "watering_frequency_days is a single indoor guideline value per plant from the curated care sources; seasonal or pot-size adjustments are not modelled and no plant carries a range."))

    # 6. care medians
    cm = s["care"]
    hr = s["humidity_rows"]
    top_h = max(hr, key=lambda t: t[1])
    charts["humidity"] = svg_hbar(site, "Ideal humidity of the care-core houseplants", f"{n(s['plants'])} plants by target humidity",
                                  [(f"{h}%", c, f"{n(c)} ({p}%)") for h, c, p in hr], src_note, label_w=80)
    cd = {c["metric"]: c for c in cm}
    sections.append(section(
        site, "care-medians", "Care requirements: medians and ranges",
        f"The median care-core houseplant wants <strong>{n(cd['Minimum light']['median'])} to {n(cd['Maximum light']['median'])} lux</strong>, water every {num(cd['Watering interval']['median'])} days, "
        f"{num(cd['Minimum temperature']['median'])} to {num(cd['Maximum temperature']['median'])} °C and {num(cd['Ideal humidity']['median'])}% humidity. "
        f"{n(top_h[1])} plants ({top_h[2]}%) target {top_h[0]}% humidity; {n(sum(c for h, c, p in hr if h <= 30))} ({pct(sum(c for h, c, p in hr if h <= 30), s['plants'])}%) target 30% or less.",
        figure(site, "humidity", charts["humidity"], "Ideal humidity of the care-core houseplants", f"{n(s['plants'])} plants"),
        table(["Metric", "Median", "Mean", "Minimum", "Maximum", "Most common value", "Plants at that value"],
              [(f"{c['metric']} ({c['unit']})", num(c["median"]), num(c["mean"]), num(c["min"]), num(c["max"]), num(c["mode"]), f"{n(c['mode_n'])} ({c['mode_pct']}%)") for c in cm],
              {1, 2, 3, 4, 5, 6})
        + "<h3>Temperature range</h3>"
        + table(["Minimum temperature (°C)", "Plants"], [(num(t), n(c)) for t, c in s["temp_min_rows"]], {1})
        + table(["Maximum temperature (°C)", "Plants"], [(num(t), n(c)) for t, c in s["temp_max_rows"]], {1}),
        f"All {n(s['plants'])} plants carry every care metric, so each denominator is {n(s['plants'])}. Values are the curated indoor guideline per plant; "
        f"care_confidence records how well the sources agree: {', '.join(f'{n(c)} {k}' for k, c, p in s['confidence'])}."))

    contents = toc([("pet-toxicity", "Toxic to cats or dogs"), ("aspca-index", "The ASPCA index overall"), ("families", "Plant families"),
                    ("light", "Light requirements"), ("watering", "Watering intervals"), ("care-medians", "Care medians and ranges"),
                    ("method", "Method, reuse and citation")])
    tile_html = tiles([("Care-core plants", n(s["plants"])), ("With ASPCA determination", n(s["tox_known"])), ("ASPCA index entries", n(s["aspca_entries"])),
                       ("Families", n(s["families"])), ("Species index", n(s["species_index"])), ("Snapshot", snap)])
    title_tag = f"Houseplant Statistics {snap[:4]} — Pet Toxicity, Light, Watering, Families | FloraDB"
    desc = (f"Houseplants in numbers: {s['tox_toxic_pct']}% of {n(s['tox_known'])} determined care-core plants are toxic to cats or dogs (ASPCA), "
            f"{s['aspca_either_pct']}% of the ASPCA index; light and watering distributions, families with the most plants, care medians. Free to cite and embed.")
    ld = article_ld(site, "Houseplants in numbers: statistics from the FloraDB care core and the ASPCA index", desc, FIRST_PUBLISHED,
                    f"{site.base_url}/og-image.png", ["houseplants", "pet toxicity", "ASPCA", "plant care", "GBIF"])

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title_tag)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{site.page_url}">
  <link rel="alternate" hreflang="en" href="{site.page_url}">
  <meta property="og:title" content="Houseplants in numbers — FloraDB statistics {snap[:4]}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{site.page_url}">
  <meta property="og:image" content="{site.base_url}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#12140f">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet"></noscript>
{ld}
  <style>{CSS}{STATS_CSS}  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Flora<span class="accent">DB</span></a>
      <div>
        <a href="/#explorer" class="btn-link">Explorer</a>
        <a href="/#pricing" class="btn-link">Collection</a>
      </div>
    </div>
  </header>
<main class="stats-wrap">
  <p class="crumb"><a href="/">Home</a> &rsaquo; <span>Statistics</span></p>
  <p class="eyebrow">Statistics · snapshot {esc(snap)}</p>
  <h1>Houseplants in numbers</h1>
  <p class="lede">Aggregate statistics computed from the full FloraDB snapshot: {n(s['plants'])} care-core houseplants with quantitative light, watering, temperature and humidity requirements, joined to the {n(s['aspca_entries'])}-entry ASPCA toxicity index and verified against the GBIF backbone. Every figure states its denominator and is free to cite, quote and embed with a link to this page.</p>
  <ul class="tiles">{tile_html}</ul>
  <nav class="toc" aria-label="Contents"><strong>On this page</strong><ol>{contents}</ol></nav>

{"".join(sections)}

  <section class="stat" id="method">
    <h2 class="serif">Method, reuse and citation</h2>
    <ul class="method">
      <li><strong>Source.</strong> The full FloraDB snapshot of {snap}: {n(s['plants'])} care-core plants, {n(s['aspca_entries'])} ASPCA index entries (crawled {s['aspca_date']}), {n(s['species_index'])} GBIF-accepted species in the taxonomic index and {n(s['enriched'])} enriched species. Every row keeps its source URL and retrieval time; see the <a href="/DATA_DICTIONARY.md">data dictionary</a>.</li>
      <li><strong>Nothing is estimated.</strong> Toxicity is the ASPCA verdict for the species or, when every entry of the genus agrees, for the genus, and is otherwise NULL and excluded from the share. Care values are the curated guideline per plant. Where a denominator is smaller than {n(s['plants'])}, the section says so.</li>
      <li><strong>Not veterinary advice.</strong> Toxicity data is informational. If a pet ingests a plant, contact a veterinarian or ASPCA Animal Poison Control.</li>
      <li><strong>Refresh.</strong> The care core is re-verified against GBIF monthly; the ASPCA index is re-crawled on a manual, roughly quarterly cadence. This page and its charts are regenerated with each snapshot, so figures move. Cite the snapshot date.</li>
      <li><strong>Reuse.</strong> The figures and charts on this page are published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>: use them in articles, slides and posts with a link to <span translate="no">{site.page_url}</span>. The machine-readable version is <a href="/stats/data.json">data.json</a>. The underlying row-level dataset is a separate <a href="/#pricing">commercial product</a>; a free 100-plant sample is in the <a href="https://github.com/FloraaDB/houseplants-botanical-floradb">public repository</a>.</li>
      <li><strong>Suggested citation.</strong> <span translate="no">FloraDB ({snap[:4]}). <em>Houseplants in numbers</em>, snapshot {snap}. DataEngineered. {site.page_url}</span></li>
      <li><strong>Questions or corrections:</strong> <a href="/#support">contact form</a> or floradb@dataengineered.io.</li>
    </ul>
  </section>

  <div class="cta-inline">
    <h3 class="serif" style="margin:0">Need the plant-level records behind these numbers?</h3>
    <p>Every plant with its lux band, watering interval, temperature and humidity targets, ASPCA verdict and clinical signs, GBIF key and source URL, as SQLite, CSV and JSON.</p>
    <a class="btn-primary" href="/#pricing">Get the full dataset ($49)</a>
  </div>
</main>
<footer>
  <div class="container">
    <p>FloraDB — Botanical Houseplant Care &amp; Pet-Toxicity Snapshot · <a href="/#pricing">Get Full Relational Dataset ($49)</a></p>
    <div class="safety-strip">Toxicity data is informational, not veterinary advice. If a pet ingests a plant, contact a vet or ASPCA Animal Poison Control.</div>
    <div class="catalog-line" style="text-align:center; margin-top:14px; font-size:0.85rem; opacity:0.85;"><a href="https://dataengineered.io/">Part of the DataEngineered catalog &rarr;</a> &middot; <a href="https://dataengineered.io/about">About</a> &middot; <a href="https://dataengineered.io/terms">Terms</a> &middot; <a href="https://dataengineered.io/privacy">Privacy</a> &middot; <a href="https://dataengineered.io/refund-policy">Refund policy</a></div>
  </div>
</footer>
{COPY_JS}
</body>
</html>
"""


def build_data_json(s):
    return {
        "dataset": SITE.brand, "page": SITE.page_url, "generated": dt.date.today().isoformat(), "snapshot": s["snapshot_date"],
        "aspca_crawled": s["aspca_date"],
        "license": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) - attribute with a link to the page",
        "totals": {k: s[k] for k in ("plants", "families", "aspca_entries", "species_index", "enriched")},
        "pet_toxicity_care_core": {"determined": s["tox_known"], "toxic_to_cats_or_dogs": s["tox_toxic"], "toxic_pct_of_determined": s["tox_toxic_pct"],
                                   "non_toxic": s["tox_nontoxic"], "no_determination": s["tox_unknown"], "cat_dog_verdicts_differ": s["cats_dogs_differ"],
                                   "by_determination": [dict(determination=lbl, plants=c) for lbl, c in s["tox_rows"]]},
        "aspca_index": {"entries": s["aspca_entries"], "with_both_verdicts": s["aspca_both_known"], "toxic_to_cats_or_dogs": s["aspca_either"],
                        "toxic_pct": s["aspca_either_pct"], "toxic_to_both": s["aspca_both"], "cats_only": s["aspca_cats_only"], "dogs_only": s["aspca_dogs_only"],
                        "non_toxic_to_both": s["aspca_neither"],
                        "by_animal": [dict(animal="cats", with_verdict=s["aspca_cats_known"], toxic=s["aspca_cats"]),
                                      dict(animal="dogs", with_verdict=s["aspca_dogs_known"], toxic=s["aspca_dogs"]),
                                      dict(animal="horses", with_verdict=s["aspca_horses_known"], toxic=s["aspca_horses"])],
                        "families": [dict(family=f, entries=c, with_both_verdicts=k, toxic=t, toxic_pct=p) for f, c, k, t, p in s["aspca_families"]]},
        "families": [dict(family=f, plants=c, share_pct=p, determined=k, toxic=t) for f, c, p, k, t in s["family_rows"]],
        "light": [dict(category=lv, plants=c, share_pct=p, median_min_lux=a, median_max_lux=b, median_watering_days=w, median_humidity_pct=h) for lv, c, p, a, b, w, h in s["light_rows"]],
        "watering": {"median_days": s["watering_median"], "rows": [dict(days=d, plants=c, share_pct=p) for d, c, p in s["watering_rows"]]},
        "care_metrics": s["care"],
        "humidity": [dict(humidity_pct=h, plants=c, share_pct=p) for h, c, p in s["humidity_rows"]],
        "temperature": {"min": [dict(celsius=t, plants=c) for t, c in s["temp_min_rows"]], "max": [dict(celsius=t, plants=c) for t, c in s["temp_max_rows"]]},
        "care_confidence": [dict(level=k, plants=c, share_pct=p) for k, c, p in s["confidence"]],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--db", default=os.environ.get("FLORADB_SQLITE", str(DEFAULT_DB)))
    args = ap.parse_args()
    db = Path(args.db)
    if not db.is_file():
        raise SystemExit(f"SQLite snapshot not found: {db}")
    s = compute(db)
    charts = {}
    page = build_page(s, charts)
    write_outputs(OUT_DIR, page, charts, build_data_json(s))
    print(f"stats/index.html + {len(charts)} charts + data.json  (snapshot {s['snapshot_date']}, {s['plants']:,} plants)")


if __name__ == "__main__":
    main()
