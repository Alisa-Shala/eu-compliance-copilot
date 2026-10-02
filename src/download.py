import requests
from pathlib import Path

BASE = "https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:{celex}"
DOCS = {
    "ai_act_en": ("EN", "32024R1689"),
    "ai_act_de": ("DE", "32024R1689"),
    "gdpr_en": ("EN", "32016R0679"),
    "gdpr_de": ("DE", "32016R0679"),
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

Path("data/raw").mkdir(parents=True, exist_ok=True)

for name, (lang, celex) in DOCS.items():
    url = BASE.format(lang=lang, celex=celex)
    r = requests.get(url, headers=HEADERS, timeout=60)
    print(name, r.status_code, len(r.text))
    if r.status_code == 200 and len(r.text) > 100_000:
        Path(f"data/raw/{name}.html").write_text(r.text, encoding="utf-8")
        print("  saved")
    else:
        print("  FAILED or blocked")