<p align="center"><img src="assets/header.svg" alt="SignalForge — Discover. Validate. Prioritize." width="100%"></p>
<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-7c5cfc" alt="Claude Code skill and plugin">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/runtime%20dependencies-0-2da44e" alt="No runtime dependencies">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license">
  <img src="https://img.shields.io/badge/status-pre--release-777777" alt="Pre-release">
</p>
<p align="center"><img src="assets/demo.svg" width="760" alt="Animated radar: collect public signals, normalize creator-relative performance, rank opportunities"></p>
<p align="center"><img src="assets/bench-card.svg" width="760" alt="Local synthetic test evidence; no external certification"></p>

# SignalForge
**Discover. Validate. Prioritize.** A local-first intelligence skill that extracts explainable patterns from authorized public-content metadata. Instead of blindly ranking views, it compares each video with the same creator's own baseline.

## What works in v0.1.0
- Offline, standard-library Python analysis of owner-supplied JSON; no accounts, telemetry, cookies, API calls, downloads, scheduled tasks or AI provider needed.
- Creator-relative baseline: median of up to 10 earlier and 10 later comparable videos, with at least five valid neighbors.
- Topic ranking across distinct creators and platforms, with explicit confidence and uncertainty.
- Safe URL normalization, deduplication, input-size limits, no-overwrite outputs and separation of hostile text from executable instructions.
- Versioned read-only `--candidates` export intended for downstream review by VISION or other systems.
- Agent skill, Claude Code plugin manifests, regression tests and security documentation.

**Not implemented:** live Instagram/TikTok/YouTube/GitHub collectors, velocity over time, automatic fact-checking, VISION live write-back, signed releases, certified OpenSSF score or paid LLM evaluation.

## Quick start
```bash
python -m signalforge examples/sample.json
python -m signalforge examples/sample.json --out result.json
python -m signalforge examples/sample.json --candidates --out proposals.json
python -m unittest discover -s tests -v
```

Input format:
```json
{"items":[{"url":"https://youtube.com/shorts/example","platform":"youtube","creator":"creator-a","title":"Example short","topic":"ai agents","views":12000,"published_at":"2026-11-01T12:00:00Z"}]}
```
Missing views/date are retained as missing rather than inferred. Rejects external code and unsupported URL schemes.

## Install as an agent skill
Claude Code plugin:
```text
/plugin marketplace add maumoya/SignalForge
/plugin install signalforge@signalforge
```
Compatible skill readers:
```bash
npx skills add maumoya/SignalForge
```
These are documented paths; a live installation and trigger test are still pending.

## Why SignalForge?
A video with 80,000 views may be ordinary for a large creator, while one with 8,000 could outperform a small creator's typical posts by 8×. SignalForge distinguishes raw popularity from *relative performance* and independent repetition. It never equates virality with truth, security or expected ROI.

The median-neighbor concept was independently implemented based on a viral-video research method described in a Spanish guide credited to Pedro (2026). The PDF's prompts, artwork, scripts and branding are not copied or distributed.

## Limitations and evidence
See [validation](VALIDATION.md), [methodology](skills/signalforge/references/methodology.md), [integration](skills/signalforge/references/integration.md) and [security](SECURITY.md). Topic scores are heuristics, not calibrated probabilities or verified economic impacts. Synthetic tests do not constitute real-world benchmarks or certification. OpenSSF and Best Practices badges will be added **only after verified results exist**.

## About the author
Created by **Mauricio Alonso Moya Tapia** ([@maumoya](https://github.com/maumoya)) combining finance, quantitative analysis and agent engineering. See [Skill Forger E2E](https://github.com/maumoya/skill-forger-e2e) and [portfolio](https://maumoya.github.io/).

MIT licensed. Copyright 2026 Mauricio Moya.
