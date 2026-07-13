import csv
import os
import re
import datetime

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(root_dir, 'samples', 'floradb_sample.csv')
    plants_dir = os.path.join(root_dir, 'plants')
    families_dir = os.path.join(root_dir, 'families')

    os.makedirs(plants_dir, exist_ok=True)
    os.makedirs(families_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"Error: CSV not found at {csv_path}")
        return

    plants = []
    with open(csv_path, mode='r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('scientific_name') and row.get('common_name'):
                plants.append(row)

    print(f"Loaded {len(plants)} houseplant specimen records from CSV.")

    # Group by family
    families = {}
    for p in plants:
        fam = p.get('family', 'Unclassified').strip() or 'Unclassified'
        if fam not in families:
            families[fam] = []
        families[fam].append(p)

    sitemap_urls = [
        ("https://houseplants-botanical-floradb.pages.dev/", "1.0", "weekly")
    ]

    # Generate Plant Specimen Pages
    for p in plants:
        sci = p.get('scientific_name', '').strip()
        common = p.get('common_name', '').strip()
        fam = p.get('family', 'Unclassified').strip()
        plant_id = p.get('plant_id', '')
        slug = slugify(f"{sci}-{common}")
        fam_slug = slugify(fam)

        min_lux = p.get('min_lux', 'N/A')
        max_lux = p.get('max_lux', 'N/A')
        water_days = p.get('watering_frequency_days', '7')
        min_temp = p.get('min_temp_celsius', '15')
        max_temp = p.get('max_temp_celsius', '30')
        humidity = p.get('ideal_humidity_percent', '50')
        light_level = p.get('light_requirement_level', 'Medium to Bright')
        
        dog_toxic = p.get('is_toxic_to_dogs', '0') == '1'
        cat_toxic = p.get('is_toxic_to_cats', '0') == '1'
        symptoms = p.get('toxicity_symptoms', 'None reported.')
        gbif_key = p.get('gbif_usage_key', '')
        gbif_url = p.get('gbif_source_url', f"https://www.gbif.org/species/{gbif_key}" if gbif_key else "#")
        img_url = p.get('image_url', '../og-image.png')
        native = p.get('native_range', 'Various indoor/tropical regions')

        pet_status_badge = '<span style="background:rgba(217,83,79,0.18);color:#ff6b6b;padding:4px 10px;border-radius:4px;font-weight:600;border:1px solid rgba(217,83,79,0.3);">⚠️ TOXIC TO PETS</span>' if (dog_toxic or cat_toxic) else '<span style="background:rgba(74,107,47,0.18);color:var(--accent);padding:4px 10px;border-radius:4px;font-weight:600;border:1px solid rgba(74,107,47,0.3);">🟢 PET SAFE</span>'

        page_url = f"https://houseplants-botanical-floradb.pages.dev/plants/{slug}"
        sitemap_urls.append((page_url, "0.8", "monthly"))

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{sci} ({common}) Care Metrics & ASPCA Pet Toxicity — FloraDB</title>
  <meta name="description" content="Quantitative care threshold for {sci} ({common}): {min_lux}–{max_lux} Lux light, watering every {water_days} days, ASPCA dog/cat toxicity verified ({symptoms}). GBIF key {gbif_key}." />
  <meta name="keywords" content="{sci}, {common}, {fam}, houseplant care, lux thresholds, watering frequency, ASPCA pet toxicity, toxic to cats dogs, GBIF taxonomy {gbif_key}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />
  <link rel="icon" href="../favicon.svg" type="image/svg+xml" />

  <meta property="og:title" content="{sci} ({common}) Care & Toxicity Record — FloraDB" />
  <meta property="og:description" content="Exact Lux light requirements ({min_lux}–{max_lux} Lux), watering intervals ({water_days} days), and ASPCA pet safety clinical symptoms." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="article" />
  <meta property="og:image" content="{img_url}" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "{sci} ({common}) Botanical Care & Pet-Toxicity Record",
    "description": "Normalized botanical care parameters for {sci} ({common}): light requirements of {min_lux} to {max_lux} Lux, watering interval of {water_days} days, ideal humidity {humidity}%, and ASPCA dog/cat toxicity verification.",
    "url": "{page_url}",
    "creator": {{"@type": "Organization", "name": "FloraDB", "url": "https://houseplants-botanical-floradb.pages.dev"}},
    "license": "https://creativecommons.org/licenses/by-nc/4.0/",
    "isAccessibleForFree": true,
    "variableMeasured": ["min/max Lux light", "watering frequency in days", "temperature range", "ideal humidity", "toxic to dogs", "toxic to cats", "clinical toxicity symptoms", "GBIF taxonomic key"]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://houseplants-botanical-floradb.pages.dev/"}},
      {{"@type": "ListItem", "position": 2, "name": "Families Hub", "item": "https://houseplants-botanical-floradb.pages.dev/families/{fam_slug}"}},
      {{"@type": "ListItem", "position": 3, "name": "{sci}", "item": "{page_url}"}}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet"></noscript>

  <style>
    :root {{
      --bg-paper: #12140f;
      --bg-paper-2: #191c14;
      --text-ink: #ece7d9;
      --text-muted: #9a9683;
      --rule-color: rgba(236, 231, 217, 0.18);
      --accent: #9cbf6a;
      --sepia: #c39a6b;
      --card-bg: #191c14;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Spline Sans', sans-serif; background: var(--bg-paper); color: var(--text-ink); line-height: 1.6; padding-bottom: 60px; }}
    .serif {{ font-family: 'Fraunces', serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    header {{ border-bottom: 1px solid var(--rule-color); padding: 20px 0; background: var(--bg-paper-2); }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 0 24px; }}
    .nav-bar {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-family: 'Fraunces', serif; font-size: 1.4rem; font-weight: 700; color: var(--text-ink); text-decoration: none; }}
    .brand .accent {{ color: var(--accent); }}
    .btn-link {{ color: var(--text-ink); text-decoration: none; font-size: 0.9rem; margin-left: 20px; border: 1px solid var(--rule-color); padding: 8px 16px; border-radius: 4px; transition: all 0.2s; }}
    .btn-link:hover {{ background: var(--accent); color: #12140f; border-color: var(--accent); }}
    .hero {{ padding: 40px 0; border-bottom: 1px solid var(--rule-color); }}
    .badge-strip {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }}
    .specimen-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 32px; }}
    @media(max-width: 768px) {{ .specimen-grid {{ grid-template-columns: 1fr; }} }}
    .card {{ background: var(--card-bg); border: 1px solid var(--rule-color); padding: 24px; border-radius: 6px; }}
    .metric-row {{ display: flex; justify-content: space-between; border-bottom: 1px dashed var(--rule-color); padding: 12px 0; }}
    .metric-row:last-child {{ border-bottom: none; }}
    .metric-label {{ color: var(--text-muted); font-size: 0.9rem; }}
    .metric-val {{ font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
    .img-box {{ width: 100%; max-height: 380px; overflow: hidden; border-radius: 6px; border: 1px solid var(--rule-color); margin-bottom: 24px; }}
    .img-box img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    footer {{ margin-top: 60px; border-top: 1px solid var(--rule-color); padding: 30px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }}
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Flora<span class="accent">DB</span></a>
      <div>
        <a href="/#explorer" class="btn-link">← Explorer</a>
        <a href="../families/{fam_slug}" class="btn-link">Family: {fam}</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <div class="badge-strip">
        <span class="mono" style="font-size:0.8rem; color:var(--sepia);">SPECIMEN NO. #{plant_id}</span>
        {pet_status_badge}
        <span class="mono" style="font-size:0.8rem; background:rgba(236,231,217,0.08); padding:4px 10px; border-radius:4px;">Family: {fam}</span>
      </div>
      <h1 class="serif" style="font-size: 2.6rem; font-weight: 700; margin-bottom: 8px;">{sci}</h1>
      <h2 style="font-size: 1.3rem; font-weight: 400; color: var(--text-muted);">Common Name: {common}</h2>
    </section>

    <div class="specimen-grid">
      <div>
        <div class="img-box">
          <img src="{img_url}" alt="{sci} ({common}) botanical field specimen photograph" onerror="this.src='../og-image.png'" />
        </div>
        <div class="card">
          <h3 class="serif" style="font-size:1.3rem; margin-bottom:16px; border-bottom:1px solid var(--rule-color); padding-bottom:10px;">ASPCA Pet Toxicity Determination</h3>
          <div class="metric-row">
            <span class="metric-label">Toxic to Dogs?</span>
            <span class="metric-val" style="color:{'#ff6b6b' if dog_toxic else 'var(--accent)'};">{'YES (Toxic)' if dog_toxic else 'NO (Safe)'}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Toxic to Cats?</span>
            <span class="metric-val" style="color:{'#ff6b6b' if cat_toxic else 'var(--accent)'};">{'YES (Toxic)' if cat_toxic else 'NO (Safe)'}</span>
          </div>
          <div style="margin-top: 16px;">
            <strong style="font-size:0.88rem; color:var(--sepia);">Clinical Symptoms:</strong>
            <p style="font-size:0.86rem; color:var(--text-muted); margin-top:6px; line-height:1.5;">{symptoms}</p>
          </div>
        </div>
      </div>

      <div>
        <div class="card" style="margin-bottom: 24px;">
          <h3 class="serif" style="font-size:1.3rem; margin-bottom:16px; border-bottom:1px solid var(--rule-color); padding-bottom:10px;">Quantitative Care Thresholds</h3>
          <div class="metric-row">
            <span class="metric-label">Light Level Profile</span>
            <span class="metric-val">{light_level}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Minimum Light Requirement</span>
            <span class="metric-val">{min_lux} Lux</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Maximum Light Tolerance</span>
            <span class="metric-val">{max_lux} Lux</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Watering Frequency</span>
            <span class="metric-val">Every {water_days} Days</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Temperature Envelope</span>
            <span class="metric-val">{min_temp}°C – {max_temp}°C</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Ideal Ambient Humidity</span>
            <span class="metric-val">{humidity}% RH</span>
          </div>
        </div>

        <div class="card">
          <h3 class="serif" style="font-size:1.3rem; margin-bottom:16px; border-bottom:1px solid var(--rule-color); padding-bottom:10px;">Taxonomic & Field Verification</h3>
          <div class="metric-row">
            <span class="metric-label">GBIF Usage Key</span>
            <span class="metric-val">{gbif_key or 'N/A'}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Native Biogeographical Range</span>
            <span class="metric-val" style="text-align:right; max-width:60%;">{native[:80] + ('...' if len(native) > 80 else '')}</span>
          </div>
          <div style="margin-top: 20px; text-align: center;">
            <a href="{gbif_url}" target="_blank" rel="noopener noreferrer" class="btn-link" style="display:inline-block; margin:0;">🔬 Verify on GBIF Species Portal</a>
          </div>
        </div>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      <p>FloraDB — Botanical Houseplant Care & Pet-Toxicity Snapshot · <a href="/#pricing" style="color:var(--accent); text-decoration:none;">Get Full Relational Dataset ($49)</a></p>
    </div>
  </footer>
</body>
</html>"""
        with open(os.path.join(plants_dir, f"{slug}.html"), mode='w', encoding='utf-8') as f_out:
            f_out.write(html_content)

    # Generate Family Hub Pages
    for fam_name, members in families.items():
        fam_slug = slugify(fam_name)
        page_url = f"https://houseplants-botanical-floradb.pages.dev/families/{fam_slug}"
        sitemap_urls.append((page_url, "0.9", "monthly"))

        total_members = len(members)
        toxic_count = sum(1 for m in members if m.get('is_toxic_to_dogs', '0') == '1' or m.get('is_toxic_to_cats', '0') == '1')
        avg_water = round(sum(int(m.get('watering_frequency_days', 7)) for m in members if m.get('watering_frequency_days', '').isdigit()) / max(1, total_members), 1)

        cards_html = ""
        for m in members:
            sci = m.get('scientific_name', '').strip()
            common = m.get('common_name', '').strip()
            m_slug = slugify(f"{sci}-{common}")
            min_l = m.get('min_lux', '1000')
            max_l = m.get('max_lux', '4000')
            w_days = m.get('watering_frequency_days', '7')
            is_tox = m.get('is_toxic_to_dogs', '0') == '1' or m.get('is_toxic_to_cats', '0') == '1'
            badge = '<span style="color:#ff6b6b;">⚠️ Toxic to Pets</span>' if is_tox else '<span style="color:var(--accent);">🟢 Pet Safe</span>'

            cards_html += f"""
        <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="mono" style="font-size:0.75rem; color:var(--sepia);">SPECIMEN #{m.get('plant_id', '')}</span>
              {badge}
            </div>
            <h3 class="serif" style="font-size:1.2rem; font-weight:700;"><a href="../plants/{m_slug}" style="color:var(--text-ink); text-decoration:none;">{sci}</a></h3>
            <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:14px;">{common}</p>
          </div>
          <div style="border-top:1px dashed var(--rule-color); padding-top:12px; font-size:0.85rem;">
            <div style="display:flex; justify-content:space-between;">
              <span style="color:var(--text-muted);">Lux Range:</span>
              <span class="mono">{min_l}–{max_l} Lux</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px;">
              <span style="color:var(--text-muted);">Watering:</span>
              <span class="mono">Every {w_days} days</span>
            </div>
            <div style="margin-top:14px; text-align:right;">
              <a href="../plants/{m_slug}" class="btn-link" style="margin:0; padding:6px 12px; font-size:0.8rem;">View Specimen Details →</a>
            </div>
          </div>
        </div>"""

        html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Botanical Family {fam_name} — Houseplant Care & Pet Toxicity — FloraDB</title>
  <meta name="description" content="Explore {total_members} houseplants in the {fam_name} botanical family. Quantitative care thresholds (Lux, watering intervals) and ASPCA pet-toxicity statuses." />
  <meta name="keywords" content="{fam_name}, houseplant family, botanical family care, ASPCA toxicity {fam_name}, lux requirements" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{page_url}" />
  <link rel="alternate" hreflang="en" href="{page_url}" />
  <link rel="alternate" hreflang="x-default" href="{page_url}" />
  <link rel="icon" href="../favicon.svg" type="image/svg+xml" />

  <meta property="og:title" content="Botanical Family: {fam_name} — FloraDB Collection" />
  <meta property="og:description" content="{total_members} verified determinations with quantitative light/water parameters and ASPCA pet safety profiles." />
  <meta property="og:url" content="{page_url}" />
  <meta property="og:type" content="website" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Botanical Family: {fam_name}",
    "description": "Taxonomic houseplant collection containing {total_members} determinations within the {fam_name} family.",
    "url": "{page_url}"
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,500&family=JetBrains+Mono:wght@400;500&family=Spline+Sans:wght@400;500;600&display=swap" rel="stylesheet"></noscript>

  <style>
    :root {{
      --bg-paper: #12140f;
      --bg-paper-2: #191c14;
      --text-ink: #ece7d9;
      --text-muted: #9a9683;
      --rule-color: rgba(236, 231, 217, 0.18);
      --accent: #9cbf6a;
      --sepia: #c39a6b;
      --card-bg: #191c14;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Spline Sans', sans-serif; background: var(--bg-paper); color: var(--text-ink); line-height: 1.6; padding-bottom: 60px; }}
    .serif {{ font-family: 'Fraunces', serif; }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    header {{ border-bottom: 1px solid var(--rule-color); padding: 20px 0; background: var(--bg-paper-2); }}
    .container {{ max-width: 1050px; margin: 0 auto; padding: 0 24px; }}
    .nav-bar {{ display: flex; justify-content: space-between; align-items: center; }}
    .brand {{ font-family: 'Fraunces', serif; font-size: 1.4rem; font-weight: 700; color: var(--text-ink); text-decoration: none; }}
    .brand .accent {{ color: var(--accent); }}
    .btn-link {{ color: var(--text-ink); text-decoration: none; font-size: 0.9rem; margin-left: 20px; border: 1px solid var(--rule-color); padding: 8px 16px; border-radius: 4px; transition: all 0.2s; }}
    .btn-link:hover {{ background: var(--accent); color: #12140f; border-color: var(--accent); }}
    .hero {{ padding: 40px 0; border-bottom: 1px solid var(--rule-color); }}
    .stat-bar {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 24px; }}
    @media(max-width:600px) {{ .stat-bar {{ grid-template-columns: 1fr; }} }}
    .stat-box {{ background: var(--bg-paper-2); border: 1px solid var(--rule-color); padding: 16px; border-radius: 6px; text-align: center; }}
    .stat-num {{ font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--accent); }}
    .stat-label {{ font-size: 0.85rem; color: var(--text-muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 24px; margin-top: 36px; }}
    .card {{ background: var(--card-bg); border: 1px solid var(--rule-color); padding: 20px; border-radius: 6px; transition: transform 0.2s; }}
    .card:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
    footer {{ margin-top: 60px; border-top: 1px solid var(--rule-color); padding: 30px 0; text-align: center; font-size: 0.85rem; color: var(--text-muted); }}
  </style>
</head>
<body>
  <header>
    <div class="container nav-bar">
      <a href="/" class="brand">Flora<span class="accent">DB</span></a>
      <div>
        <a href="/#explorer" class="btn-link">← Specimen Explorer</a>
        <a href="/#pricing" class="btn-link">Full Dataset Snapshot ($49)</a>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="hero">
      <span class="mono" style="font-size:0.8rem; color:var(--sepia);">BOTANICAL FAMILY HUB</span>
      <h1 class="serif" style="font-size: 2.8rem; font-weight: 700; margin-top: 6px;">{fam_name}</h1>
      <p style="color: var(--text-muted); max-width: 700px; margin-top: 8px;">Taxonomic classification grouping verified indoor houseplant specimens with standardized quantitative care profiles and clinical pet toxicity thresholds.</p>

      <div class="stat-bar">
        <div class="stat-box">
          <div class="stat-num">{total_members}</div>
          <div class="stat-label">Specimens in Sample</div>
        </div>
        <div class="stat-box">
          <div class="stat-num">{avg_water}d</div>
          <div class="stat-label">Avg. Watering Interval</div>
        </div>
        <div class="stat-box">
          <div class="stat-num" style="color:{'#ff6b6b' if toxic_count > 0 else 'var(--accent)'};">{toxic_count}/{total_members}</div>
          <div class="stat-label">Specimens Toxic to Pets</div>
        </div>
      </div>
    </section>

    <div class="grid">
      {cards_html}
    </div>
  </main>

  <footer>
    <div class="container">
      <p>FloraDB — Houseplant Care & Pet-Toxicity Dataset · <a href="/" style="color:var(--accent); text-decoration:none;">Back to Main Catalog</a></p>
    </div>
  </footer>
</body>
</html>"""
        with open(os.path.join(families_dir, f"{fam_slug}.html"), mode='w', encoding='utf-8') as f_out:
            f_out.write(html_content)

    # Generate updated sitemap.xml
    sitemap_path = os.path.join(root_dir, 'sitemap.xml')
    today_str = datetime.date.today().isoformat()
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, prio, freq in sitemap_urls:
        sitemap_xml.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_str}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")
    sitemap_xml.append('</urlset>')

    with open(sitemap_path, mode='w', encoding='utf-8') as f_sitemap:
        f_sitemap.write("\n".join(sitemap_xml) + "\n")

    print(f"Successfully generated {len(plants)} specimen pages (`plants/*.html`), {len(families)} family hubs (`families/*.html`), and updated sitemap.xml with {len(sitemap_urls)} URLs!")

if __name__ == '__main__':
    main()
