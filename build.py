"""Assemble the springs.church review site from the page projects on the Desktop -> docs/ (static, no build tools; GitHub Pages serves it).

Every page under review gets its own folder with its preview (mock ChurchCo header + footer) and images. Site links like
href="/groups" are rewritten to the review copy when one exists, otherwise to the live springs.church page. Every HTML file
gets noindex, and robots.txt blocks crawlers: this is a review site, not the real one.
Before anything is published, the build scans the output for API keys and tokens and stops if it finds any.

usage: python3 build.py          (then open docs/index.html through any local server)
"""
import os, re, shutil, sys, json, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
DESK = os.path.dirname(HERE)
OUT = os.path.join(HERE, "docs")  # GitHub Pages serves main:/docs

# slug, title, source folder, entry file inside it, status shown to reviewers, what to look at, live path it would replace
PAGES = [
  ("home", "Home", "springs-home-site", "option-i.html", "Mockup · Option I", "Option I is the base. Open to small tweaks. \"Welcome home\" label is coming out.", "/"),
  ("about", "About", "springs-about-site", "preview-live.html", "New draft", "Vision, the four callings, the story since 2009, Connect Over Coffee, Plan a Visit.", "/about"),
  ("visit", "Plan a Visit", "springs-visit-site", "preview-live.html", "New draft", "Your first Sunday start to finish, and a short form that goes to the Connect Team.", "/plan-a-visit"),
  ("beliefs", "Our Beliefs", "springs-beliefs-site", "preview-live.html", "New draft", "Same Statement of Faith wording (elders approve any change). Only typo and citation fixes, highlighted.", "/our-beliefs"),
  ("team", "Our Team", "springs-staff-site", "preview/d/index.html", "Mockup · Option D", "Open Doors: arched portraits and the \"I'd like to talk with someone about…\" finder.", "/our-staff"),
  ("events", "Events", "springs-events-site", "preview-live.html", "New draft", "Reads ChurchCo's own events, so the calendar stays current on its own. Add to Calendar on every event.", "/events"),
  ("connect", "Connect", "springs-connect-site", "preview-live.html", "New draft", "Plan a Visit up top, an \"I'm looking for…\" chooser, and every ministry in one place.", "/connect"),
  ("groups", "Groups", "springs-groups-site", "preview-live.html", "New draft", "Group types straight into CCB, the FAQ, and Lead a Group.", "/groups"),
  ("serve", "Serve", "springs-serve-site", "preview-live.html", "Review copy on springs.church/servecopy", "Take your place: the week as a run of show, 20 teams, Apply opens the right form.", "/serve"),
  ("missions", "Missions", "springs-missions-site", "preview-live.html", "Review copy on springs.church/missionscopy", "Pray. Send. Go. Missionary cards, Pray This Week, give to a missionary.", "/missions"),
  ("care", "Care", "springs-care-site", "preview-live.html", "Review copy on springs.church/carecopy", "Care Team, Help in a Hard Season, mentorship, pop-up request forms.", "/care"),
  ("prayer", "Prayer", "springs-prayer-site", "preview-live.html", "Review copy on springs.church/prayercopy", "Wednesday prayer night and the prayer request form.", "/prayer"),
  ("give", "Give", "springs-give-site", "preview-live.html", "Review copy on springs.church/givecopy", "Give composer that fills in Pushpay for you. Tithing and Generosity copy unchanged.", "/give"),
  ("contact", "Contact Us", "springs-contact-site", "preview-live.html", "New draft", "Tap-to-call, open-now hours, and a message composer that reaches the right inbox.", "/contact-us"),
  ("app", "Download App", "springs-app-site", "preview-live.html", "New draft", "What's in the app, real screenshots, and Springs app vs. Bible App.", "/download-app"),
]
LIVE = [("Sermons", "/sermons"), ("Podcasts", "/podcasts"), ("Stories", "/stories"), ("Media", "/media"), ("Bible App", "/youversion"),
        ("Kids site", "https://kids.springs.church"), ("Youth site", "https://youth.springs.church"), ("Young Adults site", "https://ya.springs.church")]
ROUTES = {p[6]: p[0] for p in PAGES}
SECRET = re.compile(r"AIza[0-9A-Za-z_\-]{30,}|sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY|\"token\"\s*:\s*\"eyJ")
NOINDEX = '<meta name="robots" content="noindex,nofollow">'
FONT_FALLBACK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">'

CHROME_SRC = os.path.join(HERE, "chrome")
_ch = open(os.path.join(CHROME_SRC, "chrome.html"), encoding="utf-8").read()
CH_HEADER = _ch.split("<!--SC-HEADER-->")[1].split("<!--/SC-HEADER-->")[0]
CH_FOOTER = _ch.split("<!--SC-FOOTER-->")[1].split("<!--/SC-FOOTER-->")[0]

