"""Pull the public calendar and the group finder from CCB (Pushpay ChMS API v1) and write public-safe JSON for the website.

Runs in GitHub Actions (.github/workflows/ccb-sync.yml) with the login in repo secrets CCB_API_USER / CCB_API_PASS.
This repo is PUBLIC, so the output files and the job log are public too. The rules below keep it that way:
  - Only whitelisted fields are written. Leader names, phones and emails from CCB are never read into the output.
  - Events at a home (home groups, "Residence", or a street address that isn't the church) are dropped entirely.
  - Off-campus venues keep their name only ("Camp Elim"), never a street address. Campus rooms keep the room name.
  - Descriptions are stripped of HTML, and of any email or phone number that isn't the church's own.
  - Groups for kids and students are left out (those ministries have their own sites).
  - The log prints counts only, never names or values.
  - If CCB errors or returns nothing, the previous files are kept as they are.

usage: python3 scripts/ccb_sync.py --mode write     (writes docs/data/events.json + groups.json when the content changed)
       python3 scripts/ccb_sync.py --mode inspect   (prints field names and counts only; writes nothing)
"""
import argparse, base64, datetime as dt, hashlib, html, json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Denver")
SUB = os.environ.get("CCB_SUBDOMAIN", "springschurch")
API = f"https://{SUB}.ccbchurch.com/api.php"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data")
DAYS_AHEAD = 120

