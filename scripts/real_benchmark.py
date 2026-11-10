#!/usr/bin/env python3
"""Measured run on real public video metadata.

Collects the public video list of each channel in a handle file with yt-dlp (metadata only, rate-limited,
read-only, no download), converts it, scores it and tests the pre-registered title rules. Times every stage.
The raw records stay in --raw-dir (outside the repository by default); only totals are written to --out.

"Watch time" is the sum of the real durations of the collected videos: the time one person needs to watch each
video once. SignalForge reads the metadata; it does not watch, download or transcribe any video.
"""
from __future__ import annotations
import argparse, json, platform, re, shutil, statistics, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from signalforge.core import analyze
from signalforge.features import run_hypotheses
from signalforge.ingest import convert

HANDLE = re.compile(r"^@[A-Za-z0-9._-]{1,60}$")

def collect(handle: str, limit: int, raw_dir: Path, sleep: float) -> tuple[list[dict], float]:
    cmd = ["yt-dlp", "--flat-playlist", "-j", "--playlist-end", str(limit), "--sleep-requests", str(sleep),
           "--extractor-args", "youtubetab:approximate_date", "--no-warnings",
           f"https://www.youtube.com/{handle}/videos"]
    start = time.perf_counter()
    done = subprocess.run(cmd, capture_output=True, text=True, timeout=900, check=False)
    elapsed = time.perf_counter() - start
    (raw_dir / f"{handle[1:]}.jsonl").write_text(done.stdout, encoding="utf-8")
    items, _ = convert(done.stdout.splitlines(), topic="")
    return items, elapsed

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channels", type=Path, required=True)
    ap.add_argument("--hypotheses", type=Path, required=True)
    ap.add_argument("--per-channel", type=int, default=300)
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between yt-dlp requests")
    ap.add_argument("--repeats", type=int, default=7)
    ap.add_argument("--raw-dir", type=Path, default=None, help="where raw records go (default: a new temp folder)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if not shutil.which("yt-dlp"):
        print("real_benchmark: yt-dlp is not installed", file=sys.stderr); return 2
    if not 10 <= args.per_channel <= 1000 or args.sleep < 0.5 or not 3 <= args.repeats <= 30:
        print("real_benchmark: --per-channel 10..1000, --sleep >= 0.5, --repeats 3..30", file=sys.stderr); return 2
    handles = [l.strip() for l in args.channels.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    bad = [h for h in handles if not HANDLE.match(h)]
    if bad or not handles:
        print(f"real_benchmark: bad or missing handles: {bad}", file=sys.stderr); return 2
    raw_dir = args.raw_dir or Path(tempfile.mkdtemp(prefix="signalforge-real-"))
    raw_dir.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=False).stdout.strip()

    items, per_channel, collect_seconds = [], [], 0.0
    for handle in handles:
        rows, elapsed = collect(handle, args.per_channel, raw_dir, args.sleep)
        collect_seconds += elapsed
        per_channel.append({"channel": handle, "videos": len(rows), "collect_seconds": round(elapsed, 2)})
        items.extend(rows)
        print(f"{handle}: {len(rows)} videos in {elapsed:.1f}s", file=sys.stderr)
    if len(items) < 100:
        print("real_benchmark: fewer than 100 videos collected; nothing to report", file=sys.stderr); return 1

    report = analyze(items)  # warm-up, not timed
    timings = []
    for _ in range(args.repeats):
        t = time.perf_counter(); report = analyze(items); timings.append(time.perf_counter() - t)
    t = time.perf_counter()
    rules = run_hypotheses(items, json.loads(args.hypotheses.read_text(encoding="utf-8")))
    rules_seconds = time.perf_counter() - t

    scored = report["items"]
    durations = [x["duration_seconds"] for x in items if isinstance(x.get("duration_seconds"), (int, float))]
    watch_seconds = float(sum(durations))
    analyze_seconds = statistics.median(timings)
    skill_seconds = collect_seconds + analyze_seconds + rules_seconds
    with_baseline = [x for x in scored if x.get("multiplier") is not None]
    result = {
        "schema_version": "signalforge-real-benchmark/1.0",
        "benchmark_type": "real-public-metadata",
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "channels_requested": len(handles),
        "channels_with_videos": sum(1 for c in per_channel if c["videos"]),
        "videos_collected": len(items),
        "videos_scored": len(scored),
        "videos_with_creator_baseline": len(with_baseline),
        "videos_over_3x_own_channel_median": sum(1 for x in with_baseline if x["multiplier"] >= 3),
        "videos_over_10x_own_channel_median": sum(1 for x in with_baseline if x["multiplier"] >= 10),
        "videos_with_duration": len(durations),
        "median_video_seconds": statistics.median(durations) if durations else None,
        "watch_hours_once_each": round(watch_seconds / 3600, 1),
        "collect_seconds": round(collect_seconds, 1),
        "analyze_median_seconds": round(analyze_seconds, 4),
        "rules_seconds": round(rules_seconds, 4),
        "skill_total_seconds": round(skill_seconds, 1),
        "watch_time_over_skill_time": round(watch_seconds / skill_seconds) if skill_seconds else None,
        "analyze_repeats": args.repeats,
        "per_channel": per_channel,
        "rules": rules,
        "environment": {"python": platform.python_version(), "os": platform.system(), "architecture": platform.machine(),
                        "yt_dlp": version, "sleep_between_requests": args.sleep, "per_channel_limit": args.per_channel},
        "what_this_is": [
            "Real public metadata: titles, view counts, durations and approximate dates of each channel's newest videos",
            "Watch time is the sum of the real video durations: one person watching each video once",
            "Skill time is collection plus scoring plus rule tests, measured on this machine in this run",
            "SignalForge reads metadata only. It does not watch, download or transcribe any video",
            "View counts are rounded and dates approximate in this collection mode; counts change every day, so a rerun gives close, not identical, numbers",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: {len(items)} videos, {result['watch_hours_once_each']} watch hours, "
          f"{result['skill_total_seconds']} s, x{result['watch_time_over_skill_time']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