def add_chrome(html, slug):
    """Swap each preview's stand-in header/footer for the shared Springs chrome (Option I menu + SPRINGS. footer, mark centered)."""
    up = "../_chrome"
    if slug == "home":  # Option I already has this header/footer: use the mark in the middle and the Media label
        html = html.replace('<a class="logo" href="#" aria-label="Springs Church home"><img src="img/logo-white.png" alt="Springs Church"></a>',
                            '<a class="logo" href="#" aria-label="Springs Church home"><img src="img/mark-white.png" alt="Springs Church" style="width:46px;height:46px"></a>')
        html = re.sub(r'(<a[^>]*data-l="sermons"[^>]*>)Sermons(</a>)', r'\1Media\2', html)
        html = html.replace("https://www.springs.church/new-here", "/plan-a-visit")
        return html
    html = re.sub(r'<div class="topbar">.*?</div>', '', html, count=1, flags=re.S)
    html = re.sub(r'<footer class="cc-ftr">.*?</footer>', '', html, count=1, flags=re.S)
    if slug == "team":
        html = re.sub(r'<header class="topbar">.*?</header>', '', html, count=1, flags=re.S)
        html = re.sub(r'<footer>[^<]*local mockup[^<]*</footer>', '', html, count=1, flags=re.S)
    html = html.replace("</head>", f'<link rel="stylesheet" href="{up}/chrome.css"></head>', 1)
    html = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + CH_HEADER.replace("{CHROME}", up), html, count=1)
    i = html.rfind("</body>")
    html = html[:i] + CH_FOOTER + f'<script src="{up}/chrome.js"></script>' + html[i:]
    return html

def rewrite_links(html, depth):
    up = "../" * depth
    def fix(m):
        attr, path = m.group(1), m.group(2)
        base, frag = (path.split("#", 1) + [""])[:2]
        base = base.rstrip("/") or "/"
        if base in ROUTES:
            return f'{attr}="{up}{ROUTES[base]}/{("#" + frag) if frag else ""}"'
        return f'{attr}="https://www.springs.church{path}"'
    return re.sub(r'(href)="(/(?!/)[^"]*)"', fix, html)

def finish_html(path, depth, slug=None):
    s = open(path, encoding="utf-8").read()
    if slug: s = add_chrome(s, slug)
    s = rewrite_links(s, depth)
    if "noindex" not in s:
        s = s.replace("<head>", "<head>" + NOINDEX + FONT_FALLBACK, 1) if "<head>" in s else NOINDEX + FONT_FALLBACK + s
    open(path, "w", encoding="utf-8").write(s)

def copy_page(slug, src, entry):
    srcdir = os.path.join(DESK, src)
    dst = os.path.join(OUT, slug)
    if not os.path.exists(os.path.join(srcdir, entry)):
        return False
    os.makedirs(dst, exist_ok=True)
    if slug == "team":  # mock ChurchCo page + contributor stubs it fetches
        shutil.copy(os.path.join(srcdir, entry), os.path.join(dst, "index.html"))
        shutil.copytree(os.path.join(srcdir, "preview", "contributor"), os.path.join(dst, "contributor"), dirs_exist_ok=True)
        s = open(os.path.join(dst, "index.html"), encoding="utf-8").read().replace("'/contributor/'", "'contributor/'").replace('"/contributor/', '"contributor/').replace("fetch('/contributor/", "fetch('contributor/")
        open(os.path.join(dst, "index.html"), "w", encoding="utf-8").write(s)
        for root, _, files in os.walk(os.path.join(dst, "contributor")):
            for f in files:
                if f.endswith(".html"):
                    finish_html(os.path.join(root, f), os.path.relpath(root, OUT).count(os.sep) + 1)
    else:
        shutil.copy(os.path.join(srcdir, entry), os.path.join(dst, "index.html"))
        for extra in ("shared.js",):
            if os.path.exists(os.path.join(srcdir, extra)): shutil.copy(os.path.join(srcdir, extra), dst)
        if os.path.isdir(os.path.join(srcdir, "img")):
            shutil.copytree(os.path.join(srcdir, "img"), os.path.join(dst, "img"), dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("src", "*-orig.*", "*.mov", "*.mp4", "*.psd", "*.tif", "*.ARW"))
    finish_html(os.path.join(dst, "index.html"), 1, slug)
    return True

