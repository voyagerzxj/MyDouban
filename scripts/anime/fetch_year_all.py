# -*- coding: utf-8 -*-
"""第一步：从 Jikan API 拉取 YEAR 年全部动画（四个季度 + 剧场版），存为 JSON"""
import json, time, urllib.request, urllib.parse, sys

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "anime-yearly-list/1.0"}
YEAR = sys.argv[1] if len(sys.argv) > 1 else "2025"

def get_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  retry {i+1} for {url}: {e}", file=sys.stderr)
            time.sleep(3)
    return None

all_entries = {}

def collect(data):
    for it in data.get("data", []):
        mid = it["mal_id"]
        if mid in all_entries:
            continue
        all_entries[mid] = {
            "mal_id": mid,
            "title": it.get("title"),
            "title_jp": it.get("title_japanese"),
            "type": it.get("type"),
            "score": it.get("score"),
            "scored_by": it.get("scored_by"),
            "members": it.get("members"),
            "aired_from": (it.get("aired") or {}).get("from"),
            "studios": [s["name"] for s in it.get("studios", [])],
            "genres": [g["name"] for g in it.get("genres", [])],
            "demographics": [g["name"] for g in it.get("demographics", [])],
        }

# 四个季度（含 TV/ONA/Movie 等该季度首播的全部条目）
for season in ["winter", "spring", "summer", "fall"]:
    page = 1
    while True:
        url = f"https://api.jikan.moe/v4/seasons/{YEAR}/{season}?page={page}"
        data = get_json(url)
        if not data:
            break
        collect(data)
        print(f"{season} page {page}: total so far {len(all_entries)}")
        if not data.get("pagination", {}).get("has_next_page"):
            break
        page += 1
        time.sleep(1.1)
    time.sleep(1.1)

with open(f"anime_{YEAR}_raw.json", "w", encoding="utf-8") as f:
    json.dump(list(all_entries.values()), f, ensure_ascii=False, indent=1)

print(f"\n共 {len(all_entries)} 部条目，已存 anime_{YEAR}_raw.json")
# 预览：按分数排序的前 40
scored = [e for e in all_entries.values() if e["score"]]
for e in sorted(scored, key=lambda x: -x["score"])[:40]:
    print(f'{e["score"]:.2f} ({e["scored_by"] or 0:>7}人) {e["type"]:<7} {e["title_jp"] or e["title"]}')
