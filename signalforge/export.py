"""Read-only candidate export. Never triggers installation or adoption."""
from __future__ import annotations
import hashlib
from .core import clean_text,safe_url,SignalError

def export_candidates(report: dict) -> dict:
    if report.get("schema_version")!="1.0" or not isinstance(report.get("topics"),list):
        raise SignalError("unsupported report schema")
    items=report.get("items",[]); result=[]
    for topic in report["topics"]:
        label=clean_text(topic.get("topic",""))[:120]
        if not label:continue
        refs=[]
        for item in items:
            if str(item.get("topic","")).strip().lower()!=label.lower():continue
            try:url=safe_url(item.get("url",""))
            except SignalError:continue
            if url not in refs:refs.append(url)
            if len(refs)==8:break
        result.append({"id":hashlib.sha256(("signalforge:v1:"+label).encode()).hexdigest()[:24],
            "title":label,"category":"research-lead","status":"investigate-only",
            "source":"signalforge-offline","score":topic.get("signal_score"),
            "confidence":topic.get("confidence","limited"),"evidence_urls":refs,
            "evidence_kind":"observed-metadata","risk":"unverified",
            "owner_approval_required":True,
            "recommendation":"Research primary sources before considering adoption"})
    return {"schema_version":"signalforge-candidates/1.0","read_only":True,
        "no_auto_install":True,"candidates":result}
