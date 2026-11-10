# How the result is measured

The headline numbers come from one run on real public videos, not from made-up records.

## Run it

```bash
python3 scripts/real_benchmark.py --channels benchmarks/channels.txt --hypotheses benchmarks/hypotheses-real.json --per-channel 300 --out docs/real-benchmark-YYYY-MM-DD.json
python3 scripts/render_cards.py docs/real-benchmark-YYYY-MM-DD.json
```

It needs `yt-dlp` and a network connection. It sends one listing request per page per channel, one second apart, and downloads no video.

## What is measured

| Number | How it is obtained |
|---|---|
| Videos read | The newest regular videos (up to 300) of each public channel in `benchmarks/channels.txt`, listed with `yt-dlp --flat-playlist`: URL, title, view count, duration, approximate date. |
| Watch time | The sum of the real durations of those videos: one person watching each video once, with no breaks. |
| SignalForge time | Wall-clock seconds, on the machine named in the results file, for collection + scoring (median of 7 timed runs after a warm-up) + the pre-registered rule tests. |
| Ratio | Watch time divided by SignalForge time. |
| Rule verdicts | `benchmarks/hypotheses-real.json` was written before the data was collected. Each rule is tested inside each channel and corrected for multiple tests. |

## What the ratio means, and what it does not

SignalForge reads metadata. It does not watch, download, transcribe or understand any video. The ratio says how much sooner you have the whole list scored than a person would finish watching it, so you can choose the few videos worth watching. It is not a claim about comprehension.

View counts come from the listing page and are rounded by the platform. Dates are approximate ("3 weeks ago"). Collection time depends on the network and on the one-second pause between requests. A channel that returns no videos is reported with 0 and left out.

Raw records stay on the machine that ran the collection. The repository holds only the aggregate results file.

## Checks that run on every change

- `tests/test_published_results.py` fails if the README or either card shows a number that is not in the results file, or if the ratio is not the arithmetic of the measured times.
- `scripts/benchmark.py` is a speed regression check for CI on generated records. Its numbers are not shown as results.
- `examples/study/` is a known-answer check: the sample has a ×1.5 title effect built in, and the test passes only if the tool recovers it.
