"""Opt-in public GitHub repository discovery; no tokens, code execution or installation."""
from __future__ import annotations
import argparse, json, math, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .core import SignalError, clean_text, parse_date, safe_url

MAX_RESPONSE_BYTES = 2_000_000
MAX_RESULTS = 20
API_HOST = "api.github.com"

class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SignalError("redirect refused")

def _nonnegative(value: object) -> int:
    return value if isinstance(value,int) and not isinstance(value,bool) and 0 <= value <= 10**12 else 0

def _public_search(query: str, limit: int, opener=None) -> dict:
    if not isinstance(query,str) or not 2 <= len(query.strip()) <= 100 or any(ord(x) < 32 or ord(x)==127 for x in query):
        raise SignalError("query must contain 2-100 printable characters")
    if not isinstance(limit,int) or isinstance(limit,bool) or not 1 <= limit <= MAX_RESULTS:
        raise SignalError("limit must be between 1 and 20")
    url = "https://api.github.com/search/repositories?q=" + quote(query.strip(),safe="") + "&sort=updated&order=desc&per_page=" + str(limit)
    req = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "SignalForge/0.1 (https://github.com/maumoya/SignalForge)"
    }, method="GET")
    # The only allowed origin is the fixed host above; never fetch a URL from returned data.
    client = opener if opener is not None else build_opener(NoRedirects())
    try:
        with client.open(req,timeout=10) as response:
            final = response.geturl() if hasattr(response,"geturl") else url
            parsed = urlsplit(final)
            if parsed.scheme != "https" or parsed.hostname != API_HOST or parsed.port not in (None,443):
                raise SignalError("unapproved API destination")
            if getattr(response,"status",200) != 200:
                raise SignalError("GitHub returned an unsuccessful HTTP status")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        if exc.code in (403,429):
            raise SignalError("GitHub rate limit or access restriction; retry later") from exc
        raise SignalError("public GitHub API returned HTTP "+str(exc.code)) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise SignalError("public GitHub API is not reachable") from exc
    if len(raw)>MAX_RESPONSE_BYTES:
        raise SignalError("GitHub response is larger than 2 MB")
    try: data=json.loads(raw)
    except (ValueError, UnicodeError) as exc: raise SignalError("invalid public GitHub API JSON") from exc
    if not isinstance(data,dict) or not isinstance(data.get("items"),list):
        raise SignalError("GitHub result lacks an items list")
    return data

def search_public_repositories(query: str, limit: int=10, opener=None, now: datetime|None=None) -> dict:
    """Search public repos. Stars/forks/push recency are discovery hints, NOT security ratings."""
    data=_public_search(query,limit,opener)
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: now=now.replace(tzinfo=timezone.utc)
    repos=[]; seen=set()
    for item in data["items"][:MAX_RESULTS]:
        if not isinstance(item,dict): continue
        name=clean_text(item.get("full_name"))[:160]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",name) or name.lower() in seen:continue
        try: url=safe_url(item.get("html_url",""))
        except SignalError: continue
        if urlsplit(url).hostname != "github.com":continue
        if urlsplit(url).path.rstrip("/").lower() != ("/"+name).lower():continue
        seen.add(name.lower())
        stars=_nonnegative(item.get("stargazers_count"))
        forks=_nonnegative(item.get("forks_count"))
        pushed=parse_date(item.get("pushed_at"))
        active=0.0
        if pushed:
            days=max(0,(now-datetime.fromisoformat(pushed)).total_seconds()/86400)
            active=math.exp(-days/180)
        popularity=min(1.0,math.log1p(stars)/math.log1p(5000))
        collaboration=min(1.0,math.log1p(forks)/math.log1p(1000))
        score=round(100*(.4*popularity+.45*active+.15*collaboration),1)
        repos.append({
            "full_name":name, "url":url, "description":clean_text(item.get("description"))[:280],
            "stars":stars, "forks":forks, "pushed_at":pushed,
            "archived":bool(item.get("archived",False)), "research_attention_score":score,
            "security_status":"unverified","implementation_status":"not-assessed",
            "recommendation":"investigate-only"
        })
    repos.sort(key=lambda r:(-r["research_attention_score"],r["full_name"]))
    return {"schema_version":"signalforge-github/1.0","source":"public-github-api",
        "query":query.strip(),"observed_at":now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "read_only":True,"no_auto_install":True,
        "limitations":["GitHub stars and updates are not proof of quality or security",
            "Search results and rate limits can change between runs",
            "This is discovery, not code review, dependency audit or implementation approval"],
        "repositories":repos}

def export_github_candidates(report: dict) -> dict:
    if report.get("schema_version")!="signalforge-github/1.0":
        raise SignalError("unsupported GitHub result schema")
    import hashlib
    leads=[]
    for item in report.get("repositories",[]):
        leads.append({
            "id":hashlib.sha256(("signalforge:github:"+item["full_name"].lower()).encode()).hexdigest()[:24],
            "title":item["full_name"],"category":"research-lead","status":"investigate-only",
            "source":"signalforge-github-public","score":item["research_attention_score"],
            "confidence":"unverified","evidence_urls":[item["url"]],
            "evidence_kind":"public-repository-metadata","risk":"unverified",
            "owner_approval_required":True,
            "recommendation":"Read the project, verify its licence, maintenance and security before any adoption"
        })
    return {"schema_version":"signalforge-candidates/1.0","read_only":True,
        "no_auto_install":True,"candidates":leads}

def main(argv=None):
    ap=argparse.ArgumentParser(description="Opt-in, read-only public GitHub discovery (uses internet)")
    ap.add_argument("query",help="Public GitHub repository search; avoid private information")
    ap.add_argument("--limit",type=int,default=10,help="Maximum results, 1-20")
    ap.add_argument("--out",type=Path,help="Create a new JSON file (never overwrite)")
    ap.add_argument("--candidates",action="store_true",help="Export approval-gated research leads")
    a=ap.parse_args(argv)
    try:
        report=search_public_repositories(a.query,a.limit)
        result=export_github_candidates(report) if a.candidates else report
        output=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
        if a.out:
            if a.out.is_symlink():raise SignalError("refusing symlink output")
            with a.out.open("x",encoding="utf-8") as f:f.write(output)
            print(f"Wrote {a.out}")
        else: print(output,end="")
        return 0
    except (SignalError, OSError) as exc:
        print(f"signalforge discovery: {exc}",file=sys.stderr);return 2

if __name__=="__main__":raise SystemExit(main())
