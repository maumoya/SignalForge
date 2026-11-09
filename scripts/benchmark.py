#!/usr/bin/env python3
"""Reproducible synthetic *metadata* benchmark; never downloads or watches video."""
from __future__ import annotations
import argparse, json, os, platform, statistics, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from signalforge.core import analyze

def fixture(count: int = 3000, clip_seconds: int = 60):
    if not isinstance(count,int) or count<60 or count>20000 or count%30:
        raise ValueError("count must be a multiple of 30 between 60 and 20000")
    if clip_seconds<1 or clip_seconds>3600:
        raise ValueError("clip length out of range")
    anchor=datetime(2026,1,1,tzinfo=timezone.utc)
    rows=[]
    for i in range(count):
        creator=i//30
        rows.append({
            "url":f"https://www.youtube.com/shorts/sf-synthetic-{i}",
            "platform":"youtube",
            "creator":f"synthetic-creator-{creator}",
            "title":f"Synthetic video #{i} about topic {i%12}",
            "topic":f"synthetic-topic-{i%12}",
            "views": 1000*(3 if i%30==15 else 1),
            "published_at":(anchor+timedelta(days=i%30)).isoformat(),
            "illustrative_clip_seconds":clip_seconds
        })
    return rows

def benchmark(count:int=3000,clip_seconds:int=60,repeats:int=7):
    if repeats<3 or repeats>30: raise ValueError("repeats out of range")
    rows=fixture(count,clip_seconds)
    durations=[]
    report=analyze(rows) # warm-up, not included in timings
    for _ in range(repeats):
        t=time.perf_counter()
        report=analyze(rows)
        durations.append(time.perf_counter()-t)
    if len(report["items"])!=count:raise AssertionError("fixture accepted count mismatch")
    observed=sum(1 for x in report["items"] if x["multiplier"] is not None)
    if observed!=count:raise AssertionError("baseline coverage mismatch")
    median=statistics.median(durations)
    represented_hours=count*clip_seconds/3600
    return {
      "schema_version":"signalforge-benchmark/1.0",
      "benchmark_type":"synthetic-metadata-processing-only",
      "synthetic_records":count,
      "hypothetical_duration_per_video_seconds":clip_seconds,
      "hypothetical_total_playback_hours":represented_hours,
      "records_with_baseline":observed,
      "topic_groups":len(report["topics"]),
      "repeats":repeats,
      "median_elapsed_seconds":round(median,5),
      "min_elapsed_seconds":round(min(durations),5),
      "max_elapsed_seconds":round(max(durations),5),
      "metadata_records_per_second":round(count/median),
      "theoretical_records_per_hour_at_measured_rate":round(count/median*3600),
      "environment":{"python":platform.python_version(),"os":platform.system(),"architecture":platform.machine()},
      "limitations":[
        "Processes already-collected JSON metadata; does not download, watch, transcribe or understand videos",
        "Hours represent hypothetical playback duration, not hours of information understood or reviewed",
        "One-hour capacity is a linear extrapolation of a short CPU benchmark, not a sustained 1-hour run",
        "Human browsing speed and productivity improvement were not measured; no percentage improvement is claimed",
        "Does not benchmark remote API collection, claim verification or malware scanning"
      ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--count",type=int,default=3000)
    ap.add_argument("--clip-seconds",type=int,default=60)
    ap.add_argument("--repeats",type=int,default=7)
    ap.add_argument("--out",type=Path,default=None)
    args=ap.parse_args()
    result=benchmark(args.count,args.clip_seconds,args.repeats)
    output=json.dumps(result,indent=2)+"\n"
    if args.out:
        with args.out.open("x",encoding="utf-8") as f:f.write(output)
    print(output)
if __name__=="__main__":main()
