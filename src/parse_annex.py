import json
import re
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

AREA = re.compile(r"^(\d+)\.$")
ITEM = re.compile(r"^\(?([a-z]{1,2})\)$")
LABEL = {"en": "Annex III", "de": "Anhang III"}


def clean(t):
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def parse_annex3(html, lang):
    soup = BeautifulSoup(html, "lxml")
    div = soup.find("div", id="anx_III")
    ps = [p for p in div.find_all("p") if not p.find("p")]
    heads = [clean(p.get_text(" ")) for p in ps if "oj-doc-ti" in (p.get("class") or [])]
    subtitle = heads[1] if len(heads) > 1 else ""
    body = [clean(p.get_text(" ")) for p in ps if "oj-doc-ti" not in (p.get("class") or [])]
    body = [t for t in body if t]

    intro, entries, cur, pending, area, head = [], [], None, None, 0, ""
    for t in body:
        m, i = AREA.match(t), ITEM.match(t)
        if m:
            pending = ("area", int(m.group(1)))
        elif i:
            pending = ("item", i.group(1))
        elif pending is None:
            (intro if cur is None else cur["text"]).append(t)
        elif pending[0] == "area":
            area, head = pending[1], t
            cur = {"area": area, "item": None, "head": t, "text": [t]}
            entries.append(cur)
            pending = None
        else:
            cur = {"area": area, "item": pending[1], "head": head, "text": [t]}
            entries.append(cur)
            pending = None

    areas_with_items = {e["area"] for e in entries if e["item"]}
    label = LABEL[lang]
    chunks = []

    def make(area, item, text):
        ref = f"AI Act {label}" + (f", {area}" if area else "") + (f"({item})" if item else "")
        return {
            "id": f"ai_act_{lang}_annex3_{area}_{item or 0}", "law": "AI Act", "lang": lang,
            "article": None, "paragraph": None, "annex": "III", "area": area, "item": item,
            "title": f"{label}: {subtitle}", "ref": ref, "text": text,
        }

    if intro:
        chunks.append(make(0, None, " ".join(intro)))
    for e in entries:
        if e["item"] is None and e["area"] in areas_with_items:
            continue  # bare area heading, its items carry the content
        text = " ".join(e["text"])
        if e["item"]:
            text = e["head"] + " " + text
        chunks.append(make(e["area"], e["item"], text))
    return chunks


new = []
for lang in ["en", "de"]:
    html = Path(f"data/raw/ai_act_{lang}.html").read_text(encoding="utf-8")
    new += parse_annex3(html, lang)

path = Path("data/processed/chunks.jsonl")
old = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
old = [c for c in old if not c.get("annex")]  # makes re-running safe
with open(path, "w", encoding="utf-8") as f:
    for c in old + new:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print("old:", len(old), "| annex III added:", len(new), "| total:", len(old) + len(new))
for lang in ["en", "de"]:
    print(lang, [c["ref"].replace("AI Act ", "") for c in new if c["lang"] == lang])
for c in new:
    if c["lang"] == "en" and c["ref"].endswith("4(a)"):
        print("\n", c["ref"], "\n", c["text"])