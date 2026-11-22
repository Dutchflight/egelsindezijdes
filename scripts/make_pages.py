#!/usr/bin/env python3
"""Maak per video een deelpagina (videos/<naam>.html) met Open Graph-tags.

Deel je zo'n link in WhatsApp of Signal, dan verschijnt een voorbeeld met
de poster van de video, de titel en een korte tekst. Wie erop tikt, ziet
de video direct.
"""
import json, pathlib, datetime, subprocess
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


def duration(mp4):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(mp4)], capture_output=True, text=True).stdout
        sec = round(float(out.strip()))
        return f"{sec // 60}:{sec % 60:02d}"
    except Exception:
        return ""


def make_thumb(poster, mp4, dst):
    """Poster met afspeelknop en videobalk, zodat het voorbeeld in WhatsApp op een video lijkt."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    im = Image.open(poster).convert("RGB")
    w = 960
    im = im.resize((w, round(im.height * w / im.width)))
    W, H = im.size
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for y in range(H // 3):  # donkere strook onderaan
        a = int(150 * y / (H // 3))
        d.line([(0, H - H // 3 + y), (W, H - H // 3 + y)], fill=(0, 0, 0, a))
    r = H // 7
    cx, cy = W // 2, H // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, 140), outline=(255, 255, 255, 230), width=max(3, r // 14))
    t = r * 0.5
    d.polygon([(cx - t * 0.7, cy - t), (cx - t * 0.7, cy + t), (cx + t, cy)], fill=(255, 255, 255, 240))
    m = W // 30
    bar_y = H - m
    d.rounded_rectangle([m, bar_y - 4, W - m, bar_y + 2], radius=3, fill=(255, 255, 255, 110))
    lbl = duration(mp4)
    if lbl:
        try:
            f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", H // 16)
        except OSError:
            f = ImageFont.load_default()
        d.text((m, bar_y - 14), "\u25B6  " + lbl, font=f, fill=(255, 255, 255, 240), anchor="lb")
    Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB").save(dst, quality=82)
    return True


def main():
    items = json.loads((ROOT / "videos.json").read_text() or "[]")
    for v in items:
        mp4 = pathlib.Path(v["file"])
        page_rel = mp4.with_suffix(".html")
        poster = v.get("poster") or "og.jpg"
        share_img = poster
        if v.get("poster"):
            thumb = mp4.with_name(mp4.stem + "-voorbeeld.jpg")
            if make_thumb(ROOT / v["poster"], ROOT / mp4, ROOT / thumb):
                share_img = thumb.as_posix()
        html = PAGE.format(
            title=escape(v["title"]),
            desc=escape(f"Nieuwe egelvideo uit de Merenwijk, {date_nl(v['date'])}. Tik om te kijken!"),
            page=BASE + page_rel.as_posix(),
            poster=BASE + share_img,
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
