#!/usr/bin/env python3
"""Maak per video een deelpagina (videos/<naam>.html) met Open Graph-tags.

Deel je zo'n link in WhatsApp of Signal, dan verschijnt een voorbeeld met
de poster van de video, de titel en een korte tekst. Wie erop tikt, ziet
de video direct.
"""
import json, pathlib, datetime
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://egelsindezijdes.nl/"
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]

PAGE = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} – Egels in de Zijdes</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{page}">
<meta property="og:type" content="video.other">
<meta property="og:site_name" content="Egels in de Zijdes">
<meta property="og:locale" content="nl_NL">
<meta property="og:title" content="🦔 {title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{page}">
<meta property="og:image" content="{poster}">
<meta property="og:image:secure_url" content="{poster}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="{title}">
<meta property="og:video" content="{video}">
<meta property="og:video:secure_url" content="{video}">
<meta property="og:video:type" content="video/mp4">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{poster}">
<style>
  :root{{--bg:#f6f1e7;--paper:#fffdf8;--ink:#2b2620;--muted:#6b6257;--moss:#4f6b3a;--moss-dark:#3a5229;--line:#e4dccd}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
  main{{max-width:760px;margin:0 auto;padding:24px 16px 48px}}
  a.home{{display:inline-block;margin-bottom:16px;font-weight:700;color:var(--moss-dark);text-decoration:none}}
  video{{width:100%;height:auto;display:block;border-radius:16px;background:#000;box-shadow:0 8px 24px rgba(43,38,32,.18)}}
  h1{{font-family:Georgia,serif;color:var(--moss-dark);font-size:1.7rem;line-height:1.2;margin:18px 0 4px}}
  time{{color:var(--muted)}}
  .btn{{display:inline-block;margin-top:20px;background:var(--moss);color:#fff;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700}}
  .btn:hover{{background:var(--moss-dark)}}
</style>
</head>
<body>
<main>
  <a class="home" href="../">🦔 Egels in de Zijdes</a>
  <video src="{video_rel}" poster="{poster_rel}" controls playsinline muted autoplay loop preload="metadata"></video>
  <h1>{title}</h1>
  <time datetime="{date}">{date_nl}</time>
  <p><a class="btn" href="../#videos">Bekijk alle video's</a></p>
</main>
</body>
</html>
"""


def date_nl(d):
    dt = datetime.datetime.strptime(d, "%Y-%m-%d")
    return f"{dt.day} {MAANDEN[dt.month - 1]} {dt.year}"


def main():
    items = json.loads((ROOT / "videos.json").read_text() or "[]")
    for v in items:
        mp4 = pathlib.Path(v["file"])
        page_rel = mp4.with_suffix(".html")
        poster = v.get("poster") or "og.jpg"
        html = PAGE.format(
            title=escape(v["title"]),
            desc=escape(f"Nieuwe egelvideo uit de Merenwijk, {date_nl(v['date'])}. Tik om te kijken!"),
            page=BASE + page_rel.as_posix(),
            poster=BASE + poster,
            video=BASE + mp4.as_posix(),
            video_rel=mp4.name,
            poster_rel=pathlib.Path(poster).name if v.get("poster") else "../og.jpg",
            date=v["date"],
            date_nl=date_nl(v["date"]),
        )
        (ROOT / page_rel).write_text(html)
    print(f"deelpagina's: {len(items)}")


if __name__ == "__main__":
    main()
