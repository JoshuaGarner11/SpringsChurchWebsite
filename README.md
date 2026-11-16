# Springs site review (all redesigned pages in one place)

`python3 build.py` collects every page under review from its Desktop project into `docs/` (static HTML, no build tools):
the hub page (`docs/index.html`), one folder per page with its preview and images, noindex on every page, robots.txt that
blocks crawlers, and a key/token scan that stops the build if anything secret shows up. Local preview:
launch.json "springs-new-pages" → http://localhost:5220/review/ (the scratchpad web root links `review` → `docs/`).

Started 11/15/2026 after Josh asked about putting the whole site under review up on GitHub so people could review it.
Published 11/15/2026 to GitHub Pages from https://github.com/JoshuaGarner11/SpringsChurchWebsite (main, /docs).
Review site: https://joshuagarner11.github.io/SpringsChurchWebsite/

## Pages
The page list (title, source project, status) is `PAGES` in build.py. Trello card links are in NOTES.local.md, which stays off GitHub.

## How the build treats links
`href="/groups"` style site links point at the review copy when one exists (`../groups/`), otherwise at the live page
(`https://www.springs.church/sermons`). The Team mock's `/contributor/<slug>` stubs are copied in and its fetch path made relative.
Fonts: the Typekit kit (ktn0utw) is domain-locked, so on a new domain Gotham/Proxima fall back to Montserrat/system fonts
unless the review domain is added to the kit's allowed domains in Adobe Fonts.

## Publishing
- GitHub repo under JoshuaGarner11 (or a Springs org account), GitHub Pages serving `site/`.
- GitHub Pages sites are public even from a private repo. noindex + robots.txt keep it out of search, but anyone with the link can open it.
- Everything here is already public on springs.church or its review copies, but git keeps history, so anything pushed stays retrievable.
- Update = `python3 build.py` (secret scan must say clean) → commit → push.
- Later (Josh 11/15): the plan is to move springs.church off ChurchCo; this repo can grow into the real site project.

## CCB sync (calendar + groups)
CCB is the master calendar. `.github/workflows/ccb-sync.yml` runs `scripts/ccb_sync.py` every hour (and on demand from the
Actions tab) with the login in repo secrets `CCB_API_USER` / `CCB_API_PASS` (a website-only API user; the secrets are entered
by Josh in GitHub settings and are never in the code). It calls `public_calendar_listing` (today + 120 days) and
`group_search`, and writes `docs/data/events.json` and `docs/data/groups.json` only when the content changed.
Served at https://joshuagarner11.github.io/SpringsChurchWebsite/data/events.json (GitHub Pages allows cross-site reads,
so the ChurchCo Events block can use it via `data-events-src`).

Public-safe rules (the repo and the job logs are public): whitelisted fields only; no leader names, phones or emails;
events at a home (home groups, "Residence", or a non-church street address) dropped; venues are names only; descriptions
lose HTML and any email/phone that isn't the church's; kids and student groups left out of groups.json; the log prints counts.
Test the rules offline: `python3 scripts/test_ccb_sync.py scripts/ccb_sync.py`.
Before a local build + push, run `git pull --rebase` (the sync job commits to main). build.py keeps docs/data.
