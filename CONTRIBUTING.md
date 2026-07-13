# Contributing to FloraDB

Thanks for your interest! This repository is the **public showcase** for the
FloraDB houseplant care dataset — it holds a free sample, documentation, and a
starter notebook. The data pipeline itself is not open source, so contributions
here focus on **data quality, docs, and examples**.

## Ways to help

### 🐛 Report a data issue
Spotted a wrong care value, family, or toxicity flag in the sample? Open an issue
with:
- the `plant_id` and `scientific_name`,
- what's wrong and what it should be,
- ideally the `gbif_source_url` or an ASPCA reference so we can re-verify.

Toxicity errors are the highest priority — if a plant is flagged safe that
shouldn't be (or vice versa), please flag it immediately.

### ✏️ Improve docs or examples
Typos, clearer explanations, or a better `examples/load_sample.py` / notebook are
welcome via pull request.

### 💡 Request a field or plant
Want a column the dataset doesn't have yet, or a specific set of plants? Open an
issue describing the use case — it helps prioritize snapshots and informs custom
builds.

## Correction or removal requests

To request a plant record be corrected, email **floradb.hardhat456@simplelogin.com** (or open an
issue).

## Pull request guidelines

- Keep PRs focused and describe the *why*.
- Docs/examples only — please don't add scraping/pipeline code here.
- Data changes to the sample should preserve the schema in
  [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## Licensing of contributions

By contributing, you agree that your contributions to the sample and docs are
licensed under **CC-BY-NC-4.0**, the same license as this repository (see
[`LICENSE`](LICENSE)).

Questions? **floradb.hardhat456@simplelogin.com** · full dataset: [floradb](https://houseplants-botanical-floradb.pages.dev)

*Toxicity data is informational, not veterinary advice.*
