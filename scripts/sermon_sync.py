"""Keep the newest sermons current for the Home page: read the public "Sunday Sermons" YouTube playlist (newest first), the top
few videos' public pages, and the channel's Live tab (for each sermon's "Full Service | <title> | <date>" stream), then write
docs/data/sermons.json when something changed. No login, no API key, read-only.

Runs from .github/workflows/sermon-sync.yml. If YouTube doesn't answer the way we expect (consent page, rate limit), it changes
nothing and the Home page keeps showing the last good list.
usage: python3 scripts/sermon_sync.py
"""
import datetime as dt, hashlib, html, json, os, re, sys, time, urllib.error, urllib.request

PLAYLIST = "PL0-75bzYYynk7GXBRfMBT-JD0AyuKTZIo"
STREAMS = "https://www.youtube.com/@springs.church/streams"
SITE = "https://www.springs.church/"   # the live ChurchCo site; its hero carries the week's sermon photo
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


def playlist_items_raw(page):
    """newest-first lockups on a playlist or channel tab page: id, full title, metadata parts"""
    m = re.search(r"var ytInitialData\s*=\s*(\{.+?\});</script>", page, re.S)
    if not m: return []
    found = []
    def walk(x):
        if isinstance(x, dict):
            if "lockupViewModel" in x: found.append(x["lockupViewModel"])
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(json.loads(m.group(1)))
    out = []
    for v in found:
        md = ((v.get("metadata") or {}).get("lockupMetadataViewModel") or {})
        rows = (((md.get("metadata") or {}).get("contentMetadataViewModel") or {}).get("metadataRows") or [])
        parts = [((p.get("text") or {}).get("content") or "") for r in rows for p in (r.get("metadataParts") or [])]
        title = ((md.get("title") or {}).get("content") or "").strip()
        if v.get("contentId") and title:
            out.append({"id": v["contentId"], "title": title, "parts": parts})
    return out


def playlist_items(page):
    """newest-first entries from the playlist page itself: id, title, speaker and YouTube's "8h ago" style age"""
    out = []
    for e in playlist_items_raw(page):
        title, _, speaker = e["title"].partition(" | ")
        age = next((x for x in e["parts"] if re.search(r"\bago$", x)), "")
        out.append({"id": e["id"], "title": title.strip(), "speaker": speaker.strip(), "age": age})
    return out


def norm(t):
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower().replace("\u2019", "'"))


def full_services(page):
    """{normalized sermon title: stream id} for finished "Full Service | <title> | <date>" streams on the Live tab
    (skips upcoming and still-live ones, which have no "Streamed ..." line yet)"""
    out = {}
    for e in playlist_items_raw(page):
        parts = [p.strip() for p in e["title"].split("|")]
        if len(parts) >= 2 and parts[0].lower() == "full service" and any(x.startswith("Streamed") for x in e["parts"]):
            out.setdefault(norm(parts[1]), e["id"])
    return out


def live_sermon_photo():
    """the photo on the live springs.church hero (the image ChurchCo preloads with high priority). While ChurchCo is live,
    staff swap it every week, so Home's sermon panel follows it."""
    page = get(SITE)
    for tag in re.findall(r"<link\b[^>]*>", page):
        if 'rel="preload"' in tag and 'as="image"' in tag and re.search(r'fetch[Pp]riority="high"', tag):
            m = re.search(r'href="(https://[^"]+)"', tag)
            if m and re.search(r"\.(jpe?g|png|webp)$", html.unescape(m.group(1)), re.I):
                return html.unescape(m.group(1))
    return None


def sunday_from_age(age):
    """'8h ago' / '7d ago' / '2w ago' / '1mo ago' -> the Sunday on or before that day (Colorado time), as 'November 15, 2026'"""
    m = re.match(r"(\d+)\s*(mo|min|s|m|h|d|w|y)", age or "")   # "mo" before "m", or "1mo" reads as one minute
    if not m: return ""
    n, unit = int(m.group(1)), m.group(2)
    days = {"s": 0, "m": 0, "min": 0, "h": n / 24, "d": n, "w": 7 * n, "mo": 30 * n, "y": 365 * n}[unit]
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=-7)))
    day = (now - dt.timedelta(days=days)).date()
    day -= dt.timedelta(days=(day.weekday() + 1) % 7)   # back to Sunday
    return day.strftime("%B %-d, %Y")


def main():
    try:
        page = get(f"https://www.youtube.com/playlist?list={PLAYLIST}")
    except Exception as e:
        print("Couldn't read the playlist page:", type(e).__name__, "- keeping the last list."); return
    top = playlist_items(page)[:TAKE]
    if len(top) < TAKE:
        print(f"Playlist page looked wrong ({len(top)} entries) - keeping the last list."); return
    try:
        prev = json.load(open(OUT, encoding="utf-8"))
    except (OSError, ValueError):
        prev = {}
    old = {i["id"]: i for i in prev.get("items", [])}
    try:
        photo = live_sermon_photo()
    except Exception as e:
        print("Couldn't read springs.church:", type(e).__name__); photo = None
    photo = photo or prev.get("photo")
    try:
        services = full_services(get(STREAMS))
    except Exception as e:
        print("Couldn't read the Live tab:", type(e).__name__, "- keeping the last Full Service links."); services = {}
    print(f"Live tab: {len(services)} Full Service streams; springs.church photo: {'found' if photo else 'none'}")
    items, exact, estimated = [], 0, 0
    for e in top:
        if e["id"] in old and old[e["id"]].get("date"):
            date = old[e["id"]]["date"]
        else:
            v = None
            try: v = video(e["id"])
            except Exception: pass
            if v and v.get("date"): date = v["date"]; exact += 1
            else: date = sunday_from_age(e["age"]); estimated += 1
            time.sleep(1.5)
        item = {"id": e["id"], "title": e["title"], "speaker": e["speaker"], "date": date,
                "thumb": f"https://i.ytimg.com/vi/{e['id']}/hqdefault.jpg"}
        service = services.get(norm(e["title"])) or (old.get(e["id"]) or {}).get("service")
        if service: item["service"] = service   # the "Full Service" livestream of that Sunday
        items.append(item)
    body = json.dumps({"items": items, "photo": photo}, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    if prev.get("hash") == digest:
        print("sermons.json unchanged; newest:", items[0]["title"]); return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": "YouTube playlist " + PLAYLIST + " via scripts/sermon_sync.py",
                   "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"), "hash": digest,
                   "photo": photo, "items": items},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"sermons.json updated; newest: {items[0]['title']} | {items[0]['date']} (new dates: {exact} exact, {estimated} from upload age)")


if __name__ == "__main__":
    main()
