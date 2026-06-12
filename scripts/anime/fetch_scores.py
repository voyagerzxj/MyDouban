# -*- coding: utf-8 -*-
"""查询 Bangumi 和 MyAnimeList(Jikan) 的真实评分"""
import json, time, urllib.request, urllib.parse, sys

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "anime-yearly-list/1.0 (personal script)"}

TITLES = [
    ("タコピーの原罪", "Takopii no Genzai"),
    ("メダリスト", "Medalist TV"),
    ("アポカリプスホテル", "Apocalypse Hotel"),
    ("ダンダダン 第2期", "Dandadan 2nd Season"),
    ("薬屋のひとりごと 第2期", "Kusuriya no Hitorigoto 2nd Season"),
    ("ウマ娘 シンデレラグレイ", "Umamusume Cinderella Gray"),
    ("薫る花は凛と咲く", "Kaoru Hana wa Rin to Saku"),
    ("光が死んだ夏", "Hikaru ga Shinda Natsu"),
    ("劇場版チェンソーマン レゼ篇", "Chainsaw Man Movie Reze"),
    ("劇場版 鬼滅の刃 無限城編", "Kimetsu no Yaiba Mugen Jouhen"),
    ("ひゃくえむ。", "Hyakuemu"),
    ("瑠璃の宝石", "Ruri no Houseki"),
    ("ロックは淑女の嗜みでして", "Rock wa Lady no Tashinami deshite"),
    ("トリツカレ男", "Toritsukare Otoko"),
    ("ChaO", "ChaO"),
]

def get_json(url, data=None):
    req = urllib.request.Request(url, headers={**UA, "Content-Type": "application/json"},
                                 data=json.dumps(data).encode() if data else None)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def bangumi(kw):
    try:
        res = get_json("https://api.bgm.tv/v0/search/subjects?limit=3",
                       {"keyword": kw, "filter": {"type": [2]}})
        out = []
        for it in res.get("data", []):
            r = it.get("rating") or {}
            out.append(f'{it.get("name","?")} | score={r.get("score","-")} rank={r.get("rank","-")} votes={r.get("total","-")} | date={it.get("date","-")}')
        return out
    except Exception as e:
        return [f"ERROR {e}"]

def jikan(kw):
    try:
        q = urllib.parse.urlencode({"q": kw, "limit": 3})
        res = get_json(f"https://api.jikan.moe/v4/anime?{q}")
        out = []
        for it in res.get("data", []):
            out.append(f'{it.get("title","?")} | score={it.get("score","-")} members={it.get("members","-")} | {it.get("type","-")} {it.get("aired",{}).get("string","-")}')
        return out
    except Exception as e:
        return [f"ERROR {e}"]

for bgm_kw, mal_kw in TITLES:
    print(f"\n===== {bgm_kw} =====")
    for line in bangumi(bgm_kw):
        print("  BGM:", line)
    time.sleep(0.4)
    for line in jikan(mal_kw):
        print("  MAL:", line)
    time.sleep(0.7)
