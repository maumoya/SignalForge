# Changelog

## Unreleased
- Skill rewritten around a nine-step niche study: search-led sampling, channel filters, same-creator multipliers, pre-registered title and hook rules, a fixed report template and a list of mistakes to stop.
- New `python -m signalforge.features`: tests dated, pre-registered regex rules inside each creator, with clustered 95% intervals, Benjamini-Hochberg q-values and plain verdicts.
- New `python -m signalforge.ingest`: converts yt-dlp JSON lines into the input format (local file only, no network).
- Engine options `--min-neighbors` and `--drop-newest`; reports now include the parameters used and the share of videos over 3x and 10x. Defaults are unchanged.
- Optional `hook` and `duration_seconds` input fields.
- Synthetic study sample with planted effects, 18 new unit tests (43 total), three new eval scenarios and a 20-query trigger set with near misses.
- Not done: no LLM run of the eval scenarios or trigger set, and the yt-dlp commands are starting points that have not been checked against a live collection run.

## 0.1.0 — 2026-11-08 (pre-release foundation)
- Opt-in public GitHub repository discovery, independent research-attention scoring, and approval-gated candidate export.
- Creator-relative median performance and explainable topic signal scoring.
- Offline and read-only source processing with safe URL validation and no automatic adoption.
- Public CI tests, lint, CodeQL, Scorecard, Dependabot and a prepared signed-tag release workflow.
- Agent skill and plugin manifests, three eval scenarios, privacy and security documentation.
- Premium marketing header featuring Mauricio Moya, a synthetic animated pipeline demo, measured CI result card.
- Integrated `your-authorship-skill` and `skill-forger-e2e` as CI audits.
- No signed public release, Best Practices certification, live install test or LLM skill ablation has been claimed.

Next: authorized video/social collectors, longitudinal trends, external evidence verification, VISION adapter and reproducible real-world benchmarks.
