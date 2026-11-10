"""Test pre-registered title or hook hypotheses against same-creator multipliers.

Each hypothesis is a regular expression that marks a video as having a feature.
The effect is the within-creator difference in log(multiplier): creator fixed
effects, creator-clustered standard errors, Benjamini-Hochberg across hypotheses.
Standard library only. Patterns and titles are data; nothing here executes them.
"""
from __future__ import annotations
import argparse,json,math,re,sys
from collections import defaultdict
from pathlib import Path
from .core import SignalError,load_items,median_neighbors

SCHEMA="signalforge-features/1.0"
MAX_HYPOTHESES=40
MIN_FEATURE_VIDEOS=30
MIN_PER_SIDE=3
DIRECTIONS=("up","down","none")

def load_hypotheses(raw: object) -> tuple[str,list[dict]]:
    if not isinstance(raw,dict) or not isinstance(raw.get("hypotheses"),list):
        raise SignalError("hypotheses file needs registered_at and a hypotheses list")
    registered=str(raw.get("registered_at",""))[:40]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}.*",registered):
        raise SignalError("registered_at must start with a YYYY-MM-DD date")
    rows=raw["hypotheses"]
    if not 1<=len(rows)<=MAX_HYPOTHESES: raise SignalError("1 to 40 hypotheses allowed")
    out,seen=[],set()
    for row in rows:
        if not isinstance(row,dict): raise SignalError("hypothesis must be an object")
        name=str(row.get("id",""))[:60]; pattern=row.get("pattern"); field=row.get("field","title")
        direction=row.get("direction")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*",name) or name in seen: raise SignalError("hypothesis id invalid or repeated")
        if field not in ("title","hook"): raise SignalError(f"{name}: field must be title or hook")
        if direction not in DIRECTIONS: raise SignalError(f"{name}: direction must be up, down or none")
        if not isinstance(pattern,str) or not 1<=len(pattern)<=200: raise SignalError(f"{name}: pattern must be 1-200 characters")
        try: compiled=re.compile(pattern,re.IGNORECASE)
        except re.error as exc: raise SignalError(f"{name}: bad pattern ({exc})") from None
        seen.add(name)
        out.append(dict(id=name,field=field,direction=direction,pattern=pattern,regex=compiled))
    return registered,out

def _effect(rows: list[tuple[str,float,bool]]) -> dict | None:
    """Creator fixed-effects slope of log multiplier on the feature flag."""
    groups=defaultdict(list)
    for creator,y,x in rows: groups[creator].append((y,1.0 if x else 0.0))
    sxx=sxy=0.0; parts=[]
    for creator,vals in groups.items():
        my=sum(v[0] for v in vals)/len(vals); mx=sum(v[1] for v in vals)/len(vals)
        dev=[(y-my,x-mx) for y,x in vals]
        sxx+=sum(dx*dx for _,dx in dev); sxy+=sum(dy*dx for dy,dx in dev); parts.append(dev)
    if sxx<=0: return None
    beta=sxy/sxx
    meat=sum(sum(dx*(dy-beta*dx) for dy,dx in dev)**2 for dev in parts)
    clusters=sum(1 for dev in parts if any(dx for _,dx in dev))
    if clusters<2: return None
    se=math.sqrt(meat*clusters/(clusters-1))/sxx
    if se<=0: return dict(beta=beta,se=0.0,p=0.0 if beta else 1.0)
    return dict(beta=beta,se=se,p=math.erfc(abs(beta/se)/math.sqrt(2)))

def _benjamini_hochberg(pvalues: list[float | None]) -> list[float | None]:
    ranked=sorted((p,i) for i,p in enumerate(pvalues) if p is not None)
    out=[None]*len(pvalues); running=1.0
    for rank in range(len(ranked),0,-1):
        p,i=ranked[rank-1]; running=min(running,p*len(ranked)/rank); out[i]=running
    return out

