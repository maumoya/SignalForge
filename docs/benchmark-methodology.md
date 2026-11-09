# Synthetic metadata throughput — reproducible method

Run `python scripts/benchmark.py --count 3000 --clip-seconds 60 --repeats 7` from repository root.

The benchmark creates 3,000 synthetic metadata records belonging to 100 synthetic creators with 30 uploads per creator. It includes creator, public-form URL, title, topics, upload date and view count. The first invocation warms up the Python process. Seven measured iterations invoke the existing `analyze` pipeline (input validation, URL checks, hash deduplication, per-creator median baselines and topic ranking); the median elapsed wall-clock is reported using Python's `time.perf_counter`.

For arithmetic context only: 3,000 × 60-second hypothetical clips = **50 hours of sequential playback**. However, **SignalForge does not actually watch, download, transcribe, listen to, understand or fact-check those 50 hours.** It processes existing *metadata*, and therefore this is not a human-equivalent review speed or a legitimate measured productivity percentage. The theoretical one-hour throughput assumes linear scaling from a very short local CPU run, which has not been sustained for an hour.

Do not market this as '50 hours of video watched in N seconds', '3000% more productive', '99% time saved' or '30× faster analysis' without measuring a comparable human task.

To measure real business productivity, run a separate controlled human-vs-assisted study using the **same** decision task (e.g., triage 100 video *metadata records* for anomalies), time both groups, score accuracy/recall against a blind independent reference, and report speedup as `human_minutes / automated_minutes` and time saved as `(human_minutes - automated_minutes)/human_minutes × 100`, including sample size and error bars. Do not extrapolate visual watch time to metadata triage.

The CI benchmark writes `benchmark-results.json` to a downloadable GitHub Actions artifact. Only use observed numbers with a link to the exact Actions run, Python version and date.
