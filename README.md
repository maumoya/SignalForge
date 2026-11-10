<p align="center">
  <img src="assets/header.svg" alt="SignalForge by Mauricio Moya: Spot the signal. Build what matters. Evidence-backed insights, no blind adoption." width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-7c5cfc" alt="Claude Code skill and plugin">
  <a href="#results-measured-2026-11-10"><img src="https://img.shields.io/badge/6%2C855%20real%20videos-read%20in%20293%20s-2da44e" alt="6,855 real videos read and scored in 293 seconds, measured 2026-11-10"></a>
  <a href="https://github.com/maumoya/SignalForge/actions/workflows/test.yml"><img src="https://github.com/maumoya/SignalForge/actions/workflows/test.yml/badge.svg" alt="GitHub CI tests"></a>
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT license">
  <a href="https://opensource.org/license/mit"><img src="https://img.shields.io/badge/Open%20Source-OSI%20approved-3DA639?logo=opensourceinitiative&amp;logoColor=white" alt="OSI-approved open source license"></a>
  <a href="PRIVACY.md"><img src="https://img.shields.io/badge/privacy-no%20tracking%20%C2%B7%20offline-7c5cfc" alt="No tracking, offline processing"></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/maumoya/SignalForge"><img src="https://api.scorecard.dev/projects/github.com/maumoya/SignalForge/badge" alt="Live OpenSSF Scorecard, not a hardcoded score"></a>
  <img src="https://img.shields.io/badge/release-pre--release-777777" alt="Pre-release; signed public release pending">
</p>

<p align="center">
  <a href="#results-measured-2026-11-10"><img src="assets/demo.gif" width="900" alt="Ten-second animation of a run measured on 2026-11-10. SignalForge reads the public metadata of 6,855 real videos from 23 public channels while a counter runs up. Two bars compare the time: SignalForge finishes in 293 seconds, one person watching each video once needs 3,558 hours, 148 days nonstop. The ratio is 43,712 times."></a>
</p>

<p align="center">
  <a href="#results-measured-2026-11-10"><img src="assets/bench-card.svg" width="760" alt="Measured on real videos, 2026-11-10: 6,855 real videos read and scored, 3,558 hours to watch each one once, 293 seconds for SignalForge to collect and score them, 23 public channels. SignalForge reads metadata; it does not watch or download videos."></a>
</p>

# SignalForge

**Spot the signal. Build what matters.** SignalForge is an open-source agent skill and Python CLI that helps researchers, creators and builders identify **unusually strong content signals**, compare them against each creator's normal performance and turn recurring themes into **read-only research leads**.

**The promise:** find what deserves investigation, with inspectable evidence. Not another black-box “viral score.” Not automatic software installation. Not a claim that popularity proves value.

> **Current scope (v0.2.0):** analyzes user-provided video JSON **offline**, tests your own pre-registered title and hook rules across creators, plus an **opt-in, read-only public GitHub repository search**. Collection is not built in: for YouTube the skill gives rate-limited `yt-dlp` starting commands that you run and approve yourself, and a converter for their output. Instagram and TikTok collection, longitudinal growth measurements, automatic evidence verification and live VISION integration are **not implemented yet**. The animated card and the Results section show a run on real public videos; the 8× walk-through below is a small worked example.

## Install

**Claude Code plugin:**
```text
/plugin marketplace add maumoya/SignalForge
/plugin install signalforge@signalforge
```

**Agents that read SKILL.md files:**
```bash
npx skills add maumoya/SignalForge
```

**Standalone Python (3.10+, no runtime dependencies):**
```bash
python -m signalforge examples/sample.json
python -m signalforge examples/sample.json --out report.json
python -m signalforge examples/sample.json --candidates --out leads.json
```

**Niche study: which title and hook rules hold across creators (offline, known-answer sample included):**
```bash
python -m signalforge examples/study/videos.json --min-neighbors 10 --drop-newest 5
python -m signalforge.features examples/study/videos.json --hypotheses examples/study/hypotheses.json
python -m signalforge.ingest all.jsonl --topic "your niche" --out videos.json   # yt-dlp JSON lines -> input JSON
```
You write the rules down first (`hypotheses.json`, dated), then the engine compares videos with and without each feature **inside the same creator**, and reports an effect size, a 95% interval, a false-discovery-adjusted q-value and a plain verdict: `rule`, `reversed`, `not supported`, `lead` or `insufficient data`. The full nine-step protocol is in [study-protocol.md](skills/signalforge/references/study-protocol.md).

