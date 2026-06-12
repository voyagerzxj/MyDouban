# YouTube 频道刷新脚本：抓取频道最新视频列表，把【新视频】追加到对应 md 表格顶部。
# 只新增行、重算统计行，绝不改动已有行的状态/日期/备注，所以和 Wiki.js 网页标记互不冲突。
#
# 用法（在仓库根目录）：
#   git pull                          # 先拉回 wiki 上的最新标记
#   python scripts/sync_channels.py   # 依赖：pip install yt-dlp
#   git add -A && git commit -m "刷新频道视频" && git push
#
# 新增频道：在 CHANNELS 里加一行，并按 youtube/ 下现有文件的格式建好对应 md。

import re
import sys
from pathlib import Path

import yt_dlp

CHANNELS = [
    ("https://www.youtube.com/@GeographyNow/videos", "youtube/geography-now.md"),
    ("https://www.youtube.com/@Leisadventure/videos", "youtube/lei-adventure.md"),
    ("https://www.youtube.com/@yuegemovie/videos", "youtube/yuege-movies.md"),
]

REPO_ROOT = Path(__file__).resolve().parent.parent
TABLE_SEP = "|---|---|---|---|"
STATS_RE = re.compile(r"^\*\*总计 \d+ · ✅ 已看 \d+\*\*$", re.M)
VIDEO_ID_RE = re.compile(r"watch\?v=([\w-]{6,})")


def esc(t):
    return (t.replace("\\", "\\\\")
             .replace("|", "\\|")
             .replace("[", "\\[")
             .replace("]", "\\]"))


def fetch_channel(url):
    opts = {"extract_flat": True, "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.sanitize_info(ydl.extract_info(url, download=False))
    videos = []
    for e in info.get("entries", []):
        vid, title = e.get("id"), (e.get("title") or "").strip()
        if vid and title:
            videos.append((vid, title))
    return videos  # 频道列表顺序：新→旧


def update_md(md_path, videos):
    text = md_path.read_text(encoding="utf-8")
    known = set(VIDEO_ID_RE.findall(text))
    new = [(vid, title) for vid, title in videos if vid not in known]

    if new:
        rows = "\n".join(
            f"| [{esc(title)}](https://www.youtube.com/watch?v={vid}) | ⬜ |  |  |"
            for vid, title in new
        )
        if TABLE_SEP not in text:
            sys.exit(f"错误：{md_path} 里找不到表格分隔行 {TABLE_SEP}")
        text = text.replace(TABLE_SEP, TABLE_SEP + "\n" + rows, 1)

    total = len(set(VIDEO_ID_RE.findall(text)))
    viewed = len(re.findall(r"\)\s*\|\s*✅\s*\|", text))
    text = STATS_RE.sub(f"**总计 {total} · ✅ 已看 {viewed}**", text, count=1)

    md_path.write_text(text, encoding="utf-8", newline="\n")
    return len(new), total, viewed


def main():
    for url, rel in CHANNELS:
        md_path = REPO_ROOT / rel
        print(f"抓取 {url} ...")
        videos = fetch_channel(url)
        added, total, viewed = update_md(md_path, videos)
        print(f"  {rel}: 新增 {added} 条（总计 {total} · 已看 {viewed}）")
    print("完成。检查无误后 git add / commit / push。")


if __name__ == "__main__":
    main()
