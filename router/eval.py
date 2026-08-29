import json, os, sys
_HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,_HERE)
from router import BM25, load, route
idx = BM25(load())
top1=top3=n=0; misses=[]
for line in open(os.path.join(_HERE,'golden.jsonl')):
    c=json.loads(line); n+=1
    sl=[name for _,name in route(c['q'], idx, k=3)]
    if sl[:1]==[c['want']]: top1+=1
    if c['want'] in sl: top3+=1
    else: misses.append((c['q'][:52], c['want'], sl))
print(f"Zero-download BM25 router over {idx.N} skills, {n} golden cases:")
print(f"  top-1 accuracy: {top1}/{n} = {100*top1/n:.0f}%")
print(f"  top-3 recall  : {top3}/{n} = {100*top3/n:.0f}%")
if misses:
    print("  top-3 misses:")
    for q,w,sl in misses: print(f"    '{q}' want={w} got={sl}")
