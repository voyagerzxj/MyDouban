# -*- coding: utf-8 -*-
"""第二步：对候选作品逐部查询 Bangumi API 评分和 Filmarks 评分
用法: python fetch_bgm_filmarks.py <年份>
"""
import json, re, time, html, urllib.request, urllib.parse, sys

sys.stdout.reconfigure(encoding="utf-8")
YEAR = sys.argv[1] if len(sys.argv) > 1 else "2025"
UA_API = {"User-Agent": "anime-yearly-list/1.0"}
UA_WEB = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
          "Accept-Language": "ja,en;q=0.8"}

# 非日本动画（中国/韩国）、回顾总集篇、PV、成人向 —— 按年份排除
EXCLUDE = {
"2025": {
    "凸变英雄X", "诡秘之主 小丑篇", "罗小黑战记2", "凡人修仙传 第四季",
    "天官賜福 全新动画短片", "哪吒之魔童闹海", "灵笼 第二季", "光阴之外",
    "武动乾坤 第五季", "鲲吞天下之掌门归来", "龙族Ⅱ 悼亡者之瞳", "魔法公主的小烦恼",
    "이 별에 필요한", "제발 조용히 좀 해!",
    "チェンソーマン 総集篇", "この素晴らしい世界に祝福を！３ーBONUS STAGEー",
    "OVA「SK∞ エスケーエイト EXTRA PART」", "夏目友人帳 漆 伸ばした手は",
    "『リコリス・リコイル』Friends are thieves of time.", "アンデッドアンラック ウィンター編",
    "カイリューとゆうびんやさん", "My Melody & Kuromi",
    "風紀委員とフーゾク活動", "元カレとはできなかったセックスしてもいいですか?",
    "シスターブリーダー", "インモラルーティーン THE ANIMATION",
},
"2024": {
    "牧神记", "時光代理人 英都篇", "伍六七之记忆碎片", "一念永恒 第3季", "沧元图2",
    "《原神》「烬中歌」", "斩神之凡尘神域", "成何体统", "爱上她的理由", "诛仙 第二季",
    "《崩坏：星穹铁道》：「格拉默的余烬」", "剑来", "《原神》「未行之路」",
    "亏成首富从游戏开始", "邂逅她的少女时代",
    "Bleach 20th PV", "ぼっち・ざ・ろっく！劇場総集編",
    "SPECIAL EDITED VERSION『ONE PIECE』魚人島編", "傷物語 -こよみヴァンプ-",
    "俺だけレベルアップな件 -ReAwakening-",
    "入り浸りギャルにま〇こ使わせて貰う話", "陰キャカップルが陽ギャル達とSEXトレーニングする話",
},
}
# 低于阈值但值得核查的小众作品，手动加入
MANUAL_ADD = {
"2025": [
    ("トリツカレ男", "Movie"), ("ChaO", "Movie"), ("終末ツーリング", "TV"),
    ("永久のユウグレ", "TV"), ("太陽よりも眩しい星", "TV"), ("ベルサイユのばら", "Movie"),
],
"2024": [
    ("ネガポジアングラー", "TV"), ("義妹生活", "TV"), ("オーイ!とんぼ", "TV"),
    ("数分間のエールを", "Movie"), ("化け猫あんずちゃん", "Movie"), ("トラペジウム", "Movie"),
    ("終末トレインどこへいく？", "TV"), ("先輩はおとこのこ", "TV"),
    ("姫様“拷問”の時間です", "TV"), ("クラメルカガリ", "Movie"),
],
}

def get(url, headers, retries=2):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(2)
    return None

def post_json(url, payload, retries=2):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={**UA_API, "Content-Type": "application/json"},
                                         data=json.dumps(payload).encode())
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(2)
    return None

def bangumi_score(title):
    res = post_json("https://api.bgm.tv/v0/search/subjects?limit=5", {"keyword": title, "filter": {"type": [2]}})
    if not res:
        return None
    best = None
    for it in res.get("data", []):
        date = it.get("date") or ""
        r = it.get("rating") or {}
        cand = {"bgm_name": it.get("name"), "bgm_score": r.get("score"), "bgm_rank": r.get("rank"),
                "bgm_votes": r.get("total"), "bgm_date": date}
        if date.startswith(YEAR) and (r.get("total") or 0) >= 50:
            return cand
        if best is None:
            best = cand
    return best

ITEM_RE = re.compile(r'p-content-cassette__title[^>]*>([^<]+)<.*?c-rating__score">([\d.]+|-)<', re.S)

def filmarks_score(title, typ):
    paths = ["/search/animes"] if typ != "Movie" else ["/search/movies", "/search/animes"]
    for p in paths:
        q = urllib.parse.urlencode({"q": title})
        page = get(f"https://filmarks.com{p}?{q}", UA_WEB)
        if not page:
            continue
        items = ITEM_RE.findall(page)
        for name, score in items[:8]:
            name = html.unescape(name).strip()
            if score == "-":
                continue
            key = title.replace("。", "").replace(" ", "")[:6]
            if key and key in name.replace(" ", ""):
                return {"fm_name": name, "fm_score": float(score)}
        if items:
            name, score = items[0]
            if score != "-":
                return {"fm_name": html.unescape(name).strip() + " (首结果)", "fm_score": float(score)}
    return None

raw = json.load(open(f"anime_{YEAR}_raw.json", encoding="utf-8"))
excl = EXCLUDE.get(YEAR, set())
cands = []
for e in raw:
    t = e["title_jp"] or e["title"]
    if t in excl or (e["title"] or "") in excl:
        continue
    if e["type"] in ("Music", "CM", "PV"):
        continue
    if e["score"] and e["score"] >= 7.5 and (e["scored_by"] or 0) >= 1000:
        cands.append(e)
known = {(c["title_jp"] or c["title"]) for c in cands}
for t, typ in MANUAL_ADD.get(YEAR, []):
    hit = next((e for e in raw if t in (e["title_jp"] or e["title"] or "")), None)
    if hit and (hit["title_jp"] or hit["title"]) not in known:
        cands.append(hit)
    elif not hit:
        cands.append({"title_jp": t, "title": t, "type": typ, "score": None, "scored_by": None, "members": None})

print(f"候选 {len(cands)} 部，开始逐部查询 Bangumi + Filmarks ...", flush=True)
out = []
for i, e in enumerate(cands, 1):
    t = e["title_jp"] or e["title"]
    row = {"title_jp": t, "type": e["type"], "mal_score": e["score"], "mal_votes": e["scored_by"]}
    b = bangumi_score(t)
    if b: row.update(b)
    time.sleep(0.6)
    f = filmarks_score(t, e["type"])
    if f: row.update(f)
    time.sleep(0.6)
    out.append(row)
    print(f'[{i}/{len(cands)}] {t} | MAL={row.get("mal_score")} BGM={row.get("bgm_score")}({str(row.get("bgm_name",""))[:14]}) FM={row.get("fm_score")}({str(row.get("fm_name",""))[:14]})', flush=True)

with open(f"scores_{YEAR}.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp, ensure_ascii=False, indent=1)
print(f"\n已存 scores_{YEAR}.json")