def run_hypotheses(raw_items: object, raw_hypotheses: object, minimum: int=10, drop_newest: int=5) -> dict:
    registered,hypotheses=load_hypotheses(raw_hypotheses)
    items=[x for x in median_neighbors(load_items(raw_items),minimum=minimum,drop_newest=drop_newest)
           if x.get("multiplier") and x["multiplier"]>0]
    results=[]
    for h in hypotheses:
        rows=[(x["creator"],math.log(x["multiplier"]),bool(h["regex"].search(x[h["field"]] or ""))) for x in items
              if h["field"]=="title" or x.get("hook")]
        hits=[x for x in items if (h["field"]=="title" or x.get("hook")) and h["regex"].search(x[h["field"]] or "")]
        by=defaultdict(lambda: ([],[]))
        for creator,y,flag in rows: by[creator][0 if flag else 1].append(y)
        diffs=[sum(a)/len(a)-sum(b)/len(b) for a,b in by.values() if len(a)>=MIN_PER_SIDE and len(b)>=MIN_PER_SIDE]
        r=dict(id=h["id"],field=h["field"],pattern=h["pattern"],predicted=h["direction"],videos_tested=len(rows),
            videos_with_feature=len(hits),creators_compared=len(diffs),effect_multiplier=None,ci95=None,p_value=None,
            q_value=None,share_creators_up=None,share_creators_as_predicted=None,verdict="insufficient data",
            review_examples=[x[h["field"]] for x in sorted(hits,key=lambda v:v["id"])[:10]])
        fit=_effect(rows) if len(hits)>=MIN_FEATURE_VIDEOS and diffs else None
        if fit:
            r["effect_multiplier"]=round(math.exp(fit["beta"]),3)
            r["ci95"]=[round(math.exp(fit["beta"]-1.96*fit["se"]),3),round(math.exp(fit["beta"]+1.96*fit["se"]),3)]
            r["p_value"]=round(fit["p"],6)
            up=sum(d>0 for d in diffs)/len(diffs); r["share_creators_up"]=round(up,3)
            if h["direction"]!="none":
                r["share_creators_as_predicted"]=round(up if h["direction"]=="up" else sum(d<0 for d in diffs)/len(diffs),3)
            r["_beta"]=fit["beta"]
        results.append(r)
    for r,q in zip(results,_benjamini_hochberg([r["p_value"] for r in results])):
        beta=r.pop("_beta",None)
        if q is None: continue
        r["q_value"]=round(q,6); observed="up" if beta>0 else "down"; significant=q<0.05
        if r["predicted"]=="none": r["verdict"]="no change, as predicted" if not significant else f"lead: unpredicted {observed} effect"
        elif not significant: r["verdict"]="not supported"
        elif observed!=r["predicted"]: r["verdict"]="reversed"
        elif r["share_creators_as_predicted"]>0.5: r["verdict"]="rule"
        else: r["verdict"]="lead: significant but not repeated in most creators"
    order={"rule":0,"reversed":1}
    results.sort(key=lambda r:(order.get(r["verdict"],2),-abs(math.log(r["effect_multiplier"])) if r["effect_multiplier"] else 0,r["id"]))
    return {"schema_version":SCHEMA,"method":"creator-fixed-effects-log-multiplier-v1","registered_at":registered,
        "parameters":{"minimum_neighbors":minimum,"drop_newest":drop_newest,"min_feature_videos":MIN_FEATURE_VIDEOS,
            "min_videos_per_side_per_creator":MIN_PER_SIDE,"false_discovery_rate":0.05},
        "videos_scored":len(items),"creators":len({x["creator"] for x in items}),
        "limitations":["Associations inside creators are not causal evidence",
            "Normal-approximation p-values are optimistic with fewer than about 30 creators",
            "Regex features mislabel some titles; read review_examples before trusting a row",
            "Rules describe this niche and sample only"],
        "hypotheses":results}

def main(argv=None):
    ap=argparse.ArgumentParser(prog="python -m signalforge.features",description="Test pre-registered title or hook hypotheses")
    ap.add_argument("input",type=Path)
    ap.add_argument("--hypotheses",type=Path,required=True,help="JSON file written before looking at results")
    ap.add_argument("--out",type=Path,help="Write new JSON report (never overwrites)")
    ap.add_argument("--min-neighbors",type=int,default=10)
    ap.add_argument("--drop-newest",type=int,default=5)
    args=ap.parse_args(argv)
    try:
        for path in (args.input,args.hypotheses):
            if not path.is_file() or path.is_symlink() or path.stat().st_size>15*1024*1024:
                raise SignalError(f"{path.name}: missing, symlink, or over 15 MiB")
        report=run_hypotheses(json.loads(args.input.read_text(encoding="utf-8")),
            json.loads(args.hypotheses.read_text(encoding="utf-8")),args.min_neighbors,args.drop_newest)
        output=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
        if args.out:
            if args.out.is_symlink(): raise SignalError("refusing symlink output")
            with args.out.open("x",encoding="utf-8") as fh: fh.write(output)
            print(f"Wrote {args.out}")
        else: sys.stdout.write(output)
    except (OSError,ValueError,SignalError) as exc:
        print(f"signalforge: {exc}",file=sys.stderr); return 2
    return 0

if __name__=="__main__": raise SystemExit(main())
