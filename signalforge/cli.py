"""Offline command line; no HTTP, subprocesses, cookies, or accounts."""
import argparse,json,sys
from pathlib import Path
from .core import analyze,SignalError
from .export import export_candidates

def main(argv=None):
    ap=argparse.ArgumentParser(prog="signalforge",description="Analyze public signal metadata offline")
    ap.add_argument("input",type=Path)
    ap.add_argument("--out",type=Path,help="Write new JSON report (never overwrites)")
    ap.add_argument("--candidates",action="store_true",help="Export read-only proposal records")
    args=ap.parse_args(argv)
    try:
        if not args.input.is_file() or args.input.is_symlink() or args.input.stat().st_size>15*1024*1024:
            raise SignalError("input missing, symlink, or over 15 MiB")
        report=analyze(json.loads(args.input.read_text(encoding="utf-8")))
        result=export_candidates(report) if args.candidates else report
        output=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
        if args.out:
            if args.out.is_symlink(): raise SignalError("refusing symlink output")
            with args.out.open("x",encoding="utf-8") as f:f.write(output)
            print(f"Wrote {args.out}")
        else:print(output,end="")
        return 0
    except (SignalError,OSError,ValueError) as exc:
        print(f"signalforge: {exc}",file=sys.stderr)
        return 2