**Opt-in public GitHub discovery (sends only your search phrase to GitHub):**
```bash
python -m signalforge.discovery "local ai coding agents" --limit 10
python -m signalforge.discovery "local ai coding agents" --limit 10 --candidates --out github-leads.json
```
This mode makes one unauthenticated HTTPS request to the fixed public GitHub API. No API key or extra dependency. Public repo stars, forks and recency produce *research attention* signals, never a security or ROI rating. See [public GitHub collector documentation](skills/signalforge/references/github-discovery.md).

The repository is public, but a real Claude Code plugin installation and trigger/ablation benchmark have **not** been recorded yet.

## See the difference

A big creator gets 100,000 views on every post; a small creator typically gets 100. Counting absolute views alone favors the big creator. SignalForge instead calculates:

```text
One creator's normal views:      100  (median of 20 neighboring videos)
Standout video's views:          800
Relative performance:           8.0×
Decision:                       Investigate, don't auto-adopt
```

That 8.0× is a worked example with a known answer, checked by the unit test `test_relative_baseline`. For numbers from real videos see [Results](#results-measured-2026-11-10).

| Stage | SignalForge does | Why it matters |
|---|---|---|
| **01 Discover** | Loads video JSON offline or optionally searches public GitHub repos | Independent, inspectable inputs |
| **02 Validate** | Checks URLs and data; deduplicates; compares same-creator neighbor medians | A small creator's outlier can matter |
| **03 Prioritize** | Ranks repeat topics using creator breadth and relative performance | Repeatability matters more than one viral clip |
| **04 Handoff** | Exports versioned `investigate-only` candidates | Other agents can review findings without auto-installing anything |

### Your input

```json
{
  "items": [
    {
      "url": "https://www.youtube.com/",
      "platform": "youtube",
      "creator": "creator-a",
      "title": "Example short",
      "topic": "ai agents",
      "views": 12000,
      "published_at": "2026-11-01T12:00:00Z"
    }
  ]
}
```

Missing dates, creator identities and view counts are reported as gaps, not guessed. At least five neighboring videos from the same creator and platform are required to compute a relative multiplier (`--min-neighbors` raises this; `--drop-newest N` leaves each creator's newest N uploads unscored because their views are still growing). Optional `hook` and `duration_seconds` fields are kept when present. No HTTP requests are made by the offline **video** engine.

## Results (measured 2026-11-10)

**In plain terms:** SignalForge read and scored **6,855 real videos** from **23 public channels** in **293 seconds**. One person watching each of those videos once would need **3,558 hours**, which is 148 days without a break. That is **×43,712**. SignalForge does not watch the videos: it reads their public titles, view counts, durations and dates, then tells you which few are worth your time.

| Measured on real videos | Value | How |
|---|---:|---|
| Videos read and scored | **6,855** | Newest regular videos, up to 300 per channel, 23 public channels |
| Time to watch each one once | **3,558 hours** | Sum of the real video durations (median video: 11 min 17 s) |
| SignalForge, collect + score + rule tests | **293 seconds** | Wall clock, one desktop, one request per second |
| Scoring alone | **0.16 seconds** | Median of 7 timed runs after a warm-up |
| Watch time ÷ SignalForge time | **×43,712** | 3,558 h × 3,600 ÷ 293 s |
| Videos over 3× their own channel's median | **1,117** (17%) | Same-channel baseline, 6,589 videos had enough neighbors |
| Videos over 10× their own channel's median | **340** (5%) | The shortlist to open first |

**What it found about title rules.** Five common title rules were written down before the data was collected ([hypotheses](benchmarks/hypotheses-real.json)) and tested inside each channel. **None held up**: a number in the title (×0.84, 95% interval 0.65 to 1.08), a question mark (×1.10, 0.87 to 1.39), starting with "how" or "why" (×0.97, 0.84 to 1.10) and "live" or "stream" (×0.60, 0.38 to 0.94, not significant after correction) were not supported, and one rule matched almost every title so it could not be tested. On these 23 channels, the popular title tips are not evidence.

[Results file](docs/real-benchmark-2026-11-10.json) · [Method and limits](docs/benchmark-methodology.md) · [Channel list](benchmarks/channels.txt) · [Measurement script](scripts/real_benchmark.py)

Repeat it yourself (needs `yt-dlp`, about five minutes, downloads no video):

```bash
python3 scripts/real_benchmark.py --channels benchmarks/channels.txt --hypotheses benchmarks/hypotheses-real.json --out my-run.json
```

**Checks behind the code:**

| Check | Observed result | Evidence |
|---|---|---|
| Python unit tests | **48/48 pass** | [GitHub CI](https://github.com/maumoya/SignalForge/actions/workflows/test.yml), [test cases](tests/) |
| Published numbers match the results file | **Enforced in CI** | [test_published_results](tests/test_published_results.py) |
| Known-answer check | A sample with a ×1.5 title effect built in returns **×1.46** (95% interval 1.34 to 1.59) | [sample generator](examples/study/make_sample.py), [test_study](tests/test_study.py) |
| Required runtime dependencies | **0** | [pyproject.toml](pyproject.toml) |
| Read-only handoff | **Enabled**; adoption requires approval | [export schema](skills/signalforge/references/integration.md) |
| OpenSSF | **Live report**, not an arbitrary certification | [Scorecard viewer](https://scorecard.dev/viewer/?uri=github.com/maumoya/SignalForge) |
| LLM skill eval / live install | **Not yet executed** | [Validation status](VALIDATION.md) |

**Limits:** one run, one day, 23 large English-language channels, regular videos only (the Shorts listing carries no duration or date). View counts are rounded by the platform and dates are approximate. The ratio compares reading metadata with watching, not understanding. Associations inside channels are not causes, and the topic score is not a forecast.

## Security and privacy

The video-analysis engine:
- Does **not** connect to YouTube or any network; it reads the supplied local JSON. The separate GitHub collector makes one **explicitly requested** public HTTPS search.
- Does **not** use browser cookies, private messages, tokens, paid APIs or telemetry. GitHub receives search terms only when that optional command is invoked.
- Does **not** execute instructions inside captions, titles, repos, links or documents.
- Does **not** install software, overwrite output files or approve its own findings.
- Exports leads for further human/agent research; adoption requires separate gates.

See [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md) and the [threat model](skills/signalforge/references/security.md). These boundaries must be reviewed again before adding live collectors.

## Evaluations and development

```bash
python -m unittest discover -s tests -v
bash scripts/lint_skill.sh
```

Six [agent-evaluation scenarios](evals/) are included: relative virality, prompt-injection resistance, owner approval, pre-registered rules, fresh uploads and one-video honesty, plus 20 trigger queries. **Their presence is not proof that an LLM has run or passed them.** `skill-forger-e2e` readiness and `your-authorship-skill` are wired into CI to surface release and ownership checks.

See [release gates](README_RELEASE_GATES.md), [validation](VALIDATION.md), [methodology](skills/signalforge/references/methodology.md), and [read-only integration](skills/signalforge/references/integration.md).

## Frequently asked questions

### Can it discover YouTube or Instagram videos by itself?
Not by itself. Supply authorized video metadata as JSON, or collect public YouTube metadata yourself with the rate-limited `yt-dlp` commands in the study protocol and convert it with `python -m signalforge.ingest`. It **can** discover public GitHub repositories through a separate opt-in API call. Video collectors will need separate security and platform-rule review.

### Does it send my data to an AI model or cloud server?
The video-analysis engine is offline and uses no cloud model. The optional GitHub discovery command sends the **public search phrase** to GitHub's API and receives public metadata; it does not send your local video datasets or secrets. If you run SignalForge through a separate AI agent, that agent's own privacy and model configuration still apply.

### Is an 8× multiplier a guaranteed viral trend?
No. It is an observed relative outlier in the sample. Platform view definitions, video age, selection bias and missing history matter.

### Can it install a GitHub library or change VISION automatically?
No. SignalForge produces read-only `investigate-only` leads. Any downstream VISION adapter must preserve Reward Radar's independent risk scoring and owner approval.

### Can I use this as a GitHub Action?

Yes. On GitHub CI you can validate a JSON dataset without downloading or running external code:

```yaml
name: Check public signals
on: [pull_request]
permissions: read-all
jobs:
  signals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
        with:
          persist-credentials: false
      - uses: maumoya/SignalForge@main
        with:
          dataset: examples/sample.json
```

Pin the Action to a verified immutable commit SHA in production. The self-test in CI proves that valid data pass and unsafe-only data fail. GitHub Marketplace listing is a separate publication step.

### Is it security-certified?
No. OpenSSF Scorecard is independently evaluated, but Best Practices and a signed public release have not been completed.

## About the author

**Mauricio Moya** ([@maumoya](https://github.com/maumoya)) combines finance, quantitative analytics, operations and software engineering to build practical systems that turn data into decisions. SignalForge grew from a real need: separate interesting social signals from changes worth investigating and eventually implementing, without weakening the controls of an agent-driven development workflow.

Explore [my portfolio](https://maumoya.github.io/), [Skill Forger E2E](https://github.com/maumoya/skill-forger-e2e), [Your Authorship Skill](https://github.com/maumoya/your-authorship-skill) or [LinkedIn](https://www.linkedin.com/in/mba-mmoyat/).

## License

**MIT**, copyright © 2026 **Mauricio Moya**. See [LICENSE](LICENSE).

The creator-neighbor-median research idea was independently implemented after reviewing a 2026 Spanish-language viral-video methodology guide credited to Pedro. No copyrighted PDF pages, artwork or scripts were republished.
