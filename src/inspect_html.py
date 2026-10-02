from bs4 import BeautifulSoup
from pathlib import Path

for f in sorted(Path("data/raw").glob("*.html")):
    soup = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
    art_divs = [d for d in soup.find_all("div", id=True) if d["id"].startswith("art_") and "." not in d["id"]]
    titles = soup.select("p.oj-ti-art")
    print(f"\n=== {f.name} ===")
    print("art_ divs:", len(art_divs), "| p.oj-ti-art:", len(titles))
    if art_divs:
        d = art_divs[0]
        print("first id:", d["id"], "| classes:", d.get("class"))
        print(d.get_text(" ", strip=True)[:300])
    if titles:
        print("first titles:", [t.get_text(strip=True) for t in titles[:3]])