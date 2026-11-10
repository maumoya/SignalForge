# Methodology and statistical limits

## Multiplier

For video `i`: `multiplier(i) = views(i) / median(views(neighbors(i)))`.

- Neighbors are up to 10 earlier and 10 later uploads by the same creator on the same
  platform, ordered by timestamp then stable ID. The video itself is excluded.
- A multiplier is given only with at least `--min-neighbors` valid neighbors. The default is 5
  (backward compatible, good for a quick look at one channel). The study protocol uses 10.
- `--drop-newest N` marks each creator's N most recent uploads `too-fresh`. They get no
  multiplier and are not in any baseline. Default 0; the study protocol uses 5.
- Videos missing views, a date or a creator are kept in the output and never scored. A zero
  baseline gets `zero-baseline`, never an invented number.
- No comparison across creators, ever.

`distribution` in the report is the share of scored videos above 3x and above 10x.

## Hypothesis tests (`python -m signalforge.features`)

Input: scored videos and a dated list of hypotheses. Each hypothesis is a case-insensitive
regular expression on `title` or `hook`, with a predicted direction.

- **Model.** `log(multiplier) = creator effect + b * has_feature + error`, estimated by
  demeaning both sides within each creator (creator fixed effects). `effect_multiplier` is
  `exp(b)`: 1.20 means 20% above the same creator's videos without the feature.
- **Uncertainty.** Standard errors are clustered by creator with the usual small-sample
  factor `G/(G-1)`. The 95% range is `exp(b ± 1.96·se)`; the p-value uses the normal
  approximation. With fewer than about 30 creators this is optimistic: say so in the report.
- **Multiple tests.** Benjamini-Hochberg across every testable hypothesis in the file;
  `q_value` under 0.05 counts as significant.
- **Repetition.** `share_creators_as_predicted` is the share of creators, among those with at
  least 3 videos on each side, whose own difference in mean log multiplier went the predicted way.
- **Verdict.** `rule` needs all three: significant, predicted direction, more than half of
  creators. Significant in the other direction is `reversed`. Significant but in half or
  fewer creators is a `lead`. A `none` prediction is `no change, as predicted` when not
  significant. Fewer than 30 videos with the feature is `insufficient data` and is left out of
  the correction.

The engine is standard library only and deterministic: the same files give the same report.

## Topic signal score

A ranking heuristic for the candidate export: creator repetition (40%), median multiplier
(40%), platform breadth (20%). It is not a probability, forecast or estimate of return.

## Limits

- Associations inside creators are not causes. A title pattern may travel with a topic, a
  posting day or an editing style that does the work.
- A single snapshot cannot show growth speed. Platforms count views differently; do not pool
  platforms in one test.
- Regex features mislabel some titles. The `review_examples` exist so a person checks them.
- Search-based sampling is less biased than a hand-picked list, not unbiased.
- Rules describe the sampled niche and dates. Elsewhere they are hypotheses.

## Attribution

The neighbor-median multiplier and the study sequence (search-led sampling, pre-registered
hypotheses, within-channel tests) follow a method described in a Spanish-language guide to
analysing viral videos credited to Pedro (2026). This repository is an independent
implementation in its own words and does not copy or distribute that guide.
