import json
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

SOURCES = [
    {"id":"cnil","name":"CNIL","country":"FR","url":"https://www.cnil.fr/fr/rss.xml","color":"#003189","icon":"🇫🇷"},
    {"id":"anssi","name":"ANSSI","country":"FR","url":"https://www.cert.ssi.gouv.fr/feed/","color":"#005B8E","icon":"🛡️"},
    {"id":"edpb","name":"EDPB","country":"EU","url":"https://www.edpb.europa.eu/news/news_en.rss","color":"#003399","icon":"🇪🇺"},
    {"id":"commission","name":"Commission européenne","country":"EU","url":"https://ec.europa.eu/newsroom/dgt/rss.cfm?service=1&thema=1","color":"#FFD700","icon":"🇪🇺"},
    {"id":"dpc","name":"DPC Ireland","country":"IE","url":"https://www.dataprotection.ie/en/news-media/news/rss.xml","color":"#169B62","icon":"🇮🇪"},
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
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:MAX_ITEMS]:
            items.append({
                "title": entry.get("title","Sans titre").strip(),
                "link": entry.get("link",""),
                "date": parse_date(entry),
                "summary": (entry.get("summary","") or "")[:300].strip(),
                "source_id": source["id"],
                "source_name": source["name"],
            })
    except Exception as e:
        print(f"[ERREUR] {source['name']}: {e}")
    return items

def main():
    all_items = []
    meta = {}
    for source in SOURCES:
        print(f"Fetching {source['name']}...")
        items = fetch_source(source)
        print(f"  → {len(items)} articles")
        all_items.extend(items)
        meta[source["id"]] = {"name":source["name"],"country":source["country"],"color":source["color"],"icon":source["icon"],"count":len(items)}
    all_items.sort(key=lambda x: x["date"], reverse=True)
    output = {"updated":datetime.now(timezone.utc).isoformat(),"sources_meta":meta,"items":all_items}
    with open("data/feeds.json","w",encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ {len(all_items)} articles enregistrés dans data/feeds.json")

if __name__ == "__main__":
    main()
