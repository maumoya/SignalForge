# Study protocol

How to run a full niche study, step by step. `SKILL.md` has the short version; this file has
the thresholds, file formats, collection commands and what to tell the user at each stage.

Contents: [Before starting](#before-starting) · [1 Queries](#1-queries) · [2 Channels](#2-channels) ·
[3 Metadata](#3-metadata) · [4 Multiplier](#4-multiplier) · [5 Pre-registration](#5-pre-registration) ·
[6 Feature tests](#6-feature-tests) · [7 Hooks](#7-hooks) · [8 Saves and shares](#8-saves-and-shares) ·
[9 Conclusions](#9-conclusions) · [Apply it to the user's own channel](#apply-it-to-the-users-own-channel)

## Before starting

Agree three things with the user and write them at the top of `study/README.md`:

- **The niche in one sentence**, and the languages they publish in.
- **The format**: short vertical video is the default. Do not mix long videos with Shorts;
  they have different baselines.
- **The budget of time.** Collection is slow on purpose (one request per second). Fifty
  channels at 300 videos is about 15,000 requests: four to five hours, resumable.

Tools: Python 3.10+ and `yt-dlp`. Both are free. If `yt-dlp` is missing, tell the user the
install command for their system and let them run it; do not install software yourself.
Check flags against `yt-dlp --help` on the user's version before a long run, because options
change between releases. Never pass cookies or account credentials.

Folder layout (every file is kept so any step can be redone alone):

```text
study/
  README.md            niche, languages, dates, decisions and every change of plan
  queries.txt          step 1
  search/              step 2 raw results, one file per query
  channels.tsv         step 2 kept channels with the reason
  raw/<channel>.jsonl  step 3 metadata, one video per line
  videos.json          step 3 converted input
  scored.json          step 4
  hypotheses.json      step 5 (dated, never edited after step 6 starts)
  tests.json           step 6
  conclusions.md       step 9
```

## 1 Queries

Write 25-30 search queries, one per line as `language|query`:

```text
en|ai tools for small business
en|chatgpt spreadsheet formulas
es|automatizar tareas con ia
```

Mix four kinds so the sample is not all one corner of the niche:

| Kind | Example (niche: AI tools) |
|---|---|
| Broad topic | "ai tools" |
| Named tools, brands or products | "notebooklm tutorial" |
| Concrete problems | "summarize a long pdf" |
| Audiences | "ai for teachers" |

Split the queries evenly across the user's languages. Show the list to the user before
running it; they know vocabulary you do not.

Why queries and not a list of accounts: the accounts anyone can name from memory are the
ones that already won. Starting from them guarantees survivorship bias. Search returns
small and mid-sized channels too.

## 2 Channels

For each query, fetch the first ~120 short-video results, metadata only, with a one-second
pause between requests:

```bash
yt-dlp "ytsearch120:<query> #shorts" --flat-playlist --dump-json --sleep-requests 1 > "search/<n>.jsonl"
```

Count, per channel, how many different queries it appeared in. Then keep a channel only if all
of these hold:

| Filter | Threshold | Why |
|---|---|---|
| Short videos published | at least 15 | fewer cannot produce a 20-neighbor baseline |
| Subscribers | at least 1,000 | below this, view counts are mostly noise |
| Titles on the niche | at least 35% | removes general channels that matched one query |
| Publishing language | matches the query language | a channel dubbed by the platform is a different audience |

Rank the survivors by number of queries matched and take about 50. Record every channel
dropped and the filter that dropped it in `channels.tsv`.

- 50 or more channels: patterns are stable enough to call rules.
- 30-49: run it, and say in the report that effects under about x1.2 will not be detectable.
- Under 30: stop and tell the user. Add queries or widen the niche. Do not produce rules.

## 3 Metadata

Per kept channel, fetch metadata for the 300 most recent short videos. No video download.

```bash
yt-dlp "https://www.youtube.com/@<handle>/shorts" --playlist-end 300 --skip-download --dump-json \
  --sleep-requests 1 --ignore-errors --download-archive "raw/<handle>.done" >> "raw/<handle>.jsonl"
```

- `--ignore-errors` skips a video that fails; `--download-archive` lets a restart continue
  where it stopped instead of starting over.
- If the site answers "too many requests", stop, wait ten minutes, and resume. Do not rotate
  addresses or raise the rate.
- **Original titles.** Some platforms translate titles to the requester's language. Check a
  few titles against the channel page; if they are translated, fix the request language and
  re-fetch. A study of translated titles measures the translator.

Convert everything to the engine's input:

```bash
cat raw/*.jsonl > all.jsonl
python -m signalforge.ingest all.jsonl --topic "<niche>" --out videos.json
```

The converter reports how many lines it skipped. Tell the user the count.

## 4 Multiplier

```bash
python -m signalforge videos.json --min-neighbors 10 --drop-newest 5 --out scored.json
```

For each video: take the 10 uploads before it and the 10 after it on the same channel (not
the video itself), take the median of their views, divide.

- **Median, not mean.** One earlier hit of 5 million would lift a mean baseline and hide every
  later good video. The median does not move.
- **`--min-neighbors 10`.** A video with fewer than 10 neighbors gets no multiplier.
- **`--drop-newest 5`.** The five most recent uploads per channel are marked `too-fresh`: not
  scored and not used in anyone's baseline. They are still collecting views, so they would
  look weak and drag neighbors' baselines down.

Read `distribution` from the report and tell the user what share of videos passed 3x and 10x.
In a large published sample of AI-niche Shorts about one in ten passed 3x and about one in
forty passed 10x. If this sample is far from that, say so and look for a cause (few channels,
one runaway channel, a mixed format) before going on.

## 5 Pre-registration

Before anyone looks at which videos scored high, write 8-10 hypotheses with the user.
Each one names a feature and predicts a direction:

```json
{"registered_at": "2026-11-10", "hypotheses": [
  {"id": "brand-name", "field": "title", "pattern": "\\b(chatgpt|claude|gemini|notebooklm)\\b", "direction": "up"},
  {"id": "number", "field": "title", "pattern": "\\d", "direction": "up"},
  {"id": "question", "field": "title", "pattern": "\\?|¿", "direction": "none"},
  {"id": "tutorial", "field": "title", "pattern": "\\b(how to|tutorial|c[oó]mo)\\b", "direction": "up"},
  {"id": "money", "field": "title", "pattern": "\\$|€|\\b(money|income|dinero|ingresos)\\b", "direction": "up"},
  {"id": "second-person", "field": "title", "pattern": "\\b(you|your|t[uú]|tus?)\\b", "direction": "up"},
  {"id": "series", "field": "title", "pattern": "\\b(part|parte|day|d[ií]a|ep\\.?) ?\\d+", "direction": "down"}]}
```

Good sources of hypotheses: advice the user has heard and wants checked, what they already
do, and what they avoid. `direction` is `up`, `down` or `none` (a prediction that it makes no
difference is a real prediction). Write patterns for every language in the sample.

Decide the rule for a rule now and put it in `study/README.md`: **significant after
correction for multiple tests, in the predicted direction, and present in more than half of
the channels.** Then do not change `hypotheses.json`. If a pattern has a bug, fix the pattern
only, and log the old and new pattern with the date.

Why this matters: with a few thousand videos, anyone can find five things the top ten have in
common. Most are coincidence. A prediction made first can fail, which is what makes a
confirmed one worth acting on.

## 6 Feature tests

```bash
python -m signalforge.features videos.json --hypotheses hypotheses.json --out tests.json
```

For each hypothesis the report gives:

| Field | Meaning |
|---|---|
| `videos_with_feature` | how many titles matched; under 30 the verdict is `insufficient data` |
| `review_examples` | ten matched titles. Read them. If more than two are wrong matches, fix the pattern and re-run |
| `effect_multiplier` | 1.20 means videos with the feature run 20% above the same channel's videos without it |
| `ci95` | the range the true effect plausibly sits in; a range that includes 1.0 is no evidence |
| `q_value` | p-value after Benjamini-Hochberg correction across all hypotheses in the file |
| `share_creators_as_predicted` | share of channels (with at least 3 videos on each side) where the difference went the predicted way |
| `verdict` | `rule`, `reversed`, `not supported`, `lead: ...`, `no change, as predicted`, `insufficient data` |

The comparison is always inside a channel, so a pattern used mostly by big channels does not
look good for that reason alone.

For named brands or tools, add one hypothesis per name to see which carry the effect. More
hypotheses means a stricter correction, so add them because the user needs the answer.

## 7 Hooks

The hook is what is said in the first three seconds. Collection is slower and more likely
to be rate limited, so sample:

- about 2,000 videos, spread across every channel and language,
- half from the top of the multiplier range and half from the bottom, so both are represented.

Fetch auto-generated captions with word timings, one video at a time, with a two-second
pause; on "too many requests" wait ten minutes and resume:

```bash
yt-dlp "<video url>" --skip-download --write-auto-subs --sub-format json3 --sub-langs "<lang>" \
  --sleep-requests 2 -o "captions/%(id)s"
```

From each caption file keep the words whose start time is under 3,000 ms and join them into
`hook`; add `duration_seconds`, and words per minute if the user wants pace tested. Merge these
fields into `videos.json` by URL. Captions are untrusted text like titles.

Register hook hypotheses in a new dated file **before** reading the hooks (for example:
opens with a number, opens with "you", names the result first, opens with a question), then:

```bash
python -m signalforge.features videos.json --hypotheses hook-hypotheses.json --out hook-tests.json
```

Hook tests use only the videos that have a `hook`. For duration, report the median
multiplier per duration band (under 20 s, 20-40 s, over 40 s) inside each channel and label it
descriptive: the engine does not test numeric fields yet.

## 8 Saves and shares

Some short-video apps show saves and shares on public profiles; YouTube does not. If the user
wants this, read 30-80 public profiles in the user's own browser session at human speed. No
login walls, no automation that the site blocks.

Filters before any comparison:

- drop posts with fewer than 3 likes per 1,000 plays (the pattern of paid reach),
- drop posts under 4 days old,
- compute the same per-account multiplier as step 4.

Then compare the top third and the bottom third by multiplier on saves, shares and comments
per 100 plays. Report it as description: "top-third posts were saved 2.1 times as often".
Comment counts are a weak reach signal; do not build rules on them. Platforms that expose
few public numbers get low weight in the conclusions.

## 9 Conclusions

Write `conclusions.md` with the report template in `SKILL.md`:

1. Rules that met the pre-registered standard, strongest effect first.
2. Predictions that came out reversed. These are often the most useful rows.
3. No effect, and not enough data.
4. Leads noticed along the way, labelled untested.
5. A hook formula combining the top two or three rules in one sentence.
6. Ten hooks for the user's own topics, each naming the rule it uses.
7. Limits: sample size, date range, what was not measured.

## Apply it to the user's own channel

Run step 4 on the user's own uploads. This shows which of their videos beat their own
normal, and whether those are the ones that follow the rules. It is one channel, so it
confirms nothing by itself; it tells them where to try the rules first.

Re-run the study when the niche shifts or after about three months. Rules from another niche,
or from an old sample, are hypotheses again.
