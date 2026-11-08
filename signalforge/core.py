"""Deterministic, offline signal intelligence; content is data, never commands."""
from __future__ import annotations
import hashlib, ipaddress, math, re, statistics
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

SCHEMA_VERSION = "1.0"
MAX_ITEMS = 100000
MAX_TEXT = 2000
TRACKING_KEYS = {"fbclid", "gclid", "igshid", "mc_cid", "mc_eid"}

class SignalError(ValueError):
    pass

def safe_url(value: str) -> str:
    """Canonicalize public HTTPS references without ever fetching them."""
    if not isinstance(value, str) or len(value)>2048 or any(ord(c)<32 or ord(c)==127 for c in value):
        raise SignalError("invalid URL")
    try:
        p=urlsplit(value)
        host=(p.hostname or "").lower()
        try:
            if not ipaddress.ip_address(host).is_global: raise SignalError("non-public IP")
        except ValueError as e:
            if isinstance(e,SignalError): raise
        if (p.scheme!="https" or not host or p.username or p.password or p.port not in (None,443)
            or host in {"localhost","localhost.localdomain"} or host.endswith((".local",".internal"))
            or ":" in host or not re.fullmatch(r"[a-z0-9.-]+",host) or "." not in host
            or host.startswith(".") or ".." in host):
            raise SignalError("non-public URL")
        query=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True)
            if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS])
        return urlunsplit(("https",host,p.path or "/",query,""))
    except ValueError as exc:
        raise SignalError("invalid URL") from exc

def clean_text(value: object) -> str:
    if not isinstance(value,str): return ""
    text=re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]","",value)
    return " ".join("".join(c for c in text if ord(c)>=32 or c in "\n\t").split())[:MAX_TEXT]

def parse_date(value: object) -> str | None:
    if not isinstance(value,str): return None
    try:
        dt=datetime.fromisoformat(value.replace("Z","+00:00"))
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat(timespec="seconds")
    except ValueError:
        return None

def load_items(raw: object) -> list[dict]:
    if isinstance(raw,dict): raw=raw.get("items",[])
    if not isinstance(raw,list) or len(raw)>MAX_ITEMS: raise SignalError("expected <=100000 items")
    out=[]; seen=set()
    for row in raw:
        if not isinstance(row,dict): continue
        try: url=safe_url(row.get("url",""))
        except SignalError: continue
        creator=clean_text(row.get("creator",""))[:120]
        platform=clean_text(row.get("platform",""))[:40].lower()
        title=clean_text(row.get("title",""))[:300]
        topic=clean_text(row.get("topic",""))[:120]
        if not platform or not title: continue
        views=row.get("views")
        if not isinstance(views,int) or isinstance(views,bool) or not 0<=views<=10**13: views=None
        date=parse_date(row.get("published_at"))
        key=hashlib.sha256(url.encode()).hexdigest()[:24]
        if key in seen: continue
        seen.add(key)
        out.append(dict(id=key,url=url,creator=creator,platform=platform,title=title,
                        topic=topic,views=views,published_at=date))
    return out

def median_neighbors(items: list[dict], n: int=10, minimum: int=5) -> list[dict]:
    if not 1<=n<=50: raise SignalError("neighbors out of range")
    groups=defaultdict(list)
    for item in items:
        if item["views"] is not None and item["published_at"] and item["creator"]:
            groups[(item["platform"],item["creator"])].append(item)
    out={v["id"]:{**v,"baseline":None,"multiplier":None,
            "neighbor_count":0,"evidence_level":"insufficient"} for v in items}
    for group in groups.values():
        group.sort(key=lambda v:(v["published_at"],v["id"]))
        for i,item in enumerate(group):
            neighbors=[v["views"] for v in group[max(0,i-n):i]+group[i+1:i+1+n]]
            o=out[item["id"]];o["neighbor_count"]=len(neighbors)
            if len(neighbors)<minimum: continue
            base=statistics.median(neighbors);o["baseline"]=base
            if base>0:
                o["multiplier"]=round(item["views"]/base,4);o["evidence_level"]="observed"
            else:o["evidence_level"]="zero-baseline"
    return [out[item["id"]] for item in items]

def summarize(items: list[dict]) -> list[dict]:
    groups=defaultdict(list)
    for x in items:
        topic=(x.get("topic") or "").lower().strip()
        if topic: groups[topic].append(x)
    results=[]
    for topic,rows in groups.items():
        obs=[x["multiplier"] for x in rows if x.get("multiplier") is not None]
        creators={(x["platform"],x["creator"]) for x in rows if x["creator"]}
        platforms={x["platform"] for x in rows}
        multiple=round(statistics.median(obs),3) if obs else None
        strength=min(1.0,len(creators)/5)
        momentum=min(1.0,math.log1p(multiple)/math.log1p(10)) if multiple else 0.0
        coverage=min(1.0,len(platforms)/3)
        score=round(100*(.4*strength+.4*momentum+.2*coverage),1)
        confidence="moderate" if len(creators)>=3 and len(obs)>=5 else "limited"
        results.append(dict(topic=topic,signal_score=score,confidence=confidence,
            items=len(rows),independent_creators=len(creators),platforms=sorted(platforms),
            observed_multipliers=len(obs),median_relative_performance=multiple))
    return sorted(results,key=lambda r:(-r["signal_score"],-r["independent_creators"],r["topic"]))

def analyze(raw: object) -> dict:
    items=median_neighbors(load_items(raw))
    return {"schema_version":SCHEMA_VERSION,"method":"same-creator-neighbor-median-v1",
        "limitations":["Relative views are not causal evidence",
        "A current snapshot cannot establish growth velocity",
        "Topic scores are heuristic, not probabilities",
        "Sparse groups remain unscored"],"items":items,"topics":summarize(items)}
