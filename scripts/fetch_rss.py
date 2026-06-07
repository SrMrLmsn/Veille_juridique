import json
import urllib.request
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

SOURCES = [
    {"id":"cnil","name":"CNIL","country":"FR","url":"https://www.cnil.fr/fr/rss.xml","color":"#003189","icon":"🇫🇷"},
    {"id":"anssi","name":"ANSSI","country":"FR","url":"https://www.cert.ssi.gouv.fr/feed/","color":"#005B8E","icon":"🛡️"},
    {"id":"edpb","name":"EDPB","country":"EU","url":"https://www.edpb.europa.eu/feed/news_en","color":"#003399","icon":"🇪🇺"},
    {"id":"commission","name":"Commission européenne","country":"EU","url":"https://digital-strategy.ec.europa.eu/en/rss.xml","color":"#9a7e00","icon":"🇪🇺"},
]

MAX_ITEMS = 25

def parse_date(entry):
    for attr in ("published", "updated"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return parsedate_to_datetime(val).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()

def fetch_source(source):
    items = []
    try:
        req = urllib.request.Request(source["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
        feed = feedparser.parse(raw)
        print(f"  → {len(feed.entries)} entrées brutes")
        for entry in feed.entries[:MAX_ITEMS]:
            items.append({
                "title": entry.get("title", "Sans titre").strip(),
                "link": entry.get("link", ""),
                "date": parse_date(entry),
                "summary": (entry.get("summary", "") or "")[:300].strip(),
                "source_id": source["id"],
                "source_name": source["name"],
            })
    except Exception as e:
        print(f"  [ERREUR] {e}")
    return items

def main():
    all_items = []
    meta = {}
    for source in SOURCES:
        print(f"Fetching {source['name']} — {source['url']}")
        items = fetch_source(source)
        print(f"  ✓ {len(items)} articles retenus")
        all_items.extend(items)
        meta[source["id"]] = {
            "name": source["name"],
            "country": source["country"],
            "color": source["color"],
            "icon": source["icon"],
            "count": len(items),
        }
    all_items.sort(key=lambda x: x["date"], reverse=True)
    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "sources_meta": meta,
        "items": all_items,
    }
    with open("data/feeds.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ {len(all_items)} articles enregistrés")

if __name__ == "__main__":
    main()
