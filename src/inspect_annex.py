import warnings
from pathlib import Path

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

soup = BeautifulSoup(Path("data/raw/ai_act_en.html").read_text(encoding="utf-8"), "lxml")
annexes = [d for d in soup.find_all("div", id=True) if d["id"].startswith("anx_") and d["id"].count("_") == 1]
print("annex divs:", [d["id"] for d in annexes])

d = soup.find("div", id="anx_III")
if d:
    print("\nanx_III total chars:", len(d.get_text()))
    print("\nFirst 25 <p> elements (class | text):")
    for p in d.find_all("p")[:25]:
        print(" ", p.get("class"), "|", " ".join(p.get_text(' ', strip=True).split())[:110])
    print("\nTables inside:", len(d.find_all("table")))