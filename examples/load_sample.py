"""Load the FloraDB free sample and print a quick summary.

    python examples/load_sample.py

No dependencies beyond the Python standard library.
Full dataset: https://houseplants-botanical-floradb.pages.dev
"""

import csv
import os
from collections import Counter

SAMPLE = os.path.join(os.path.dirname(__file__), "..", "samples", "floradb_sample.csv")


def main() -> None:
    with open(SAMPLE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    families = {r["family"] for r in rows}
    print(f"{len(rows)} plants from {len(families)} families\n")

    print("Top families:")
    for family, n in Counter(r["family"] for r in rows).most_common(5):
        print(f"  {family:16} {n}")

    print("\nPet safety (toxicity determined vs unknown):")
    for status, n in Counter(r["toxicity_status"] for r in rows).most_common():
        print(f"  {status:22} {n}")

    # Plants safe for cats (explicitly determined non-toxic — never guessed)
    cat_safe = [r for r in rows if r["toxicity_status"] != "unknown" and r["is_toxic_to_cats"] == "0"]
    print(f"\nExplicitly cat-safe plants in sample: {len(cat_safe)}")
    for r in cat_safe[:5]:
        print(f"  {r['common_name']} ({r['scientific_name']})")

    print("\nExample — care metrics + provenance:")
    r = rows[0]
    print(f"  {r['common_name']} — {r['scientific_name']}")
    print(f"    light  : {r['light_requirement_level']} ({r['min_lux']}-{r['max_lux']} lux)")
    print(f"    water  : every {r['watering_frequency_days']} days · {r['min_temp_celsius']}-{r['max_temp_celsius']}C · {r['ideal_humidity_percent']}% humidity")
    print(f"    toxic  : dogs={r['is_toxic_to_dogs'] or '?'} cats={r['is_toxic_to_cats'] or '?'} [{r['toxicity_status']}]")
    print(f"    source : {r['gbif_source_url']}")


if __name__ == "__main__":
    main()
