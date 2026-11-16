"""Keep the newest sermons current for the Home page: read the public "Sunday Sermons" YouTube playlist (newest first) and the top
few videos' public pages, then write docs/data/sermons.json when something changed. No login, no API key, read-only.

Runs from .github/workflows/sermon-sync.yml. If YouTube doesn't answer the way we expect (consent page, rate limit), it changes
nothing and the Home page keeps showing the last good list.
usage: python3 scripts/sermon_sync.py
"""
import datetime as dt, hashlib, json, os, re, sys, time, urllib.error, urllib.request

PLAYLIST = "PL0-75bzYYynk7GXBRfMBT-JD0AyuKTZIo"
TAKE = 4  # the featured sermon + the three before it
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data", "sermons.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def get(url, tries=3):
    for n in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code != 429 or n == tries - 1: raise
            time.sleep(15 * (n + 1))


def video(vid):
    h = get(f"https://www.youtube.com/watch?v={vid}")
    m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});(?:var|</script)", h, re.S)
    if not m: return None
    p = json.loads(m.group(1))
    vd = p.get("videoDetails") or {}
    mf = (p.get("microformat") or {}).get("playerMicroformatRenderer") or {}
    title, _, speaker = (vd.get("title") or "").partition(" | ")
    d = re.search(r"Sermon Date:\s*([A-Z][a-z]+ \d{1,2}, \d{4})", vd.get("shortDescription") or "")
    pub = (mf.get("publishDate") or "")[:10]
    date = d.group(1) if d else (dt.date.fromisoformat(pub).strftime("%B %-d, %Y") if pub else "")
    if not title or not vd.get("videoId"): return None
    return {"id": vid, "title": title.strip(), "speaker": speaker.strip(), "date": date, "published": pub,
            "thumb": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"}


def main():
    try:
        page = get(f"https://www.youtube.com/playlist?list={PLAYLIST}")
    except Exception as e:
        print("Couldn't read the playlist page:", type(e).__name__, "- keeping the last list."); return
    ids = list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', page)))
    if len(ids) < TAKE:
        print(f"Playlist page looked wrong ({len(ids)} videos found) - keeping the last list."); return
    items = []
    for vid in ids[:TAKE]:
        try:
            v = video(vid)
        except Exception as e:
            print("Couldn't read a video page:", type(e).__name__); v = None
        if v: items.append(v)
        time.sleep(1.5)
    if len(items) < TAKE:
        print(f"Only {len(items)} of {TAKE} videos read cleanly - keeping the last list."); return
    body = json.dumps(items, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    try:
        if json.load(open(OUT, encoding="utf-8")).get("hash") == digest:
            print("sermons.json unchanged; newest:", items[0]["title"]); return
    except (OSError, ValueError):
        pass
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": "YouTube playlist " + PLAYLIST + " via scripts/sermon_sync.py",
                   "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"), "hash": digest, "items": items},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("sermons.json updated; newest:", items[0]["title"], "|", items[0]["date"])


if __name__ == "__main__":
    main()