def hub(built):
    now = datetime.datetime.now().strftime("%B %-d, %Y")
    cards = "".join(
        f'<a class="card" href="{slug}/"><b>{title}</b><span class="st">{status}</span><p>{look}</p></a>'
        for slug, title, _, _, status, look, _ in PAGES if slug in built)
    live = "".join(f'<a href="{u if u.startswith("http") else "https://www.springs.church" + u}" target="_blank" rel="noopener">{t}</a>' for t, u in LIVE)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{NOINDEX}<title>Springs Site Review</title>{FONT_FALLBACK}<link rel="stylesheet" href="https://use.typekit.net/ktn0utw.css">
<style>:root{{--ink:#0E0E0E;--ink-2:#444;--gold:#D8C9A6;--gold-t:#7d6a3f;--sand:#F3EEE4;--hd:gotham,Montserrat,sans-serif;--bd:proxima-nova,system-ui,sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:#fff;color:var(--ink);font:400 18px/1.6 var(--bd);-webkit-font-smoothing:antialiased}}
header{{background:#111;color:#fff;padding:72px 0 64px}}.w{{max-width:1180px;margin:0 auto;padding:0 clamp(20px,5vw,40px)}}
h1{{font:600 clamp(40px,6vw,76px)/.95 var(--hd);letter-spacing:-.03em;margin:0 0 18px}}h1 i{{font-style:normal;color:var(--gold)}}
header p{{max-width:40em;color:rgba(255,255,255,.78);margin:0}}header small{{display:block;margin-top:18px;color:rgba(255,255,255,.5);font-size:15px}}
h2{{font:600 clamp(24px,2.6vw,32px)/1.1 var(--hd);text-transform:uppercase;letter-spacing:-.01em;margin:0 0 22px}}
main section{{padding:56px 0 8px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.card{{display:flex;flex-direction:column;gap:8px;padding:22px;border-radius:18px;background:var(--sand);color:inherit;text-decoration:none;transition:transform .3s cubic-bezier(.16,1,.3,1),background .2s}}
.card:hover{{transform:translateY(-3px);background:#ece5d6}}.card b{{font:600 22px/1.15 var(--hd)}}.card .st{{font:600 12px/1.3 var(--hd);letter-spacing:.04em;text-transform:uppercase;color:var(--gold-t)}}
.card p{{margin:0;font-size:16px;line-height:1.5;color:var(--ink-2)}}.live{{display:flex;flex-wrap:wrap;gap:10px}}
.live a{{display:inline-flex;align-items:center;min-height:42px;padding:0 16px;border-radius:999px;background:#fff;box-shadow:inset 0 0 0 1.5px rgba(14,14,14,.2);color:var(--ink);font:600 14px/1 var(--hd);text-decoration:none}}
.live a:hover{{background:var(--ink);color:#fff}}.how{{color:var(--ink-2);max-width:44em}}.how li{{margin:6px 0}}footer{{padding:64px 0 80px;color:#888;font-size:14px}}</style></head>
<body><header><div class="w"><h1>Springs site <i>review</i></h1>
<p>Every springs.church page that's being redesigned, in one place. Each page opens with a stand-in for the real site header and footer. Tap <b>Show to-confirm</b> on any page to highlight new wording and facts that still need a yes.</p>
<small>Drafts for staff review, not the live website. Updated {now}.</small></div></header>
<main class="w"><section><h2>Pages in review</h2><div class="grid">{cards}</div></section>
<section><h2>Already live</h2><div class="live">{live}</div></section>
<section><h2>How to review</h2><ul class="how"><li>Look at each page on your phone too. Most people visit on a phone.</li>
<li>Yellow highlights (Show to-confirm) are new words or facts. Tell Josh what's wrong or missing.</li>
<li>Forms, giving and some links go to the real systems (CCB, Pushpay). Please don't submit test forms.</li></ul></section></main>
<footer class="w">Springs Church · 1515 Auto Mall Loop, Colorado Springs, CO 80920</footer></body></html>"""

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
    built = [p[0] for p in PAGES if copy_page(p[0], p[2], p[3])]
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(hub(built))
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    hits = []
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith((".html", ".js", ".json", ".txt", ".css")):
                t = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
                for m in SECRET.finditer(t): hits.append(f"{os.path.relpath(os.path.join(root, f), OUT)}: {m.group(0)[:12]}…")
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print("built:", ", ".join(built)); print("missing:", ", ".join(p[0] for p in PAGES if p[0] not in built) or "none")
    print(f"docs/ {size/1e6:.1f} MB")
    if hits:
        print("SECRET SCAN FAILED, do not publish:\n  " + "\n  ".join(hits)); sys.exit(1)
    print("secret scan: clean")

if __name__ == "__main__":
    main()
