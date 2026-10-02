import json
import re
import sys

from rank_bm25 import BM25Okapi


def tok(t):
    return re.findall(r"\w+", t.lower())


def load_chunks(path="data/processed/chunks.jsonl"):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build(chunks, lang):
    cs = [c for c in chunks if c["lang"] == lang]
    bm = BM25Okapi([tok(c["title"] + " " + c["text"]) for c in cs])
    return cs, bm


def search(cs, bm, query, k=5):
    scores = bm.get_scores(tok(query))
    top = sorted(range(len(cs)), key=lambda i: -scores[i])[:k]
    return [(scores[i], cs[i]) for i in top]


if __name__ == "__main__":
    lang = sys.argv[1]
    query = " ".join(sys.argv[2:])
    cs, bm = build(load_chunks(), lang)
    for score, c in search(cs, bm, query):
        print(f"{score:.2f}  {c['ref']} | {c['title']}")
        print("    ", c["text"][:200])