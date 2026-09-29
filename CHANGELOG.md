# Changelog

All notable changes to the FloraDB dataset snapshots.

> Counts are stated as **minimums** (e.g. `20,000+`). The dataset is refreshed
> on a recurring schedule, so the live figures only grow — the numbers below
> stay accurate between snapshots.

## Site update — 2026-09-29

- **Visit counts**: Cloudflare Web Analytics adds its cookie-free page-view beacon to every page, but the Content-Security-Policy in `_headers` let browsers run scripts from this site only, so they refused the beacon and no visits were counted since Web Analytics was switched on (2026-09-05). The policy now also allows the beacon script (`https://static.cloudflareinsights.com`, `script-src`) and the address it reports to (`https://cloudflareinsights.com`, `connect-src`). No other source is added.

## Site update — 2026-09-28

- **Chart titles on `/stats/`**: every chart's built-in title and description (what a screen reader announces for the chart) used the same two ids, `t` and `d`, repeated once per chart, so the page had duplicate ids and every chart was announced with the first chart's title. The ids now carry the chart's name (`t-families` / `d-families`, and so on) on the page and in the downloadable SVGs under `/stats/charts/`. `scripts/stats_common.py` is the current portfolio copy, which writes them on the next regeneration; the committed page and SVGs were patched to exactly what it writes, without regenerating (no figure, date or `data.json` changes).
- **Repository files off the website**: the translation catalogs (`/locales/`), the build scripts (`/scripts/`), `i18n.config.json`, `README.md`, `vercel.json` and the dotfiles belong to this repository, not to the website, but the site served them as plain files. They now answer the site's normal 404 page (also when requested as `/locales%2Fes.json` or `//locales/es.json`) and stay available here on GitHub. Pages, data files, samples, `llms.txt` and the sitemap are unchanged (2026-09-28).

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
