"""Assemble the new springs.church as one whole site from the page projects on the Desktop -> docs/ (static; GitHub Pages serves it).

The site opens on the Home page (Option I) and every page sits at its real springs.church address (/about/, /events/,
/plan-a-visit/ ...), all joined by the shared header and footer in chrome/ (Option I menu + SPRINGS. footer, mark centered).
Links to pages that are part of the redesign stay inside this site; links to pages that are already live and unchanged
(Sermons, Podcasts, Stories, Media, Bible App, the Kids/Youth/YA sites) go to the real ones.
Every HTML file gets noindex and robots.txt blocks crawlers: this is a draft for staff review, not the real website.
Before anything is published, the build scans the output for API keys and tokens and stops if it finds any.

usage: python3 build.py          (then open docs/index.html through any local server)
"""
import os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DESK = os.path.dirname(HERE)
OUT = os.path.join(HERE, "docs")  # GitHub Pages serves main:/docs
BASE = "/SpringsChurchWebsite/"   # GitHub Pages project path (used only by 404.html, which can be served at any depth)

# folder in the site (= the springs.church path), source project, entry file in it
PAGES = [
  ("",             "springs-home-site",     "option-i.html"),
  ("about",        "springs-about-site",    "preview-live.html"),
  ("plan-a-visit", "springs-visit-site",    "preview-live.html"),
  ("our-beliefs",  "springs-beliefs-site",  "preview-live.html"),
  ("our-staff",    "springs-staff-site",    "preview/d/index.html"),
  ("events",       "springs-events-site",   "preview-live.html"),
  ("connect",      "springs-connect-site",  "preview-live.html"),
  ("groups",       "springs-groups-site",   "preview-live.html"),
  ("serve",        "springs-serve-site",    "preview-live.html"),
  ("missions",     "springs-missions-site", "preview-live.html"),
  ("care",         "springs-care-site",     "preview-live.html"),
  ("prayer",       "springs-prayer-site",   "preview-live.html"),
  ("give",         "springs-give-site",     "preview-live.html"),
  ("contact-us",   "springs-contact-site",  "preview-live.html"),
  ("download-app", "springs-app-site",      "preview-live.html"),
]
ROUTES = {"/" + f if f else "/": f for f, _, _ in PAGES}
ROUTES["/new-here"] = "plan-a-visit"   # old Option I link
SECRET = re.compile(r"AIza[0-9A-Za-z_\-]{30,}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY|\"token\"\s*:\s*\"eyJ")
NOINDEX = '<meta name="robots" content="noindex,nofollow">'
FONT_FALLBACK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">'
DRAFT_NOTE = 'Draft of the new springs.church for staff review. Nothing here is live yet.'

CHROME_SRC = os.path.join(HERE, "chrome")
_ch = open(os.path.join(CHROME_SRC, "chrome.html"), encoding="utf-8").read()
CH_HEADER = _ch.split("<!--SC-HEADER-->")[1].split("<!--/SC-HEADER-->")[0]
CH_FOOTER = _ch.split("<!--SC-FOOTER-->")[1].split("<!--/SC-FOOTER-->")[0]


def target(path, depth):
    """A springs.church path -> a link inside this site (relative), or the live page if it isn't part of the redesign."""
    base, frag = (path.split("#", 1) + [""])[:2]
    base, query = (base.split("?", 1) + [""])[:2]
    key = base.rstrip("/") or "/"
    if key in ROUTES:
        up = "../" * depth
        f = ROUTES[key]
        return (up + (f + "/" if f else "") or "./") + (("?" + query) if query else "") + (("#" + frag) if frag else "")
    return "https://www.springs.church" + path


def rewrite_links(text, depth, js=False):
    text = re.sub(r'href="(/(?!/)[^"]*)"', lambda m: f'href="{target(m.group(1), depth)}"', text)
    text = re.sub(r'href="https?://(?:www\.)?springs\.church(/[^"]*)?"', lambda m: f'href="{target(m.group(1) or "/", depth)}"', text)
    if js:  # string literals in shared.js (Option I's link map)
        text = re.sub(r"(['\"])https?://(?:www\.)?springs\.church(/[^'\"]*)?\1", lambda m: m.group(1) + target(m.group(2) or "/", depth) + m.group(1), text)
    return text


def add_chrome(html, folder, depth):
    up = "../" * depth + "_chrome"
    if folder == "":  # Option I keeps its own header/footer: mark in the middle, "Media", Plan a Visit, draft note in the bar
        html = html.replace('<a class="logo" href="#" aria-label="Springs Church home"><img src="img/logo-white.png" alt="Springs Church"></a>',
                            '<a class="logo" href="./" aria-label="Springs Church home"><img src="img/mark-white.png" alt="Springs Church" style="width:46px;height:46px"></a>')
        html = re.sub(r'<a([^>]*)data-l="sermons"([^>]*)>Sermons</a>', r'<a\1data-l="media"\2>Media</a>', html)
        html = html.replace("https://www.springs.church/new-here", "/plan-a-visit")
        html = re.sub(r'(<div class="announce" id="announce">).*?(<button)', r'\g<1>' + DRAFT_NOTE + r'\2', html, count=1, flags=re.S)
        return html
    html = re.sub(r'<div class="topbar">.*?</div>', '', html, count=1, flags=re.S)
    html = re.sub(r'<footer class="cc-ftr">.*?</footer>', '', html, count=1, flags=re.S)
    if folder == "our-staff":
        html = re.sub(r'<header class="topbar">.*?</header>', '', html, count=1, flags=re.S)
        html = re.sub(r'<footer>[^<]*local mockup[^<]*</footer>', '', html, count=1, flags=re.S)
    html = html.replace("</head>", f'<link rel="stylesheet" href="{up}/chrome.css"></head>', 1)
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + CH_HEADER.replace("{CHROME}", up), html, count=1)
    i = html.rfind("</body>")
    return html[:i] + CH_FOOTER + f'<script src="{up}/chrome.js"></script>' + html[i:]


