import json
import re
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

FILES = {
    "ai_act_en": ("AI Act", "en"),
    "ai_act_de": ("AI Act", "de"),
    "gdpr_en": ("GDPR", "en"),
    "gdpr_de": ("GDPR", "de"),
}
MARKER = re.compile(r"^(\(\w{1,4}\)|\d+\.)$")
PARA_START = [re.compile(r"^(\d+)\.\s+(.*)$", re.S), re.compile(r"^\((\d+)\)\s+(.*)$", re.S)]


def clean(t):
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def article_lines(div):
    lines, pending = [], ""
    for p in div.find_all("p"):
        if p.find("p") or "oj-ti-art" in (p.get("class") or []) or "oj-sti-art" in (p.get("class") or []):
            continue
        t = clean(p.get_text(" "))
        if not t:
            continue
        if MARKER.match(t):
            pending = t
            continue
        lines.append((pending + " " + t).strip())
        pending = ""
    return lines


def split_paragraphs(lines):
    paras, current, expected = [], [], 1
    num = 0
    for line in lines:
        m = None
        for pat in PARA_START:
            m = pat.match(line)
            if m and int(m.group(1)) == expected:
                break
            m = None
        if m:
            if current:
                paras.append((num, " ".join(current)))
            num, expected = expected, expected + 1
            current = [m.group(2)]
        else:
            current.append(line)
    if current:
        paras.append((num, " ".join(current)))
    return paras


chunks = []
for name, (law, lang) in FILES.items():
    soup = BeautifulSoup(Path(f"data/raw/{name}.html").read_text(encoding="utf-8"), "lxml")
    for div in soup.find_all("div", id=True):
        if not div["id"].startswith("art_") or "." in div["id"]:
            continue
        art = int(div["id"].split("_")[1])
        sti = div.select_one("p.oj-sti-art")
        title = clean(sti.get_text(" ")) if sti else ""
        for num, text in split_paragraphs(article_lines(div)):
            ref = f"{law} Art. {art}" + (f"({num})" if num else "")
            chunks.append({
                "id": f"{name}_{art}_{num}", "law": law, "lang": lang,
                "article": art, "paragraph": num, "title": title,
                "ref": ref, "text": text,
            })

out = Path("data/processed")
out.mkdir(parents=True, exist_ok=True)
with open(out / "chunks.jsonl", "w", encoding="utf-8") as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")

print("total chunks:", len(chunks))
for name in FILES:
    print(name, sum(1 for c in chunks if c["id"].startswith(name)))
for want in ["ai_act_en_6_1", "gdpr_en_17_1", "ai_act_de_5_1"]:
    c = next((c for c in chunks if c["id"] == want), None)
    if c:
        print("\n", c["ref"], "|", c["title"], "\n", c["text"][:350])