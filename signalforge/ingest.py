"""Convert yt-dlp JSON lines (one video per line, metadata only) to SignalForge input.

Reads a local file. Makes no network request and runs nothing from the file.
Lines that are not a video object, or lack a URL, are counted and skipped.
"""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
from .core import SignalError

MAX_BYTES=200*1024*1024

def convert_line(row: object, topic: str="") -> dict | None:
    if not isinstance(row,dict): return None
    url=row.get("webpage_url") or row.get("original_url") or row.get("url")
    if not isinstance(url,str) or not url.startswith("https://"): return None
    stamp=row.get("timestamp") or row.get("release_timestamp"); day=row.get("upload_date")
    published=None
    if isinstance(stamp,(int,float)) and not isinstance(stamp,bool) and 0<stamp<4102444800:
        published=datetime.fromtimestamp(stamp,timezone.utc).isoformat()
    elif isinstance(day,str) and len(day)==8 and day.isdigit():
        published=f"{day[:4]}-{day[4:6]}-{day[6:]}T00:00:00+00:00"
    views=row.get("view_count"); duration=row.get("duration")
    out={"url":url,"platform":str(row.get("extractor_key") or row.get("extractor") or "").lower().split(":")[0],
        "creator":str(row.get("uploader_id") or row.get("channel_id") or row.get("channel") or row.get("uploader")
            or row.get("playlist_uploader_id") or row.get("playlist_channel_id") or ""),
        "title":row.get("title") if isinstance(row.get("title"),str) else "","topic":topic,
        "views":views if isinstance(views,int) and not isinstance(views,bool) else None,"published_at":published}
    if isinstance(duration,(int,float)) and not isinstance(duration,bool) and duration>0: out["duration_seconds"]=duration
    return out

def convert(lines, topic: str="") -> tuple[list[dict],int]:
    items,skipped=[],0
    for line in lines:
        line=line.strip()
        if not line: continue
        try: item=convert_line(json.loads(line),topic)
        except ValueError: item=None
        if item: items.append(item)
        else: skipped+=1
    return items,skipped

def main(argv=None):
    ap=argparse.ArgumentParser(prog="python -m signalforge.ingest",description="yt-dlp JSON lines to SignalForge input JSON")
    ap.add_argument("input",type=Path)
    ap.add_argument("--topic",default="",help="Topic label for every item, e.g. the niche name")
    ap.add_argument("--out",type=Path,required=True,help="Write new JSON file (never overwrites)")
    args=ap.parse_args(argv)
    try:
        if not args.input.is_file() or args.input.is_symlink() or args.input.stat().st_size>MAX_BYTES:
            raise SignalError("input missing, symlink, or over 200 MiB")
        if args.out.is_symlink(): raise SignalError("refusing symlink output")
        with args.input.open(encoding="utf-8",errors="replace") as fh: items,skipped=convert(fh,args.topic[:120])
        with args.out.open("x",encoding="utf-8") as fh: json.dump({"items":items},fh,ensure_ascii=False)
        print(f"Wrote {args.out}: {len(items)} videos, {skipped} lines skipped")
    except (SignalError,OSError,ValueError) as exc:
        print(f"signalforge: {exc}",file=sys.stderr); return 2
    return 0

if __name__=="__main__": raise SystemExit(main())