def finish_html(path, depth, folder=None):
    s = open(path, encoding="utf-8").read()
    if folder is not None:
        s = add_chrome(s, folder, depth)
    s = rewrite_links(s, depth)
    if "noindex" not in s:
        s = s.replace("<head>", "<head>" + NOINDEX + FONT_FALLBACK, 1) if "<head>" in s else NOINDEX + FONT_FALLBACK + s
    open(path, "w", encoding="utf-8").write(s)


def copy_page(folder, src, entry):
    srcdir = os.path.join(DESK, src)
    if not os.path.exists(os.path.join(srcdir, entry)):
        return False
    dst = os.path.join(OUT, folder) if folder else OUT
    depth = 1 if folder else 0
    os.makedirs(dst, exist_ok=True)
    shutil.copy(os.path.join(srcdir, entry), os.path.join(dst, "index.html"))
    if folder == "our-staff":  # mock ChurchCo page + the contributor stubs it fetches
        shutil.copytree(os.path.join(srcdir, "preview", "contributor"), os.path.join(dst, "contributor"), dirs_exist_ok=True)
        p = os.path.join(dst, "index.html")
        s = open(p, encoding="utf-8").read().replace("'/contributor/'", "'contributor/'").replace('"/contributor/', '"contributor/').replace("fetch('/contributor/", "fetch('contributor/")
        open(p, "w", encoding="utf-8").write(s)
        for root, _, files in os.walk(os.path.join(dst, "contributor")):
            for f in files:
                if f.endswith(".html"):
                    finish_html(os.path.join(root, f), os.path.relpath(root, OUT).count(os.sep) + 1)
    else:
        if os.path.exists(os.path.join(srcdir, "shared.js")):
            s = open(os.path.join(srcdir, "shared.js"), encoding="utf-8").read()
            s = rewrite_links(s, depth, js=True).replace("links: {", "links: {\n    media: 'https://www.springs.church/media',", 1)
            open(os.path.join(dst, "shared.js"), "w", encoding="utf-8").write(s)
        if os.path.isdir(os.path.join(srcdir, "img")):
            shutil.copytree(os.path.join(srcdir, "img"), os.path.join(dst, "img"), dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("src", "*-orig.*", "*.mov", "*.mp4", "*.psd", "*.tif", "*.ARW"))
    finish_html(os.path.join(dst, "index.html"), depth, folder)
    return True


def page_404():
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{NOINDEX}
<title>Page Not Found | Springs Church (draft)</title><link rel="stylesheet" href="https://use.typekit.net/ktn0utw.css">{FONT_FALLBACK}
<link rel="stylesheet" href="{BASE}_chrome/chrome.css"><style>body{{margin:0;background:#111;color:#fff;font:400 18px/1.6 'proxima-nova',system-ui,sans-serif}}
.nf{{min-height:70vh;display:grid;place-content:center;text-align:center;padding:160px 20px 80px}}.nf h1{{font:600 clamp(44px,7vw,84px)/.95 gotham,Montserrat,sans-serif;letter-spacing:-.03em;margin:0 0 16px}}
.nf p{{color:rgba(255,255,255,.75);margin:0 0 28px}}.nf a{{display:inline-flex;align-items:center;height:50px;padding:0 24px;border-radius:10px;background:#fff;color:#0E0E0E;font:700 13px/1 gotham,Montserrat,sans-serif;letter-spacing:.05em;text-transform:uppercase;text-decoration:none}}</style></head>
<body>{CH_HEADER.replace("{CHROME}", BASE + "_chrome")}<main class="nf"><h1>Page not found</h1><p>This page isn’t part of the draft site yet.</p><p><a href="{BASE}">Go to the home page</a></p></main>
{CH_FOOTER}<script src="{BASE}_chrome/chrome.js"></script></body></html>"""


def main():
    # Clear the old build but keep docs/data (written hourly by the CCB sync job) and any CNAME.
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name in ("data", "CNAME"): continue
        p = os.path.join(OUT, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(OUT, "_chrome"), exist_ok=True)
    for f in ("chrome.css", "chrome.js"): shutil.copy(os.path.join(CHROME_SRC, f), os.path.join(OUT, "_chrome", f))
    shutil.copy(os.path.join(DESK, "springs-home-site", "img", "mark-white.png"), os.path.join(OUT, "_chrome", "mark-white.png"))
    built = [f or "home" for f, s, e in PAGES if copy_page(f, s, e)]
    # 404.html: links must be absolute because GitHub serves it at whatever path was missing
    s404 = rewrite_links(page_404(), 0).replace('href="./', f'href="{BASE}')
    s404 = re.sub(r'href="(?!https?:|mailto:|tel:|/|#)([^"]*)"', lambda m: f'href="{BASE}{m.group(1)}"', s404)
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(s404)
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    hits = []
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith((".html", ".js", ".json", ".txt", ".css")):
                t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
                for m in SECRET.finditer(t): hits.append(f"{os.path.relpath(os.path.join(root, f), OUT)}: {m.group(0)[:12]}…")
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print("built:", ", ".join(built)); print("missing:", ", ".join((f or "home") for f, _, _ in PAGES if (f or "home") not in built) or "none")
    print(f"docs/ {size/1e6:.1f} MB")
    if hits:
        print("SECRET SCAN FAILED, do not publish:\n  " + "\n  ".join(hits)); sys.exit(1)
    print("secret scan: clean")


if __name__ == "__main__":
    main()
