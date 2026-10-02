import json
import sys

sys.path.insert(0, "src")
from baseline import build, load_chunks, search


def key(c):
    if c.get("annex"):
        return f"{c['law']}:annex{c['annex']}"
    return f"{c['law']}:{c['article']}"


chunks = load_chunks()
indexes = {}
rows = []
for line in open("eval/golden.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    q = json.loads(line)
    if q["lang"] not in indexes:
        indexes[q["lang"]] = build(chunks, q["lang"])
    cs, bm = indexes[q["lang"]]
    results = search(cs, bm, q["question"], k=10)
    rank = next((i + 1 for i, (_, c) in enumerate(results) if key(c) in q["gold"]), None)
    rows.append((q["id"], rank, q["question"]))

for id_, rank, question in rows:
    print(f"{id_:>3}  rank={rank if rank else '-':>2}  {question}")

n = len(rows)
print()
for k in (1, 5, 10):
    hits = sum(1 for _, r, _ in rows if r and r <= k)
    print(f"hit@{k}: {hits}/{n} = {hits / n:.0%}")
print(f"MRR@10: {sum(1 / r for _, r, _ in rows if r) / n:.2f}")