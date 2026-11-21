#!/usr/bin/env python3
"""Maak feed.xml (RSS) uit videos.json."""
import json, pathlib, datetime
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://egelsindezijdes.nl/"

def rfc822(d):
    dt = datetime.datetime.strptime(d, "%Y-%m-%d").replace(hour=21, tzinfo=datetime.timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

items = json.loads((ROOT / "videos.json").read_text() or "[]")
items.sort(key=lambda v: v.get("date", ""), reverse=True)
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
       '<title>Egels in de Zijdes – nieuwe video\'s</title>',
       f'<link>{BASE}</link>',
       f'<atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>',
       '<description>Nieuwe egelvideo\'s uit de tuinen in de Merenwijk, Leiden.</description>',
       '<language>nl</language>']
for v in items:
    url = BASE + v["file"]
    poster = BASE + v["poster"] if v.get("poster") else ""
    desc = f'<p>Nieuwe egelvideo: {escape(v["title"])}</p>'
    if poster:
        desc += f'<p><a href="{BASE}#videos"><img src="{poster}" alt="" width="480"></a></p>'
    desc += f'<p><a href="{BASE}#videos">Bekijk de video op egelsindezijdes.nl</a></p>'
    size = (ROOT / v["file"]).stat().st_size if (ROOT / v["file"]).exists() else 0
    out += ['<item>', f'<title>{escape(v["title"])}</title>', f'<link>{BASE}#videos</link>',
            f'<guid isPermaLink="false">{escape(v["driveId"])}</guid>',
            f'<pubDate>{rfc822(v["date"])}</pubDate>',
            f'<description>{escape(desc)}</description>',
            f'<enclosure url="{url}" length="{size}" type="video/mp4"/>', '</item>']
out += ['</channel>', '</rss>']
(ROOT / "feed.xml").write_text("\n".join(out) + "\n")
print(f"feed.xml: {len(items)} video's")