CHURCH_ADDR = re.compile(r"1515\s*auto\s*-?\s*mall", re.I)
HOME_WORDS = re.compile(r"\b(home\s*group|residence|house\s*church|home\b)", re.I)
STREET = re.compile(r"^\s*\d{2,6}\s+\w+")  # "6910 Bear Tooth..." style first segment
KIDS_YOUTH = re.compile(r"\b(kids?|children|nursery|youth|students?|middle\s*school|high\s*school|rooted|anthem|awaken|jr\.?\s*high|teen)\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
CHURCH_PHONE = re.compile(r"488[\s.-]?8331")


def call(srv, **params):
    user, pw = os.environ.get("CCB_API_USER"), os.environ.get("CCB_API_PASS")
    if not user or not pw:
        print("CCB_API_USER / CCB_API_PASS are not both set yet (add them as repository secrets). Skipping this run.")
        sys.exit(0)
    q = urllib.parse.urlencode({"srv": srv, **params})
    req = urllib.request.Request(f"{API}?{q}", headers={
        "Authorization": "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode(),
        "User-Agent": "springs-website-sync/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    err = root.find(".//errors/error")
    if err is not None:
        sys.exit(f"CCB returned an error for {srv}: code {err.get('number') or err.get('code') or '?'}")
    return root


def text(el, tag):
    x = el.find(tag)
    return (x.text or "").strip() if x is not None and x.text else ""


def clean_desc(s):
    s = html.unescape(re.sub(r"<br\s*/?>|</p>", "\n", s or "", flags=re.I))
    s = re.sub(r"<[^>]+>", "", s)
    s = EMAIL.sub(lambda m: m.group(0) if m.group(0).lower().endswith("@springs.church") else "", s)
    s = PHONE.sub(lambda m: m.group(0) if CHURCH_PHONE.search(m.group(0)) else "", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s).strip()
    return s[:1200]


def venue_of(loc):
    """Room or venue name only. Returns (venue, on_campus, looks_like_home)."""
    loc = html.unescape(loc or "").strip()
    if not loc:
        return "", True, False
    first = loc.split(",")[0].strip()
    on_campus = bool(CHURCH_ADDR.search(loc)) or first.lower() in ("springs church", "the springs church")
    homeish = bool(HOME_WORDS.search(loc)) or (not on_campus and bool(STREET.match(first)))
    if CHURCH_ADDR.search(first):  # location is just the church address
        first = "Springs Church"
    return first, on_campus, homeish


def iso(date_s, time_s):
    d = dt.datetime.strptime(f"{date_s} {time_s or '00:00:00'}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
    return d.isoformat()


def build_events(root, stats):
    out, seen = [], set()
    for it in root.iter("item"):
        title = text(it, "event_name")
        if not title:
            continue
        gname, gtype = text(it, "group_name"), text(it, "group_type")
        venue, on_campus, homeish = venue_of(text(it, "location"))
        if homeish or HOME_WORDS.search(f"{title} {gname} {gtype}"):
            stats["dropped_home"] += 1
            continue
        date_s, st, et = text(it, "date"), text(it, "start_time"), text(it, "end_time")
        try:
            start = iso(date_s, st)
            end = iso(date_s, et) if et and et != st else None
        except ValueError:
            stats["dropped_bad_date"] += 1
            continue
        all_day = (st in ("", "00:00:00") and (et in ("", "00:00:00", "23:59:00", "23:59:59")))
        ev_el = it.find("event_name")
        ccb_id = ev_el.get("ccb_id") if ev_el is not None else ""
        key = (ccb_id or title, start)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "id": f"{ccb_id}-{date_s}" if ccb_id else hashlib.sha1(f"{title}{start}".encode()).hexdigest()[:12],
            "title": title,
            "desc": clean_desc(text(it, "event_description")),
            "start": start, "end": end, "allDay": all_day,
            "venue": venue, "onCampus": on_campus,
            "group": gname, "category": text(it, "grouping_name") or gtype,
            "type": text(it, "event_type"),
        })
        stats["kept"] += 1
    out.sort(key=lambda e: (e["start"], e["title"]))
    return out


def build_groups(root, stats):
    out = []
    for it in root.iter("item"):
        name = text(it, "name")
        if not name:
            continue
        gtype, grouping, desc = text(it, "group_type_name"), text(it, "grouping_name"), text(it, "description")
        if KIDS_YOUTH.search(f"{name} {gtype} {grouping}"):
            stats["groups_dropped_kids_youth"] += 1
            continue
        area = it.find("area_name")
        out.append({
            "id": text(it, "id") or text(it, "item_id"),
            "name": re.sub(r"\*\*", "", name).strip(),
            "type": gtype, "department": grouping,
            "area": (area.text or "").strip() if area is not None and area.text else "",
            "day": text(it, "meet_day_name"), "time": text(it, "meet_time_name"),
            "membership": text(it, "membership_type"),
            "desc": clean_desc(desc),
        })
        stats["groups_kept"] += 1
    out.sort(key=lambda g: (g["type"], g["name"]))
    return out


def write_if_changed(name, items, meta):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    body = json.dumps(items, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    try:
        old = json.load(open(path, encoding="utf-8"))
        if old.get("hash") == digest:
            return False
    except (OSError, ValueError):
        pass
    doc = {"source": "CCB (Pushpay ChMS) via scripts/ccb_sync.py", "updated": dt.datetime.now(TZ).isoformat(timespec="minutes"),
           "hash": digest, **meta, "items": items}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["write", "inspect"], default="write")
    a = ap.parse_args()
    today = dt.datetime.now(TZ).date()
    end = today + dt.timedelta(days=DAYS_AHEAD)

    cal = call("public_calendar_listing", date_start=today.isoformat(), date_end=end.isoformat())
    grp = call("group_search", limit_records_per_page=500)

    if a.mode == "inspect":
        for label, root in (("public_calendar_listing", cal), ("group_search", grp)):
            items = list(root.iter("item"))
            tags = sorted({c.tag for i in items for c in i})
            print(f"{label}: {len(items)} items; fields: {', '.join(tags)}")
        return

    stats = {k: 0 for k in ("kept", "dropped_home", "dropped_bad_date", "groups_kept", "groups_dropped_kids_youth")}
    events = build_events(cal, stats)
    groups = build_groups(grp, stats)
    if not events and not groups:
        sys.exit("CCB returned no events and no groups; keeping the previous files.")
    ch_e = write_if_changed("events.json", events, {"range": [today.isoformat(), end.isoformat()], "timezone": "America/Denver"})
    ch_g = write_if_changed("groups.json", groups, {})
    print("events kept {kept}, dropped at a home {dropped_home}, bad dates {dropped_bad_date}; "
          "groups kept {groups_kept}, kids/youth left out {groups_dropped_kids_youth}".format(**stats))
    print("events.json", "updated" if ch_e else "unchanged", "| groups.json", "updated" if ch_g else "unchanged")


if __name__ == "__main__":
    main()
