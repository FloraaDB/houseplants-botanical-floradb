# Changelog

All notable changes to the FloraDB dataset snapshots.

> Counts are stated as **minimums** (e.g. `20,000+`). The dataset is refreshed
> on a recurring schedule, so the live figures only grow — the numbers below
> stay accurate between snapshots.

## 2026.07 — 2026-07-06

- Initial public snapshot.
- **270** curated houseplants with quantitative care metrics (Lux light thresholds, watering-day intervals, temperature and humidity ranges) across **54** botanical families.
- **891** ASPCA pet-toxicity records (dog / cat / horse) with clinical ingestion signs; **125** care plants species-verified and **45** conservatively genus-inferred.
- **20,000+** species GBIF taxonomic index; **702** species enriched with vernacular names, native range, and CC-licensed image references.
- Every record GBIF-verified with a `gbif_source_url`; per-record quality flags (`care_confidence`, `toxicity_status`, `image_commercial_safe`).
- Care metrics are category-normalized; toxicity is ASPCA-sourced or explicitly `unknown` — never guessed safe.

Full dataset & updates: [floradb](https://houseplants-botanical-floradb.pages.dev)
