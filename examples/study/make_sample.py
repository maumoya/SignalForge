"""Write the known-answer study sample. Invented creators and titles; fixed seed.

Planted effects: a number in the title lifts views about 1.5x, the word
"tutorial" cuts them to about 0.7x, a question mark does nothing.
Usage: python examples/study/make_sample.py > examples/study/videos.json
"""
import json,random
from datetime import datetime,timedelta,timezone

rng=random.Random(20261110)
SUBJECTS=["prompt templates","an agent workflow","a spreadsheet bot","voice notes","a research helper","image edits"]
items=[]
for c in range(14):
    base=rng.choice([800,3000,12000,60000,250000])
    for n in range(60):
        number=rng.random()<0.35; tutorial=rng.random()<0.3; question=rng.random()<0.3
        title=("Tutorial: " if tutorial else "")+(f"{rng.randint(3,9)} ways to use " if number else "I tried ")+rng.choice(SUBJECTS)+("?" if question else "")
        views=base*rng.lognormvariate(0,0.5)*(1.5 if number else 1)*(0.7 if tutorial else 1)
        items.append({"url":f"https://youtube.com/shorts/study-{c:02d}-{n:02d}","platform":"youtube",
            "creator":f"sample-channel-{c:02d}","title":title,"topic":"ai tools","views":int(views),
            "published_at":(datetime(2026,6,1,tzinfo=timezone.utc)+timedelta(days=n,hours=c)).isoformat()})
print(json.dumps({"items":items},separators=(",",":")))
