# FloraDB — Data Dictionary

Field reference for the FloraDB houseplant care dataset (snapshot `2026.07`).
The free sample (`samples/floradb_sample.csv`) uses the columns below. The full
dataset ships the same fields in CSV and JSON, plus a relational SQLite build with
the ASPCA toxicity layer, the 20,000+ species taxonomic index, and enrichment.

## Columns

| Column | Type | Description | Coverage* |
| :--- | :--- | :--- | ---: |
| `plant_id` | integer | Stable identifier for the plant record | 100% |
| `scientific_name` | string | GBIF-accepted canonical Latin binomial | 100% |
| `synonym_scientific_name` | string | Widely-used horticultural/trade synonym, where it differs | 22% |
| `common_name` | string | Primary English common name | 100% |
| `family` | string | Botanical family (GBIF-verified) | 100% |
| `light_requirement_level` | enum | `Low` · `Medium to Low` · `Medium` · `Medium to Bright` · `Bright Indirect` · `Direct Sun` · `Low to Bright` | 100% |
| `min_lux` | integer | Minimum light for active growth, in Lux (normalized from the light category) | 100% |
| `max_lux` | integer | Maximum tolerated light before leaf scorch, in Lux | 100% |
| `watering_frequency_days` | integer | Recommended watering interval, in days | 100% |
| `min_temp_celsius` | float | Minimum healthy ambient temperature (°C) | 100% |
| `max_temp_celsius` | float | Maximum healthy ambient temperature (°C) | 100% |
| `ideal_humidity_percent` | integer | Target relative humidity (%) | 100% |
| `is_toxic_to_dogs` | boolean | `1` toxic · `0` safe · blank when `toxicity_status = unknown` | 63%† |
| `is_toxic_to_cats` | boolean | `1` toxic · `0` safe · blank when unknown | 63%† |
| `toxicity_symptoms` | string | Clinical ingestion signs (ASPCA) where determined | 63% |
| `toxicity_status` | enum | `aspca_verified` · `aspca_genus_inferred` · `unknown` — never guessed "safe" | 100% |
| `care_confidence` | enum | `high` (hand-authored) · `medium` (family-normalized) · `low` (generic default) | 100% |
| `vernacular_names_en` | string | Representative English common name from GBIF vernacular data | 81% |
| `native_range` | string | Best-effort distribution / establishment locality (GBIF) | 96% |
| `image_url` | string | Reference to one representative CC-licensed image (not redistributed) | 99% |
| `image_license` | string | License of the referenced image | 99% |
| `image_commercial_safe` | boolean | `1` = CC0/CC-BY/CC-BY-SA (commercial OK); `0` = NC/ND/all-rights-reserved | 99% |
| `gbif_usage_key` | integer | GBIF backbone usage key | 100% |
| `gbif_source_url` | string | GBIF species page the taxonomy was verified against | 100% |
| `dataset_version` | string | Snapshot id, e.g. `2026.07` | 100% |

\* Share of the full care core (270 plants) with a non-empty value.
† Toxicity is determined for 63% (species-verified or conservatively genus-inferred); the rest are `unknown` by design.

## Sources & collection methodology

**Sources**
- **GBIF — Global Biodiversity Information Facility** ([gbif.org](https://www.gbif.org), API `api.gbif.org/v1`) — Taxonomic Backbone used to verify scientific names, resolve synonyms to accepted names, assign botanical family, and supply vernacular names and native range. *GBIF Backbone Taxonomy is licensed CC BY 4.0.*
- **ASPCA — Animal Poison Control, Toxic and Non-Toxic Plants** ([aspca.org](https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants)) — source of the dog/cat/horse toxicity determinations and clinical ingestion signs. *Toxicity facts are credited to ASPCA.*
- **Image references** via GBIF occurrence media (e.g. iNaturalist) — one representative image URL per species under its own license (`image_license`, mostly CC BY-NC). *Images are referenced, not redistributed.*
- **Curated horticultural references** — the quantitative care metrics are a normalization of standard horticultural knowledge, not a single scraped database.

**Collection methodology**
1. **Taxonomy (GBIF, live API).** Each name is matched against the GBIF backbone (`/species/match`); synonyms are followed to the accepted name (e.g. *Sansevieria trifasciata* → *Dracaena trifasciata*), family is recorded, and a re-verifiable `gbif_source_url` is stored on every row.
2. **Toxicity (ASPCA).** Ingested politely, honoring the site's `robots.txt` 10-second crawl-delay with a descriptive User-Agent. `toxicity_status` records the origin of each determination — `aspca_verified` (species listed), `aspca_genus_inferred` (conservative, safe-direction only), or `unknown` — and toxicity is **never guessed "safe."**
3. **Care (category-normalized).** A standardized light category maps to a fixed Lux band; watering interval, temperature range, and humidity come from plant-type and family profiles. Every row is graded by `care_confidence`.

All collection was rate-limited and politely identified. **Update frequency: quarterly** (snapshot `2026.07`).

## Notes

- **Care metrics are category-normalized, not measurements.** A `light_requirement_level` maps to a standard `min_lux`/`max_lux` band; watering/temperature/humidity come from plant-type and family norms. The `care_confidence` flag grades each row.
- **Toxicity is safety-first.** `aspca_verified` is a species-level ASPCA determination; `aspca_genus_inferred` means the species' genus has ASPCA-listed toxic members (conservative over-warning, pending review); `unknown` is never treated as "safe".
- **Images are references only.** We store a URL + license + attribution, not the pixels. Filter on `image_commercial_safe = 1` before any commercial use.
- **Provenance.** `gbif_source_url` re-verifies the taxonomy; the full dataset's `data_sources` ledger records the exact ASPCA/GBIF endpoints and timestamps for every record.
- **Relational build (full dataset).** The SQLite export includes `plants`, `plant_families`, `data_sources`, `taxonomy_verifications`, `species_index` (20,000+), `aspca_toxicity` (891), and `species_enrichment` (702).

Full dataset: **[floradb](https://houseplants-botanical-floradb.pages.dev)** · Questions: **[floradb.hardhat456@simplelogin.com](mailto:floradb.hardhat456@simplelogin.com)**

*Toxicity data is informational, not veterinary advice.*
