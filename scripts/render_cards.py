#!/usr/bin/env python3
"""Render the README cards (assets/demo.svg, assets/bench-card.svg) from a measured results file.

Every number on both cards comes from the JSON written by scripts/real_benchmark.py. Nothing is typed by hand.
Usage: python3 scripts/render_cards.py docs/real-benchmark-YYYY-MM-DD.json
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
DUR = 10  # seconds per loop

def n(x) -> str: return f"{x:,.0f}"

def steps(values: list[str], start: float, end: float, attrs: str, hold: float = 0.99) -> str:
    """Stacked texts shown one after another between start and end (fractions of the loop); the last one stays."""
    out, span = [], (end - start) / len(values)
    for i, v in enumerate(values):
        a = start + i * span
        b = hold if i == len(values) - 1 else a + span
        keys = f"0;{a:.4f};{b:.4f};1" if a > 0 else f"0;{b:.4f};1"
        vals = "0;1;0;0" if a > 0 else "1;0;0"
        out.append(f'<text {attrs} opacity="0">{v}<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
                   f'calcMode="discrete" keyTimes="{keys}" values="{vals}"/></text>')
    return "\n".join(out)

def demo(r: dict) -> str:
    videos, hours, secs, ratio = r["videos_collected"], r["watch_hours_once_each"], r["skill_total_seconds"], r["watch_time_over_skill_time"]
    days, chans, date = hours / 24, r["channels_with_videos"], r["measured_at"][:10]
    count = steps([n(videos * i / 10) for i in range(1, 11)], 0.02, 0.27,
                  f'x="816" y="213" text-anchor="middle" font-size="46" font-weight="800" fill="#75e7d8"')
    day_marks = [f"day {max(1, round(days * i / 6))} of {days:,.0f}, still watching" for i in range(1, 6)] + [f"{n(hours)} hours = {days:,.0f} days nonstop"]
    watching = steps(day_marks, 0.30, 0.84, 'x="42" y="437" font-size="15" fill="#f7d67e" font-weight="650"')
    to_scale = 640 * secs / (hours * 3600)
    anim = f'dur="{DUR}s" repeatCount="indefinite"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540" role="img" aria-labelledby="title description">
<title id="title">SignalForge read {n(videos)} real videos in {n(secs)} seconds; watching them once each takes {n(hours)} hours</title>
<desc id="description">A {DUR}-second animation of a run measured on {date}. SignalForge reads the public metadata of {n(videos)} real videos from {chans} public channels while a counter runs up. Two bars compare the measured time: {n(secs)} seconds for SignalForge to collect and score them all, against {n(hours)} hours ({days:,.0f} days nonstop) for one person to watch each video once. The ratio is {n(ratio)} times. SignalForge reads metadata; it does not watch videos.</desc>
<defs>
  <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#100c26"/><stop offset="1" stop-color="#18143b"/></linearGradient>
  <linearGradient id="fast" x1="0" x2="1"><stop stop-color="#3ddbb2"/><stop offset="1" stop-color="#80f7e3"/></linearGradient>
  <linearGradient id="slow" x1="0" x2="1"><stop stop-color="#b9792a"/><stop offset="1" stop-color="#ffdf84"/></linearGradient>
  <pattern id="dim" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="12" height="12" rx="2.5" fill="#2a2251"/></pattern>
  <pattern id="lit" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="12" height="12" rx="2.5" fill="#6f58d6"/><rect x="2.5" y="3" width="7" height="1.6" fill="#c9bbff"/><rect x="2.5" y="6.4" width="5" height="1.6" fill="#8ff0e2"/></pattern>
  <clipPath id="scan"><rect x="42" y="150" height="96" width="0"><animate attributeName="width" {anim} keyTimes="0;0.02;0.27;0.99;1" values="0;0;640;640;0"/></rect></clipPath>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<rect width="960" height="540" rx="24" fill="url(#bg)"/>
<g font-family="{FONT}">
 <g transform="translate(35 28)">
  <path d="M21 0 4 23h13L7 46l36-31H27L34 0Z" fill="#ae84ff"/>
  <text x="52" y="31" font-size="31" font-weight="800" fill="#fff">Signal<tspan fill="#b68cff">Forge</tspan></text>
  <text x="54" y="54" font-size="14" fill="#b8b0d4">Reads the whole niche while you would still be on video one.</text>
 </g>
 <rect x="716" y="33" width="208" height="32" rx="16" fill="#123d3b" stroke="#2f8f86"/>
 <text x="820" y="54" font-size="12" font-weight="700" fill="#8ff0e2" text-anchor="middle" letter-spacing="1">MEASURED RUN · {date}</text>
 <path d="M34 100H925" stroke="#42335c"/>

 <text x="42" y="134" fill="#aa9dca" font-size="12" font-weight="700" letter-spacing="1.6">01  REAL VIDEOS READ · {chans} PUBLIC CHANNELS</text>
 <rect x="42" y="150" width="640" height="96" fill="url(#dim)"/>
 <rect x="42" y="150" width="640" height="96" fill="url(#lit)" clip-path="url(#scan)"/>
 <rect x="40" y="146" width="5" height="104" rx="2.5" fill="#9ff8ec" filter="url(#glow)" opacity="0"><animate attributeName="x" {anim} keyTimes="0;0.02;0.27;1" values="40;40;680;680"/><animate attributeName="opacity" {anim} calcMode="discrete" keyTimes="0;0.02;0.27;1" values="0;1;0;0"/></rect>
 <rect x="706" y="146" width="220" height="104" rx="14" fill="#1a1536" stroke="#46365f"/>
 <text x="816" y="170" text-anchor="middle" fill="#b2a6d2" font-size="13">videos read and scored</text>
 <text x="816" y="213" text-anchor="middle" font-size="46" font-weight="800" fill="#4a4270">0<animate attributeName="opacity" {anim} calcMode="discrete" keyTimes="0;0.045;1" values="1;0;0"/></text>
 {count}
 <text x="816" y="238" text-anchor="middle" fill="#8d80ab" font-size="12">titles · views · durations · dates</text>

 <text x="42" y="286" fill="#aa9dca" font-size="12" font-weight="700" letter-spacing="1.6">02  TIME TO GET THROUGH THE SAME {n(videos)} VIDEOS</text>
 <text x="42" y="316" fill="#fff" font-size="16" font-weight="700">SignalForge <tspan fill="#b8b0d4" font-weight="400">collects and scores every one</tspan></text>
 <rect x="42" y="326" width="640" height="24" rx="7" fill="#221b45"/>
 <g opacity="0"><rect x="42" y="326" width="7" height="24" rx="3" fill="url(#fast)"/><text x="60" y="344" fill="#8ff0e2" font-size="16" font-weight="800">✓ done in {n(secs)} seconds</text><animate attributeName="opacity" {anim} calcMode="discrete" keyTimes="0;0.27;0.99;1" values="0;1;1;0"/></g>
 <text x="42" y="386" fill="#fff" font-size="16" font-weight="700">One person <tspan fill="#b8b0d4" font-weight="400">watches each video once</tspan></text>
 <rect x="42" y="396" width="640" height="24" rx="7" fill="#221b45"/>
 <rect x="42" y="396" width="0" height="24" rx="7" fill="url(#slow)"><animate attributeName="width" {anim} keyTimes="0;0.30;0.84;0.99;1" values="0;0;640;640;0"/></rect>
 {watching}
 <text x="42" y="462" fill="#8d80ab" font-size="12">To scale, SignalForge's bar is {to_scale:.3f} of a pixel wide. It is drawn at 7 px so you can see it.</text>

 <rect x="706" y="270" width="220" height="196" rx="14" fill="#1a1536" stroke="#46365f"/>
 <text x="816" y="300" text-anchor="middle" fill="#b2a6d2" font-size="13">watch time ÷ SignalForge time</text>
 <text x="816" y="380" text-anchor="middle" fill="#4a4270" font-size="60" font-weight="800">×?<animate attributeName="opacity" {anim} calcMode="discrete" keyTimes="0;0.84;0.99;1" values="1;0;0;1"/></text>
 <g opacity="0"><circle cx="816" cy="360" r="62" fill="#3ddbb2" opacity=".22" filter="url(#glow)"/><text x="816" y="380" text-anchor="middle" fill="#75e7d8" font-size="{56 if ratio < 10000 else 46 if ratio < 100000 else 40}" font-weight="800">×{n(ratio)}</text><text x="816" y="418" text-anchor="middle" fill="#f0eaff" font-size="14" font-weight="650">faster than watching</text><text x="816" y="442" text-anchor="middle" fill="#8d80ab" font-size="12">{n(hours)} h against {n(secs)} s</text><animate attributeName="opacity" {anim} calcMode="discrete" keyTimes="0;0.84;0.99;1" values="0;1;1;0"/></g>

 <text x="42" y="505" fill="#8d80ab" font-size="12">Real public metadata, measured {date} on one desktop · SignalForge reads metadata, it does not watch videos · it finds what to watch first</text>
</g>
</svg>
'''

def bench(r: dict) -> str:
    videos, hours, secs, ratio = r["videos_collected"], r["watch_hours_once_each"], r["skill_total_seconds"], r["watch_time_over_skill_time"]
    env, date = r["environment"], r["measured_at"][:10]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="title desc">
<title id="title">SignalForge measured on real videos: {n(videos)} videos, {n(hours)} hours of watch time, read and scored in {n(secs)} seconds</title>
<desc id="desc">Measured on {date}: SignalForge collected and scored the public metadata of {n(videos)} real videos from {r["channels_with_videos"]} public channels in {n(secs)} seconds. Watching each video once takes {n(hours)} hours, {n(ratio)} times longer. Scoring alone took {r["analyze_median_seconds"]} seconds (median of {r["analyze_repeats"]} runs). SignalForge reads metadata; it does not watch videos.</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0b2a1f"/><stop offset=".55" stop-color="#0f3a2a"/><stop offset="1" stop-color="#0c2a38"/></linearGradient>
<linearGradient id="teal" x1="0" y1="0" x2="1"><stop stop-color="#3ddbb2"/><stop offset="1" stop-color="#80f7e3"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1"><stop stop-color="#efb74e"/><stop offset="1" stop-color="#ffdf84"/></linearGradient>
</defs>
<rect width="960" height="330" rx="22" fill="url(#bg)"/>
<rect x="1" y="1" width="958" height="328" rx="21" stroke="#2f8f6a" stroke-width="2" fill="none"/>
<g font-family="{FONT}">
<text x="33" y="37" font-size="15" font-weight="750" letter-spacing="2" fill="#9be8c8">MEASURED ON REAL VIDEOS · {date}</text>
<text x="33" y="73" font-size="22" font-weight="700" fill="#fff">×{n(ratio)} faster than watching them. Then it tells you which to watch.</text>
<rect x="32" y="95" width="279" height="131" rx="13" fill="#123d2e" stroke="#2f8f6a"/>
<text x="51" y="125" fill="#bfe6d6" font-size="15">Real videos read and scored</text>
<text x="50" y="190" fill="url(#teal)" font-size="61" font-weight="830">{n(videos)}</text>
<rect x="326" y="95" width="279" height="131" rx="13" fill="#2c2a16" stroke="#8f7a2f"/>
<text x="345" y="125" fill="#e6dcb7" font-size="15">Time to watch each one once</text>
<text x="345" y="190" fill="url(#gold)" font-size="{60 if hours < 1000 else 52}" font-weight="820">{n(hours)}<tspan font-size="26"> hours</tspan></text>
<rect x="620" y="95" width="307" height="131" rx="13" fill="#18313c" stroke="#4b9a96"/>
<text x="638" y="125" fill="#b3d1d3" font-size="15">SignalForge, collect + score</text>
<text x="638" y="190" fill="#e9fff9" font-size="60" font-weight="820">{n(secs)}<tspan font-size="28"> seconds</tspan></text>
<path d="M33 247H927" stroke="#2f6b55"/>
<circle cx="44" cy="272" r="7" fill="#58e5c4"/>
<text x="61" y="278" fill="#f1eafa" font-size="17" font-weight="650">{r["channels_with_videos"]} public channels</text>
<circle cx="275" cy="272" r="7" fill="#bd99ff"/>
<text x="293" y="278" fill="#d0e6dc" font-size="16">Scoring alone: {r["analyze_median_seconds"]:.2f} s, median of {r["analyze_repeats"]} runs</text>
<circle cx="637" cy="272" r="7" fill="#f3cb74"/>
<text x="654" y="278" fill="#e7f4ec" font-size="16">Python {env["python"]} · {env["os"]} {env["architecture"]}</text>
<text x="33" y="311" fill="#a5c9b9" font-size="13">Real public metadata: titles, views, durations, dates · SignalForge reads metadata, it does not watch or download videos</text>
</g></svg>
'''

def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr); return 2
    r = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    if r.get("benchmark_type") != "real-public-metadata":
        print("render_cards: the results file is not a real-public-metadata run", file=sys.stderr); return 2
    (ROOT / "assets/demo.svg").write_text(demo(r), encoding="utf-8")
    (ROOT / "assets/bench-card.svg").write_text(bench(r), encoding="utf-8")
    print("Wrote assets/demo.svg and assets/bench-card.svg")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
