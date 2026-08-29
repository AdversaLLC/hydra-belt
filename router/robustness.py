import json, os, sys
_H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_H)
from router import BM25, load, route
idx=BM25(load())
def score(fn):
    t1=t3=n=0; miss=[]
    for line in open(os.path.join(_H,fn)):
        c=json.loads(line); n+=1
        sl=[nm for _,nm in route(c['q'],idx,k=3)]
        if sl[:1]==[c['want']]: t1+=1
        if c['want'] in sl: t3+=1
        else: miss.append((c['q'][:46],c['want'],sl[:3]))
    return n,t1,t3,miss
for label,fn in [("GOLDEN (friendly)","golden.jsonl"),("ADVERSARIAL (paraphrase)","adversarial.jsonl")]:
    n,t1,t3,miss=score(fn)
    print(f"{label}: top1 {t1}/{n}={100*t1//n}%  top3 {t3}/{n}={100*t3//n}%")
    for q,w,sl in miss: print(f"   MISS '{q}' want={w} got={sl}")
