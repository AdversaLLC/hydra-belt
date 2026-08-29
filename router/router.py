#!/usr/bin/env python3
"""hydra-router (Tier 2): zero-dependency BM25 skill dispatcher.
Reads 104 SKILL.md descriptions, returns a ranked shortlist for a request.
No model download. Pure stdlib. Falls back-compatible with wisdom.py's tf-idf lineage."""
import os, re, math, json, sys
from collections import Counter

SKILLS_DIR = os.environ.get("HYDRA_SKILLS", "/home/paladin/.claude/skills")
STOP = set("""a an the and or but if then else for to of in on at by with from as is are was were be been being
this that these those it its their there here we you your i my me he she they them do does did done have has had
use used using when where what which who whom how why not no nor so than too very can will just should now also
run running via per into over under only other any all both each more most some such own same s t don should've""".split())

def toks(s):
    return [w for w in re.findall(r"[a-z0-9][a-z0-9_+-]{1,}", s.lower()) if w not in STOP and len(w) > 2]

def load(skills_dir=SKILLS_DIR):
    docs = []
    for d in sorted(os.listdir(skills_dir)):
        fp = os.path.join(skills_dir, d, "SKILL.md")
        if not os.path.isfile(fp): continue
        t = open(fp, encoding="utf-8", errors="replace").read()
        m = re.search(r"^---\s*\n(.*?)\n---", t, re.S)
        desc = ""
        if m:
            dm = re.search(r"^description:\s*(.*?)(?=\n[a-z_-]+:\s|\Z)", m.group(1), re.S | re.M)
            if dm: desc = " ".join(dm.group(1).split())
        if not desc:
            desc = " ".join(t.split())[:600]
        # name tokens weighted 3x -- the folder name is the strongest signal
        docs.append({"skill": d, "desc": desc, "toks": toks(d.replace("-", " ")) * 3 + toks(desc)})
    return docs

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.N = len(docs)
        self.tf = [Counter(d["toks"]) for d in docs]
        self.len = [len(d["toks"]) for d in docs]
        self.avg = sum(self.len) / max(1, self.N)
        df = Counter()
        for c in self.tf: df.update(c.keys())
        self.idf = {w: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for w, n in df.items()}
    def score(self, q):
        qt = toks(q); out = []
        for i, c in enumerate(self.tf):
            s = 0.0
            for w in qt:
                f = c.get(w, 0)
                if not f: continue
                s += self.idf.get(w, 0) * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            if s > 0: out.append((s, self.docs[i]["skill"]))
        out.sort(reverse=True)
        return out

def route(q, idx, k=5, rel=0.35):
    """Return shortlist: top-k, cut at `rel` fraction of the top score (adaptive width)."""
    sc = idx.score(q)
    if not sc: return []
    top = sc[0][0]
    return [(round(s, 2), n) for s, n in sc[:k] if s >= top * rel]

if __name__ == "__main__":
    idx = BM25(load())
    if len(sys.argv) > 1:
        for s, n in route(" ".join(sys.argv[1:]), idx): print(f"{s:7.2f}  {n}")
    else:
        print(f"indexed {idx.N} skills, avg {idx.avg:.0f} tokens/skill")
