#!/usr/bin/env python3
"""Voeg een video toe aan de site.

Gebruik:
  python3 scripts/add_video.py <bronbestand> --drive-id ID --date JJJJ-MM-DD [--title "Titel"]

Comprimeert de video naar max. 720p H.264 (zonder geluid weg te halen),
maakt een posterafbeelding en zet een regel in videos.json.
Slaat over als de drive-id al in videos.json staat.
"""
import argparse, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "videos"
INDEX = ROOT / "videos.json"
MAX_MB = 95  # GitHub weigert bestanden boven 100 MB


def slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:40] or "egel"


def encode(src, dst, crf):
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
        "-vf", "scale='min(1280,iw)':-2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart", str(dst)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--drive-id", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--title", default="")
    a = ap.parse_args()

    items = json.loads(INDEX.read_text() or "[]")
    if any(i.get("driveId") == a.drive_id for i in items):
        print("al aanwezig, overgeslagen")
        return

    name = f"{a.date}-{slug(a.title or "egel")}-{a.drive_id[:6]}"
    mp4 = VIDEOS / f"{name}.mp4"
    jpg = VIDEOS / f"{name}.jpg"

    for crf in (26, 30, 34):
        encode(a.src, mp4, crf)
        if mp4.stat().st_size / 1e6 <= MAX_MB:
            break
    else:
        mp4.unlink(missing_ok=True)
        sys.exit("video blijft te groot na compressie")

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", str(mp4),
                    "-frames:v", "1", "-q:v", "4", str(jpg)], check=False)

    items.append({
        "driveId": a.drive_id,
        "date": a.date,
        "title": a.title or "Egelbezoek",
        "file": f"videos/{mp4.name}",
        "poster": f"videos/{jpg.name}" if jpg.exists() else "",
    })
    INDEX.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    print(f"toegevoegd: {mp4.name} ({mp4.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
