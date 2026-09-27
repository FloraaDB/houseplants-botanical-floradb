# Changelog

All notable changes to the FloraDB dataset snapshots.

> Counts are stated as **minimums** (e.g. `20,000+`). The dataset is refreshed
> on a recurring schedule, so the live figures only grow — the numbers below
> stay accurate between snapshots.

## Site update — 2026-09-28

- **Directory pages render sooner**: the botanical family and plant directories (`/families/`, `/plants/` and their Spanish, German, French and Portuguese copies) loaded the Google Fonts stylesheet twice: once without blocking, and once as a render-blocking copy of the no-JavaScript fallback, which had lost its `<noscript>` wrapper. The fallback is wrapped again, so these pages no longer wait for the font file before they render. Nothing visible changes (2026-09-28).

## Site update — 2026-09-27

- **Edition string**: the pricing card, README badge and data dictionary named Snapshot 2026.07; buyers have had the 2026.09 edition since the 2026-09-03 refresh. The dictionary's update frequency now says monthly (ASPCA toxicity re-crawled quarterly).
- **Section links**: links to a part of a page (`/#pricing`, `/#faq`, `/es/#explorer`, …) now land with the heading clear of the sticky site header, including on phones where the header wraps, and a visitor arriving from another page is put back on the section once the web fonts have loaded and moved the page (a small shared script after the header of the home page, its four language copies and `/stats/`). The "Embed this chart" snippets on `/stats/` now link to the chart itself (`#fig-<chart>`); three of them (pet toxicity, ASPCA families, humidity) pointed at an anchor that did not exist. Figures, charts and visible text are unchanged (2026-09-27).
- **Translated Dataset markup**: on the Spanish, German, French and Portuguese pages the Dataset structured data now names its English original in `sameAs` (next to any existing `sameAs` links), so dataset search can tie the language copies to one canonical entry. English pages and all visible text are unchanged (2026-09-27).

## Site update — 2026-09-20

- **Sale attribution**: every Stripe buy link carries `?client_reference_id=<brand>_<lang>_<surface>` (`home` / `landing`); the i18n build swaps the language token per locale and the delivery worker prints the id in the order email. Stripe does not store UTM parameters, so this is the only per-page attribution that reaches the order record (2026-09-20).

## 2026.07 — 2026-07-06

- Initial public snapshot.
- **270** curated houseplants with quantitative care metrics (Lux light thresholds, watering-day intervals, temperature and humidity ranges) across **54** botanical families.
- **891** ASPCA pet-toxicity records (dog / cat / horse) with clinical ingestion signs; **125** care plants species-verified and **45** conservatively genus-inferred.
- **20,000+** species GBIF taxonomic index; **702** species enriched with vernacular names, native range, and CC-licensed image references.
- Every record GBIF-verified with a `gbif_source_url`; per-record quality flags (`care_confidence`, `toxicity_status`, `image_commercial_safe`).
- Care metrics are category-normalized; toxicity is ASPCA-sourced or explicitly `unknown` — never guessed safe.

Full dataset & updates: [floradb](https://floradb.dataengineered.io)
